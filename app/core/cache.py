import json
import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class InMemoryCache:
    """Simple in-memory cache as fallback when Redis is not available"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, datetime] = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if key in self._cache:
            if key in self._expiry and datetime.utcnow() > self._expiry[key]:
                # Expired
                del self._cache[key]
                del self._expiry[key]
                return None
            return json.dumps(self._cache[key])
        return None
    
    async def set(self, key: str, value: str, expire: int = 300) -> bool:
        """Set value in cache with expiration"""
        try:
            self._cache[key] = json.loads(value)
            self._expiry[key] = datetime.utcnow() + timedelta(seconds=expire)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
        return True

class CacheManager:
    """Cache manager that tries Redis first, falls back to in-memory cache"""
    
    def __init__(self):
        self.redis_client = None
        self.fallback_cache = InMemoryCache()
        self._redis_available = False
        
    async def initialize_redis(self):
        """Try to initialize Redis connection"""
        try:
            import redis.asyncio as redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_timeout=1,
                socket_connect_timeout=1
            )
            # Test connection
            await self.redis_client.ping()
            self._redis_available = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self._redis_available = False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if self._redis_available and self.redis_client:
            try:
                return await self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                self._redis_available = False
        
        return await self.fallback_cache.get(key)
    
    async def set(self, key: str, value: str, expire: int = 300) -> bool:
        """Set value in cache with expiration"""
        if self._redis_available and self.redis_client:
            try:
                return await self.redis_client.setex(key, expire, value)
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                self._redis_available = False
        
        return await self.fallback_cache.set(key, value, expire)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if self._redis_available and self.redis_client:
            try:
                result = await self.redis_client.delete(key)
                return result > 0
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                self._redis_available = False
        
        return await self.fallback_cache.delete(key)
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"user_accounts:{user_id}",
            f"user_categories:{user_id}",
            f"user_stats:{user_id}:*"
        ]
        
        for pattern in patterns:
            await self.delete(pattern)

# Global cache instance
cache_manager = CacheManager()

def cached(expire: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    pass
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                try:
                    await cache_manager.set(cache_key, json.dumps(result, default=str), expire)
                except Exception as e:
                    logger.error(f"Failed to cache result: {e}")
            
            return result
        
        return wrapper
    return decorator

async def initialize_cache():
    """Initialize cache on application startup"""
    await cache_manager.initialize_redis()

async def cleanup_cache():
    """Cleanup cache on application shutdown"""
    if cache_manager.redis_client:
        await cache_manager.redis_client.close() 