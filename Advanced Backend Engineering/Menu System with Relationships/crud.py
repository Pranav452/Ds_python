from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models import Restaurant, MenuItem
from schemas import RestaurantCreate, RestaurantUpdate, MenuItemCreate, MenuItemUpdate, MenuItemSearch
from datetime import datetime
from decimal import Decimal

# Restaurant CRUD Operations
async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate) -> Restaurant:
    """Create a new restaurant"""
    try:
        db_restaurant = Restaurant(**restaurant.dict())
        db.add(db_restaurant)
        await db.commit()
        await db.refresh(db_restaurant)
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

async def get_restaurant_with_menu(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
    """Get restaurant with all menu items"""
    query = select(Restaurant).options(selectinload(Restaurant.menu_items)).where(Restaurant.id == restaurant_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_restaurant(db: AsyncSession, restaurant_id: int, restaurant_update: RestaurantUpdate) -> Optional[Restaurant]:
    """Update restaurant information"""
    existing_restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not existing_restaurant:
        return None
    
    update_data = restaurant_update.dict(exclude_unset=True)
    if not update_data:
        return existing_restaurant
    
    try:
        if 'name' in update_data:
            name_query = select(Restaurant).where(
                Restaurant.name == update_data['name'],
                Restaurant.id != restaurant_id
            )
            existing_name = await db.execute(name_query)
            if existing_name.scalar_one_or_none():
                raise ValueError("Restaurant with this name already exists")
        
        query = update(Restaurant).where(Restaurant.id == restaurant_id).values(**update_data)
        await db.execute(query)
        await db.commit()
        
        return await get_restaurant_by_id(db, restaurant_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Restaurant with this name already exists")

async def delete_restaurant(db: AsyncSession, restaurant_id: int) -> bool:
    """Delete a restaurant (cascade delete will handle menu items)"""
    existing_restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not existing_restaurant:
        return False
    
    query = delete(Restaurant).where(Restaurant.id == restaurant_id)
    await db.execute(query)
    await db.commit()
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

# MenuItem CRUD Operations
async def create_menu_item(db: AsyncSession, menu_item: MenuItemCreate) -> MenuItem:
    """Create a new menu item"""
    # Verify restaurant exists
    restaurant = await get_restaurant_by_id(db, menu_item.restaurant_id)
    if not restaurant:
        raise ValueError("Restaurant not found")
    
    try:
        db_menu_item = MenuItem(**menu_item.dict())
        db.add(db_menu_item)
        await db.commit()
        await db.refresh(db_menu_item)
        return db_menu_item
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error creating menu item")

async def get_menu_items(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[MenuItem]:
    """Get all menu items with pagination"""
    query = select(MenuItem).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_menu_item_by_id(db: AsyncSession, item_id: int) -> Optional[MenuItem]:
    """Get menu item by ID"""
    query = select(MenuItem).where(MenuItem.id == item_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_menu_item_with_restaurant(db: AsyncSession, item_id: int) -> Optional[MenuItem]:
    """Get menu item with restaurant details"""
    query = select(MenuItem).options(selectinload(MenuItem.restaurant)).where(MenuItem.id == item_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_restaurant_menu(db: AsyncSession, restaurant_id: int) -> List[MenuItem]:
    """Get all menu items for a specific restaurant"""
    # Verify restaurant exists
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        return []
    
    query = select(MenuItem).where(MenuItem.restaurant_id == restaurant_id)
    result = await db.execute(query)
    return result.scalars().all()

async def update_menu_item(db: AsyncSession, item_id: int, menu_item_update: MenuItemUpdate) -> Optional[MenuItem]:
    """Update menu item information"""
    existing_item = await get_menu_item_by_id(db, item_id)
    if not existing_item:
        return None
    
    update_data = menu_item_update.dict(exclude_unset=True)
    if not update_data:
        return existing_item
    
    try:
        query = update(MenuItem).where(MenuItem.id == item_id).values(**update_data)
        await db.execute(query)
        await db.commit()
        
        return await get_menu_item_by_id(db, item_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error updating menu item")

async def delete_menu_item(db: AsyncSession, item_id: int) -> bool:
    """Delete a menu item"""
    existing_item = await get_menu_item_by_id(db, item_id)
    if not existing_item:
        return False
    
    query = delete(MenuItem).where(MenuItem.id == item_id)
    await db.execute(query)
    await db.commit()
    return True

# Advanced Querying and Search
async def search_menu_items(db: AsyncSession, search_params: MenuItemSearch, skip: int = 0, limit: int = 10) -> List[MenuItem]:
    """Search menu items with filters"""
    query = select(MenuItem)
    conditions = []
    
    if search_params.category:
        conditions.append(MenuItem.category.ilike(f"%{search_params.category}%"))
    
    if search_params.vegetarian is not None:
        conditions.append(MenuItem.is_vegetarian == search_params.vegetarian)
    
    if search_params.vegan is not None:
        conditions.append(MenuItem.is_vegan == search_params.vegan)
    
    if search_params.available is not None:
        conditions.append(MenuItem.is_available == search_params.available)
    
    if search_params.min_price is not None:
        conditions.append(MenuItem.price >= search_params.min_price)
    
    if search_params.max_price is not None:
        conditions.append(MenuItem.price <= search_params.max_price)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_menu_items_by_category(db: AsyncSession, category: str, skip: int = 0, limit: int = 10) -> List[MenuItem]:
    """Get menu items by category"""
    query = select(MenuItem).where(MenuItem.category.ilike(f"%{category}%")).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_vegetarian_menu_items(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[MenuItem]:
    """Get all vegetarian menu items"""
    query = select(MenuItem).where(MenuItem.is_vegetarian == True).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_vegan_menu_items(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[MenuItem]:
    """Get all vegan menu items"""
    query = select(MenuItem).where(MenuItem.is_vegan == True).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_available_menu_items(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[MenuItem]:
    """Get all available menu items"""
    query = select(MenuItem).where(MenuItem.is_available == True).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# Analytics and Statistics
async def get_average_menu_price_per_restaurant(db: AsyncSession) -> List[dict]:
    """Calculate average menu price per restaurant"""
    query = select(
        Restaurant.id,
        Restaurant.name,
        func.avg(MenuItem.price).label('average_price'),
        func.count(MenuItem.id).label('menu_item_count')
    ).join(MenuItem, Restaurant.id == MenuItem.restaurant_id).group_by(Restaurant.id, Restaurant.name)
    
    result = await db.execute(query)
    return [
        {
            "restaurant_id": row.id,
            "restaurant_name": row.name,
            "average_price": float(row.average_price) if row.average_price else 0.0,
            "menu_item_count": row.menu_item_count
        }
        for row in result.fetchall()
    ]

async def get_restaurants_with_menu_stats(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[dict]:
    """Get restaurants with menu statistics"""
    query = select(
        Restaurant,
        func.count(MenuItem.id).label('menu_item_count'),
        func.avg(MenuItem.price).label('average_price'),
        func.min(MenuItem.price).label('min_price'),
        func.max(MenuItem.price).label('max_price')
    ).outerjoin(MenuItem, Restaurant.id == MenuItem.restaurant_id).group_by(Restaurant.id).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return [
        {
            "restaurant": restaurant,
            "menu_item_count": row.menu_item_count,
            "average_price": float(row.average_price) if row.average_price else 0.0,
            "min_price": float(row.min_price) if row.min_price else 0.0,
            "max_price": float(row.max_price) if row.max_price else 0.0
        }
        for row, restaurant in result.fetchall()
    ] 