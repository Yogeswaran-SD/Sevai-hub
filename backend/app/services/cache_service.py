"""
Redis caching service for improved performance.
Handles session caching, technician availability, and service data.
"""

import json
import redis.asyncio as redis
from typing import Any, Optional
from app.core.config import settings

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get or create Redis connection."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
            # Test connection
            await _redis_client.ping()
            print("[OK] Redis connected successfully")
        except Exception as e:
            print(f"[WARN] Redis connection failed: {str(e)}")
            return None
    return _redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    try:
        r = await get_redis()
        if not r:
            return None
        value = await r.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except Exception as e:
        print(f"[WARN] Cache get failed for {key}: {str(e)}")
        return None


async def cache_set(key: str, value: Any, expire: int = 3600) -> bool:
    """Set value in cache with TTL."""
    try:
        r = await get_redis()
        if not r:
            return False

        # Serialize to JSON if not already a string
        if not isinstance(value, str):
            value = json.dumps(value)

        await r.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"[WARN] Cache set failed for {key}: {str(e)}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete key from cache."""
    try:
        r = await get_redis()
        if not r:
            return False
        await r.delete(key)
        return True
    except Exception as e:
        print(f"[WARN] Cache delete failed for {key}: {str(e)}")
        return False


async def cache_clear_pattern(pattern: str) -> bool:
    """Delete all keys matching pattern."""
    try:
        r = await get_redis()
        if not r:
            return False
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
        return True
    except Exception as e:
        print(f"[WARN] Cache clear pattern failed for {pattern}: {str(e)}")
        return False


async def cache_technician_status(technician_id: int, status: str, expire: int = 86400) -> bool:
    """Cache technician availability status."""
    key = f"technician:{technician_id}:status"
    return await cache_set(key, status, expire)


async def get_technician_status(technician_id: int) -> Optional[str]:
    """Get cached technician status."""
    key = f"technician:{technician_id}:status"
    return await cache_get(key)


async def cache_service_locations(service_id: int, locations: list, expire: int = 3600) -> bool:
    """Cache service location data."""
    key = f"service:{service_id}:locations"
    return await cache_set(key, locations, expire)


async def get_service_locations(service_id: int) -> Optional[list]:
    """Get cached service locations."""
    key = f"service:{service_id}:locations"
    return await cache_get(key)


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
