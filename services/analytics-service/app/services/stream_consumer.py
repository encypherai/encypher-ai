"""
Redis Stream Consumer for Analytics Service.

Consumes metric events from Redis Streams and persists them to the database.
Uses consumer groups for reliable, scalable processing.

Features:
- Consumer groups: Multiple instances can process in parallel
- Acknowledgment: Events are only removed after successful processing
- Retry: Failed events are automatically retried
- Batching: Processes events in batches for efficiency
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..core.config import settings
from ..db.models import UsageMetric
from ..db.session import SessionLocal

logger = logging.getLogger(__name__)


class StreamConsumer:
    """
    Redis Stream consumer for processing metric events.
    
    Uses consumer groups for reliable, distributed processing.
    """
    
    # Stream and consumer group names
    STREAM_NAME = "encypher:metrics:events"
    CONSUMER_GROUP = "analytics-service"
    
    # Processing settings
    BATCH_SIZE = 100
    BLOCK_MS = 5000  # Block for 5 seconds waiting for new messages
    RETRY_DELAY_MS = 1000
    
    def __init__(
        self,
        redis_url: str = None,
        consumer_name: str = None,
    ):
        """
        Initialize stream consumer.
        
        Args:
            redis_url: Redis connection URL
            consumer_name: Unique name for this consumer instance
        """
        self.redis_url = redis_url or getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        self.consumer_name = consumer_name or f"consumer-{uuid4().hex[:8]}"
        self._redis: Optional[Any] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
    async def connect(self) -> bool:
        """
        Connect to Redis and create consumer group.
        
        Returns:
            True if connected successfully
        """
        try:
            import redis.asyncio as redis
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            
            # Create consumer group if it doesn't exist
            try:
                await self._redis.xgroup_create(
                    self.STREAM_NAME,
                    self.CONSUMER_GROUP,
                    id="0",  # Start from beginning
                    mkstream=True,  # Create stream if it doesn't exist
                )
                logger.info(f"Created consumer group: {self.CONSUMER_GROUP}")
            except Exception as e:
                if "BUSYGROUP" in str(e):
                    logger.debug(f"Consumer group already exists: {self.CONSUMER_GROUP}")
                else:
                    raise
            
            logger.info(f"Stream consumer connected: {self.consumer_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect stream consumer: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Stop consumer and close Redis connection."""
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
            logger.info("Stream consumer disconnected")
    
    async def start(self) -> None:
        """Start consuming messages in the background."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._consume_loop())
        logger.info(f"Stream consumer started: {self.consumer_name}")
    
    async def stop(self) -> None:
        """Stop consuming messages."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Stream consumer stopped")
    
    async def _consume_loop(self) -> None:
        """Main consumption loop."""
        while self._running:
            try:
                # First, claim any pending messages that weren't acknowledged
                await self._process_pending()
                
                # Then read new messages
                messages = await self._redis.xreadgroup(
                    groupname=self.CONSUMER_GROUP,
                    consumername=self.consumer_name,
                    streams={self.STREAM_NAME: ">"},  # Only new messages
                    count=self.BATCH_SIZE,
                    block=self.BLOCK_MS,
                )
                
                if messages:
                    for stream_name, stream_messages in messages:
                        await self._process_batch(stream_messages)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in consume loop: {e}")
                await asyncio.sleep(1)  # Brief pause before retry
    
    async def _process_pending(self) -> None:
        """Process any pending messages that weren't acknowledged."""
        try:
            # Get pending messages for this consumer
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
            
            # Claim and process pending messages
            message_ids = [p["message_id"] for p in pending]
            claimed = await self._redis.xclaim(
                self.STREAM_NAME,
                self.CONSUMER_GROUP,
                self.consumer_name,
                min_idle_time=self.RETRY_DELAY_MS,
                message_ids=message_ids,
            )
            
            if claimed:
                await self._process_batch(claimed)
                logger.info(f"Processed {len(claimed)} pending messages")
                
        except Exception as e:
            logger.error(f"Error processing pending messages: {e}")
    
    async def _process_batch(self, messages: List) -> None:
        """
        Process a batch of messages and persist to database.
        
        Args:
            messages: List of (message_id, data) tuples
        """
        if not messages:
            return
        
        db = SessionLocal()
        processed_ids = []
        
        try:
            for message_id, data in messages:
                try:
                    metric = self._parse_metric(data)
                    if metric:
                        db.add(metric)
                        processed_ids.append(message_id)
                except Exception as e:
                    logger.error(f"Error parsing message {message_id}: {e}")
                    # Still acknowledge to avoid infinite retry
                    processed_ids.append(message_id)
            
            # Commit all metrics
            db.commit()
            
            # Acknowledge processed messages
            if processed_ids:
                await self._redis.xack(
                    self.STREAM_NAME,
                    self.CONSUMER_GROUP,
                    *processed_ids,
                )
                logger.debug(f"Processed and acknowledged {len(processed_ids)} messages")
                
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _parse_metric(self, data: Dict[str, Any]) -> Optional[UsageMetric]:
        """
        Parse message data into a UsageMetric model.
        
        Args:
            data: Message data dictionary
            
        Returns:
            UsageMetric instance or None if invalid
        """
        def _coerce_int(value: Any) -> Optional[int]:
            if value is None:
                return None
            if isinstance(value, bool):
                return int(value)
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return int(round(value))
            if isinstance(value, str):
                stripped = value.strip()
                if not stripped:
                    return None
                try:
                    return int(stripped)
                except ValueError:
                    try:
                        return int(round(float(stripped)))
                    except ValueError:
                        return None
            return None

        try:
            # Extract required fields
            metric_type = data.get("metric_type")
            organization_id = data.get("organization_id")
            
            if not metric_type or not organization_id:
                logger.warning(f"Missing required fields in metric: {data}")
                return None
            
            # Parse timestamp
            timestamp_str = data.get("timestamp")
            if timestamp_str:
                try:
                    created_at = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                except ValueError:
                    created_at = datetime.utcnow()
            else:
                created_at = datetime.utcnow()
            
            # Parse metadata
            metadata = data.get("metadata")
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    metadata = None
            
            # Create metric
            return UsageMetric(
                id=data.get("event_id", str(uuid4())),
                user_id=data.get("user_id") or organization_id,
                organization_id=organization_id,
                metric_type=metric_type,
                service_name=data.get("service_name", "enterprise-api"),
                endpoint=data.get("endpoint"),
                count=1,
                value=None,
                response_time_ms=_coerce_int(data.get("response_time_ms")),
                status_code=_coerce_int(data.get("status_code")),
                meta=metadata,
                date=created_at.strftime("%Y-%m-%d"),
                hour=created_at.hour,
            )
            
        except Exception as e:
            logger.error(f"Error parsing metric: {e}")
            return None


# Global consumer instance
_stream_consumer: Optional[StreamConsumer] = None


def get_stream_consumer() -> Optional[StreamConsumer]:
    """Get the global stream consumer instance."""
    return _stream_consumer


async def start_stream_consumer(redis_url: str = None) -> StreamConsumer:
    """Start the global stream consumer."""
    global _stream_consumer
    
    if _stream_consumer is None:
        _stream_consumer = StreamConsumer(redis_url=redis_url)
        await _stream_consumer.connect()
        await _stream_consumer.start()
    
    return _stream_consumer


async def stop_stream_consumer() -> None:
    """Stop the global stream consumer."""
    global _stream_consumer
    
    if _stream_consumer:
        await _stream_consumer.stop()
        await _stream_consumer.disconnect()
        _stream_consumer = None
