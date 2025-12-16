"""
Metrics Client - Non-blocking metrics collection using Redis Streams.

This client provides fire-and-forget metrics emission that won't slow down
API requests. Metrics are written to Redis Streams and consumed by the
analytics-service for aggregation.

Usage:
    from encypher_commercial_shared.metrics import MetricsClient, MetricType
    
    # Initialize once at startup
    metrics = MetricsClient(redis_url="redis://localhost:6379/0")
    await metrics.connect()
    
    # Emit metrics (non-blocking)
    await metrics.emit(
        metric_type=MetricType.API_CALL,
        organization_id="org_123",
        user_id="user_456",
        endpoint="/api/v1/sign",
        method="POST",
        status_code=200,
        response_time_ms=150.5,
    )
"""
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

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
        # Convert enum to string
        data["metric_type"] = self.metric_type.value
        # Remove None values to save space
        return {k: v for k, v in data.items() if v is not None}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class MetricsClient:
    """
    Non-blocking metrics client using Redis Streams.
    
    Features:
    - Fire-and-forget: emit() returns immediately, doesn't block
    - Batching: collects metrics and flushes periodically
    - Resilient: gracefully handles Redis unavailability
    - Backpressure: drops metrics if buffer is full
    """
    
    # Redis Stream name for metrics
    STREAM_NAME = "encypher:metrics:events"
    
    # Maximum events to buffer before forcing flush
    MAX_BUFFER_SIZE = 100
    
    # Flush interval in seconds
    FLUSH_INTERVAL = 1.0
    
    # Maximum stream length (Redis will trim older entries)
    MAX_STREAM_LENGTH = 100000
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        service_name: str = "unknown",
        enabled: bool = True,
    ):
        """
        Initialize metrics client.
        
        Args:
            redis_url: Redis connection URL
            service_name: Name of the service emitting metrics
            enabled: Whether metrics collection is enabled
        """
        self.redis_url = redis_url
        self.service_name = service_name
        self.enabled = enabled
        self._redis: Optional[Any] = None
        self._buffer: list[MetricEvent] = []
        self._buffer_lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._connected = False
        
    async def connect(self) -> bool:
        """
        Establish Redis connection and start background flush task.
        
        Returns:
            True if connected successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Metrics collection disabled")
            return False
            
        try:
            import redis.asyncio as redis
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            self._connected = True
            
            # Start background flush task
            self._flush_task = asyncio.create_task(self._flush_loop())
            
            logger.info(f"Metrics client connected to Redis: {self.redis_url}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to connect metrics client to Redis: {e}")
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
        
        # Final flush
        await self._flush_buffer()
        
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._connected = False
            logger.info("Metrics client disconnected")
    
    async def emit(
        self,
        metric_type: MetricType,
        organization_id: str,
        **kwargs,
    ) -> bool:
        """
        Emit a metric event (non-blocking).
        
        This method returns immediately. The metric is buffered and
        flushed to Redis in the background.
        
        Args:
            metric_type: Type of metric
            organization_id: Organization ID
            **kwargs: Additional metric fields
            
        Returns:
            True if metric was buffered, False if dropped
        """
        if not self.enabled:
            return False
        
        event = MetricEvent(
            metric_type=metric_type,
            organization_id=organization_id,
            **kwargs,
        )
        
        async with self._buffer_lock:
            # Drop if buffer is full (backpressure)
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
        request_size_bytes: Optional[int] = None,
        response_size_bytes: Optional[int] = None,
    ) -> bool:
        """Convenience method for emitting API call metrics."""
        return await self.emit(
            metric_type=MetricType.API_CALL,
            organization_id=organization_id,
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            request_size_bytes=request_size_bytes,
            response_size_bytes=response_size_bytes,
        )
    
    async def emit_document_signed(
        self,
        organization_id: str,
        document_id: str,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        document_size_bytes: Optional[int] = None,
    ) -> bool:
        """Convenience method for emitting document signed metrics."""
        return await self.emit(
            metric_type=MetricType.DOCUMENT_SIGNED,
            organization_id=organization_id,
            user_id=user_id,
            api_key_id=api_key_id,
            metadata={"document_id": document_id, "size_bytes": document_size_bytes},
        )
    
    async def emit_error(
        self,
        organization_id: str,
        endpoint: str,
        error_code: str,
        error_message: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Convenience method for emitting error metrics."""
        return await self.emit(
            metric_type=MetricType.ERROR,
            organization_id=organization_id,
            user_id=user_id,
            endpoint=endpoint,
            error_code=error_code,
            error_message=error_message,
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
            # Use pipeline for efficiency
            pipe = self._redis.pipeline()
            
            for event in events:
                # Add to stream with auto-generated ID
                pipe.xadd(
                    self.STREAM_NAME,
                    event.to_dict(),
                    maxlen=self.MAX_STREAM_LENGTH,
                    approximate=True,
                )
            
            await pipe.execute()
            logger.debug(f"Flushed {len(events)} metrics to Redis")
            
        except Exception as e:
            logger.error(f"Failed to flush metrics to Redis: {e}")
            # Re-add events to buffer for retry (up to limit)
            async with self._buffer_lock:
                remaining_capacity = self.MAX_BUFFER_SIZE - len(self._buffer)
                if remaining_capacity > 0:
                    self._buffer = events[:remaining_capacity] + self._buffer


# Global singleton instance
_metrics_client: Optional[MetricsClient] = None


def get_metrics_client() -> Optional[MetricsClient]:
    """Get the global metrics client instance."""
    return _metrics_client


def set_metrics_client(client: MetricsClient) -> None:
    """Set the global metrics client instance."""
    global _metrics_client
    _metrics_client = client
