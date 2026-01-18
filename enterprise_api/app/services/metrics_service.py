"""
Metrics Service for Enterprise API.

Provides non-blocking metrics collection using Redis Streams.
Metrics are consumed by the analytics-service for aggregation.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, cast
from uuid import uuid4

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics that can be recorded."""

    API_CALL = "api_call"
    DOCUMENT_SIGNED = "document_signed"
    DOCUMENT_VERIFIED = "document_verified"
    BATCH_OPERATION = "batch_operation"
    STREAMING_SESSION = "streaming_session"
    MERKLE_ENCODE = "merkle_encode"
    LOOKUP = "lookup"
    ERROR = "error"
    RATE_LIMIT = "rate_limit"


@dataclass
class MetricEvent:
    """A single metric event to be recorded."""

    metric_type: MetricType
    organization_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = field(default_factory=lambda: str(uuid4()))

    # Optional fields
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        data["metric_type"] = self.metric_type.value
        # Remove None values to save space
        return {k: str(v) if v is not None else "" for k, v in data.items() if v is not None}


class MetricsService:
    """
    Non-blocking metrics service using Redis Streams.

    Features:
    - Fire-and-forget: emit() returns immediately
    - Batching: collects metrics and flushes periodically
    - Resilient: gracefully handles Redis unavailability
    """

    STREAM_NAME = "encypher:metrics:events"
    MAX_BUFFER_SIZE = 100
    FLUSH_INTERVAL = 1.0
    MAX_STREAM_LENGTH = 100000

    def __init__(self, redis_url: Optional[str] = None, enabled: bool = True):
        self.redis_url = redis_url or settings.redis_url or "redis://localhost:6379/0"
        self.enabled = enabled
        self._redis: Optional[redis.Redis] = None
        self._buffer: List[MetricEvent] = []
        self._buffer_lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._connected = False

    async def connect(self) -> bool:
        """Establish Redis connection and start background flush task."""
        if not self.enabled:
            logger.info("Metrics collection disabled")
            return False

        try:
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await cast(Any, self._redis.ping())
            self._connected = True

            # Start background flush task
            self._flush_task = asyncio.create_task(self._flush_loop())

            logger.info("Metrics service connected to Redis")
            return True

        except Exception as e:
            logger.warning(f"Failed to connect metrics service to Redis: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Close Redis connection and stop flush task."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None

        await self._flush_buffer()

        if self._redis:
            await self._redis.close()
            self._redis = None
            self._connected = False
            logger.info("Metrics service disconnected")

    async def emit(
        self,
        metric_type: MetricType,
        organization_id: str,
        **kwargs,
    ) -> bool:
        """Emit a metric event (non-blocking)."""
        if not self.enabled or not organization_id:
            return False

        event = MetricEvent(
            metric_type=metric_type,
            organization_id=organization_id,
            **kwargs,
        )

        async with self._buffer_lock:
            if len(self._buffer) >= self.MAX_BUFFER_SIZE:
                logger.warning("Metrics buffer full, dropping event")
                return False
            self._buffer.append(event)

        return True

    async def emit_api_call(
        self,
        organization_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
    ) -> bool:
        """Convenience method for API call metrics."""
        return await self.emit(
            metric_type=MetricType.API_CALL,
            organization_id=organization_id,
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
        )

    async def emit_document_signed(
        self,
        organization_id: str,
        document_id: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Convenience method for document signed metrics."""
        return await self.emit(
            metric_type=MetricType.DOCUMENT_SIGNED,
            organization_id=organization_id,
            user_id=user_id,
            metadata={"document_id": document_id},
        )

    async def _flush_loop(self) -> None:
        """Background task that periodically flushes the buffer."""
        while True:
            try:
                await asyncio.sleep(self.FLUSH_INTERVAL)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics flush loop: {e}")

    async def _flush_buffer(self) -> None:
        """Flush buffered metrics to Redis Stream."""
        if not self._connected or not self._redis:
            return

        async with self._buffer_lock:
            if not self._buffer:
                return
            events = self._buffer.copy()
            self._buffer.clear()

        try:
            pipe = self._redis.pipeline()
            for event in events:
                payload = cast(
                    Dict[str | int | float | bytes, str | int | float | bytes],
                    event.to_dict(),
                )
                pipe.xadd(
                    self.STREAM_NAME,
                    payload,
                    maxlen=self.MAX_STREAM_LENGTH,
                    approximate=True,
                )
            await pipe.execute()
            logger.debug(f"Flushed {len(events)} metrics to Redis")
        except Exception as e:
            logger.error(f"Failed to flush metrics to Redis: {e}")


# Global singleton
_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> Optional[MetricsService]:
    """Get the global metrics service instance."""
    return _metrics_service


async def init_metrics_service() -> MetricsService:
    """Initialize and return the global metrics service."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
        await _metrics_service.connect()
    return _metrics_service


async def shutdown_metrics_service() -> None:
    """Shutdown the global metrics service."""
    global _metrics_service
    if _metrics_service:
        await _metrics_service.disconnect()
        _metrics_service = None
