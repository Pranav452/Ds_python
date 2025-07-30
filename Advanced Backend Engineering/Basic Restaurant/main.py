from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uvicorn
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

app = FastAPI(
    title="Zomato-like Restaurant Management System",
    description="A basic restaurant management system with CRUD operations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Delete a restaurant"""
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

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Zomato-like Restaurant Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 