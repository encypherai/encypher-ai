"""
Redis-backed idempotency helper for batch endpoints.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class IdempotencyService:
    """Lightweight helper that stores idempotency keys in Redis."""

    def __init__(self, redis_url: Optional[str] = None, default_ttl_seconds: int = 86_400):
        self.redis_url = redis_url or getattr(settings, "redis_url", "redis://localhost:6379/0")
        self.default_ttl_seconds = default_ttl_seconds
        self._redis: Optional[redis.Redis] = None
        self._lock = asyncio.Lock()

    async def _client(self) -> Optional[redis.Redis]:
        """Return a connected Redis client, if possible."""

        if self._redis:
            return self._redis

        async with self._lock:
            if self._redis:
                return self._redis
            try:
                self._redis = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                await self._redis.ping()
                logger.info("Idempotency Redis connection established")
            except Exception as exc:  # pragma: no cover - network failures
                logger.warning("Redis unavailable for idempotency: %s", exc)
                self._redis = None
        return self._redis

    @staticmethod
    def _key(scope: str, idem_key: str) -> str:
        return f"idempotency:{scope}:{idem_key}"

    async def register(
        self,
        *,
        scope: str,
        idem_key: str,
        payload_hash: str,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Register an idempotency key.

        Returns True when registration succeeded (no prior entry) or Redis is unavailable.
        Returns False when a different payload hash already exists for the key.
        """

        client = await self._client()
        if not client:
            return True  # best-effort when Redis missing

        key = self._key(scope, idem_key)
        ttl = ttl_seconds or self.default_ttl_seconds
        try:
            added = await client.set(key, payload_hash, nx=True, ex=ttl)
            if added:
                return True

            existing = await client.get(key)
            return existing == payload_hash
        except Exception as exc:  # pragma: no cover - redis failures
            logger.warning("Failed to register idempotency key %s: %s", key, exc)
            return True

    async def get(self, *, scope: str, idem_key: str) -> Optional[str]:
        """Return stored payload hash for idempotency key."""

        client = await self._client()
        if not client:
            return None
        try:
            return await client.get(self._key(scope, idem_key))
        except Exception:  # pragma: no cover
            return None

    async def clear(self, *, scope: str, idem_key: str) -> None:
        """Remove idempotency key (used after expiration or cleanup)."""

        client = await self._client()
        if not client:
            return
        try:
            await client.delete(self._key(scope, idem_key))
        except Exception:  # pragma: no cover
            logger.debug("Failed to delete idempotency key %s", idem_key)


idempotency_service = IdempotencyService()

