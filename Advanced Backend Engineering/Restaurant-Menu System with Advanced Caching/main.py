from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uvicorn
import time
import logging
from datetime import time
from decimal import Decimal
from database import get_db
from models import Restaurant, MenuItem
from schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantWithMenu,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, MenuItemWithRestaurant,
    MenuItemSearch
)
from crud import (
    # Restaurant operations
    create_restaurant, get_restaurants, get_restaurant_by_id, get_restaurant_with_menu,
    update_restaurant, delete_restaurant, search_restaurants_by_cuisine, get_active_restaurants,
    # Menu item operations
    create_menu_item, get_menu_items, get_menu_item_by_id, get_menu_item_with_restaurant,
    get_restaurant_menu, update_menu_item, delete_menu_item,
    # Search and analytics
    search_menu_items, get_menu_items_by_category, get_vegetarian_menu_items,
    get_vegan_menu_items, get_available_menu_items, get_average_menu_price_per_restaurant,
    get_restaurants_with_menu_stats, get_popular_cuisines, get_price_range_analytics,
    get_dietary_preference_stats, warm_frequently_accessed_data
)
from cache_config import (
    init_cache, clear_cache, get_detailed_cache_stats, log_cache_performance,
    cache_restaurant_data, cache_menu_item_data, cache_restaurant_menu_data,
    cache_search_results, cache_analytics_data, cache_by_category,
    CacheCategory, get_cache_performance_metrics, reset_cache_stats
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Restaurant-Menu System with Advanced Caching",
    description="A comprehensive restaurant management system with advanced Redis caching strategies",
    version="2.0.0"
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
    """Initialize cache and warm frequently accessed data on startup"""
    await init_cache()
    logger.info("Advanced Redis cache initialized successfully")
    
    # Warm cache with frequently accessed data
    try:
        async for db in get_db():
            warm_result = await warm_frequently_accessed_data(db)
            logger.info(f"Cache warming completed: {warm_result}")
            break
    except Exception as e:
        logger.warning(f"Cache warming failed: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Restaurant-Menu System with Advanced Caching",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "cache_endpoints": {
            "stats": "/cache/stats/detailed",
            "performance": "/cache/performance",
            "clear_all": "/cache/clear",
            "clear_menu": "/cache/clear/menu-items",
            "clear_search": "/cache/clear/search"
        },
        "demo_endpoints": {
            "performance_comparison": "/demo/performance-comparison",
            "sample_data": "/demo/sample-data"
        }
    }

# Restaurant Endpoints with Advanced Caching
@app.post("/restaurants/", response_model=RestaurantResponse, status_code=201)
async def create_new_restaurant(
    restaurant: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new restaurant"""
    start_time = time.time()
    try:
        result = await create_restaurant(db, restaurant)
        response_time = (time.time() - start_time) * 1000
        log_cache_performance("create_restaurant", False, response_time, "restaurants")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/restaurants/", response_model=List[RestaurantResponse])
@cache_restaurant_data()
async def list_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all restaurants with pagination - Cached with 10-minute TTL"""
    start_time = time.time()
    result = await get_restaurants(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("list_restaurants", True, response_time, "restaurants")
    return result

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
@cache_restaurant_data()
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific restaurant by ID - Cached with 10-minute TTL"""
    start_time = time.time()
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_restaurant", True, response_time, "restaurants")
    return restaurant

@app.get("/restaurants/{restaurant_id}/with-menu", response_model=RestaurantWithMenu)
@cache_restaurant_menu_data()
async def get_restaurant_with_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant with all menu items - Cached with 15-minute TTL"""
    start_time = time.time()
    restaurant = await get_restaurant_with_menu(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_restaurant_with_menu", True, response_time, "restaurant-menus")
    return restaurant

@app.put("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant_info(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update restaurant information"""
    start_time = time.time()
    try:
        updated_restaurant = await update_restaurant(db, restaurant_id, restaurant_update)
        if not updated_restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        response_time = (time.time() - start_time) * 1000
        log_cache_performance("update_restaurant", False, response_time, "restaurants")
        return updated_restaurant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/restaurants/{restaurant_id}", status_code=204)
async def delete_restaurant_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a restaurant (cascade delete will handle menu items)"""
    start_time = time.time()
    success = await delete_restaurant(db, restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("delete_restaurant", False, response_time, "restaurants")

@app.get("/restaurants/search", response_model=List[RestaurantResponse])
@cache_search_results()
async def search_restaurants_by_cuisine_type(
    cuisine: str = Query(..., description="Cuisine type to search for"),
    db: AsyncSession = Depends(get_db)
):
    """Search restaurants by cuisine type - Cached with 5-minute TTL"""
    start_time = time.time()
    result = await search_restaurants_by_cuisine(db, cuisine)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("search_restaurants", True, response_time, "search-results")
    return result

@app.get("/restaurants/active", response_model=List[RestaurantResponse])
@cache_restaurant_data()
async def list_active_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List only active restaurants - Cached with 10-minute TTL"""
    start_time = time.time()
    result = await get_active_restaurants(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("list_active_restaurants", True, response_time, "restaurants")
    return result

# Menu Item Endpoints with Advanced Caching
@app.post("/restaurants/{restaurant_id}/menu-items/", response_model=MenuItemResponse, status_code=201)
async def add_menu_item_to_restaurant(
    restaurant_id: int,
    menu_item: MenuItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add menu item to restaurant"""
    if menu_item.restaurant_id != restaurant_id:
        raise HTTPException(status_code=400, detail="Restaurant ID mismatch")
    
    start_time = time.time()
    try:
        result = await create_menu_item(db, menu_item)
        response_time = (time.time() - start_time) * 1000
        log_cache_performance("create_menu_item", False, response_time, "menu-items")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/menu-items/", response_model=List[MenuItemResponse])
@cache_menu_item_data()
async def list_menu_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all menu items with pagination - Cached with 8-minute TTL"""
    start_time = time.time()
    result = await get_menu_items(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("list_menu_items", True, response_time, "menu-items")
    return result

@app.get("/menu-items/{item_id}", response_model=MenuItemResponse)
@cache_menu_item_data()
async def get_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific menu item by ID - Cached with 8-minute TTL"""
    start_time = time.time()
    menu_item = await get_menu_item_by_id(db, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_menu_item", True, response_time, "menu-items")
    return menu_item

@app.get("/menu-items/{item_id}/with-restaurant", response_model=MenuItemWithRestaurant)
@cache_menu_item_data()
async def get_menu_item_with_restaurant_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get menu item with restaurant details - Cached with 8-minute TTL"""
    start_time = time.time()
    menu_item = await get_menu_item_with_restaurant(db, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_menu_item_with_restaurant", True, response_time, "menu-items")
    return menu_item

@app.get("/restaurants/{restaurant_id}/menu", response_model=List[MenuItemResponse])
@cache_restaurant_menu_data()
async def get_restaurant_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a restaurant - Cached with 15-minute TTL"""
    start_time = time.time()
    menu_items = await get_restaurant_menu(db, restaurant_id)
    if not menu_items:
        # Check if restaurant exists
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_restaurant_menu", True, response_time, "restaurant-menus")
    return menu_items

@app.put("/menu-items/{item_id}", response_model=MenuItemResponse)
async def update_menu_item_endpoint(
    item_id: int,
    menu_item_update: MenuItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update menu item"""
    start_time = time.time()
    try:
        updated_item = await update_menu_item(db, item_id, menu_item_update)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        response_time = (time.time() - start_time) * 1000
        log_cache_performance("update_menu_item", False, response_time, "menu-items")
        return updated_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/menu-items/{item_id}", status_code=204)
async def delete_menu_item_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a menu item"""
    start_time = time.time()
    success = await delete_menu_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("delete_menu_item", False, response_time, "menu-items")

# Search and Filter Endpoints with Category-Specific Caching
@app.get("/menu-items/search", response_model=List[MenuItemResponse])
@cache_search_results()
async def search_menu_items_endpoint(
    category: Optional[str] = Query(None, description="Category to filter by"),
    vegetarian: Optional[bool] = Query(None, description="Filter by vegetarian items"),
    vegan: Optional[bool] = Query(None, description="Filter by vegan items"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search menu items with filters - Cached with 5-minute TTL"""
    start_time = time.time()
    search_params = MenuItemSearch(
        category=category,
        vegetarian=vegetarian,
        vegan=vegan,
        available=available,
        min_price=min_price,
        max_price=max_price
    )
    result = await search_menu_items(db, search_params, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("search_menu_items", True, response_time, "search-results")
    return result

@app.get("/menu-items/category/{category}", response_model=List[MenuItemResponse])
@cache_by_category(CacheCategory.POPULAR)
async def get_menu_items_by_category_endpoint(
    category: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get menu items by category - Cached with 10-minute TTL"""
    start_time = time.time()
    result = await get_menu_items_by_category(db, category, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_menu_items_by_category", True, response_time, "search-results")
    return result

@app.get("/menu-items/vegetarian", response_model=List[MenuItemResponse])
@cache_by_category(CacheCategory.VEGETARIAN)
async def get_vegetarian_menu_items_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all vegetarian menu items - Cached with 4-minute TTL"""
    start_time = time.time()
    result = await get_vegetarian_menu_items(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_vegetarian_menu_items", True, response_time, "search-results")
    return result

@app.get("/menu-items/vegan", response_model=List[MenuItemResponse])
@cache_by_category(CacheCategory.VEGAN)
async def get_vegan_menu_items_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all vegan menu items - Cached with 4-minute TTL"""
    start_time = time.time()
    result = await get_vegan_menu_items(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_vegan_menu_items", True, response_time, "search-results")
    return result

@app.get("/menu-items/available", response_model=List[MenuItemResponse])
@cache_menu_item_data()
async def get_available_menu_items_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all available menu items - Cached with 8-minute TTL"""
    start_time = time.time()
    result = await get_available_menu_items(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_available_menu_items", True, response_time, "menu-items")
    return result

# Analytics Endpoints with Business Logic Caching
@app.get("/analytics/average-menu-prices")
@cache_analytics_data()
async def get_average_menu_prices(
    db: AsyncSession = Depends(get_db)
):
    """Get average menu price per restaurant - Cached with 30-minute TTL"""
    start_time = time.time()
    result = await get_average_menu_price_per_restaurant(db)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_average_menu_prices", True, response_time, "analytics")
    return result

@app.get("/analytics/restaurants-with-stats")
@cache_analytics_data()
async def get_restaurants_with_stats(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get restaurants with menu statistics - Cached with 30-minute TTL"""
    start_time = time.time()
    result = await get_restaurants_with_menu_stats(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_restaurants_with_stats", True, response_time, "analytics")
    return result

@app.get("/analytics/popular-cuisines")
@cache_analytics_data()
async def get_popular_cuisines_endpoint(
    db: AsyncSession = Depends(get_db)
):
    """Get popular cuisines with restaurant counts - Cached with 30-minute TTL"""
    start_time = time.time()
    result = await get_popular_cuisines(db)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_popular_cuisines", True, response_time, "analytics")
    return result

@app.get("/analytics/price-range")
@cache_analytics_data()
async def get_price_range_analytics_endpoint(
    db: AsyncSession = Depends(get_db)
):
    """Get price range analytics for menu items - Cached with 30-minute TTL"""
    start_time = time.time()
    result = await get_price_range_analytics(db)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_price_range_analytics", True, response_time, "analytics")
    return result

@app.get("/analytics/dietary-preferences")
@cache_analytics_data()
async def get_dietary_preference_stats_endpoint(
    db: AsyncSession = Depends(get_db)
):
    """Get dietary preference statistics - Cached with 30-minute TTL"""
    start_time = time.time()
    result = await get_dietary_preference_stats(db)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_dietary_preference_stats", True, response_time, "analytics")
    return result

# Advanced Cache Management Endpoints
@app.get("/cache/stats/detailed")
async def get_detailed_cache_statistics():
    """Get detailed cache statistics by namespace"""
    return await get_detailed_cache_stats()

@app.get("/cache/performance")
async def get_cache_performance_metrics():
    """Get cache performance metrics"""
    return get_cache_performance_metrics()

@app.delete("/cache/clear")
async def clear_entire_cache():
    """Clear entire cache"""
    await clear_cache()
    return {"message": "Entire cache cleared successfully"}

@app.delete("/cache/clear/menu-items")
async def clear_menu_item_cache():
    """Clear menu-related caches"""
    await clear_cache(namespace="menu-items")
    return {"message": "Menu item cache cleared successfully"}

@app.delete("/cache/clear/search")
async def clear_search_cache():
    """Clear search result caches"""
    await clear_cache(namespace="search-results")
    return {"message": "Search result cache cleared successfully"}

@app.post("/cache/reset-stats")
async def reset_cache_statistics():
    """Reset cache statistics"""
    reset_cache_stats()
    return {"message": "Cache statistics reset successfully"}

# Demo and Performance Testing Endpoints
@app.get("/demo/performance-comparison")
async def demonstrate_performance_comparison(
    db: AsyncSession = Depends(get_db)
):
    """Compare cached vs non-cached performance"""
    results = {}
    
    # Test restaurant list performance
    start_time = time.time()
    restaurants = await get_restaurants(db, skip=0, limit=10)
    db_time = (time.time() - start_time) * 1000
    
    # Test cached version (this will be a cache hit if data exists)
    start_time = time.time()
    restaurants_cached = await get_restaurants(db, skip=0, limit=10)
    cache_time = (time.time() - start_time) * 1000
    
    results["restaurant_list"] = {
        "database_time_ms": round(db_time, 2),
        "cache_time_ms": round(cache_time, 2),
        "improvement_percent": round((db_time - cache_time) / db_time * 100, 2) if db_time > 0 else 0
    }
    
    # Test menu items performance
    start_time = time.time()
    menu_items = await get_menu_items(db, skip=0, limit=10)
    db_time = (time.time() - start_time) * 1000
    
    start_time = time.time()
    menu_items_cached = await get_menu_items(db, skip=0, limit=10)
    cache_time = (time.time() - start_time) * 1000
    
    results["menu_items"] = {
        "database_time_ms": round(db_time, 2),
        "cache_time_ms": round(cache_time, 2),
        "improvement_percent": round((db_time - cache_time) / db_time * 100, 2) if db_time > 0 else 0
    }
    
    # Test analytics performance
    start_time = time.time()
    analytics = await get_popular_cuisines(db)
    db_time = (time.time() - start_time) * 1000
    
    start_time = time.time()
    analytics_cached = await get_popular_cuisines(db)
    cache_time = (time.time() - start_time) * 1000
    
    results["analytics"] = {
        "database_time_ms": round(db_time, 2),
        "cache_time_ms": round(cache_time, 2),
        "improvement_percent": round((db_time - cache_time) / db_time * 100, 2) if db_time > 0 else 0
    }
    
    return {
        "performance_comparison": results,
        "cache_performance": get_cache_performance_metrics()
    }

@app.post("/demo/sample-data")
async def create_sample_data(db: AsyncSession = Depends(get_db)):
    """Create sample restaurants and menu items for testing"""
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
            opening_time=time(11, 0),
            closing_time=time(22, 0)
        ),
        RestaurantCreate(
            name="Sushi Express",
            description="Fresh sushi and Japanese cuisine",
            cuisine_type="Japanese",
            address="456 Oak Ave",
            phone_number="555-0102",
            rating=4.8,
            is_active=True,
            opening_time=time(12, 0),
            closing_time=time(21, 0)
        ),
        RestaurantCreate(
            name="Taco Fiesta",
            description="Authentic Mexican tacos",
            cuisine_type="Mexican",
            address="789 Pine St",
            phone_number="555-0103",
            rating=4.2,
            is_active=True,
            opening_time=time(10, 0),
            closing_time=time(23, 0)
        )
    ]
    
    created_restaurants = []
    for restaurant_data in sample_restaurants:
        try:
            restaurant = await create_restaurant(db, restaurant_data)
            created_restaurants.append(restaurant)
        except ValueError as e:
            logger.warning(f"Failed to create restaurant {restaurant_data.name}: {e}")
    
    # Create sample menu items
    sample_menu_items = [
        # Pizza Palace menu items
        MenuItemCreate(
            name="Margherita Pizza",
            description="Classic tomato and mozzarella",
            price=Decimal("12.99"),
            category="Pizza",
            is_vegetarian=True,
            is_vegan=False,
            is_available=True,
            preparation_time=15,
            restaurant_id=created_restaurants[0].id if created_restaurants else 1
        ),
        MenuItemCreate(
            name="Pepperoni Pizza",
            description="Spicy pepperoni with cheese",
            price=Decimal("14.99"),
            category="Pizza",
            is_vegetarian=False,
            is_vegan=False,
            is_available=True,
            preparation_time=18,
            restaurant_id=created_restaurants[0].id if created_restaurants else 1
        ),
        # Sushi Express menu items
        MenuItemCreate(
            name="California Roll",
            description="Crab, avocado, and cucumber",
            price=Decimal("8.99"),
            category="Sushi",
            is_vegetarian=False,
            is_vegan=False,
            is_available=True,
            preparation_time=10,
            restaurant_id=created_restaurants[1].id if len(created_restaurants) > 1 else 2
        ),
        MenuItemCreate(
            name="Vegetarian Roll",
            description="Avocado, cucumber, and carrot",
            price=Decimal("7.99"),
            category="Sushi",
            is_vegetarian=True,
            is_vegan=True,
            is_available=True,
            preparation_time=8,
            restaurant_id=created_restaurants[1].id if len(created_restaurants) > 1 else 2
        ),
        # Taco Fiesta menu items
        MenuItemCreate(
            name="Beef Taco",
            description="Ground beef with lettuce and cheese",
            price=Decimal("3.99"),
            category="Tacos",
            is_vegetarian=False,
            is_vegan=False,
            is_available=True,
            preparation_time=5,
            restaurant_id=created_restaurants[2].id if len(created_restaurants) > 2 else 3
        ),
        MenuItemCreate(
            name="Veggie Taco",
            description="Grilled vegetables with salsa",
            price=Decimal("3.49"),
            category="Tacos",
            is_vegetarian=True,
            is_vegan=True,
            is_available=True,
            preparation_time=6,
            restaurant_id=created_restaurants[2].id if len(created_restaurants) > 2 else 3
        )
    ]
    
    created_menu_items = []
    for menu_item_data in sample_menu_items:
        try:
            menu_item = await create_menu_item(db, menu_item_data)
            created_menu_items.append(menu_item)
        except ValueError as e:
            logger.warning(f"Failed to create menu item {menu_item_data.name}: {e}")
    
    return {
        "message": f"Created {len(created_restaurants)} restaurants and {len(created_menu_items)} menu items",
        "restaurants": created_restaurants,
        "menu_items": created_menu_items
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 