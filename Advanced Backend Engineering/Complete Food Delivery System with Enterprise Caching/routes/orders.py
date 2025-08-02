from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from database import get_db
from models import Order, OrderStatus
from schemas import (
    OrderCreate, OrderUpdate, OrderResponse, OrderWithDetails
)
from crud import (
    create_order, get_orders, get_order_by_id, get_order_with_details,
    get_customer_orders, get_restaurant_orders, update_order_status,
    update_order, delete_order, filter_orders_with_criteria
)

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/customers/{customer_id}/orders/", response_model=OrderResponse, status_code=201)
async def place_new_order(
    customer_id: int,
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Place a new order for a customer"""
    try:
        return await create_order(db, customer_id, order_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all orders with pagination"""
    return await get_orders(db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific order by ID"""
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/{order_id}/with-details", response_model=OrderWithDetails)
async def get_order_with_details_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get order with full details (customer, restaurant, order items)"""
    order = await get_order_with_details(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}/status")
async def update_order_status_endpoint(
    order_id: int,
    new_status: OrderStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update order status with business logic validation"""
    try:
        updated_order = await update_order_status(db, order_id, new_status)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": f"Order status updated to {new_status.value}", "order": updated_order}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_endpoint(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update order information"""
    try:
        updated_order = await update_order(db, order_id, order_update)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{order_id}", status_code=204)
async def delete_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an order"""
    success = await delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")

# Customer-specific order endpoints
@router.get("/customers/{customer_id}/orders", response_model=List[OrderResponse])
async def get_customer_orders_endpoint(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific customer"""
    orders = await get_customer_orders(db, customer_id, skip=skip, limit=limit)
    if not orders:
        # Check if customer exists
        from crud import get_customer_by_id
        customer = await get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    return orders

# Restaurant-specific order endpoints
@router.get("/restaurants/{restaurant_id}/orders", response_model=List[OrderResponse])
async def get_restaurant_orders_endpoint(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific restaurant"""
    orders = await get_restaurant_orders(db, restaurant_id, skip=skip, limit=limit)
    if not orders:
        # Check if restaurant exists
        from crud import get_restaurant_by_id
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return orders

# Search and filter endpoints
@router.get("/search", response_model=List[OrderResponse])
async def search_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Minimum order amount"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Maximum order amount"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search and filter orders with multiple criteria"""
    return await filter_orders_with_criteria(
        db, status, start_date, end_date, min_amount, max_amount, skip, limit
    ) 