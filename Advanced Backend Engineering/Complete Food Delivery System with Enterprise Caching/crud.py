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
from enterprise_cache_config import (
    invalidate_customer_cache, invalidate_restaurant_cache, invalidate_order_cache,
    invalidate_delivery_cache, invalidate_review_cache, write_through_cache,
    cache_aside_get, ENTERPRISE_TTL, CacheNamespace
)

# Restaurant CRUD Operations with Enterprise Caching
async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate) -> Restaurant:
    """Create a new restaurant with write-through caching"""
    try:
        db_restaurant = Restaurant(**restaurant.dict())
        db.add(db_restaurant)
        await db.commit()
        await db.refresh(db_restaurant)
        
        # Write-through caching for restaurant data
        await write_through_cache(
            key=f"restaurant:{db_restaurant.id}",
            value=db_restaurant,
            namespace=CacheNamespace.RESTAURANTS.value,
            expire=ENTERPRISE_TTL["restaurants"]
        )
        
        return db_restaurant
    except IntegrityError:
        await db.rollback()
        raise ValueError("Restaurant with this name already exists")

async def get_restaurants(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Restaurant]:
    """Get all restaurants with pagination - Cache-aside pattern"""
    async def fetch_restaurants():
        query = select(Restaurant).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"restaurants:list:{skip}:{limit}",
        namespace=CacheNamespace.RESTAURANTS.value,
        fetch_func=fetch_restaurants,
        expire=ENTERPRISE_TTL["restaurants"]
    )

