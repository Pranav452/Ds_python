from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uvicorn
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
    get_restaurants_with_menu_stats
)

app = FastAPI(
    title="Restaurant-Menu Management System",
    description="A comprehensive restaurant management system with menu management and relationships",
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

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Restaurant-Menu Management System API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Restaurant Endpoints
@app.post("/restaurants/", response_model=RestaurantResponse, status_code=201)
async def create_new_restaurant(
    restaurant: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new restaurant"""
    try:
        return await create_restaurant(db, restaurant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/restaurants/", response_model=List[RestaurantResponse])
async def list_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all restaurants with pagination"""
    return await get_restaurants(db, skip=skip, limit=limit)

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific restaurant by ID"""
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.get("/restaurants/{restaurant_id}/with-menu", response_model=RestaurantWithMenu)
async def get_restaurant_with_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant with all menu items"""
    restaurant = await get_restaurant_with_menu(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.put("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant_info(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update restaurant information"""
    try:
        updated_restaurant = await update_restaurant(db, restaurant_id, restaurant_update)
        if not updated_restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return updated_restaurant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/restaurants/{restaurant_id}", status_code=204)
async def delete_restaurant_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a restaurant (cascade delete will handle menu items)"""
    success = await delete_restaurant(db, restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@app.get("/restaurants/search", response_model=List[RestaurantResponse])
async def search_restaurants_by_cuisine_type(
    cuisine: str = Query(..., description="Cuisine type to search for"),
    db: AsyncSession = Depends(get_db)
):
    """Search restaurants by cuisine type"""
    return await search_restaurants_by_cuisine(db, cuisine)

@app.get("/restaurants/active", response_model=List[RestaurantResponse])
async def list_active_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List only active restaurants"""
    return await get_active_restaurants(db, skip=skip, limit=limit)

# Menu Item Endpoints
@app.post("/restaurants/{restaurant_id}/menu-items/", response_model=MenuItemResponse, status_code=201)
async def add_menu_item_to_restaurant(
    restaurant_id: int,
    menu_item: MenuItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add menu item to restaurant"""
    if menu_item.restaurant_id != restaurant_id:
        raise HTTPException(status_code=400, detail="Restaurant ID mismatch")
    
    try:
        return await create_menu_item(db, menu_item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/menu-items/", response_model=List[MenuItemResponse])
async def list_menu_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all menu items with pagination"""
    return await get_menu_items(db, skip=skip, limit=limit)

@app.get("/menu-items/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific menu item by ID"""
    menu_item = await get_menu_item_by_id(db, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.get("/menu-items/{item_id}/with-restaurant", response_model=MenuItemWithRestaurant)
async def get_menu_item_with_restaurant_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get menu item with restaurant details"""
    menu_item = await get_menu_item_with_restaurant(db, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.get("/restaurants/{restaurant_id}/menu", response_model=List[MenuItemResponse])
async def get_restaurant_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a restaurant"""
    menu_items = await get_restaurant_menu(db, restaurant_id)
    if not menu_items:
        # Check if restaurant exists
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return menu_items

@app.put("/menu-items/{item_id}", response_model=MenuItemResponse)
async def update_menu_item_endpoint(
    item_id: int,
    menu_item_update: MenuItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update menu item"""
    try:
        updated_item = await update_menu_item(db, item_id, menu_item_update)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return updated_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/menu-items/{item_id}", status_code=204)
async def delete_menu_item_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a menu item"""
    success = await delete_menu_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")

# Search and Filter Endpoints
@app.get("/menu-items/search", response_model=List[MenuItemResponse])
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
    """Search menu items with filters"""
    search_params = MenuItemSearch(
        category=category,
        vegetarian=vegetarian,
        vegan=vegan,
        available=available,
        min_price=min_price,
        max_price=max_price
    )
    return await search_menu_items(db, search_params, skip=skip, limit=limit)

@app.get("/menu-items/category/{category}", response_model=List[MenuItemResponse])
async def get_menu_items_by_category_endpoint(
    category: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get menu items by category"""
    return await get_menu_items_by_category(db, category, skip=skip, limit=limit)

@app.get("/menu-items/vegetarian", response_model=List[MenuItemResponse])
async def get_vegetarian_menu_items_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all vegetarian menu items"""
    return await get_vegetarian_menu_items(db, skip=skip, limit=limit)

@app.get("/menu-items/vegan", response_model=List[MenuItemResponse])
async def get_vegan_menu_items_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all vegan menu items"""
    return await get_vegan_menu_items(db, skip=skip, limit=limit)

@app.get("/menu-items/available", response_model=List[MenuItemResponse])
async def get_available_menu_items_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all available menu items"""
    return await get_available_menu_items(db, skip=skip, limit=limit)

# Analytics Endpoints
@app.get("/analytics/average-menu-prices")
async def get_average_menu_prices(
    db: AsyncSession = Depends(get_db)
):
    """Get average menu price per restaurant"""
    return await get_average_menu_price_per_restaurant(db)

@app.get("/analytics/restaurants-with-stats")
async def get_restaurants_with_stats(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get restaurants with menu statistics"""
    return await get_restaurants_with_menu_stats(db, skip=skip, limit=limit)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 