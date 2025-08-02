from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from models import Restaurant
from schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantWithMenu,
    RestaurantSearch
)
from crud import (
    create_restaurant, get_restaurants, get_restaurant_by_id, get_restaurant_with_menu,
    update_restaurant, delete_restaurant, search_restaurants_with_criteria,
    get_restaurant_analytics
)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/", response_model=RestaurantResponse, status_code=201)
async def create_new_restaurant(
    restaurant: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new restaurant"""
    try:
        return await create_restaurant(db, restaurant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[RestaurantResponse])
async def list_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all restaurants with pagination"""
    return await get_restaurants(db, skip=skip, limit=limit)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific restaurant by ID"""
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.get("/{restaurant_id}/with-menu", response_model=RestaurantWithMenu)
async def get_restaurant_with_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant with all menu items"""
    restaurant = await get_restaurant_with_menu(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.put("/{restaurant_id}", response_model=RestaurantResponse)
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

@router.delete("/{restaurant_id}", status_code=204)
async def delete_restaurant_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a restaurant (cascade delete will handle related data)"""
    success = await delete_restaurant(db, restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@router.get("/search", response_model=List[RestaurantResponse])
async def search_restaurants(
    cuisine_type: Optional[str] = Query(None, description="Cuisine type to search for"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    max_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Maximum rating"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search restaurants with multiple criteria"""
    return await search_restaurants_with_criteria(
        db, cuisine_type, min_rating, max_rating, is_active, skip, limit
    )

@router.get("/{restaurant_id}/analytics")
async def get_restaurant_analytics_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant analytics and performance metrics"""
    try:
        analytics = await get_restaurant_analytics(db, restaurant_id)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 