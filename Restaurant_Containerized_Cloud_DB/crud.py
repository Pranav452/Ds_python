from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models import (
    User, Restaurant, Category, MenuItem, Order, OrderItem, 
    Review, DeliveryDriver, Delivery
)
from schemas import (
    UserCreate, UserUpdate, RestaurantCreate, RestaurantUpdate,
    CategoryCreate, CategoryUpdate, MenuItemCreate, MenuItemUpdate,
    OrderCreate, OrderUpdate, ReviewCreate, ReviewUpdate,
    DeliveryDriverCreate, DeliveryDriverUpdate, DeliveryCreate, DeliveryUpdate
)
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

logger = structlog.get_logger()


# User CRUD operations
def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            phone=user.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info("User created successfully", user_id=db_user.id, username=user.username)
        return db_user
    except Exception as e:
        logger.error("Failed to create user", error=str(e), username=user.username)
        db.rollback()
        raise


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user information."""
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            db_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_user)
            
            logger.info("User updated successfully", user_id=user_id)
            return db_user
        return None
    except Exception as e:
        logger.error("Failed to update user", error=str(e), user_id=user_id)
        db.rollback()
        raise


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user."""
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            logger.info("User deleted successfully", user_id=user_id)
            return True
        return False
    except Exception as e:
        logger.error("Failed to delete user", error=str(e), user_id=user_id)
        db.rollback()
        raise


# Restaurant CRUD operations
def create_restaurant(db: Session, restaurant: RestaurantCreate) -> Restaurant:
    """Create a new restaurant."""
    try:
        db_restaurant = Restaurant(**restaurant.dict())
        db.add(db_restaurant)
        db.commit()
        db.refresh(db_restaurant)
        
        logger.info("Restaurant created successfully", restaurant_id=db_restaurant.id, name=restaurant.name)
        return db_restaurant
    except Exception as e:
        logger.error("Failed to create restaurant", error=str(e), name=restaurant.name)
        db.rollback()
        raise


def get_restaurant(db: Session, restaurant_id: int) -> Optional[Restaurant]:
    """Get restaurant by ID."""
    return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()


def get_restaurants(db: Session, skip: int = 0, limit: int = 100, cuisine_type: Optional[str] = None) -> List[Restaurant]:
    """Get restaurants with optional filtering."""
    query = db.query(Restaurant).filter(Restaurant.is_active == True)
    
    if cuisine_type:
        query = query.filter(Restaurant.cuisine_type == cuisine_type)
    
    return query.offset(skip).limit(limit).all()


def update_restaurant(db: Session, restaurant_id: int, restaurant_update: RestaurantUpdate) -> Optional[Restaurant]:
    """Update restaurant information."""
    try:
        db_restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if db_restaurant:
            update_data = restaurant_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_restaurant, field, value)
            db_restaurant.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_restaurant)
            
            logger.info("Restaurant updated successfully", restaurant_id=restaurant_id)
            return db_restaurant
        return None
    except Exception as e:
        logger.error("Failed to update restaurant", error=str(e), restaurant_id=restaurant_id)
        db.rollback()
        raise


def delete_restaurant(db: Session, restaurant_id: int) -> bool:
    """Delete restaurant (soft delete)."""
    try:
        db_restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if db_restaurant:
            db_restaurant.is_active = False
            db_restaurant.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Restaurant deleted successfully", restaurant_id=restaurant_id)
            return True
        return False
    except Exception as e:
        logger.error("Failed to delete restaurant", error=str(e), restaurant_id=restaurant_id)
        db.rollback()
        raise


# Category CRUD operations
def create_category(db: Session, category: CategoryCreate) -> Category:
    """Create a new category."""
    try:
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        logger.info("Category created successfully", category_id=db_category.id, name=category.name)
        return db_category
    except Exception as e:
        logger.error("Failed to create category", error=str(e), name=category.name)
        db.rollback()
        raise


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Get category by ID."""
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get all categories."""
    return db.query(Category).filter(Category.is_active == True).offset(skip).limit(limit).all()


