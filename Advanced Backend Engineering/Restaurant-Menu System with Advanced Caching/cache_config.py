from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
import time
import psutil
import logging
from typing import Optional, Dict, Any
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheNamespace(Enum):
    """Cache namespace enumeration"""
    RESTAURANTS = "restaurants"
    MENU_ITEMS = "menu-items"
    RESTAURANT_MENUS = "restaurant-menus"
    SEARCH_RESULTS = "search-results"
    ANALYTICS = "analytics"

class CacheCategory(Enum):
    """Cache category enumeration for different TTLs"""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    POPULAR = "popular"
    EXPENSIVE = "expensive"
    BUDGET = "budget"

# Cache TTL Configuration
CACHE_TTL = {
    "restaurants": 600,  # 10 minutes
    "menu_items": 480,   # 8 minutes
    "restaurant_menus": 900,  # 15 minutes
    "search_results": 300,  # 5 minutes
    "analytics": 1800,  # 30 minutes
    "vegetarian": 240,  # 4 minutes (more dynamic)
    "vegan": 240,       # 4 minutes
    "popular": 600,     # 10 minutes
    "expensive": 900,   # 15 minutes
    "budget": 300       # 5 minutes
}

# Cache hit/miss tracking
cache_stats = {
    "hits": 0,
    "misses": 0,
    "namespace_hits": {},
    "namespace_misses": {}
}

async def init_cache():
    """Initialize Redis cache with advanced configuration"""
    redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="restaurant-menu-cache")
    logger.info("Advanced Redis cache initialized successfully")

async def clear_cache(namespace: Optional[str] = None, key: Optional[str] = None):
    """Clear cache by namespace and optional key"""
    if namespace and key:
        await FastAPICache.clear(namespace=namespace, key=key)
        logger.info(f"Cleared cache for namespace: {namespace}, key: {key}")
    elif namespace:
        await FastAPICache.clear(namespace=namespace)
        logger.info(f"Cleared cache for namespace: {namespace}")
    else:
        await FastAPICache.clear()
        logger.info("Cleared entire cache")

async def get_detailed_cache_stats() -> Dict[str, Any]:
    """Get detailed cache statistics by namespace"""
    redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
    
    # Get all keys
    keys = await redis.keys("*")
    
    # Count keys by namespace
    namespace_counts = {}
    namespace_sizes = {}
    
    for key in keys:
        if "restaurant-menu-cache" in key:
            parts = key.split(":")
            if len(parts) >= 2:
                namespace = parts[1]
                namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
                
                # Get key size
                try:
                    value = await redis.get(key)
                    if value:
                        namespace_sizes[namespace] = namespace_sizes.get(namespace, 0) + len(value)
                except:
                    pass
    
    # Get memory usage
    memory_info = psutil.virtual_memory()
    
    return {
        "total_keys": len(keys),
        "restaurant_menu_cache_keys": len([k for k in keys if "restaurant-menu-cache" in k]),
        "namespace_counts": namespace_counts,
        "namespace_sizes": namespace_sizes,
        "cache_hit_ratio": cache_stats["hits"] / (cache_stats["hits"] + cache_stats["misses"]) if (cache_stats["hits"] + cache_stats["misses"]) > 0 else 0,
        "cache_stats": cache_stats,
        "memory_usage": {
            "total": memory_info.total,
            "available": memory_info.available,
            "percent": memory_info.percent
        },
        "cache_keys": keys[:50]  # Show first 50 keys
    }

def log_cache_performance(func_name: str, cache_hit: bool, response_time: float, namespace: str = None):
    """Log cache performance metrics with namespace tracking"""
    status = "CACHE HIT" if cache_hit else "CACHE MISS"
    
    # Update global stats
    if cache_hit:
        cache_stats["hits"] += 1
        if namespace:
            cache_stats["namespace_hits"][namespace] = cache_stats["namespace_hits"].get(namespace, 0) + 1
    else:
        cache_stats["misses"] += 1
        if namespace:
            cache_stats["namespace_misses"][namespace] = cache_stats["namespace_misses"].get(namespace, 0) + 1
    
    logger.info(f"{func_name}: {status} - Response time: {response_time:.2f}ms - Namespace: {namespace}")

