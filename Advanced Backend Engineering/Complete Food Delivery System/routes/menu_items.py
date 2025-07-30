from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from models import MenuItem
from schemas import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, MenuItemWithRestaurant
)
from crud import (
    create_menu_item, get_menu_items, get_menu_item_by_id, get_restaurant_menu,
    update_menu_item, delete_menu_item
)

router = APIRouter(prefix="/menu-items", tags=["menu-items"])

@router.post("/", response_model=MenuItemResponse, status_code=201)
async def create_menu_item_endpoint(
    menu_item: MenuItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new menu item"""
    try:
        return await create_menu_item(db, menu_item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[MenuItemResponse])
async def list_menu_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all menu items with pagination"""
    return await get_menu_items(db, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific menu item by ID"""
    menu_item = await get_menu_item_by_id(db, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@router.put("/{item_id}", response_model=MenuItemResponse)
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

@router.delete("/{item_id}", status_code=204)
async def delete_menu_item_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a menu item"""
    success = await delete_menu_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")

# Restaurant-specific menu endpoints
@router.get("/restaurant/{restaurant_id}", response_model=List[MenuItemResponse])
async def get_restaurant_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a restaurant"""
    menu_items = await get_restaurant_menu(db, restaurant_id)
    if not menu_items:
        # Check if restaurant exists
        from crud import get_restaurant_by_id
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return menu_items 