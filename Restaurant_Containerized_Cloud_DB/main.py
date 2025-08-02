from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog
from datetime import datetime

from database import get_db, init_db, check_db_connection, get_db_stats
from config import settings
from crud import *
from schemas import *
from tasks import process_order, generate_analytics_report, monitor_system_health
from redis import Redis
from config import get_redis_url

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="Restaurant Menu System v3.0",
    description="Containerized Restaurant Menu System with Cloud Database Integration",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for container orchestration."""
    try:
        # Check database connection
        db_healthy = check_db_connection()
        
        # Check Redis connection
        redis_client = Redis.from_url(get_redis_url())
        redis_healthy = redis_client.ping()
        
        return HealthCheck(
            status="healthy" if db_healthy and redis_healthy else "unhealthy",
            timestamp=datetime.utcnow(),
            database=db_healthy,
            redis=redis_healthy,
            version="3.0.0"
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            database=False,
            redis=False,
            version="3.0.0"
        )


# System monitoring endpoints
@app.get("/metrics")
async def get_metrics():
    """Get system metrics for monitoring."""
    try:
        db_stats = get_db_stats()
        
        # Get Redis info
        redis_client = Redis.from_url(get_redis_url())
        redis_info = redis_client.info()
        
        return {
            "database": db_stats,
            "redis": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory": redis_info.get("used_memory", 0),
                "total_commands_processed": redis_info.get("total_commands_processed", 0)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@app.post("/analytics/generate")
async def generate_analytics(background_tasks: BackgroundTasks):
    """Generate analytics report in background."""
    try:
        task = generate_analytics_report.delay()
        return {"task_id": task.id, "status": "started"}
    except Exception as e:
        logger.error("Failed to start analytics generation", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start analytics generation")


# User endpoints
@app.post("/users/", response_model=User)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        db_user = get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        return create_user(db=db, user=user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create user", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users."""
    try:
        users = get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error("Failed to get users", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    try:
        db_user = get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Internal server error")


# Restaurant endpoints
@app.post("/restaurants/", response_model=Restaurant)
def create_restaurant_endpoint(restaurant: RestaurantCreate, db: Session = Depends(get_db)):
    """Create a new restaurant."""
    try:
        return create_restaurant(db=db, restaurant=restaurant)
    except Exception as e:
        logger.error("Failed to create restaurant", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/restaurants/", response_model=List[Restaurant])
def read_restaurants(
    skip: int = 0, 
    limit: int = 100, 
    cuisine_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get restaurants with optional filtering."""
    try:
        restaurants = get_restaurants(db, skip=skip, limit=limit, cuisine_type=cuisine_type)
        return restaurants
    except Exception as e:
        logger.error("Failed to get restaurants", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/restaurants/{restaurant_id}", response_model=Restaurant)
def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get restaurant by ID."""
    try:
        db_restaurant = get_restaurant(db, restaurant_id=restaurant_id)
        if db_restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return db_restaurant
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get restaurant", error=str(e), restaurant_id=restaurant_id)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/restaurants/{restaurant_id}", response_model=Restaurant)
def update_restaurant_endpoint(
    restaurant_id: int, 
    restaurant: RestaurantUpdate, 
    db: Session = Depends(get_db)
):
    """Update restaurant information."""
    try:
        db_restaurant = update_restaurant(db=db, restaurant_id=restaurant_id, restaurant_update=restaurant)
        if db_restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return db_restaurant
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update restaurant", error=str(e), restaurant_id=restaurant_id)
        raise HTTPException(status_code=500, detail="Internal server error")


# Category endpoints
@app.post("/categories/", response_model=Category)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    try:
        return create_category(db=db, category=category)
    except Exception as e:
        logger.error("Failed to create category", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/categories/", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all categories."""
    try:
        categories = get_categories(db, skip=skip, limit=limit)
        return categories
    except Exception as e:
        logger.error("Failed to get categories", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


# Menu item endpoints
@app.post("/menu-items/", response_model=MenuItem)
def create_menu_item_endpoint(menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item."""
    try:
        return create_menu_item(db=db, menu_item=menu_item)
    except Exception as e:
        logger.error("Failed to create menu item", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/menu-items/restaurant/{restaurant_id}", response_model=List[MenuItem])
def read_menu_items_by_restaurant(
    restaurant_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get menu items for a specific restaurant."""
    try:
        menu_items = get_menu_items_by_restaurant(db, restaurant_id=restaurant_id, skip=skip, limit=limit)
        return menu_items
    except Exception as e:
        logger.error("Failed to get menu items", error=str(e), restaurant_id=restaurant_id)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/menu-items/{menu_item_id}", response_model=MenuItem)
def read_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    """Get menu item by ID."""
    try:
        db_menu_item = get_menu_item(db, menu_item_id=menu_item_id)
        if db_menu_item is None:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return db_menu_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get menu item", error=str(e), menu_item_id=menu_item_id)
        raise HTTPException(status_code=500, detail="Internal server error")


# Order endpoints
@app.post("/orders/", response_model=Order)
def create_order_endpoint(
    order: OrderCreate, 
    user_id: int = 1,  # In production, get from authentication
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Create a new order."""
    try:
        db_order = create_order(db=db, order=order, user_id=user_id)
        
        # Process order in background
        if background_tasks:
            background_tasks.add_task(process_order, {"id": db_order.id})
        else:
            process_order.delay({"id": db_order.id})
        
        return db_order
    except Exception as e:
        logger.error("Failed to create order", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID."""
    try:
        db_order = get_order(db, order_id=order_id)
        if db_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get order", error=str(e), order_id=order_id)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/orders/user/{user_id}", response_model=List[Order])
def read_user_orders(
    user_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get orders for a specific user."""
    try:
        orders = get_user_orders(db, user_id=user_id, skip=skip, limit=limit)
        return orders
    except Exception as e:
        logger.error("Failed to get user orders", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/orders/{order_id}", response_model=Order)
def update_order_endpoint(
    order_id: int, 
    order_update: OrderUpdate, 
    db: Session = Depends(get_db)
):
    """Update order information."""
    try:
        db_order = update_order(db=db, order_id=order_id, order_update=order_update)
        if db_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update order", error=str(e), order_id=order_id)
        raise HTTPException(status_code=500, detail="Internal server error")


# Review endpoints
@app.post("/reviews/", response_model=Review)
def create_review_endpoint(
    review: ReviewCreate, 
    user_id: int = 1,  # In production, get from authentication
    db: Session = Depends(get_db)
):
    """Create a new review."""
    try:
        return create_review(db=db, review=review, user_id=user_id)
    except Exception as e:
        logger.error("Failed to create review", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/reviews/restaurant/{restaurant_id}", response_model=List[Review])
def read_restaurant_reviews(
    restaurant_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get reviews for a specific restaurant."""
    try:
        reviews = get_restaurant_reviews(db, restaurant_id=restaurant_id, skip=skip, limit=limit)
        return reviews
    except Exception as e:
        logger.error("Failed to get restaurant reviews", error=str(e), restaurant_id=restaurant_id)
        raise HTTPException(status_code=500, detail="Internal server error")


# Delivery driver endpoints
@app.post("/delivery-drivers/", response_model=DeliveryDriver)
def create_delivery_driver_endpoint(driver: DeliveryDriverCreate, db: Session = Depends(get_db)):
    """Create a new delivery driver."""
    try:
        return create_delivery_driver(db=db, driver=driver)
    except Exception as e:
        logger.error("Failed to create delivery driver", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/delivery-drivers/available", response_model=List[DeliveryDriver])
def read_available_drivers(db: Session = Depends(get_db)):
    """Get all available delivery drivers."""
    try:
        drivers = get_available_drivers(db)
        return drivers
    except Exception as e:
        logger.error("Failed to get available drivers", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


# System endpoints
@app.get("/system/health")
async def system_health():
    """Comprehensive system health check."""
    try:
        task = monitor_system_health.delay()
        return {"task_id": task.id, "status": "started"}
    except Exception as e:
        logger.error("Failed to start system health check", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start system health check")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        logger.info("Starting Restaurant Menu System v3.0")
        
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Check Redis connection
        redis_client = Redis.from_url(get_redis_url())
        redis_client.ping()
        logger.info("Redis connection established")
        
        logger.info("Application startup completed")
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    try:
        logger.info("Shutting down Restaurant Menu System v3.0")
        # Add any cleanup logic here
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error("Application shutdown failed", error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 