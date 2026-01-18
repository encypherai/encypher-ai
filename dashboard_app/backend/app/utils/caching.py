"""
Caching utilities for the dashboard application.
"""

import asyncio
import functools
import logging
from collections.abc import Awaitable
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# In-memory cache storage
_cache: Dict[str, Dict[str, Any]] = {}


def cached_async(key_prefix: str, ttl_seconds: int = 300, key_generator: Optional[Callable[..., str]] = None):
    """
    Decorator for caching async function results.

    Args:
        key_prefix: Prefix for the cache key
        ttl_seconds: Time to live in seconds
        key_generator: Optional function to generate a custom cache key

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., Awaitable[Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = f"{key_prefix}:{key_generator(*args, **kwargs)}"
            else:
                # Default key generation based on args and kwargs
                args_str = ":".join(str(arg) for arg in args)
                kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{args_str}:{kwargs_str}"

            # Check if we have a valid cached result
            if cache_key in _cache:
                cache_entry = _cache[cache_key]
                if datetime.now() < cache_entry.get("expires_at", datetime.min):
                    logger.debug(f"Cache hit for {cache_key}")
                    return cache_entry["data"]

            # No valid cache, execute the function
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            _cache[cache_key] = {"data": result, "expires_at": datetime.now() + timedelta(seconds=ttl_seconds)}

            return result

        return wrapper

    return decorator


def invalidate_cache(key_prefix: Optional[str] = None):
    """
    Invalidate cache entries.

    Args:
        key_prefix: Optional prefix to invalidate only specific entries
    """
    global _cache
    if key_prefix:
        # Remove only entries with matching prefix
        keys_to_remove = [k for k in _cache.keys() if k.startswith(f"{key_prefix}:")]
        for key in keys_to_remove:
            del _cache[key]
        logger.debug(f"Invalidated {len(keys_to_remove)} cache entries with prefix {key_prefix}")
    else:
        # Clear entire cache
        _cache = {}
        logger.debug("Invalidated entire cache")


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the current cache.

    Returns:
        Dictionary with cache statistics
    """
    now = datetime.now()
    valid_entries = [k for k, v in _cache.items() if v.get("expires_at", datetime.min) > now]

    return {
        "total_entries": len(_cache),
        "valid_entries": len(valid_entries),
        "expired_entries": len(_cache) - len(valid_entries),
        "keys": list(_cache.keys()),
    }


# Periodic cache cleanup task
async def cleanup_expired_cache_entries():
    """
    Periodically clean up expired cache entries.
    """
    while True:
        try:
            now = datetime.now()
            keys_to_remove = [k for k, v in _cache.items() if v.get("expires_at", datetime.min) <= now]

            for key in keys_to_remove:
                del _cache[key]

            if keys_to_remove:
                logger.debug(f"Cleaned up {len(keys_to_remove)} expired cache entries")

            # Sleep for 5 minutes
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"Error in cache cleanup task: {e}")
            await asyncio.sleep(60)  # Sleep for 1 minute on error
