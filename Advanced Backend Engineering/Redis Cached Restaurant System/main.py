from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uvicorn
import time
import logging
from datetime import time
from database import get_db
from models import Restaurant
from schemas import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from crud import (
    create_restaurant,
    get_restaurants,
    get_restaurant_by_id,
    update_restaurant,
    delete_restaurant,
    search_restaurants_by_cuisine,
    get_active_restaurants
)
from cache_config import (
    init_cache, clear_cache, get_cache_stats, log_cache_performance,
    cache_restaurant_list, cache_restaurant_detail, cache_search_results, cache_active_restaurants
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zomato-like Restaurant Management System with Redis Cache",
    description="A restaurant management system with Redis caching for improved performance",
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
    """Initialize cache on startup"""
    await init_cache()
    logger.info("Redis cache initialized successfully")

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
        log_cache_performance("create_restaurant", False, response_time)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/restaurants/", response_model=List[RestaurantResponse])
@cache_restaurant_list()
async def list_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all restaurants with pagination - Cached with 300s TTL"""
    start_time = time.time()
    result = await get_restaurants(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("list_restaurants", True, response_time)
    return result

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
@cache_restaurant_detail()
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific restaurant by ID - Cached with 600s TTL"""
    start_time = time.time()
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("get_restaurant", True, response_time)
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
        log_cache_performance("update_restaurant", False, response_time)
        return updated_restaurant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/restaurants/{restaurant_id}", status_code=204)
async def delete_restaurant_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a restaurant"""
    start_time = time.time()
    success = await delete_restaurant(db, restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("delete_restaurant", False, response_time)

@app.get("/restaurants/search", response_model=List[RestaurantResponse])
@cache_search_results()
async def search_restaurants_by_cuisine_type(
    cuisine: str = Query(..., description="Cuisine type to search for"),
    db: AsyncSession = Depends(get_db)
):
    """Search restaurants by cuisine type - Cached with 180s TTL"""
    start_time = time.time()
    result = await search_restaurants_by_cuisine(db, cuisine)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("search_restaurants", True, response_time)
    return result

@app.get("/restaurants/active", response_model=List[RestaurantResponse])
@cache_active_restaurants()
async def list_active_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List only active restaurants - Cached with 240s TTL"""
    start_time = time.time()
    result = await get_active_restaurants(db, skip=skip, limit=limit)
    response_time = (time.time() - start_time) * 1000
    log_cache_performance("list_active_restaurants", True, response_time)
    return result

# Cache Management Endpoints
@app.get("/cache/stats")
async def get_cache_statistics():
    """View cache statistics and keys"""
    return await get_cache_stats()

@app.delete("/cache/clear")
async def clear_entire_cache():
    """Clear entire cache"""
    await clear_cache()
    return {"message": "Entire cache cleared successfully"}

@app.delete("/cache/clear/restaurants")
async def clear_restaurant_cache():
    """Clear only restaurant-related caches"""
    await clear_cache(namespace="restaurants")
    return {"message": "Restaurant cache cleared successfully"}

# Demo Endpoints
@app.get("/demo/cache-test/{restaurant_id}")
async def demonstrate_cache_performance(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Demonstrate cache performance with timing"""
    start_time = time.time()
    
    # First request (cache miss)
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    first_request_time = (time.time() - start_time) * 1000
    
    # Second request (cache hit)
    start_time = time.time()
    restaurant_cached = await get_restaurant_by_id(db, restaurant_id)
    second_request_time = (time.time() - start_time) * 1000
    
    return {
        "restaurant": restaurant,
        "performance_metrics": {
            "first_request_time_ms": round(first_request_time, 2),
            "second_request_time_ms": round(second_request_time, 2),
            "performance_improvement": round((first_request_time - second_request_time) / first_request_time * 100, 2)
        }
    }

@app.post("/demo/sample-data")
async def create_sample_restaurants(db: AsyncSession = Depends(get_db)):
    """Create sample restaurants for testing"""
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
        ),
        RestaurantCreate(
            name="Burger Joint",
            description="Classic American burgers",
            cuisine_type="American",
            address="321 Elm St",
            phone_number="555-0104",
            rating=4.0,
            is_active=True,
            opening_time=time(11, 0),
            closing_time=time(22, 0)
        ),
        RestaurantCreate(
            name="Curry House",
            description="Authentic Indian cuisine",
            cuisine_type="Indian",
            address="654 Maple Dr",
            phone_number="555-0105",
            rating=4.6,
            is_active=True,
            opening_time=time(12, 0),
            closing_time=time(21, 0)
        )
    ]
    
    created_restaurants = []
    for restaurant_data in sample_restaurants:
        try:
            restaurant = await create_restaurant(db, restaurant_data)
            created_restaurants.append(restaurant)
        except ValueError as e:
            logger.warning(f"Failed to create restaurant {restaurant_data.name}: {e}")
    
    return {
        "message": f"Created {len(created_restaurants)} sample restaurants",
        "restaurants": created_restaurants
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Zomato-like Restaurant Management System with Redis Cache",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "cache_endpoints": {
            "stats": "/cache/stats",
            "clear_all": "/cache/clear",
            "clear_restaurants": "/cache/clear/restaurants"
        },
        "demo_endpoints": {
            "cache_test": "/demo/cache-test/{restaurant_id}",
            "sample_data": "/demo/sample-data"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 