async def get_restaurant_by_id(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
    """Get restaurant by ID - Cache-aside pattern"""
    async def fetch_restaurant():
        query = select(Restaurant).where(Restaurant.id == restaurant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"restaurant:{restaurant_id}",
        namespace=CacheNamespace.RESTAURANTS.value,
        fetch_func=fetch_restaurant,
        expire=ENTERPRISE_TTL["restaurants"]
    )

async def get_restaurant_with_menu(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
    """Get restaurant with all menu items - Cache-aside pattern"""
    async def fetch_restaurant_with_menu():
        query = select(Restaurant).options(selectinload(Restaurant.menu_items)).where(Restaurant.id == restaurant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"restaurant:with_menu:{restaurant_id}",
        namespace=CacheNamespace.RESTAURANTS.value,
        fetch_func=fetch_restaurant_with_menu,
        expire=ENTERPRISE_TTL["restaurants"]
    )

async def update_restaurant(db: AsyncSession, restaurant_id: int, restaurant_update: RestaurantUpdate) -> Optional[Restaurant]:
    """Update restaurant information with intelligent invalidation"""
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
        
        # Invalidate restaurant cache
        await invalidate_restaurant_cache(restaurant_id)
        
        # Write-through caching for updated restaurant
        updated_restaurant = await get_restaurant_by_id(db, restaurant_id)
        await write_through_cache(
            key=f"restaurant:{restaurant_id}",
            value=updated_restaurant,
            namespace=CacheNamespace.RESTAURANTS.value,
            expire=ENTERPRISE_TTL["restaurants"]
        )
        
        return updated_restaurant
    except IntegrityError:
        await db.rollback()
        raise ValueError("Restaurant with this name already exists")

async def delete_restaurant(db: AsyncSession, restaurant_id: int) -> bool:
    """Delete a restaurant with cache invalidation"""
    existing_restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not existing_restaurant:
        return False
    
    query = delete(Restaurant).where(Restaurant.id == restaurant_id)
    await db.execute(query)
    await db.commit()
    
    # Invalidate restaurant cache
    await invalidate_restaurant_cache(restaurant_id)
    
    return True

# MenuItem CRUD Operations with Enterprise Caching
async def create_menu_item(db: AsyncSession, menu_item: MenuItemCreate) -> MenuItem:
    """Create a new menu item with write-through caching"""
    # Verify restaurant exists
    restaurant = await get_restaurant_by_id(db, menu_item.restaurant_id)
    if not restaurant:
        raise ValueError("Restaurant not found")
    
    try:
        db_menu_item = MenuItem(**menu_item.dict())
        db.add(db_menu_item)
        await db.commit()
        await db.refresh(db_menu_item)
        
        # Write-through caching for menu item
        await write_through_cache(
            key=f"menu_item:{db_menu_item.id}",
            value=db_menu_item,
            namespace=CacheNamespace.MENU_ITEMS.value,
            expire=ENTERPRISE_TTL["menu_items"]
        )
        
        # Invalidate restaurant menu cache
        await invalidate_restaurant_cache(menu_item.restaurant_id)
        
        return db_menu_item
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error creating menu item")

async def get_menu_items(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[MenuItem]:
    """Get all menu items with pagination - Cache-aside pattern"""
    async def fetch_menu_items():
        query = select(MenuItem).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"menu_items:list:{skip}:{limit}",
        namespace=CacheNamespace.MENU_ITEMS.value,
        fetch_func=fetch_menu_items,
        expire=ENTERPRISE_TTL["menu_items"]
    )

async def get_menu_item_by_id(db: AsyncSession, item_id: int) -> Optional[MenuItem]:
    """Get menu item by ID - Cache-aside pattern"""
    async def fetch_menu_item():
        query = select(MenuItem).where(MenuItem.id == item_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"menu_item:{item_id}",
        namespace=CacheNamespace.MENU_ITEMS.value,
        fetch_func=fetch_menu_item,
        expire=ENTERPRISE_TTL["menu_items"]
    )

async def get_restaurant_menu(db: AsyncSession, restaurant_id: int) -> List[MenuItem]:
    """Get all menu items for a specific restaurant - Cache-aside pattern"""
    async def fetch_restaurant_menu():
        restaurant = await get_restaurant_by_id(db, restaurant_id)
        if not restaurant:
            return []
        
        query = select(MenuItem).where(MenuItem.restaurant_id == restaurant_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"restaurant_menu:{restaurant_id}",
        namespace=CacheNamespace.MENU_ITEMS.value,
        fetch_func=fetch_restaurant_menu,
        expire=ENTERPRISE_TTL["menu_items"]
    )

async def update_menu_item(db: AsyncSession, item_id: int, menu_item_update: MenuItemUpdate) -> Optional[MenuItem]:
    """Update menu item with intelligent invalidation"""
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
        
        # Invalidate menu item and restaurant caches
        await invalidate_restaurant_cache(existing_item.restaurant_id)
        
        # Write-through caching for updated menu item
        updated_item = await get_menu_item_by_id(db, item_id)
        await write_through_cache(
            key=f"menu_item:{item_id}",
            value=updated_item,
            namespace=CacheNamespace.MENU_ITEMS.value,
            expire=ENTERPRISE_TTL["menu_items"]
        )
        
        return updated_item
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error updating menu item")

async def delete_menu_item(db: AsyncSession, item_id: int) -> bool:
    """Delete a menu item with cache invalidation"""
    existing_item = await get_menu_item_by_id(db, item_id)
    if not existing_item:
        return False
    
    restaurant_id = existing_item.restaurant_id
    
    query = delete(MenuItem).where(MenuItem.id == item_id)
    await db.execute(query)
    await db.commit()
    
    # Invalidate restaurant cache
    await invalidate_restaurant_cache(restaurant_id)
    
    return True

# Customer CRUD Operations with Enterprise Caching
async def create_customer(db: AsyncSession, customer: CustomerCreate) -> Customer:
    """Create a new customer with write-through caching"""
    try:
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        
        # Write-through caching for customer data
        await write_through_cache(
            key=f"customer:{db_customer.id}",
            value=db_customer,
            namespace=CacheNamespace.CUSTOMERS.value,
            expire=ENTERPRISE_TTL["customer_profiles"]
        )
        
        return db_customer
    except IntegrityError:
        await db.rollback()
        raise ValueError("Customer with this email already exists")

async def get_customers(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Customer]:
    """Get all customers with pagination - Cache-aside pattern"""
    async def fetch_customers():
        query = select(Customer).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"customers:list:{skip}:{limit}",
        namespace=CacheNamespace.CUSTOMERS.value,
        fetch_func=fetch_customers,
        expire=ENTERPRISE_TTL["customer_profiles"]
    )

async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    """Get customer by ID - Cache-aside pattern"""
    async def fetch_customer():
        query = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"customer:{customer_id}",
        namespace=CacheNamespace.CUSTOMERS.value,
        fetch_func=fetch_customer,
        expire=ENTERPRISE_TTL["customer_profiles"]
    )

