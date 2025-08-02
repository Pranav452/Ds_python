from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models import Restaurant
from schemas import RestaurantCreate, RestaurantUpdate
from datetime import datetime
from cache_config import clear_cache, CACHE_NAMESPACE_RESTAURANTS

async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate) -> Restaurant:
    """Create a new restaurant"""
    try:
        db_restaurant = Restaurant(**restaurant.dict())
        db.add(db_restaurant)
        await db.commit()
        await db.refresh(db_restaurant)
        
        # Clear restaurant cache on creation
        await clear_cache(namespace=CACHE_NAMESPACE_RESTAURANTS)
        
        return db_restaurant
    except IntegrityError:
        await db.rollback()
        raise ValueError("Restaurant with this name already exists")

async def get_restaurants(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Restaurant]:
    """Get all restaurants with pagination"""
    query = select(Restaurant).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_restaurant_by_id(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
    """Get restaurant by ID"""
    query = select(Restaurant).where(Restaurant.id == restaurant_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_restaurant(db: AsyncSession, restaurant_id: int, restaurant_update: RestaurantUpdate) -> Optional[Restaurant]:
    """Update restaurant information"""
    # First check if restaurant exists
    existing_restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not existing_restaurant:
        return None
    
    # Prepare update data
    update_data = restaurant_update.dict(exclude_unset=True)
    if not update_data:
        return existing_restaurant
    
    try:
        # Check for name uniqueness if name is being updated
        if 'name' in update_data:
            name_query = select(Restaurant).where(
                Restaurant.name == update_data['name'],
                Restaurant.id != restaurant_id
            )
            existing_name = await db.execute(name_query)
            if existing_name.scalar_one_or_none():
                raise ValueError("Restaurant with this name already exists")
        
        # Update the restaurant
        query = update(Restaurant).where(Restaurant.id == restaurant_id).values(**update_data)
        await db.execute(query)
        await db.commit()
        
        # Clear restaurant cache on update
        await clear_cache(namespace=CACHE_NAMESPACE_RESTAURANTS)
        
        # Return updated restaurant
        return await get_restaurant_by_id(db, restaurant_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Restaurant with this name already exists")

async def delete_restaurant(db: AsyncSession, restaurant_id: int) -> bool:
    """Delete a restaurant"""
    existing_restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not existing_restaurant:
        return False
    
    query = delete(Restaurant).where(Restaurant.id == restaurant_id)
    await db.execute(query)
    await db.commit()
    
    # Clear restaurant cache on deletion
    await clear_cache(namespace=CACHE_NAMESPACE_RESTAURANTS)
    
    return True

async def search_restaurants_by_cuisine(db: AsyncSession, cuisine_type: str) -> List[Restaurant]:
    """Search restaurants by cuisine type"""
    query = select(Restaurant).where(Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
    result = await db.execute(query)
    return result.scalars().all()

async def get_active_restaurants(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Restaurant]:
    """Get only active restaurants with pagination"""
    query = select(Restaurant).where(Restaurant.is_active == True).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all() 