from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict
from models import Restaurant, MenuItem, Customer, Order, OrderItem, Review, OrderStatus
from schemas import (
    RestaurantCreate, RestaurantUpdate, MenuItemCreate, MenuItemUpdate,
    CustomerCreate, CustomerUpdate, OrderCreate, OrderUpdate, ReviewCreate
)
from utils.business_logic import (
    OrderBusinessLogic, RestaurantBusinessLogic, CustomerBusinessLogic,
    SearchBusinessLogic, ValidationBusinessLogic
)
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
    """Delete a restaurant (cascade delete will handle related data)"""
    existing_restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not existing_restaurant:
        return False
    
    query = delete(Restaurant).where(Restaurant.id == restaurant_id)
    await db.execute(query)
    await db.commit()
    return True

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

async def get_restaurant_menu(db: AsyncSession, restaurant_id: int) -> List[MenuItem]:
    """Get all menu items for a specific restaurant"""
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

# Customer CRUD Operations
async def create_customer(db: AsyncSession, customer: CustomerCreate) -> Customer:
    """Create a new customer"""
    try:
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        await db.rollback()
        raise ValueError("Customer with this email already exists")

async def get_customers(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Customer]:
    """Get all customers with pagination"""
    query = select(Customer).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    """Get customer by ID"""
    query = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_customer_with_orders(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    """Get customer with all orders"""
    query = select(Customer).options(selectinload(Customer.orders)).where(Customer.id == customer_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_customer(db: AsyncSession, customer_id: int, customer_update: CustomerUpdate) -> Optional[Customer]:
    """Update customer information"""
    existing_customer = await get_customer_by_id(db, customer_id)
    if not existing_customer:
        return None
    
    update_data = customer_update.dict(exclude_unset=True)
    if not update_data:
        return existing_customer
    
    try:
        if 'email' in update_data:
            email_query = select(Customer).where(
                Customer.email == update_data['email'],
                Customer.id != customer_id
            )
            existing_email = await db.execute(email_query)
            if existing_email.scalar_one_or_none():
                raise ValueError("Customer with this email already exists")
        
        query = update(Customer).where(Customer.id == customer_id).values(**update_data)
        await db.execute(query)
        await db.commit()
        
        return await get_customer_by_id(db, customer_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Customer with this email already exists")

async def delete_customer(db: AsyncSession, customer_id: int) -> bool:
    """Delete a customer (cascade delete will handle related data)"""
    existing_customer = await get_customer_by_id(db, customer_id)
    if not existing_customer:
        return False
    
    query = delete(Customer).where(Customer.id == customer_id)
    await db.execute(query)
    await db.commit()
    return True

# Order CRUD Operations
async def create_order(db: AsyncSession, customer_id: int, order_data: OrderCreate) -> Order:
    """Create a new order with business logic validation"""
    # Validate customer exists
    if not await ValidationBusinessLogic.validate_customer_exists(db, customer_id):
        raise ValueError("Customer not found or inactive")
    
    # Validate restaurant exists
    if not await ValidationBusinessLogic.validate_restaurant_exists(db, order_data.restaurant_id):
        raise ValueError("Restaurant not found or inactive")
    
    # Calculate order total and validate items
    total_amount, validated_items = await OrderBusinessLogic.calculate_order_total(db, order_data.order_items)
    
    try:
        # Create order
        db_order = Order(
            customer_id=customer_id,
            restaurant_id=order_data.restaurant_id,
            order_status=OrderStatus.PLACED,
            total_amount=total_amount,
            delivery_address=order_data.delivery_address,
            special_instructions=order_data.special_instructions
        )
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)
        
        # Create order items
        for item in validated_items:
            db_order_item = OrderItem(
                order_id=db_order.id,
                menu_item_id=item['menu_item_id'],
                quantity=item['quantity'],
                item_price=item['item_price'],
                special_requests=item['special_requests']
            )
            db.add(db_order_item)
        
        await db.commit()
        await db.refresh(db_order)
        return db_order
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error creating order")

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Order]:
    """Get all orders with pagination"""
    query = select(Order).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Get order by ID"""
    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_order_with_details(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Get order with all details (customer, restaurant, order items)"""
    query = select(Order).options(
        selectinload(Order.customer),
        selectinload(Order.restaurant),
        selectinload(Order.order_items).selectinload(OrderItem.menu_item)
    ).where(Order.id == order_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_customer_orders(db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 10) -> List[Order]:
    """Get all orders for a specific customer"""
    if not await ValidationBusinessLogic.validate_customer_exists(db, customer_id):
        return []
    
    query = select(Order).where(Order.customer_id == customer_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_restaurant_orders(db: AsyncSession, restaurant_id: int, skip: int = 0, limit: int = 10) -> List[Order]:
    """Get all orders for a specific restaurant"""
    if not await ValidationBusinessLogic.validate_restaurant_exists(db, restaurant_id):
        return []
    
    query = select(Order).where(Order.restaurant_id == restaurant_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id: int, new_status: OrderStatus) -> Optional[Order]:
    """Update order status with business logic validation"""
    existing_order = await get_order_by_id(db, order_id)
    if not existing_order:
        return None
    
    # Validate status transition
    if not await OrderBusinessLogic.validate_order_status_transition(existing_order.order_status, new_status):
        raise ValueError(f"Invalid status transition from {existing_order.order_status.value} to {new_status.value}")
    
    try:
        query = update(Order).where(Order.id == order_id).values(order_status=new_status)
        await db.execute(query)
        await db.commit()
        
        return await get_order_by_id(db, order_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error updating order status")

async def update_order(db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order information"""
    existing_order = await get_order_by_id(db, order_id)
    if not existing_order:
        return None
    
    update_data = order_update.dict(exclude_unset=True)
    if not update_data:
        return existing_order
    
    # Validate status transition if status is being updated
    if 'order_status' in update_data:
        if not await OrderBusinessLogic.validate_order_status_transition(existing_order.order_status, update_data['order_status']):
            raise ValueError(f"Invalid status transition from {existing_order.order_status.value} to {update_data['order_status'].value}")
    
    try:
        query = update(Order).where(Order.id == order_id).values(**update_data)
        await db.execute(query)
        await db.commit()
        
        return await get_order_by_id(db, order_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error updating order")

async def delete_order(db: AsyncSession, order_id: int) -> bool:
    """Delete an order (cascade delete will handle order items)"""
    existing_order = await get_order_by_id(db, order_id)
    if not existing_order:
        return False
    
    query = delete(Order).where(Order.id == order_id)
    await db.execute(query)
    await db.commit()
    return True

# Review CRUD Operations
async def create_review(db: AsyncSession, order_id: int, review_data: ReviewCreate) -> Review:
    """Create a new review with business logic validation"""
    # Get order with details
    order = await get_order_with_details(db, order_id)
    if not order:
        raise ValueError("Order not found")
    
    # Validate order can be reviewed
    if not await OrderBusinessLogic.can_add_review(order):
        raise ValueError("Can only review delivered orders")
    
    # Check if review already exists
    if not await ValidationBusinessLogic.validate_review_not_exists(db, order_id):
        raise ValueError("Review already exists for this order")
    
    try:
        db_review = Review(
            customer_id=order.customer_id,
            restaurant_id=order.restaurant_id,
            order_id=order_id,
            rating=review_data.rating,
            comment=review_data.comment
        )
        db.add(db_review)
        await db.commit()
        await db.refresh(db_review)
        
        # Update restaurant rating
        new_rating = await RestaurantBusinessLogic.calculate_restaurant_rating(db, order.restaurant_id)
        await update_restaurant(db, order.restaurant_id, RestaurantUpdate(rating=new_rating))
        
        return db_review
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error creating review")

async def get_reviews(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Review]:
    """Get all reviews with pagination"""
    query = select(Review).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_review_by_id(db: AsyncSession, review_id: int) -> Optional[Review]:
    """Get review by ID"""
    query = select(Review).where(Review.id == review_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_restaurant_reviews(db: AsyncSession, restaurant_id: int, skip: int = 0, limit: int = 10) -> List[Review]:
    """Get all reviews for a specific restaurant"""
    if not await ValidationBusinessLogic.validate_restaurant_exists(db, restaurant_id):
        return []
    
    query = select(Review).where(Review.restaurant_id == restaurant_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_customer_reviews(db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 10) -> List[Review]:
    """Get all reviews by a specific customer"""
    if not await ValidationBusinessLogic.validate_customer_exists(db, customer_id):
        return []
    
    query = select(Review).where(Review.customer_id == customer_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def delete_review(db: AsyncSession, review_id: int) -> bool:
    """Delete a review"""
    existing_review = await get_review_by_id(db, review_id)
    if not existing_review:
        return False
    
    try:
        query = delete(Review).where(Review.id == review_id)
        await db.execute(query)
        await db.commit()
        
        # Update restaurant rating
        new_rating = await RestaurantBusinessLogic.calculate_restaurant_rating(db, existing_review.restaurant_id)
        await update_restaurant(db, existing_review.restaurant_id, RestaurantUpdate(rating=new_rating))
        
        return True
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error deleting review")

# Search and Analytics Operations
async def search_restaurants_with_criteria(
    db: AsyncSession,
    cuisine_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 10
) -> List[Restaurant]:
    """Search restaurants with multiple criteria"""
    return await SearchBusinessLogic.search_restaurants(
        db, cuisine_type, min_rating, max_rating, is_active, skip, limit
    )

async def filter_orders_with_criteria(
    db: AsyncSession,
    status: Optional[OrderStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    skip: int = 0,
    limit: int = 10
) -> List[Order]:
    """Filter orders with multiple criteria"""
    return await SearchBusinessLogic.filter_orders(
        db, status, start_date, end_date, min_amount, max_amount, skip, limit
    )

async def get_restaurant_analytics(db: AsyncSession, restaurant_id: int) -> Dict:
    """Get restaurant analytics"""
    if not await ValidationBusinessLogic.validate_restaurant_exists(db, restaurant_id):
        raise ValueError("Restaurant not found")
    
    analytics = await RestaurantBusinessLogic.get_restaurant_analytics(db, restaurant_id)
    return analytics.dict()

async def get_customer_analytics(db: AsyncSession, customer_id: int) -> Dict:
    """Get customer analytics"""
    if not await ValidationBusinessLogic.validate_customer_exists(db, customer_id):
        raise ValueError("Customer not found")
    
    analytics = await CustomerBusinessLogic.get_customer_analytics(db, customer_id)
    return analytics.dict() 