async def get_customer_with_orders(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    """Get customer with all orders - Cache-aside pattern"""
    async def fetch_customer_with_orders():
        query = select(Customer).options(selectinload(Customer.orders)).where(Customer.id == customer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"customer:with_orders:{customer_id}",
        namespace=CacheNamespace.CUSTOMERS.value,
        fetch_func=fetch_customer_with_orders,
        expire=ENTERPRISE_TTL["customer_profiles"]
    )

async def update_customer(db: AsyncSession, customer_id: int, customer_update: CustomerUpdate) -> Optional[Customer]:
    """Update customer information with intelligent invalidation"""
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
        
        # Invalidate customer cache
        await invalidate_customer_cache(customer_id)
        
        # Write-through caching for updated customer
        updated_customer = await get_customer_by_id(db, customer_id)
        await write_through_cache(
            key=f"customer:{customer_id}",
            value=updated_customer,
            namespace=CacheNamespace.CUSTOMERS.value,
            expire=ENTERPRISE_TTL["customer_profiles"]
        )
        
        return updated_customer
    except IntegrityError:
        await db.rollback()
        raise ValueError("Customer with this email already exists")

async def delete_customer(db: AsyncSession, customer_id: int) -> bool:
    """Delete a customer with cache invalidation"""
    existing_customer = await get_customer_by_id(db, customer_id)
    if not existing_customer:
        return False
    
    query = delete(Customer).where(Customer.id == customer_id)
    await db.execute(query)
    await db.commit()
    
    # Invalidate customer cache
    await invalidate_customer_cache(customer_id)
    
    return True

# Order CRUD Operations with Enterprise Caching
async def create_order(db: AsyncSession, customer_id: int, order_data: OrderCreate) -> Order:
    """Create a new order with enterprise caching and intelligent invalidation"""
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
        
        # Write-through caching for order
        await write_through_cache(
            key=f"order:{db_order.id}",
            value=db_order,
            namespace=CacheNamespace.ORDERS.value,
            expire=ENTERPRISE_TTL["orders"]
        )
        
        # Invalidate related caches
        await invalidate_order_cache(db_order.id, customer_id, order_data.restaurant_id)
        
        return db_order
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error creating order")

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Order]:
    """Get all orders with pagination - Cache-aside pattern"""
    async def fetch_orders():
        query = select(Order).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"orders:list:{skip}:{limit}",
        namespace=CacheNamespace.ORDERS.value,
        fetch_func=fetch_orders,
        expire=ENTERPRISE_TTL["orders"]
    )

async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Get order by ID - Cache-aside pattern"""
    async def fetch_order():
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"order:{order_id}",
        namespace=CacheNamespace.ORDERS.value,
        fetch_func=fetch_order,
        expire=ENTERPRISE_TTL["orders"]
    )

async def get_order_with_details(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Get order with all details - Cache-aside pattern"""
    async def fetch_order_with_details():
        query = select(Order).options(
            selectinload(Order.customer),
            selectinload(Order.restaurant),
            selectinload(Order.order_items).selectinload(OrderItem.menu_item)
        ).where(Order.id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"order:with_details:{order_id}",
        namespace=CacheNamespace.ORDERS.value,
        fetch_func=fetch_order_with_details,
        expire=ENTERPRISE_TTL["orders"]
    )

async def get_customer_orders(db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 10) -> List[Order]:
    """Get all orders for a specific customer - Cache-aside pattern"""
    async def fetch_customer_orders():
        if not await ValidationBusinessLogic.validate_customer_exists(db, customer_id):
            return []
        
        query = select(Order).where(Order.customer_id == customer_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"customer_orders:{customer_id}:{skip}:{limit}",
        namespace=CacheNamespace.ORDERS.value,
        fetch_func=fetch_customer_orders,
        expire=ENTERPRISE_TTL["orders"]
    )

