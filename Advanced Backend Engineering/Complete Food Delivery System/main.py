from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uvicorn
from datetime import datetime
from decimal import Decimal
from database import get_db
from models import Restaurant, MenuItem, Customer, Order, OrderItem, Review, OrderStatus
from schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantWithMenu,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, MenuItemWithRestaurant,
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerWithOrders,
    OrderCreate, OrderUpdate, OrderResponse, OrderWithDetails,
    ReviewCreate, ReviewResponse
)
from crud import (
    # Restaurant operations
    create_restaurant, get_restaurants, get_restaurant_by_id, get_restaurant_with_menu,
    update_restaurant, delete_restaurant, search_restaurants_with_criteria,
    # Menu item operations
    create_menu_item, get_menu_items, get_menu_item_by_id, get_restaurant_menu,
    update_menu_item, delete_menu_item,
    # Customer operations
    create_customer, get_customers, get_customer_by_id, get_customer_with_orders,
    update_customer, delete_customer,
    # Order operations
    create_order, get_orders, get_order_by_id, get_order_with_details,
    get_customer_orders, get_restaurant_orders, update_order_status,
    update_order, delete_order, filter_orders_with_criteria,
    # Review operations
    create_review, get_reviews, get_review_by_id, get_restaurant_reviews,
    get_customer_reviews, delete_review,
    # Analytics operations
    get_restaurant_analytics, get_customer_analytics
)

# Import route modules
from routes import restaurants, menu_items, customers, orders, reviews

app = FastAPI(
    title="Complete Food Delivery System",
    description="A comprehensive food delivery ecosystem with customers, orders, delivery tracking, and reviews",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(restaurants.router)
app.include_router(menu_items.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(reviews.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Complete Food Delivery System API",
        "version": "3.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "Restaurant Management",
            "Menu Management", 
            "Customer Management",
            "Order Management",
            "Review System",
            "Analytics",
            "Advanced Search & Filtering"
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }

# System information endpoint
@app.get("/system/info")
async def system_info():
    """Get system information and statistics"""
    return {
        "system": "Complete Food Delivery System",
        "version": "3.0.0",
        "database": "SQLite with SQLAlchemy",
        "framework": "FastAPI",
        "features": {
            "restaurants": "Full CRUD with menu management",
            "customers": "Customer management with order history",
            "orders": "Complex order management with status workflow",
            "reviews": "Review system with rating calculations",
            "analytics": "Business intelligence and reporting",
            "search": "Advanced search and filtering capabilities"
        },
        "relationships": {
            "restaurant_menu": "One-to-Many",
            "customer_orders": "One-to-Many", 
            "restaurant_orders": "One-to-Many",
            "order_items": "Many-to-Many with association object",
            "reviews": "Complex relationships with validation"
        }
    }

# Additional convenience endpoints
@app.get("/restaurants/{restaurant_id}/menu", response_model=List[MenuItemResponse])
async def get_restaurant_menu_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a restaurant (convenience endpoint)"""
    menu_items = await get_restaurant_menu(db, restaurant_id)
    if not menu_items:
        # Check if restaurant exists
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return menu_items

@app.get("/customers/{customer_id}/orders", response_model=List[OrderResponse])
async def get_customer_orders_endpoint(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a customer (convenience endpoint)"""
    orders = await get_customer_orders(db, customer_id, skip=skip, limit=limit)
    if not orders:
        # Check if customer exists
        customer = await get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    return orders

@app.get("/restaurants/{restaurant_id}/orders", response_model=List[OrderResponse])
async def get_restaurant_orders_endpoint(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a restaurant (convenience endpoint)"""
    orders = await get_restaurant_orders(db, restaurant_id, skip=skip, limit=limit)
    if not orders:
        # Check if restaurant exists
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return orders

@app.get("/restaurants/{restaurant_id}/reviews", response_model=List[ReviewResponse])
async def get_restaurant_reviews_endpoint(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a restaurant (convenience endpoint)"""
    reviews = await get_restaurant_reviews(db, restaurant_id, skip=skip, limit=limit)
    if not reviews:
        # Check if restaurant exists
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return reviews

@app.get("/customers/{customer_id}/reviews", response_model=List[ReviewResponse])
async def get_customer_reviews_endpoint(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews by a customer (convenience endpoint)"""
    reviews = await get_customer_reviews(db, customer_id, skip=skip, limit=limit)
    if not reviews:
        # Check if customer exists
        customer = await get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    return reviews

# Analytics endpoints
@app.get("/restaurants/{restaurant_id}/analytics")
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

@app.get("/customers/{customer_id}/analytics")
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

# Search endpoints
@app.get("/search/restaurants", response_model=List[RestaurantResponse])
async def search_restaurants_endpoint(
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

@app.get("/search/orders", response_model=List[OrderResponse])
async def search_orders_endpoint(
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 