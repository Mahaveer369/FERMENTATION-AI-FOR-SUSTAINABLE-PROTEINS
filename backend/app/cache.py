"""
FermaGen AI - Redis Caching Utility
Provides caching functionality for API responses and ML predictions
"""
import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheManager:
    """Async Redis cache manager"""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self._redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self._redis.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self._redis = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis cache disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._redis:
            return None
        
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (default 5 minutes)"""
        if not self._redis:
            return
        
        try:
            await self._redis.setex(
                key, 
                ttl, 
                json.dumps(value)
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        if not self._redis:
            return
        
        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self._redis:
            return
        
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")


# Singleton instance
cache_manager = CacheManager()


async def init_cache():
    """Initialize cache on app startup"""
    await cache_manager.connect()


async def close_cache():
    """Close cache on app shutdown"""
    await cache_manager.disconnect()
