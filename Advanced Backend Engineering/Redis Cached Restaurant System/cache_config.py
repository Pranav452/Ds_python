from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
import time
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_NAMESPACE_RESTAURANTS = "restaurants"
CACHE_TTL_RESTAURANT_LIST = 300  # 5 minutes
CACHE_TTL_RESTAURANT_DETAIL = 600  # 10 minutes
CACHE_TTL_SEARCH = 180  # 3 minutes
CACHE_TTL_ACTIVE = 240  # 4 minutes

async def init_cache():
    """Initialize Redis cache"""
    redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="restaurant-cache")

async def clear_cache(namespace: Optional[str] = None):
    """Clear cache by namespace or entire cache"""
    if namespace:
        await FastAPICache.clear(namespace=namespace)
        logger.info(f"Cleared cache for namespace: {namespace}")
    else:
        await FastAPICache.clear()
        logger.info("Cleared entire cache")

async def get_cache_stats():
    """Get cache statistics"""
    redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
    
    # Get all keys
    keys = await redis.keys("*")
    
    # Count keys by namespace
    namespace_counts = {}
    for key in keys:
        if "restaurant-cache" in key:
            namespace = key.split(":")[1] if ":" in key else "general"
            namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
    
    return {
        "total_keys": len(keys),
        "restaurant_cache_keys": len([k for k in keys if "restaurant-cache" in k]),
        "namespace_counts": namespace_counts,
        "cache_keys": keys[:20]  # Show first 20 keys
    }

def log_cache_performance(func_name: str, cache_hit: bool, response_time: float):
    """Log cache performance metrics"""
    status = "CACHE HIT" if cache_hit else "CACHE MISS"
    logger.info(f"{func_name}: {status} - Response time: {response_time:.2f}ms")

# Cache decorators for different endpoints
def cache_restaurant_list():
    """Cache decorator for restaurant list endpoint"""
    return cache(namespace=CACHE_NAMESPACE_RESTAURANTS, expire=CACHE_TTL_RESTAURANT_LIST)

def cache_restaurant_detail():
    """Cache decorator for individual restaurant endpoint"""
    return cache(namespace=CACHE_NAMESPACE_RESTAURANTS, expire=CACHE_TTL_RESTAURANT_DETAIL)

def cache_search_results():
    """Cache decorator for search results"""
    return cache(namespace=CACHE_NAMESPACE_RESTAURANTS, expire=CACHE_TTL_SEARCH)

def cache_active_restaurants():
    """Cache decorator for active restaurants"""
    return cache(namespace=CACHE_NAMESPACE_RESTAURANTS, expire=CACHE_TTL_ACTIVE) 