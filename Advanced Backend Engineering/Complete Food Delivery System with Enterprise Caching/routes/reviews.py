from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from models import Review
from schemas import (
    ReviewCreate, ReviewResponse
)
from crud import (
    create_review, get_reviews, get_review_by_id, get_restaurant_reviews,
    get_customer_reviews, delete_review
)

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/orders/{order_id}/review", response_model=ReviewResponse, status_code=201)
async def add_review_after_order(
    order_id: int,
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a review after order completion"""
    try:
        return await create_review(db, order_id, review_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ReviewResponse])
async def list_reviews(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all reviews with pagination"""
    return await get_reviews(db, skip=skip, limit=limit)

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific review by ID"""
    review = await get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.delete("/{review_id}", status_code=204)
async def delete_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a review"""
    success = await delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")

# Restaurant-specific review endpoints
@router.get("/restaurants/{restaurant_id}/reviews", response_model=List[ReviewResponse])
async def get_restaurant_reviews_endpoint(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a specific restaurant"""
    reviews = await get_restaurant_reviews(db, restaurant_id, skip=skip, limit=limit)
    if not reviews:
        # Check if restaurant exists
        from crud import get_restaurant_by_id
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return reviews

# Customer-specific review endpoints
@router.get("/customers/{customer_id}/reviews", response_model=List[ReviewResponse])
async def get_customer_reviews_endpoint(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews by a specific customer"""
    reviews = await get_customer_reviews(db, customer_id, skip=skip, limit=limit)
    if not reviews:
        # Check if customer exists
        from crud import get_customer_by_id
        customer = await get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    return reviews 