async def get_restaurant_orders(db: AsyncSession, restaurant_id: int, skip: int = 0, limit: int = 10) -> List[Order]:
    """Get all orders for a specific restaurant - Cache-aside pattern"""
    async def fetch_restaurant_orders():
        if not await ValidationBusinessLogic.validate_restaurant_exists(db, restaurant_id):
            return []
        
        query = select(Order).where(Order.restaurant_id == restaurant_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"restaurant_orders:{restaurant_id}:{skip}:{limit}",
        namespace=CacheNamespace.ORDERS.value,
        fetch_func=fetch_restaurant_orders,
        expire=ENTERPRISE_TTL["orders"]
    )

async def update_order_status(db: AsyncSession, order_id: int, new_status: OrderStatus) -> Optional[Order]:
    """Update order status with intelligent invalidation"""
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
        
        # Invalidate order cache
        await invalidate_order_cache(order_id, existing_order.customer_id, existing_order.restaurant_id)
        
        # Write-through caching for updated order
        updated_order = await get_order_by_id(db, order_id)
        await write_through_cache(
            key=f"order:{order_id}",
            value=updated_order,
            namespace=CacheNamespace.ORDERS.value,
            expire=ENTERPRISE_TTL["orders"]
        )
        
        return updated_order
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error updating order status")

