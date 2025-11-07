"""Redis cache manager for API responses and data."""

import os
import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
import redis
from redis.asyncio import Redis as AsyncRedis

logger = logging.getLogger(__name__)

# Redis connection configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RedisCache:
    """Redis cache manager with sync and async support."""

    def __init__(self, url: str = REDIS_URL):
        """Initialize Redis cache."""
        self.url = url
        self._sync_client: Optional[redis.Redis] = None
        self._async_client: Optional[AsyncRedis] = None
        logger.info(f"Redis cache initialized with URL: {url}")

    def get_sync_client(self) -> redis.Redis:
        """Get synchronous Redis client."""
        if self._sync_client is None:
            self._sync_client = redis.from_url(self.url, decode_responses=True)
        return self._sync_client

    async def get_async_client(self) -> AsyncRedis:
        """Get asynchronous Redis client."""
        if self._async_client is None:
            self._async_client = AsyncRedis.from_url(self.url, decode_responses=True)
        return self._async_client

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set a value in cache (sync).

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful
        """
        try:
            client = self.get_sync_client()
            serialized = json.dumps(value)
            result = client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache SET error for key '{key}': {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache (sync).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            client = self.get_sync_client()
            value = client.get(key)
            if value is None:
                logger.debug(f"Cache MISS: {key}")
                return None
            logger.debug(f"Cache HIT: {key}")
            return json.loads(value)
        except Exception as e:
            logger.error(f"Cache GET error for key '{key}': {e}")
            return None

    async def async_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set a value in cache (async).

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            client = await self.get_async_client()
            serialized = json.dumps(value)
            result = await client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET (async): {key} (TTL: {ttl}s)")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache SET error (async) for key '{key}': {e}")
            return False

    async def async_get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache (async).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            client = await self.get_async_client()
            value = await client.get(key)
            if value is None:
                logger.debug(f"Cache MISS (async): {key}")
                return None
            logger.debug(f"Cache HIT (async): {key}")
            return json.loads(value)
        except Exception as e:
            logger.error(f"Cache GET error (async) for key '{key}': {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache (sync).

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        try:
            client = self.get_sync_client()
            result = client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache DELETE error for key '{key}': {e}")
            return False

    async def async_delete(self, key: str) -> bool:
        """
        Delete a key from cache (async).

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        try:
            client = await self.get_async_client()
            result = await client.delete(key)
            logger.debug(f"Cache DELETE (async): {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache DELETE error (async) for key '{key}': {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern (sync).

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        try:
            client = self.get_sync_client()
            keys = client.keys(pattern)
            if keys:
                deleted = client.delete(*keys)
                logger.info(f"Cache CLEAR: {deleted} keys matching '{pattern}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache CLEAR error for pattern '{pattern}': {e}")
            return 0


# Global cache instance
cache = RedisCache()


def cached(key_prefix: str, ttl: int = 3600):
    """
    Decorator for caching function results (sync).

    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds

    Example:
        @cached("user", ttl=300)
        def get_user(user_id):
            return {"id": user_id, "name": "John"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function args
            cache_key = f"{key_prefix}:{':'.join(str(arg) for arg in args)}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


def async_cached(key_prefix: str, ttl: int = 3600):
    """
    Decorator for caching async function results.

    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds

    Example:
        @async_cached("user", ttl=300)
        async def get_user(user_id):
            return {"id": user_id, "name": "John"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function args
            cache_key = f"{key_prefix}:{':'.join(str(arg) for arg in args)}"

            # Try to get from cache
            cached_value = await cache.async_get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.async_set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
