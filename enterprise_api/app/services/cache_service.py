"""Redis-backed cache for frequently accessed data.

Reduces database load by caching org/tier lookups with a short TTL.
Falls back to direct DB queries when Redis is unavailable.
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class OrgCacheService:
    """Redis-backed cache for organization lookups with configurable TTL."""

    DEFAULT_TTL = 60  # seconds

    def __init__(self) -> None:
        self._redis: Any = None

    async def connect(self, redis_client: Any) -> None:
        """Attach a Redis client for caching."""
        self._redis = redis_client

    async def get_org_tier(self, org_id: str) -> Optional[str]:
        """Get cached organization tier, or None if not cached."""
        if not self._redis:
            return None
        try:
            value = await self._redis.get(f"org:tier:{org_id}")
            return value if isinstance(value, str) else None
        except Exception as exc:
            logger.debug("cache_get_org_tier_failed org=%s: %s", org_id, exc)
            return None

    async def set_org_tier(self, org_id: str, tier: str, ttl: int = DEFAULT_TTL) -> None:
        """Cache an organization's tier."""
        if not self._redis:
            return
        try:
            await self._redis.setex(f"org:tier:{org_id}", ttl, tier)
        except Exception as exc:
            logger.debug("cache_set_org_tier_failed org=%s: %s", org_id, exc)

    async def get_org_data(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get cached organization data dict, or None if not cached."""
        if not self._redis:
            return None
        try:
            value = await self._redis.get(f"org:data:{org_id}")
            if value:
                return json.loads(value)
        except Exception as exc:
            logger.debug("cache_get_org_data_failed org=%s: %s", org_id, exc)
        return None

    async def set_org_data(self, org_id: str, data: Dict[str, Any], ttl: int = DEFAULT_TTL) -> None:
        """Cache organization data."""
        if not self._redis:
            return
        try:
            await self._redis.setex(f"org:data:{org_id}", ttl, json.dumps(data))
        except Exception as exc:
            logger.debug("cache_set_org_data_failed org=%s: %s", org_id, exc)

    async def invalidate_org(self, org_id: str) -> None:
        """Remove all cached data for an organization."""
        if not self._redis:
            return
        try:
            await self._redis.delete(f"org:tier:{org_id}", f"org:data:{org_id}")
        except Exception as exc:
            logger.debug("cache_invalidate_org_failed org=%s: %s", org_id, exc)


org_cache = OrgCacheService()
