from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from models import Customer
from schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerWithOrders,
    CustomerWithReviews
)
from crud import (
    create_customer, get_customers, get_customer_by_id, get_customer_with_orders,
    update_customer, delete_customer, get_customer_analytics
)

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_new_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer"""
    try:
        return await create_customer(db, customer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all customers with pagination"""
    return await get_customers(db, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific customer by ID"""
    customer = await get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/{customer_id}/with-orders", response_model=CustomerWithOrders)
async def get_customer_with_orders_endpoint(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer with all orders"""
    customer = await get_customer_with_orders(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer_info(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update customer information"""
    try:
        updated_customer = await update_customer(db, customer_id, customer_update)
        if not updated_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return updated_customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{customer_id}", status_code=204)
async def delete_customer_endpoint(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a customer (cascade delete will handle related data)"""
    success = await delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")

@router.get("/{customer_id}/analytics")
async def get_customer_analytics_endpoint(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer analytics and order history"""
    try:
        analytics = await get_customer_analytics(db, customer_id)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 