# Advanced cache decorators with different TTLs
def cache_restaurant_data():
    """Cache decorator for restaurant data - 10 minutes TTL"""
    return cache(namespace=CacheNamespace.RESTAURANTS.value, expire=CACHE_TTL["restaurants"])

def cache_menu_item_data():
    """Cache decorator for menu item data - 8 minutes TTL"""
    return cache(namespace=CacheNamespace.MENU_ITEMS.value, expire=CACHE_TTL["menu_items"])

def cache_restaurant_menu_data():
    """Cache decorator for restaurant-menu combinations - 15 minutes TTL"""
    return cache(namespace=CacheNamespace.RESTAURANT_MENUS.value, expire=CACHE_TTL["restaurant_menus"])

def cache_search_results():
    """Cache decorator for search results - 5 minutes TTL"""
    return cache(namespace=CacheNamespace.SEARCH_RESULTS.value, expire=CACHE_TTL["search_results"])

def cache_analytics_data():
    """Cache decorator for analytics data - 30 minutes TTL"""
    return cache(namespace=CacheNamespace.ANALYTICS.value, expire=CACHE_TTL["analytics"])

def cache_by_category(category: CacheCategory):
    """Cache decorator for category-specific data"""
    return cache(namespace=CacheNamespace.SEARCH_RESULTS.value, expire=CACHE_TTL[category.value])

# Hierarchical cache invalidation functions
async def invalidate_restaurant_cache(restaurant_id: int):
    """Invalidate restaurant-related caches"""
    await clear_cache(namespace=CacheNamespace.RESTAURANTS.value, key=f"restaurant:{restaurant_id}")
    await clear_cache(namespace=CacheNamespace.RESTAURANT_MENUS.value, key=f"restaurant:{restaurant_id}")
    logger.info(f"Invalidated restaurant cache for ID: {restaurant_id}")

async def invalidate_menu_item_cache(menu_item_id: int, restaurant_id: int):
    """Invalidate menu item-related caches"""
    await clear_cache(namespace=CacheNamespace.MENU_ITEMS.value, key=f"item:{menu_item_id}")
    await clear_cache(namespace=CacheNamespace.RESTAURANT_MENUS.value, key=f"restaurant:{restaurant_id}")
    await clear_cache(namespace=CacheNamespace.SEARCH_RESULTS.value)  # Clear all searches
    logger.info(f"Invalidated menu item cache for ID: {menu_item_id}")

async def invalidate_search_cache():
    """Invalidate all search result caches"""
    await clear_cache(namespace=CacheNamespace.SEARCH_RESULTS.value)
    logger.info("Invalidated all search result caches")

async def invalidate_analytics_cache():
    """Invalidate analytics caches"""
    await clear_cache(namespace=CacheNamespace.ANALYTICS.value)
    logger.info("Invalidated analytics caches")

# Cache warming functions
async def warm_restaurant_cache(restaurant_ids: list):
    """Warm cache with frequently accessed restaurant data"""
    logger.info(f"Warming restaurant cache for {len(restaurant_ids)} restaurants")
    # This would be implemented in the CRUD layer
    pass

async def warm_menu_cache(restaurant_id: int):
    """Warm cache with restaurant menu data"""
    logger.info(f"Warming menu cache for restaurant {restaurant_id}")
    # This would be implemented in the CRUD layer
    pass

# Performance monitoring
def get_cache_performance_metrics() -> Dict[str, Any]:
    """Get cache performance metrics"""
    total_requests = cache_stats["hits"] + cache_stats["misses"]
    hit_ratio = cache_stats["hits"] / total_requests if total_requests > 0 else 0
    
    return {
        "total_requests": total_requests,
        "cache_hits": cache_stats["hits"],
        "cache_misses": cache_stats["misses"],
        "hit_ratio": hit_ratio,
        "miss_ratio": 1 - hit_ratio,
        "namespace_performance": {
            "hits": cache_stats["namespace_hits"],
            "misses": cache_stats["namespace_misses"]
        }
    }

def reset_cache_stats():
    """Reset cache statistics"""
    global cache_stats
    cache_stats = {
        "hits": 0,
        "misses": 0,
        "namespace_hits": {},
        "namespace_misses": {}
    }
    logger.info("Cache statistics reset") 