def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
    """Update category information."""
    try:
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if db_category:
            update_data = category_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_category, field, value)
            db.commit()
            db.refresh(db_category)
            
            logger.info("Category updated successfully", category_id=category_id)
            return db_category
        return None
    except Exception as e:
        logger.error("Failed to update category", error=str(e), category_id=category_id)
        db.rollback()
        raise


# MenuItem CRUD operations
def create_menu_item(db: Session, menu_item: MenuItemCreate) -> MenuItem:
    """Create a new menu item."""
    try:
        db_menu_item = MenuItem(**menu_item.dict())
        db.add(db_menu_item)
        db.commit()
        db.refresh(db_menu_item)
        
        logger.info("Menu item created successfully", menu_item_id=db_menu_item.id, name=menu_item.name)
        return db_menu_item
    except Exception as e:
        logger.error("Failed to create menu item", error=str(e), name=menu_item.name)
        db.rollback()
        raise


def get_menu_item(db: Session, menu_item_id: int) -> Optional[MenuItem]:
    """Get menu item by ID."""
    return db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()


def get_menu_items_by_restaurant(db: Session, restaurant_id: int, skip: int = 0, limit: int = 100) -> List[MenuItem]:
    """Get menu items for a specific restaurant."""
    return db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.is_available == True
    ).offset(skip).limit(limit).all()


def update_menu_item(db: Session, menu_item_id: int, menu_item_update: MenuItemUpdate) -> Optional[MenuItem]:
    """Update menu item information."""
    try:
        db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
        if db_menu_item:
            update_data = menu_item_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_menu_item, field, value)
            db_menu_item.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_menu_item)
            
            logger.info("Menu item updated successfully", menu_item_id=menu_item_id)
            return db_menu_item
        return None
    except Exception as e:
        logger.error("Failed to update menu item", error=str(e), menu_item_id=menu_item_id)
        db.rollback()
        raise


def delete_menu_item(db: Session, menu_item_id: int) -> bool:
    """Delete menu item (soft delete)."""
    try:
        db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
        if db_menu_item:
            db_menu_item.is_available = False
            db_menu_item.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Menu item deleted successfully", menu_item_id=menu_item_id)
            return True
        return False
    except Exception as e:
        logger.error("Failed to delete menu item", error=str(e), menu_item_id=menu_item_id)
        db.rollback()
        raise


# Order CRUD operations
def create_order(db: Session, order: OrderCreate, user_id: int) -> Order:
    """Create a new order."""
    try:
        # Calculate total amount
        total_amount = 0
        for item in order.order_items:
            menu_item = get_menu_item(db, item.menu_item_id)
            if menu_item:
                total_amount += menu_item.price * item.quantity
        
        # Create order
        db_order = Order(
            user_id=user_id,
            restaurant_id=order.restaurant_id,
            total_amount=total_amount,
            delivery_address=order.delivery_address,
            delivery_instructions=order.delivery_instructions
        )
        db.add(db_order)
        db.flush()  # Get the order ID
        
        # Create order items
        for item in order.order_items:
            menu_item = get_menu_item(db, item.menu_item_id)
            if menu_item:
                db_order_item = OrderItem(
                    order_id=db_order.id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                    unit_price=menu_item.price,
                    total_price=menu_item.price * item.quantity,
                    special_instructions=item.special_instructions
                )
                db.add(db_order_item)
        
        db.commit()
        db.refresh(db_order)
        
        logger.info("Order created successfully", order_id=db_order.id, user_id=user_id)
        return db_order
    except Exception as e:
        logger.error("Failed to create order", error=str(e), user_id=user_id)
        db.rollback()
        raise


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID."""
    return db.query(Order).filter(Order.id == order_id).first()


def get_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders for a specific user."""
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_restaurant_orders(db: Session, restaurant_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders for a specific restaurant."""
    return db.query(Order).filter(Order.restaurant_id == restaurant_id).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order information."""
    try:
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if db_order:
            update_data = order_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_order, field, value)
            db_order.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_order)
            
            logger.info("Order updated successfully", order_id=order_id)
            return db_order
        return None
    except Exception as e:
        logger.error("Failed to update order", error=str(e), order_id=order_id)
        db.rollback()
        raise


