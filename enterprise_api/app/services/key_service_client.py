"""
Client for communicating with the Key Service.
Handles API key validation and caching.
"""

import json
import logging
from typing import Any, Dict, Optional, cast

import httpx
import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class KeyServiceClient:
    """
    Client for the Key Service with Redis caching.

    Validates API keys against the Key Service and caches the result
    in Redis to avoid excessive HTTP calls.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the client.

        Args:
            redis_client: Optional Redis client (for testing or shared instance)
        """
        self.base_url = settings.key_service_url
        self.redis_client = redis_client
        self.cache_ttl = 300  # Cache validation for 5 minutes
        self.cache_prefix = "key_validation:"

    async def _get_redis(self) -> Optional[redis.Redis]:
        """Get Redis client, initializing if needed."""
        if self.redis_client:
            return self.redis_client

        # Import here to avoid circular deps if any
        from app.services.session_service import session_service

        if session_service.redis_client:
            return session_service.redis_client

        return None

    async def validate_key_minimal(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return minimal key identity/permissions.

        This calls the key-service "validate-minimal" endpoint which is designed
        for the long-term architecture where services do not rely on duplicated
        tables (e.g., organizations).
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/keys/validate-minimal",
                    json={"key": api_key},
                    timeout=5.0,
                )
        except httpx.ConnectError:
            logger.warning("Key Service unavailable for validate-minimal")
            return None
        except Exception as e:
            logger.error(f"Key Service call failed (validate-minimal): {e}")
            return None

        if response.status_code != 200:
            return None

        data = cast(Dict[str, Any], response.json())
        if data.get("success") and data.get("data"):
            return cast(Dict[str, Any], data["data"])

        return None

    def _cache_key(self, api_key: str) -> str:
        return f"{self.cache_prefix}{api_key}"

    async def validate_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and return full organization context.

        First checks Redis cache. If miss, calls Key Service /validate endpoint.

        Args:
            api_key: The API key to validate

        Returns:
            Dict with organization context if valid:
            {
                "organization_id": "org_xxx",
                "organization_name": "Acme Corp",
                "tier": "business",
                "features": {...},
                "permissions": ["sign", "verify", "lookup"],
                "monthly_api_limit": 500000,
                "monthly_api_usage": 1234,
                ...
            }
            None if invalid/error
        """
        redis_conn = await self._get_redis()

        # 1. Check Cache
        if redis_conn:
            try:
                cached = await redis_conn.get(self._cache_key(api_key))
                if cached:
                    # Reset TTL on cache hit (sliding window)
                    await redis_conn.expire(self._cache_key(api_key), self.cache_ttl)
                    return cast(Dict[str, Any], json.loads(cached))
            except Exception as e:
                logger.warning(f"Redis cache read error: {e}")

        # 2. Call Key Service /validate endpoint (unified auth)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/v1/keys/validate", json={"key": api_key}, timeout=5.0)

                if response.status_code == 200:
                    data = cast(Dict[str, Any], response.json())
                    if data.get("success") and data.get("data"):
                        org_context = cast(Dict[str, Any], data["data"])

                        # 3. Update Cache
                        if redis_conn and org_context:
                            try:
                                await redis_conn.setex(self._cache_key(api_key), self.cache_ttl, json.dumps(org_context))
                            except Exception as e:
                                logger.warning(f"Redis cache write error: {e}")

                        return org_context

        except httpx.ConnectError:
            logger.warning("Key Service unavailable, falling back to demo mode")
            # Fall through to return None - dependencies.py handles demo fallback
        except Exception as e:
            logger.error(f"Key Service call failed: {e}")

        return None


# Global instance
key_service_client = KeyServiceClient()
