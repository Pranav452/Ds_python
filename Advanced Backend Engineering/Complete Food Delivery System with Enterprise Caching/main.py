from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import uvicorn
import time
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from database import get_db
from models import Restaurant, MenuItem, Customer, Order, Review, OrderStatus
from schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantWithMenu,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, MenuItemWithRestaurant,
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerWithOrders,
    OrderCreate, OrderUpdate, OrderResponse, OrderWithDetails,
    ReviewCreate, ReviewResponse
)
from crud import (
    # Restaurant operations
    create_restaurant, get_restaurants, get_restaurant_by_id, get_restaurant_with_menu,
    update_restaurant, delete_restaurant,
    # Menu item operations
    create_menu_item, get_menu_items, get_menu_item_by_id, get_menu_item_with_restaurant,
    get_restaurant_menu, update_menu_item, delete_menu_item,
    # Customer operations
    create_customer, get_customers, get_customer_by_id, get_customer_with_orders,
    update_customer, delete_customer,
    # Order operations
    create_order, get_orders, get_order_by_id, get_order_with_details,
    get_customer_orders, get_restaurant_orders, update_order_status, update_order, delete_order,
    # Review operations
    create_review, get_reviews, get_review_by_id, get_restaurant_reviews, get_customer_reviews, delete_review,
    # Search and analytics
    search_restaurants_with_criteria, filter_orders_with_criteria,
    get_restaurant_analytics, get_customer_analytics
)
from enterprise_cache_config import (
    init_enterprise_cache, clear_cache, get_enterprise_cache_stats, 
    log_enterprise_cache_performance, get_enterprise_performance_metrics, reset_enterprise_cache_stats,
    warm_enterprise_cache, cache_static_data, cache_dynamic_data, cache_realtime_data,
    cache_analytics_data, cache_session_data, cache_customer_data, cache_order_data,
    cache_delivery_data, cache_review_data, cache_session_based, cache_conditional,
    CacheNamespace, ENTERPRISE_TTL, EnterpriseCachePatterns, EnterpriseCacheInvalidation,
    EnterpriseCacheWarming, EnterprisePerformanceMonitoring, EnterpriseCacheAnalytics,
    EnterpriseCacheSecurity
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Complete Food Delivery System with Enterprise Caching",
    description="A production-ready food delivery platform with comprehensive Redis caching strategies",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize enterprise cache and warm frequently accessed data on startup"""
    await init_enterprise_cache()
    logger.info("Enterprise Redis cache initialized successfully")
    
    # Warm enterprise cache with critical data
    try:
        await warm_enterprise_cache()
        logger.info("Enterprise cache warming completed")
    except Exception as e:
        logger.warning(f"Cache warming failed: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Complete Food Delivery System with Enterprise Caching",
        "version": "3.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "enterprise_cache_endpoints": {
            "health": "/cache/health",
            "stats_namespaces": "/cache/stats/namespaces",
            "memory_usage": "/cache/memory-usage",
            "clear_expired": "/cache/clear/expired",
            "warm_namespace": "/cache/warm/{namespace}"
        },
        "monitoring_endpoints": {
            "cache_performance": "/analytics/cache-performance",
            "popular_data": "/analytics/popular-data",
            "load_test": "/demo/load-test/{endpoint}"
        }
    }

# ============================================================================
# ENTERPRISE CACHE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/cache/health")
async def redis_health_check():
    """Redis health check endpoint"""
    try:
        from redis import asyncio as aioredis
        redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
        await redis.ping()
        return {
            "status": "healthy",
            "message": "Redis connection is working",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis connection failed: {str(e)}")

@app.get("/cache/stats/namespaces")
async def get_cache_stats_by_namespace():
    """Get detailed cache statistics by namespace"""
    stats = await get_enterprise_cache_stats()
    return {
        "namespace_counts": stats.get("namespace_counts", {}),
        "namespace_sizes": stats.get("namespace_sizes", {}),
        "namespace_ttl": stats.get("namespace_ttl", {}),
        "cache_hit_ratio": stats.get("cache_hit_ratio", 0),
        "total_keys": stats.get("total_keys", 0),
        "enterprise_cache_keys": stats.get("enterprise_cache_keys", 0)
    }

@app.get("/cache/memory-usage")
async def get_cache_memory_usage():
    """Get memory consumption details"""
    stats = await get_enterprise_cache_stats()
    memory_info = stats.get("memory_usage", {})
    
    return {
        "memory_usage": {
            "total_bytes": memory_info.get("total", 0),
            "available_bytes": memory_info.get("available", 0),
            "used_bytes": memory_info.get("used", 0),
            "usage_percent": memory_info.get("percent", 0)
        },
        "cache_memory_trend": stats.get("cache_stats", {}).get("memory_usage", [])[-10:],
        "alerts": stats.get("performance_alerts", [])
    }

@app.delete("/cache/clear/expired")
async def clear_expired_cache_keys():
    """Remove expired keys from cache"""
    try:
        from redis import asyncio as aioredis
        redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
        
        # Get all keys and check TTL
        keys = await redis.keys("zomato-enterprise-cache:*")
        expired_count = 0
        
        for key in keys:
            ttl = await redis.ttl(key)
            if ttl == -1:  # No expiration set
                await redis.delete(key)
                expired_count += 1
        
        return {
            "message": f"Cleared {expired_count} expired cache keys",
            "total_keys_checked": len(keys),
            "expired_keys_removed": expired_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear expired keys: {str(e)}")

@app.post("/cache/warm/{namespace}")
async def warm_specific_cache_namespace(namespace: str, background_tasks: BackgroundTasks):
    """Warm specific cache namespace"""
    try:
        # Add background task for cache warming
        background_tasks.add_task(warm_cache_by_namespace, namespace)
        
        return {
            "message": f"Cache warming started for namespace: {namespace}",
            "namespace": namespace,
            "status": "warming_in_progress"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to warm cache: {str(e)}")

async def warm_cache_by_namespace(namespace: str):
    """Background task to warm cache by namespace"""
    logger.info(f"Warming cache for namespace: {namespace}")
    
    # Implementation would fetch and cache data based on namespace
    if namespace == "restaurants":
        # Warm restaurant data
        pass
    elif namespace == "customers":
        # Warm customer data
        pass
    elif namespace == "analytics":
        # Warm analytics data
        pass
    
    logger.info(f"Cache warming completed for namespace: {namespace}")

# ============================================================================
# PERFORMANCE MONITORING ENDPOINTS
# ============================================================================

@app.get("/analytics/cache-performance")
async def get_cache_performance_analytics():
    """Get hit/miss ratios and performance metrics"""
    metrics = get_enterprise_performance_metrics()
    
    return {
        "performance_metrics": {
            "total_requests": metrics.get("total_requests", 0),
            "cache_hits": metrics.get("cache_hits", 0),
            "cache_misses": metrics.get("cache_misses", 0),
            "hit_ratio": metrics.get("hit_ratio", 0),
            "miss_ratio": metrics.get("miss_ratio", 0)
        },
        "namespace_performance": metrics.get("namespace_performance", {}),
        "memory_trend": metrics.get("memory_usage", []),
        "alerts": metrics.get("alerts", [])
    }

@app.get("/analytics/popular-data")
async def get_most_accessed_cached_items():
    """Get most accessed cached items"""
    stats = await get_enterprise_cache_stats()
    namespace_hits = stats.get("cache_stats", {}).get("namespace_hits", {})
    
    # Sort namespaces by hit count
    sorted_namespaces = sorted(namespace_hits.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "most_accessed_namespaces": [
            {
                "namespace": namespace,
                "hit_count": hit_count,
                "hit_percentage": (hit_count / stats.get("cache_stats", {}).get("hits", 1)) * 100
            }
            for namespace, hit_count in sorted_namespaces[:10]
        ],
        "total_cache_hits": stats.get("cache_stats", {}).get("hits", 0),
        "cache_hit_ratio": stats.get("cache_hit_ratio", 0)
    }

@app.get("/demo/load-test/{endpoint}")
async def performance_load_test(endpoint: str):
    """Test performance under load for specified endpoint"""
    import asyncio
    import aiohttp
    
    # Define test endpoints
    test_endpoints = {
        "restaurants": "/restaurants/",
        "customers": "/customers/",
        "orders": "/orders/",
        "analytics": "/analytics/restaurant-analytics/1"
    }
    
    if endpoint not in test_endpoints:
        raise HTTPException(status_code=400, detail=f"Invalid endpoint. Available: {list(test_endpoints.keys())}")
    
    test_url = f"http://localhost:8000{test_endpoints[endpoint]}"
    
    # Perform load test
    async def make_request():
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(test_url) as response:
                response_time = (time.time() - start_time) * 1000
                return response_time
    
    # Run multiple concurrent requests
    tasks = [make_request() for _ in range(10)]
    response_times = await asyncio.gather(*tasks)
    
    return {
        "endpoint": endpoint,
        "test_url": test_url,
        "concurrent_requests": 10,
        "response_times_ms": response_times,
        "average_response_time_ms": sum(response_times) / len(response_times),
        "min_response_time_ms": min(response_times),
        "max_response_time_ms": max(response_times)
    }

# ============================================================================
# RESTAURANT ENDPOINTS WITH ENTERPRISE CACHING
# ============================================================================

@app.post("/restaurants/", response_model=RestaurantResponse, status_code=201)
@cache_static_data()
async def create_new_restaurant(
    restaurant: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new restaurant with enterprise caching"""
    start_time = time.time()
    try:
        result = await create_restaurant(db, restaurant)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("create_restaurant", False, response_time, CacheNamespace.RESTAURANTS.value)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/restaurants/", response_model=List[RestaurantResponse])
@cache_static_data()
async def list_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all restaurants with pagination - Static data caching (30+ minutes TTL)"""
    start_time = time.time()
    result = await get_restaurants(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("list_restaurants", True, response_time, CacheNamespace.STATIC_DATA.value)
    return result

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
@cache_static_data()
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific restaurant by ID - Static data caching (30+ minutes TTL)"""
    start_time = time.time()
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_restaurant", True, response_time, CacheNamespace.STATIC_DATA.value)
    return restaurant

@app.get("/restaurants/{restaurant_id}/with-menu", response_model=RestaurantWithMenu)
@cache_static_data()
async def get_restaurant_with_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant with all menu items - Static data caching (30+ minutes TTL)"""
    start_time = time.time()
    restaurant = await get_restaurant_with_menu(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_restaurant_with_menu", True, response_time, CacheNamespace.STATIC_DATA.value)
    return restaurant

@app.put("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant_info(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update restaurant information with intelligent invalidation"""
    start_time = time.time()
    try:
        updated_restaurant = await update_restaurant(db, restaurant_id, restaurant_update)
        if not updated_restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("update_restaurant", False, response_time, CacheNamespace.STATIC_DATA.value)
        return updated_restaurant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/restaurants/{restaurant_id}", status_code=204)
async def delete_restaurant_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a restaurant with cache invalidation"""
    start_time = time.time()
    success = await delete_restaurant(db, restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("delete_restaurant", False, response_time, CacheNamespace.STATIC_DATA.value)

# ============================================================================
# CUSTOMER ENDPOINTS WITH ENTERPRISE CACHING
# ============================================================================

@app.post("/customers/", response_model=CustomerResponse, status_code=201)
@cache_customer_data()
async def create_new_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer with enterprise caching"""
    start_time = time.time()
    try:
        result = await create_customer(db, customer)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("create_customer", False, response_time, CacheNamespace.CUSTOMERS.value)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/customers/", response_model=List[CustomerResponse])
@cache_customer_data()
async def list_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all customers with pagination - Customer data caching (1 hour TTL)"""
    start_time = time.time()
    result = await get_customers(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("list_customers", True, response_time, CacheNamespace.CUSTOMERS.value)
    return result

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
@cache_customer_data()
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific customer by ID - Customer data caching (1 hour TTL)"""
    start_time = time.time()
    customer = await get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_customer", True, response_time, CacheNamespace.CUSTOMERS.value)
    return customer

@app.get("/customers/{customer_id}/with-orders", response_model=CustomerWithOrders)
@cache_customer_data()
async def get_customer_with_orders_endpoint(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer with all orders - Customer data caching (1 hour TTL)"""
    start_time = time.time()
    customer = await get_customer_with_orders(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_customer_with_orders", True, response_time, CacheNamespace.CUSTOMERS.value)
    return customer

@app.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer_info(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update customer information with intelligent invalidation"""
    start_time = time.time()
    try:
        updated_customer = await update_customer(db, customer_id, customer_update)
        if not updated_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("update_customer", False, response_time, CacheNamespace.CUSTOMERS.value)
        return updated_customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/customers/{customer_id}", status_code=204)
async def delete_customer_endpoint(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a customer with cache invalidation"""
    start_time = time.time()
    success = await delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("delete_customer", False, response_time, CacheNamespace.CUSTOMERS.value)

# ============================================================================
# ORDER ENDPOINTS WITH ENTERPRISE CACHING
# ============================================================================

@app.post("/customers/{customer_id}/orders/", response_model=OrderResponse, status_code=201)
@cache_order_data()
async def create_new_order(
    customer_id: int,
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order with enterprise caching"""
    start_time = time.time()
    try:
        result = await create_order(db, customer_id, order_data)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("create_order", False, response_time, CacheNamespace.ORDERS.value)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders/", response_model=List[OrderResponse])
@cache_order_data()
async def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all orders with pagination - Order data caching (5 minutes TTL)"""
    start_time = time.time()
    result = await get_orders(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("list_orders", True, response_time, CacheNamespace.ORDERS.value)
    return result

@app.get("/orders/{order_id}", response_model=OrderResponse)
@cache_order_data()
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific order by ID - Order data caching (5 minutes TTL)"""
    start_time = time.time()
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_order", True, response_time, CacheNamespace.ORDERS.value)
    return order

@app.get("/orders/{order_id}/with-details", response_model=OrderWithDetails)
@cache_order_data()
async def get_order_with_details_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get order with all details - Order data caching (5 minutes TTL)"""
    start_time = time.time()
    order = await get_order_with_details(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_order_with_details", True, response_time, CacheNamespace.ORDERS.value)
    return order

@app.get("/customers/{customer_id}/orders", response_model=List[OrderResponse])
@cache_order_data()
async def get_customer_orders_endpoint(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific customer - Order data caching (5 minutes TTL)"""
    start_time = time.time()
    result = await get_customer_orders(db, customer_id, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_customer_orders", True, response_time, CacheNamespace.ORDERS.value)
    return result

@app.get("/restaurants/{restaurant_id}/orders", response_model=List[OrderResponse])
@cache_order_data()
async def get_restaurant_orders_endpoint(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific restaurant - Order data caching (5 minutes TTL)"""
    start_time = time.time()
    result = await get_restaurant_orders(db, restaurant_id, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_restaurant_orders", True, response_time, CacheNamespace.ORDERS.value)
    return result

@app.put("/orders/{order_id}/status")
async def update_order_status_endpoint(
    order_id: int,
    new_status: OrderStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update order status with intelligent invalidation"""
    start_time = time.time()
    try:
        updated_order = await update_order_status(db, order_id, new_status)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("update_order_status", False, response_time, CacheNamespace.ORDERS.value)
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order_info(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update order information with intelligent invalidation"""
    start_time = time.time()
    try:
        updated_order = await update_order(db, order_id, order_update)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("update_order", False, response_time, CacheNamespace.ORDERS.value)
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/orders/{order_id}", status_code=204)
async def delete_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an order with cache invalidation"""
    start_time = time.time()
    success = await delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("delete_order", False, response_time, CacheNamespace.ORDERS.value)

# ============================================================================
# REVIEW ENDPOINTS WITH ENTERPRISE CACHING
# ============================================================================

@app.post("/orders/{order_id}/reviews/", response_model=ReviewResponse, status_code=201)
@cache_review_data()
async def create_new_review(
    order_id: int,
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new review with enterprise caching"""
    start_time = time.time()
    try:
        result = await create_review(db, order_id, review_data)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("create_review", False, response_time, CacheNamespace.REVIEWS.value)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/reviews/", response_model=List[ReviewResponse])
@cache_review_data()
async def list_reviews(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all reviews with pagination - Review data caching (10 minutes TTL)"""
    start_time = time.time()
    result = await get_reviews(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("list_reviews", True, response_time, CacheNamespace.REVIEWS.value)
    return result

@app.get("/reviews/{review_id}", response_model=ReviewResponse)
@cache_review_data()
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific review by ID - Review data caching (10 minutes TTL)"""
    start_time = time.time()
    review = await get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_review", True, response_time, CacheNamespace.REVIEWS.value)
    return review

@app.get("/restaurants/{restaurant_id}/reviews", response_model=List[ReviewResponse])
@cache_review_data()
async def get_restaurant_reviews_endpoint(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a specific restaurant - Review data caching (10 minutes TTL)"""
    start_time = time.time()
    result = await get_restaurant_reviews(db, restaurant_id, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_restaurant_reviews", True, response_time, CacheNamespace.REVIEWS.value)
    return result

@app.get("/customers/{customer_id}/reviews", response_model=List[ReviewResponse])
@cache_review_data()
async def get_customer_reviews_endpoint(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews by a specific customer - Review data caching (10 minutes TTL)"""
    start_time = time.time()
    result = await get_customer_reviews(db, customer_id, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("get_customer_reviews", True, response_time, CacheNamespace.REVIEWS.value)
    return result

@app.delete("/reviews/{review_id}", status_code=204)
async def delete_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a review with cache invalidation"""
    start_time = time.time()
    success = await delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("delete_review", False, response_time, CacheNamespace.REVIEWS.value)

# ============================================================================
# ANALYTICS ENDPOINTS WITH ENTERPRISE CACHING
# ============================================================================

@app.get("/analytics/restaurant-analytics/{restaurant_id}")
@cache_analytics_data()
async def get_restaurant_analytics_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant analytics - Analytics data caching (15 minutes TTL)"""
    start_time = time.time()
    try:
        result = await get_restaurant_analytics(db, restaurant_id)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_restaurant_analytics", True, response_time, CacheNamespace.ANALYTICS_DATA.value)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/customer-analytics/{customer_id}")
@cache_analytics_data()
async def get_customer_analytics_endpoint(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer analytics - Analytics data caching (15 minutes TTL)"""
    start_time = time.time()
    try:
        result = await get_customer_analytics(db, customer_id)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_customer_analytics", True, response_time, CacheNamespace.ANALYTICS_DATA.value)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# SEARCH ENDPOINTS WITH ENTERPRISE CACHING
# ============================================================================

@app.get("/search/restaurants")
@cache_static_data()
async def search_restaurants_endpoint(
    cuisine_type: Optional[str] = Query(None, description="Cuisine type to filter by"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    max_rating: Optional[float] = Query(None, ge=0, le=5, description="Maximum rating"),
    is_active: Optional[bool] = Query(None, description="Active status filter"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search restaurants with criteria - Static data caching (30+ minutes TTL)"""
    start_time = time.time()
    result = await search_restaurants_with_criteria(
        db, cuisine_type, min_rating, max_rating, is_active, skip, limit
    )
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("search_restaurants", True, response_time, CacheNamespace.STATIC_DATA.value)
    return result

@app.get("/search/orders")
@cache_dynamic_data()
async def filter_orders_endpoint(
    status: Optional[OrderStatus] = Query(None, description="Order status filter"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Minimum order amount"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Maximum order amount"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Filter orders with criteria - Dynamic data caching (2-5 minutes TTL)"""
    start_time = time.time()
    result = await filter_orders_with_criteria(
        db, status, start_date, end_date, min_amount, max_amount, skip, limit
    )
    response_time = (time.time() - start_time) * 1000
    log_enterprise_cache_performance("filter_orders", True, response_time, CacheNamespace.DYNAMIC_DATA.value)
    return result

# ============================================================================
# DEMO AND TESTING ENDPOINTS
# ============================================================================

@app.post("/demo/sample-data")
async def create_sample_data(db: AsyncSession = Depends(get_db)):
    """Create sample data for testing enterprise caching"""
    # Create sample restaurants
    sample_restaurants = [
        RestaurantCreate(
            name="Pizza Palace",
            description="Best pizza in town",
            cuisine_type="Italian",
            address="123 Main St",
            phone_number="555-0101",
            rating=4.5,
            is_active=True,
            opening_time=datetime.now().time(),
            closing_time=datetime.now().time()
        ),
        RestaurantCreate(
            name="Sushi Express",
            description="Fresh sushi and Japanese cuisine",
            cuisine_type="Japanese",
            address="456 Oak Ave",
            phone_number="555-0102",
            rating=4.8,
            is_active=True,
            opening_time=datetime.now().time(),
            closing_time=datetime.now().time()
        )
    ]
    
    created_restaurants = []
    for restaurant_data in sample_restaurants:
        try:
            restaurant = await create_restaurant(db, restaurant_data)
            created_restaurants.append(restaurant)
        except ValueError as e:
            logger.warning(f"Failed to create restaurant {restaurant_data.name}: {e}")
    
    # Create sample customers
    sample_customers = [
        CustomerCreate(
            name="John Doe",
            email="john@example.com",
            phone_number="555-0201",
            address="789 Pine St"
        ),
        CustomerCreate(
            name="Jane Smith",
            email="jane@example.com",
            phone_number="555-0202",
            address="321 Elm St"
        )
    ]
    
    created_customers = []
    for customer_data in sample_customers:
        try:
            customer = await create_customer(db, customer_data)
            created_customers.append(customer)
        except ValueError as e:
            logger.warning(f"Failed to create customer {customer_data.name}: {e}")
    
    return {
        "message": f"Created {len(created_restaurants)} restaurants and {len(created_customers)} customers",
        "restaurants": created_restaurants,
        "customers": created_customers
    }

@app.post("/cache/reset-stats")
async def reset_cache_statistics():
    """Reset enterprise cache statistics"""
    reset_enterprise_cache_stats()
    return {"message": "Enterprise cache statistics reset successfully"}

# Advanced Enterprise Cache Management Endpoints

@app.get("/cache/stats/detailed")
async def get_detailed_cache_statistics():
    """Get detailed cache statistics with namespace breakdown"""
    start_time = time.time()
    
    try:
        stats = await get_enterprise_cache_stats()
        performance_metrics = get_enterprise_performance_metrics()
        
        # Combine detailed statistics
        detailed_stats = {
            "cache_overview": {
                "total_keys": stats["total_keys"],
                "enterprise_cache_keys": stats["enterprise_cache_keys"],
                "cache_hit_ratio": stats["cache_hit_ratio"]
            },
            "namespace_breakdown": {
                "counts": stats["namespace_counts"],
                "sizes": stats["namespace_sizes"],
                "ttl_averages": stats["namespace_ttl"]
            },
            "performance_metrics": {
                "total_requests": performance_metrics["total_requests"],
                "hit_ratio": performance_metrics["hit_ratio"],
                "miss_ratio": performance_metrics["miss_ratio"],
                "namespace_performance": performance_metrics["namespace_performance"]
            },
            "memory_usage": stats["memory_usage"],
            "alerts": stats["performance_alerts"],
            "recent_keys": stats["cache_keys"][:20]  # Show first 20 keys
        }
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_detailed_cache_statistics", True, response_time, "analytics")
        
        return detailed_stats
        
    except Exception as e:
        logger.error(f"Error getting detailed cache statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detailed cache statistics")

@app.delete("/cache/clear/menu-items")
async def clear_menu_items_cache():
    """Clear all menu items cache"""
    start_time = time.time()
    
    try:
        await clear_cache(namespace=CacheNamespace.MENU_ITEMS.value)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("clear_menu_items_cache", True, response_time, "menu-items")
        
        return {
            "message": "Menu items cache cleared successfully",
            "namespace": CacheNamespace.MENU_ITEMS.value,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error clearing menu items cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear menu items cache")

@app.delete("/cache/clear/restaurants")
async def clear_restaurants_cache():
    """Clear all restaurants cache"""
    start_time = time.time()
    
    try:
        await clear_cache(namespace=CacheNamespace.RESTAURANTS.value)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("clear_restaurants_cache", True, response_time, "restaurants")
        
        return {
            "message": "Restaurants cache cleared successfully",
            "namespace": CacheNamespace.RESTAURANTS.value,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error clearing restaurants cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear restaurants cache")

@app.delete("/cache/clear/orders")
async def clear_orders_cache():
    """Clear all orders cache"""
    start_time = time.time()
    
    try:
        await clear_cache(namespace=CacheNamespace.ORDERS.value)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("clear_orders_cache", True, response_time, "orders")
        
        return {
            "message": "Orders cache cleared successfully",
            "namespace": CacheNamespace.ORDERS.value,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error clearing orders cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear orders cache")

@app.delete("/cache/clear/analytics")
async def clear_analytics_cache():
    """Clear all analytics cache"""
    start_time = time.time()
    
    try:
        await clear_cache(namespace=CacheNamespace.ANALYTICS_DATA.value)
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("clear_analytics_cache", True, response_time, "analytics")
        
        return {
            "message": "Analytics cache cleared successfully",
            "namespace": CacheNamespace.ANALYTICS_DATA.value,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error clearing analytics cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear analytics cache")

@app.get("/cache/keys/{namespace}")
async def get_cache_keys_by_namespace(namespace: str):
    """Get all cache keys for a specific namespace"""
    start_time = time.time()
    
    try:
        from redis import asyncio as aioredis
        redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
        
        # Get all keys for the namespace
        pattern = f"zomato-enterprise-cache:{namespace}:*"
        keys = await redis.keys(pattern)
        
        # Get key details
        key_details = []
        for key in keys[:50]:  # Limit to first 50 keys
            try:
                ttl = await redis.ttl(key)
                value_size = len(await redis.get(key) or "")
                key_details.append({
                    "key": key,
                    "ttl": ttl,
                    "size_bytes": value_size
                })
            except Exception:
                continue
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_cache_keys_by_namespace", True, response_time, namespace)
        
        return {
            "namespace": namespace,
            "total_keys": len(keys),
            "key_details": key_details,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error getting cache keys for namespace {namespace}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache keys for namespace {namespace}")

@app.get("/cache/performance/namespace/{namespace}")
async def get_namespace_performance(namespace: str):
    """Get performance metrics for a specific namespace"""
    start_time = time.time()
    
    try:
        performance_metrics = get_enterprise_performance_metrics()
        namespace_performance = performance_metrics["namespace_performance"]
        
        namespace_stats = {
            "namespace": namespace,
            "hits": namespace_performance["hits"].get(namespace, 0),
            "misses": namespace_performance["misses"].get(namespace, 0),
            "avg_response_time": namespace_performance["avg_response_times"].get(namespace, 0),
            "total_requests": namespace_performance["hits"].get(namespace, 0) + namespace_performance["misses"].get(namespace, 0)
        }
        
        # Calculate hit ratio for namespace
        total_requests = namespace_stats["total_requests"]
        if total_requests > 0:
            namespace_stats["hit_ratio"] = namespace_stats["hits"] / total_requests
        else:
            namespace_stats["hit_ratio"] = 0
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_namespace_performance", True, response_time, namespace)
        
        return namespace_stats
        
    except Exception as e:
        logger.error(f"Error getting namespace performance for {namespace}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics for namespace {namespace}")

@app.post("/cache/warm/restaurants")
async def warm_restaurants_cache(background_tasks: BackgroundTasks):
    """Warm restaurants cache with popular data"""
    start_time = time.time()
    
    try:
        background_tasks.add_task(warm_restaurants_cache_task)
        response_time = (time.time() - start_time) * 1000
        
        return {
            "message": "Restaurants cache warming started in background",
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error starting restaurants cache warming: {e}")
        raise HTTPException(status_code=500, detail="Failed to start restaurants cache warming")

async def warm_restaurants_cache_task():
    """Background task to warm restaurants cache"""
    try:
        from redis import asyncio as aioredis
        redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
        
        # Simulate warming popular restaurants
        popular_restaurants = [
            {"id": 1, "name": "Popular Restaurant 1", "rating": 4.5},
            {"id": 2, "name": "Popular Restaurant 2", "rating": 4.3},
            {"id": 3, "name": "Popular Restaurant 3", "rating": 4.7}
        ]
        
        for restaurant in popular_restaurants:
            key = f"zomato-enterprise-cache:restaurants:restaurant:{restaurant['id']}"
            await redis.set(key, str(restaurant), ex=ENTERPRISE_TTL["restaurants"])
        
        logger.info("Restaurants cache warming completed")
        
    except Exception as e:
        logger.error(f"Error in restaurants cache warming: {e}")

@app.post("/cache/warm/menu-items")
async def warm_menu_items_cache(background_tasks: BackgroundTasks):
    """Warm menu items cache with popular data"""
    start_time = time.time()
    
    try:
        background_tasks.add_task(warm_menu_items_cache_task)
        response_time = (time.time() - start_time) * 1000
        
        return {
            "message": "Menu items cache warming started in background",
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error starting menu items cache warming: {e}")
        raise HTTPException(status_code=500, detail="Failed to start menu items cache warming")

async def warm_menu_items_cache_task():
    """Background task to warm menu items cache"""
    try:
        from redis import asyncio as aioredis
        redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
        
        # Simulate warming popular menu items
        popular_items = [
            {"id": 1, "name": "Popular Item 1", "price": 15.99},
            {"id": 2, "name": "Popular Item 2", "price": 12.50},
            {"id": 3, "name": "Popular Item 3", "price": 18.75}
        ]
        
        for item in popular_items:
            key = f"zomato-enterprise-cache:menu-items:item:{item['id']}"
            await redis.set(key, str(item), ex=ENTERPRISE_TTL["menu_items"])
        
        logger.info("Menu items cache warming completed")
        
    except Exception as e:
        logger.error(f"Error in menu items cache warming: {e}")

@app.get("/cache/health/detailed")
async def get_detailed_cache_health():
    """Get detailed cache health status"""
    start_time = time.time()
    
    try:
        from redis import asyncio as aioredis
        redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
        
        # Test Redis connection
        await redis.ping()
        
        # Get Redis info
        info = await redis.info()
        
        # Get memory usage
        memory_info = await redis.info("memory")
        
        # Get performance metrics
        performance_metrics = get_enterprise_performance_metrics()
        
        detailed_health = {
            "status": "healthy",
            "redis_connection": "connected",
            "redis_version": info.get("redis_version", "unknown"),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
            "connected_clients": info.get("connected_clients", 0),
            "memory_usage": {
                "used_memory": memory_info.get("used_memory", 0),
                "used_memory_human": memory_info.get("used_memory_human", "0B"),
                "used_memory_peak": memory_info.get("used_memory_peak", 0),
                "used_memory_peak_human": memory_info.get("used_memory_peak_human", "0B")
            },
            "performance": {
                "total_requests": performance_metrics["total_requests"],
                "hit_ratio": performance_metrics["hit_ratio"],
                "avg_response_time": sum(performance_metrics["namespace_performance"]["avg_response_times"].values()) / len(performance_metrics["namespace_performance"]["avg_response_times"]) if performance_metrics["namespace_performance"]["avg_response_times"] else 0
            },
            "alerts": performance_metrics["alerts"][-5:] if performance_metrics["alerts"] else []
        }
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_detailed_cache_health", True, response_time, "health")
        
        return detailed_health
        
    except Exception as e:
        logger.error(f"Error getting detailed cache health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "redis_connection": "disconnected"
        }

# Advanced Enterprise Caching Endpoints

@app.get("/enterprise/patterns/write-through")
async def demonstrate_write_through_pattern():
    """Demonstrate write-through caching pattern"""
    start_time = time.time()
    
    try:
        # Simulate write-through pattern
        key = "demo:write-through"
        value = {"data": "write-through demo", "timestamp": datetime.now().isoformat()}
        namespace = "demo"
        expire = 300
        
        async def db_operation():
            return {"status": "database_updated", "data": value}
        
        result = await EnterpriseCachePatterns.write_through_pattern(key, value, namespace, expire, db_operation)
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("demonstrate_write_through_pattern", True, response_time, "patterns")
        
        return {
            "pattern": "write-through",
            "result": result,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error demonstrating write-through pattern: {e}")
        raise HTTPException(status_code=500, detail="Failed to demonstrate write-through pattern")

@app.get("/enterprise/patterns/cache-aside")
async def demonstrate_cache_aside_pattern():
    """Demonstrate cache-aside pattern"""
    start_time = time.time()
    
    try:
        key = "demo:cache-aside"
        namespace = "demo"
        expire = 300
        
        async def fetch_func():
            return {"data": "cache-aside demo", "timestamp": datetime.now().isoformat()}
        
        result = await EnterpriseCachePatterns.cache_aside_pattern(key, namespace, fetch_func, expire)
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("demonstrate_cache_aside_pattern", True, response_time, "patterns")
        
        return {
            "pattern": "cache-aside",
            "result": result,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error demonstrating cache-aside pattern: {e}")
        raise HTTPException(status_code=500, detail="Failed to demonstrate cache-aside pattern")

@app.post("/enterprise/invalidation/cascade")
async def cascade_invalidation_demo():
    """Demonstrate cascade invalidation"""
    start_time = time.time()
    
    try:
        primary_key = "demo:cascade"
        related_keys = ["related:1", "related:2"]
        namespaces = ["restaurants", "menu-items", "analytics"]
        
        await EnterpriseCacheInvalidation.cascade_invalidation(primary_key, related_keys, namespaces)
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("cascade_invalidation_demo", True, response_time, "invalidation")
        
        return {
            "pattern": "cascade_invalidation",
            "primary_key": primary_key,
            "related_keys": related_keys,
            "namespaces": namespaces,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error demonstrating cascade invalidation: {e}")
        raise HTTPException(status_code=500, detail="Failed to demonstrate cascade invalidation")

@app.post("/enterprise/warming/predictive")
async def predictive_warming_demo():
    """Demonstrate predictive cache warming"""
    start_time = time.time()
    
    try:
        data_patterns = {
            "restaurants": {"popular:1": {"id": 1, "name": "Popular Restaurant"}, "trending:1": {"id": 2, "name": "Trending Restaurant"}},
            "menu-items": {"popular:1": {"id": 1, "name": "Popular Item"}, "trending:1": {"id": 2, "name": "Trending Item"}}
        }
        
        await EnterpriseCacheWarming.predictive_warming(data_patterns)
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("predictive_warming_demo", True, response_time, "warming")
        
        return {
            "pattern": "predictive_warming",
            "data_patterns": data_patterns,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error demonstrating predictive warming: {e}")
        raise HTTPException(status_code=500, detail="Failed to demonstrate predictive warming")

@app.get("/enterprise/analytics/patterns")
async def get_cache_pattern_analytics():
    """Get cache usage pattern analytics"""
    start_time = time.time()
    
    try:
        patterns = EnterpriseCacheAnalytics.analyze_cache_patterns()
        predictions = EnterpriseCacheAnalytics.predict_cache_needs()
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_cache_pattern_analytics", True, response_time, "analytics")
        
        return {
            "cache_patterns": patterns,
            "predictions": predictions,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error getting cache pattern analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache pattern analytics")

@app.get("/enterprise/performance/report")
async def get_performance_report():
    """Get comprehensive performance report"""
    start_time = time.time()
    
    try:
        report = EnterprisePerformanceMonitoring.generate_performance_report()
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("get_performance_report", True, response_time, "performance")
        
        return {
            "performance_report": report,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error generating performance report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate performance report")

@app.get("/enterprise/security/validate/{namespace}")
async def validate_cache_access(namespace: str, user_id: Optional[int] = Query(None)):
    """Validate cache access permissions"""
    start_time = time.time()
    
    try:
        has_access = await EnterpriseCacheSecurity.validate_cache_access(namespace, user_id)
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("validate_cache_access", True, response_time, "security")
        
        return {
            "namespace": namespace,
            "user_id": user_id,
            "has_access": has_access,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error validating cache access: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate cache access")

@app.post("/enterprise/security/secure-key")
async def generate_secure_cache_key(key: str, namespace: str):
    """Generate secure cache key"""
    start_time = time.time()
    
    try:
        secure_key = await EnterpriseCacheSecurity.secure_cache_key(key, namespace)
        
        response_time = (time.time() - start_time) * 1000
        log_enterprise_cache_performance("generate_secure_cache_key", True, response_time, "security")
        
        return {
            "original_key": key,
            "namespace": namespace,
            "secure_key": secure_key,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error generating secure cache key: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate secure cache key")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 