# Review CRUD operations
def create_review(db: Session, review: ReviewCreate, user_id: int) -> Review:
    """Create a new review."""
    try:
        db_review = Review(
            user_id=user_id,
            restaurant_id=review.restaurant_id,
            order_id=review.order_id,
            rating=review.rating,
            comment=review.comment
        )
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        
        logger.info("Review created successfully", review_id=db_review.id, user_id=user_id)
        return db_review
    except Exception as e:
        logger.error("Failed to create review", error=str(e), user_id=user_id)
        db.rollback()
        raise


def get_review(db: Session, review_id: int) -> Optional[Review]:
    """Get review by ID."""
    return db.query(Review).filter(Review.id == review_id).first()


def get_restaurant_reviews(db: Session, restaurant_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
    """Get reviews for a specific restaurant."""
    return db.query(Review).filter(Review.restaurant_id == restaurant_id).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()


def update_review(db: Session, review_id: int, review_update: ReviewUpdate) -> Optional[Review]:
    """Update review information."""
    try:
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review:
            update_data = review_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_review, field, value)
            db.commit()
            db.refresh(db_review)
            
            logger.info("Review updated successfully", review_id=review_id)
            return db_review
        return None
    except Exception as e:
        logger.error("Failed to update review", error=str(e), review_id=review_id)
        db.rollback()
        raise


# Delivery Driver CRUD operations
def create_delivery_driver(db: Session, driver: DeliveryDriverCreate) -> DeliveryDriver:
    """Create a new delivery driver."""
    try:
        db_driver = DeliveryDriver(**driver.dict())
        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)
        
        logger.info("Delivery driver created successfully", driver_id=db_driver.id, name=driver.name)
        return db_driver
    except Exception as e:
        logger.error("Failed to create delivery driver", error=str(e), name=driver.name)
        db.rollback()
        raise


def get_delivery_driver(db: Session, driver_id: int) -> Optional[DeliveryDriver]:
    """Get delivery driver by ID."""
    return db.query(DeliveryDriver).filter(DeliveryDriver.id == driver_id).first()


def get_available_drivers(db: Session) -> List[DeliveryDriver]:
    """Get all available delivery drivers."""
    return db.query(DeliveryDriver).filter(DeliveryDriver.is_available == True).all()


def update_delivery_driver(db: Session, driver_id: int, driver_update: DeliveryDriverUpdate) -> Optional[DeliveryDriver]:
    """Update delivery driver information."""
    try:
        db_driver = db.query(DeliveryDriver).filter(DeliveryDriver.id == driver_id).first()
        if db_driver:
            update_data = driver_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_driver, field, value)
            db_driver.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_driver)
            
            logger.info("Delivery driver updated successfully", driver_id=driver_id)
            return db_driver
        return None
    except Exception as e:
        logger.error("Failed to update delivery driver", error=str(e), driver_id=driver_id)
        db.rollback()
        raise


# Delivery CRUD operations
def create_delivery(db: Session, delivery: DeliveryCreate) -> Delivery:
    """Create a new delivery."""
    try:
        db_delivery = Delivery(**delivery.dict())
        db.add(db_delivery)
        db.commit()
        db.refresh(db_delivery)
        
        logger.info("Delivery created successfully", delivery_id=db_delivery.id, order_id=delivery.order_id)
        return db_delivery
    except Exception as e:
        logger.error("Failed to create delivery", error=str(e), order_id=delivery.order_id)
        db.rollback()
        raise


def get_delivery(db: Session, delivery_id: int) -> Optional[Delivery]:
    """Get delivery by ID."""
    return db.query(Delivery).filter(Delivery.id == delivery_id).first()


def get_order_delivery(db: Session, order_id: int) -> Optional[Delivery]:
    """Get delivery for a specific order."""
    return db.query(Delivery).filter(Delivery.order_id == order_id).first()


def update_delivery(db: Session, delivery_id: int, delivery_update: DeliveryUpdate) -> Optional[Delivery]:
    """Update delivery information."""
    try:
        db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if db_delivery:
            update_data = delivery_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_delivery, field, value)
            db_delivery.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_delivery)
            
            logger.info("Delivery updated successfully", delivery_id=delivery_id)
            return db_delivery
        return None
    except Exception as e:
        logger.error("Failed to update delivery", error=str(e), delivery_id=delivery_id)
        db.rollback()
        raise 