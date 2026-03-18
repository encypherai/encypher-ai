"""Lightweight persistent job queue backed by Redis Streams.

Provides at-least-once delivery for background tasks (webhook dispatch,
audit logging, etc.) that must survive process restarts.

Falls back to fire-and-forget asyncio tasks when Redis is unavailable.
"""

import asyncio
import json
import logging
import time
from typing import Any, Callable, Coroutine, Dict, Optional

logger = logging.getLogger(__name__)


class JobQueue:
    """Redis Streams based job queue with consumer group support."""

    STREAM_KEY = "encypher:jobs"
    GROUP_NAME = "workers"
    MAX_STREAM_LEN = 10000  # Trim stream to prevent unbounded growth
    MAX_FALLBACK_TASKS = 64  # Bound concurrent fire-and-forget tasks

    def __init__(self) -> None:
        self._redis: Any = None
        self._handlers: Dict[str, Callable[..., Coroutine[Any, Any, None]]] = {}
        self._fallback_semaphore = asyncio.Semaphore(self.MAX_FALLBACK_TASKS)

    async def connect(self, redis_client: Any) -> None:
        """Attach Redis client and create consumer group if needed."""
        self._redis = redis_client
        if self._redis:
            try:
                await self._redis.xgroup_create(self.STREAM_KEY, self.GROUP_NAME, id="0", mkstream=True)
            except Exception:
                # Group already exists
                pass

    def register_handler(self, job_type: str, handler: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """Register an async handler for a job type."""
        self._handlers[job_type] = handler

    async def enqueue(self, job_type: str, payload: Dict[str, Any]) -> Optional[str]:
        """Add a job to the queue. Returns stream entry ID or None."""
        message = {
            "type": job_type,
            "payload": json.dumps(payload),
            "enqueued_at": str(time.time()),
        }

        if self._redis:
            try:
                entry_id = await self._redis.xadd(self.STREAM_KEY, message, maxlen=self.MAX_STREAM_LEN)
                return entry_id
            except Exception as exc:
                logger.warning(
                    "job_enqueue_failed type=%s: %s -- falling back to asyncio",
                    job_type,
                    exc,
                )

        # Fallback: fire-and-forget via asyncio (bounded)
        handler = self._handlers.get(job_type)
        if handler:

            async def _run_bounded() -> None:
                async with self._fallback_semaphore:
                    try:
                        await handler(payload)
                    except Exception as exc:
                        logger.error("job_fallback_failed type=%s: %s", job_type, exc)

            asyncio.create_task(_run_bounded())
        else:
            logger.warning("job_enqueue_no_handler type=%s", job_type)
        return None

    async def process_pending(self, consumer_name: str, count: int = 10) -> int:
        """Process pending jobs from the stream. Returns number processed."""
        if not self._redis:
            return 0

        processed = 0
        try:
            entries = await self._redis.xreadgroup(
                self.GROUP_NAME,
                consumer_name,
                {self.STREAM_KEY: ">"},
                count=count,
                block=1000,
            )
            if not entries:
                return 0

            for _stream, messages in entries:
                for msg_id, fields in messages:
                    job_type = fields.get("type", "")
                    raw_payload = fields.get("payload", "{}")
                    try:
                        payload = json.loads(raw_payload)
                    except json.JSONDecodeError:
                        payload = {}

                    handler = self._handlers.get(job_type)
                    if handler:
                        try:
                            await handler(payload)
                            await self._redis.xack(self.STREAM_KEY, self.GROUP_NAME, msg_id)
                            processed += 1
                        except Exception as exc:
                            logger.error(
                                "job_processing_failed type=%s id=%s: %s",
                                job_type,
                                msg_id,
                                exc,
                            )
                    else:
                        logger.warning(
                            "job_no_handler type=%s id=%s -- acknowledging to skip",
                            job_type,
                            msg_id,
                        )
                        await self._redis.xack(self.STREAM_KEY, self.GROUP_NAME, msg_id)
        except Exception as exc:
            logger.error("job_queue_read_failed: %s", exc)

        return processed


job_queue = JobQueue()
