"""Redis Stream consumer for error events from MetricsMiddleware."""

import asyncio
import json
import logging
from typing import Any, Optional
from uuid import uuid4

from ..core.config import settings
from ..db.session import SessionLocal
from .incident_service import ingest_error_event
from .discord_notifier import notify_new_incident

logger = logging.getLogger(__name__)


class AlertStreamConsumer:
    """Consumes metric events from the shared Redis Stream, filtering for errors."""

    STREAM_NAME = "encypher:metrics:events"
    CONSUMER_GROUP = "alert-service"
    BATCH_SIZE = 50
    BLOCK_MS = 5000

    def __init__(self, redis_url: str = None, consumer_name: str = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.consumer_name = consumer_name or f"alert-{uuid4().hex[:8]}"
        self._redis: Optional[Any] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        try:
            import redis.asyncio as redis

            self._redis = await redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
            await self._redis.ping()

            try:
                await self._redis.xgroup_create(self.STREAM_NAME, self.CONSUMER_GROUP, id="0", mkstream=True)
                logger.info("Created consumer group: %s", self.CONSUMER_GROUP)
            except Exception as e:
                if "BUSYGROUP" in str(e):
                    logger.debug("Consumer group already exists: %s", self.CONSUMER_GROUP)
                else:
                    raise

            logger.info("Alert stream consumer connected: %s", self.consumer_name)
            return True
        except Exception as e:
            logger.error("Failed to connect alert stream consumer: %s", e)
            return False

    async def disconnect(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Alert stream consumer disconnected")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Alert stream consumer started: %s", self.consumer_name)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Alert stream consumer stopped")

    async def _consume_loop(self) -> None:
        while self._running:
            try:
                # Process any pending (unacked) messages first
                await self._process_pending()

                messages = await self._redis.xreadgroup(
                    groupname=self.CONSUMER_GROUP,
                    consumername=self.consumer_name,
                    streams={self.STREAM_NAME: ">"},
                    count=self.BATCH_SIZE,
                    block=self.BLOCK_MS,
                )
                if messages:
                    for _stream_name, stream_messages in messages:
                        await self._process_batch(stream_messages)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in alert consume loop: %s", e)
                await asyncio.sleep(2)

    async def _process_pending(self) -> None:
        try:
            pending = await self._redis.xpending_range(
                self.STREAM_NAME,
                self.CONSUMER_GROUP,
                min="-",
                max="+",
                count=self.BATCH_SIZE,
                consumername=self.consumer_name,
            )
            if not pending:
                return
            message_ids = [p["message_id"] for p in pending]
            claimed = await self._redis.xclaim(
                self.STREAM_NAME,
                self.CONSUMER_GROUP,
                self.consumer_name,
                min_idle_time=5000,
                message_ids=message_ids,
            )
            if claimed:
                await self._process_batch(claimed)
        except Exception as e:
            logger.error("Error processing pending messages: %s", e)

    async def _process_batch(self, messages: list) -> None:
        if not messages:
            return

        ack_ids = []
        for message_id, data in messages:
            try:
                if self._is_error_event(data):
                    await self._handle_error_event(data)
                ack_ids.append(message_id)
            except Exception as e:
                logger.error("Error processing message %s: %s", message_id, e)
                ack_ids.append(message_id)  # Ack to prevent infinite retry

        if ack_ids:
            await self._redis.xack(self.STREAM_NAME, self.CONSUMER_GROUP, *ack_ids)

    def _is_error_event(self, data: dict) -> bool:
        """Filter for error events worth tracking."""
        status_code = data.get("status_code")
        if status_code:
            try:
                code = int(status_code)
                if code >= 400:
                    return True
            except (ValueError, TypeError):
                pass

        metric_type = data.get("metric_type", "")
        if metric_type in ("error", "rate_limit"):
            return True

        if data.get("error_code") or data.get("error_message"):
            return True

        return False

    async def _handle_error_event(self, data: dict) -> None:
        """Process a single error event into the incident system."""
        metadata = data.get("metadata")
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {}
        elif not isinstance(metadata, dict):
            metadata = {}

        error_code = data.get("error_code") or metadata.get("error_code", "")
        error_message = data.get("error_message") or metadata.get("error_message", "")
        stack_trace = metadata.get("error_stack") or metadata.get("error_details")

        status_code = None
        if data.get("status_code"):
            try:
                status_code = int(data["status_code"])
            except (ValueError, TypeError):
                pass

        if not error_code and status_code:
            error_code = f"HTTP_{status_code}"

        db = SessionLocal()
        try:
            incident, is_new, should_notify = ingest_error_event(
                db=db,
                source="redis_stream",
                service_name=data.get("service_name", "unknown"),
                endpoint=data.get("endpoint", ""),
                error_code=error_code,
                error_message=error_message,
                status_code=status_code,
                organization_id=data.get("organization_id"),
                user_id=data.get("user_id"),
                request_id=data.get("request_id") or data.get("event_id"),
                stack_trace=stack_trace,
                raw_payload=data,
            )

            if is_new:
                logger.info("New incident created: %s - %s", incident.id, incident.title)
            if should_notify:
                await notify_new_incident(incident, db)
        except Exception as e:
            logger.error("Failed to ingest error event: %s", e)
            db.rollback()
        finally:
            db.close()


# Global consumer instance
_consumer: Optional[AlertStreamConsumer] = None


async def start_alert_consumer(redis_url: str = None) -> AlertStreamConsumer:
    global _consumer
    if _consumer is None:
        _consumer = AlertStreamConsumer(redis_url=redis_url)
        await _consumer.connect()
        await _consumer.start()
    return _consumer


async def stop_alert_consumer() -> None:
    global _consumer
    if _consumer:
        await _consumer.stop()
        await _consumer.disconnect()
        _consumer = None