async def update_order(db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order information with intelligent invalidation"""
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
        
        # Invalidate order cache
        await invalidate_order_cache(order_id, existing_order.customer_id, existing_order.restaurant_id)
        
        # Write-through caching for updated order
        updated_order = await get_order_by_id(db, order_id)
        await write_through_cache(
            key=f"order:{order_id}",
            value=updated_order,
            namespace=CacheNamespace.ORDERS.value,
            expire=ENTERPRISE_TTL["orders"]
        )
        
        return updated_order
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error updating order")

async def delete_order(db: AsyncSession, order_id: int) -> bool:
    """Delete an order with cache invalidation"""
    existing_order = await get_order_by_id(db, order_id)
    if not existing_order:
        return False
    
    query = delete(Order).where(Order.id == order_id)
    await db.execute(query)
    await db.commit()
    
    # Invalidate order cache
    await invalidate_order_cache(order_id, existing_order.customer_id, existing_order.restaurant_id)
    
    return True

# Review CRUD Operations with Enterprise Caching
async def create_review(db: AsyncSession, order_id: int, review_data: ReviewCreate) -> Review:
    """Create a new review with intelligent invalidation"""
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
        
        # Write-through caching for review
        await write_through_cache(
            key=f"review:{db_review.id}",
            value=db_review,
            namespace=CacheNamespace.REVIEWS.value,
            expire=ENTERPRISE_TTL["reviews"]
        )
        
        # Invalidate review and restaurant caches
        await invalidate_review_cache(db_review.id, order.restaurant_id)
        
        return db_review
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error creating review")

async def get_reviews(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Review]:
    """Get all reviews with pagination - Cache-aside pattern"""
    async def fetch_reviews():
        query = select(Review).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"reviews:list:{skip}:{limit}",
        namespace=CacheNamespace.REVIEWS.value,
        fetch_func=fetch_reviews,
        expire=ENTERPRISE_TTL["reviews"]
    )

async def get_review_by_id(db: AsyncSession, review_id: int) -> Optional[Review]:
    """Get review by ID - Cache-aside pattern"""
    async def fetch_review():
        query = select(Review).where(Review.id == review_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    return await cache_aside_get(
        key=f"review:{review_id}",
        namespace=CacheNamespace.REVIEWS.value,
        fetch_func=fetch_review,
        expire=ENTERPRISE_TTL["reviews"]
    )

async def get_restaurant_reviews(db: AsyncSession, restaurant_id: int, skip: int = 0, limit: int = 10) -> List[Review]:
    """Get all reviews for a specific restaurant - Cache-aside pattern"""
    async def fetch_restaurant_reviews():
        if not await ValidationBusinessLogic.validate_restaurant_exists(db, restaurant_id):
            return []
        
        query = select(Review).where(Review.restaurant_id == restaurant_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"restaurant_reviews:{restaurant_id}:{skip}:{limit}",
        namespace=CacheNamespace.REVIEWS.value,
        fetch_func=fetch_restaurant_reviews,
        expire=ENTERPRISE_TTL["reviews"]
    )

async def get_customer_reviews(db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 10) -> List[Review]:
    """Get all reviews by a specific customer - Cache-aside pattern"""
    async def fetch_customer_reviews():
        if not await ValidationBusinessLogic.validate_customer_exists(db, customer_id):
            return []
        
        query = select(Review).where(Review.customer_id == customer_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    return await cache_aside_get(
        key=f"customer_reviews:{customer_id}:{skip}:{limit}",
        namespace=CacheNamespace.REVIEWS.value,
        fetch_func=fetch_customer_reviews,
        expire=ENTERPRISE_TTL["reviews"]
    )

async def delete_review(db: AsyncSession, review_id: int) -> bool:
    """Delete a review with cache invalidation"""
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
        
        # Invalidate review cache
        await invalidate_review_cache(review_id, existing_review.restaurant_id)
        
        return True
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error deleting review")

# Search and Analytics Operations with Enterprise Caching
async def search_restaurants_with_criteria(
    db: AsyncSession,
    cuisine_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 10
) -> List[Restaurant]:
    """Search restaurants with multiple criteria - Cache-aside pattern"""
    async def fetch_search_results():
        return await SearchBusinessLogic.search_restaurants(
            db, cuisine_type, min_rating, max_rating, is_active, skip, limit
        )
    
    # Create cache key based on search criteria
    cache_key = f"search_restaurants:{cuisine_type}:{min_rating}:{max_rating}:{is_active}:{skip}:{limit}"
    
    return await cache_aside_get(
        key=cache_key,
        namespace=CacheNamespace.STATIC_DATA.value,
        fetch_func=fetch_search_results,
        expire=ENTERPRISE_TTL["static"]
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
    """Filter orders with multiple criteria - Cache-aside pattern"""
    async def fetch_filtered_orders():
        return await SearchBusinessLogic.filter_orders(
            db, status, start_date, end_date, min_amount, max_amount, skip, limit
        )
    
    # Create cache key based on filter criteria
    cache_key = f"filter_orders:{status}:{start_date}:{end_date}:{min_amount}:{max_amount}:{skip}:{limit}"
    
    return await cache_aside_get(
        key=cache_key,
        namespace=CacheNamespace.DYNAMIC_DATA.value,
        fetch_func=fetch_filtered_orders,
        expire=ENTERPRISE_TTL["dynamic"]
    )

async def get_restaurant_analytics(db: AsyncSession, restaurant_id: int) -> Dict:
    """Get restaurant analytics - Cache-aside pattern"""
    async def fetch_restaurant_analytics():
        if not await ValidationBusinessLogic.validate_restaurant_exists(db, restaurant_id):
            raise ValueError("Restaurant not found")
        
        analytics = await RestaurantBusinessLogic.get_restaurant_analytics(db, restaurant_id)
        return analytics.dict()
    
    return await cache_aside_get(
        key=f"restaurant_analytics:{restaurant_id}",
        namespace=CacheNamespace.ANALYTICS_DATA.value,
        fetch_func=fetch_restaurant_analytics,
        expire=ENTERPRISE_TTL["analytics"]
    )

async def get_customer_analytics(db: AsyncSession, customer_id: int) -> Dict:
    """Get customer analytics - Cache-aside pattern"""
    async def fetch_customer_analytics():
        if not await ValidationBusinessLogic.validate_customer_exists(db, customer_id):
            raise ValueError("Customer not found")
        
        analytics = await CustomerBusinessLogic.get_customer_analytics(db, customer_id)
        return analytics.dict()
    
    return await cache_aside_get(
        key=f"customer_analytics:{customer_id}",
        namespace=CacheNamespace.ANALYTICS_DATA.value,
        fetch_func=fetch_customer_analytics,
        expire=ENTERPRISE_TTL["analytics"]
    ) 