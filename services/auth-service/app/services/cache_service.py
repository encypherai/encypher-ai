"""
Redis caching service for improving performance.
"""
import hashlib
from typing import Any, Optional
from aiocache import Cache
from aiocache.serializers import JsonSerializer
import structlog

logger = structlog.get_logger()


class CacheService:
    """
    Redis caching service with automatic key generation and TTL management.
    
    Usage:
        cache = CacheService(redis_url)
        
        # Set value
        await cache.set("user", user_dict, ttl=300, user_id="123")
        
        # Get value
        user = await cache.get("user", user_id="123")
        
        # Delete value
        await cache.delete("user", user_id="123")
    """
    
    def __init__(self, redis_url: str, namespace: str = "encypher"):
        """
        Initialize cache service.
        
        Args:
            redis_url: Redis connection URL
            namespace: Namespace prefix for all keys
        """
        # Parse Redis URL
        if "://" in redis_url:
            redis_url = redis_url.split("://")[1]
        
        host, port = redis_url.split(":")
        
        self.cache = Cache(
            Cache.REDIS,
            endpoint=host,
            port=int(port),
            serializer=JsonSerializer(),
            namespace=namespace
        )
        
        self.namespace = namespace
        logger.info("cache_service_initialized", redis_host=host, redis_port=port)
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments.
        
        Args:
            prefix: Key prefix (e.g., "user", "session")
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key
            
        Returns:
            Generated cache key
        """
        # Combine all parts
        key_parts = [prefix]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        
        # Create key string
        key_string = ":".join(key_parts)
        
        # Hash if too long
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_string
    
    async def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            prefix: Key prefix
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation
            
        Returns:
            Cached value or None if not found
        """
        key = self._make_key(prefix, *args, **kwargs)
        
        try:
            value = await self.cache.get(key)
            
            if value is not None:
                logger.debug("cache_hit", key=key)
            else:
                logger.debug("cache_miss", key=key)
            
            return value
        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None
    
    async def set(
        self,
        prefix: str,
        value: Any,
        ttl: int = 300,
        *args,
        **kwargs
    ) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            prefix: Key prefix
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds (default: 5 minutes)
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation
            
        Returns:
            True if successful, False otherwise
        """
        key = self._make_key(prefix, *args, **kwargs)
        
        try:
            await self.cache.set(key, value, ttl=ttl)
            logger.debug("cache_set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))
            return False
    
    async def delete(self, prefix: str, *args, **kwargs) -> bool:
        """
        Delete value from cache.
        
        Args:
            prefix: Key prefix
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation
            
        Returns:
            True if successful, False otherwise
        """
        key = self._make_key(prefix, *args, **kwargs)
        
        try:
            await self.cache.delete(key)
            logger.debug("cache_delete", key=key)
            return True
        except Exception as e:
            logger.error("cache_delete_error", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            # This requires direct Redis access
            # For now, just log the request
            logger.info("cache_clear_pattern_requested", pattern=pattern)
            return 0
        except Exception as e:
            logger.error("cache_clear_pattern_error", pattern=pattern, error=str(e))
            return 0
    
    async def exists(self, prefix: str, *args, **kwargs) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            prefix: Key prefix
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation
            
        Returns:
            True if key exists, False otherwise
        """
        key = self._make_key(prefix, *args, **kwargs)
        
        try:
            value = await self.cache.get(key)
            return value is not None
        except Exception as e:
            logger.error("cache_exists_error", key=key, error=str(e))
            return False


# Decorator for caching function results
def cached(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results.
    
    Usage:
        @cached("user_profile", ttl=600)
        async def get_user_profile(user_id: str):
            # Expensive operation
            return profile
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get cache service from first argument (usually self)
            if args and hasattr(args[0], 'cache'):
                cache = args[0].cache
                
                # Generate cache key from function arguments
                cache_key_args = args[1:] if len(args) > 1 else []
                
                # Try to get from cache
                cached_value = await cache.get(prefix, *cache_key_args, **kwargs)
                if cached_value is not None:
                    return cached_value
                
                # Call function
                result = await func(*args, **kwargs)
                
                # Cache result
                await cache.set(prefix, result, ttl=ttl, *cache_key_args, **kwargs)
                
                return result
            else:
                # No cache available, just call function
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator
