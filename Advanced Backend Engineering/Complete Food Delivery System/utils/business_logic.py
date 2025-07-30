"""
Business logic module for the food delivery system
Contains complex business rules, calculations, and validations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from models import Order, OrderItem, MenuItem, Restaurant, Customer, Review, OrderStatus
from schemas import OrderCreate, RestaurantAnalytics, CustomerAnalytics
import logging

logger = logging.getLogger(__name__)

class OrderBusinessLogic:
    """Business logic for order operations"""
    
    @staticmethod
    async def calculate_order_total(db: AsyncSession, order_items: List[Dict]) -> Tuple[Decimal, List[Dict]]:
        """
        Calculate order total and validate menu items
        Returns: (total_amount, validated_order_items)
        """
        total_amount = Decimal('0.00')
        validated_items = []
        
        for item in order_items:
            menu_item_id = item['menu_item_id']
            quantity = item['quantity']
            
            # Get menu item and validate
            menu_item_query = select(MenuItem).where(MenuItem.id == menu_item_id)
            result = await db.execute(menu_item_query)
            menu_item = result.scalar_one_or_none()
            
            if not menu_item:
                raise ValueError(f"Menu item with ID {menu_item_id} not found")
            
            if not menu_item.is_available:
                raise ValueError(f"Menu item '{menu_item.name}' is not available")
            
            # Calculate item total
            item_total = menu_item.price * quantity
            total_amount += item_total
            
            # Create validated order item
            validated_item = {
                'menu_item_id': menu_item_id,
                'quantity': quantity,
                'item_price': menu_item.price,
                'special_requests': item.get('special_requests')
            }
            validated_items.append(validated_item)
        
        return total_amount, validated_items
    
    @staticmethod
    async def validate_order_status_transition(current_status: OrderStatus, new_status: OrderStatus) -> bool:
        """
        Validate order status transitions
        Order status workflow: placed → confirmed → preparing → out_for_delivery → delivered
        Cancelled can happen from any status except delivered
        """
        valid_transitions = {
            OrderStatus.PLACED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED],
            OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [],  # Final status
            OrderStatus.CANCELLED: []   # Final status
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    @staticmethod
    async def can_add_review(order: Order) -> bool:
        """Check if a review can be added for an order"""
        return order.order_status == OrderStatus.DELIVERED

class RestaurantBusinessLogic:
    """Business logic for restaurant operations"""
    
    @staticmethod
    async def calculate_restaurant_rating(db: AsyncSession, restaurant_id: int) -> float:
        """Calculate average rating for a restaurant"""
        query = select(func.avg(Review.rating)).where(Review.restaurant_id == restaurant_id)
        result = await db.execute(query)
        avg_rating = result.scalar()
        return float(avg_rating) if avg_rating else 0.0
    
    @staticmethod
    async def get_popular_menu_items(db: AsyncSession, restaurant_id: int, limit: int = 10) -> List[Dict]:
        """Get popular menu items for a restaurant"""
        query = select(
            MenuItem.id,
            MenuItem.name,
            func.sum(OrderItem.quantity).label('total_ordered'),
            func.sum(OrderItem.quantity * OrderItem.item_price).label('total_revenue')
        ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
         .join(Order, OrderItem.order_id == Order.id)\
         .where(
            and_(
                MenuItem.restaurant_id == restaurant_id,
                Order.order_status.in_([OrderStatus.DELIVERED, OrderStatus.OUT_FOR_DELIVERY])
            )
        ).group_by(MenuItem.id, MenuItem.name)\
         .order_by(desc('total_ordered'))\
         .limit(limit)
        
        result = await db.execute(query)
        popular_items = []
        
        for row in result.fetchall():
            popular_items.append({
                'menu_item_id': row.id,
                'name': row.name,
                'total_ordered': int(row.total_ordered),
                'total_revenue': float(row.total_revenue)
            })
        
        return popular_items
    
    @staticmethod
    async def get_restaurant_analytics(db: AsyncSession, restaurant_id: int) -> RestaurantAnalytics:
        """Get comprehensive analytics for a restaurant"""
        # Total orders and revenue
        orders_query = select(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_revenue'),
            func.avg(Order.total_amount).label('average_order_value')
        ).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.order_status.in_([OrderStatus.DELIVERED, OrderStatus.OUT_FOR_DELIVERY])
            )
        )
        
        orders_result = await db.execute(orders_query)
        orders_data = orders_result.fetchone()
        
        # Reviews data
        reviews_query = select(
            func.count(Review.id).label('total_reviews'),
            func.avg(Review.rating).label('average_rating')
        ).where(Review.restaurant_id == restaurant_id)
        
        reviews_result = await db.execute(reviews_query)
        reviews_data = reviews_result.fetchone()
        
        # Popular items
        popular_items = await RestaurantBusinessLogic.get_popular_menu_items(db, restaurant_id)
        
        return RestaurantAnalytics(
            total_orders=int(orders_data.total_orders) if orders_data.total_orders else 0,
            total_revenue=Decimal(str(orders_data.total_revenue)) if orders_data.total_revenue else Decimal('0.00'),
            average_order_value=Decimal(str(orders_data.average_order_value)) if orders_data.average_order_value else Decimal('0.00'),
            total_reviews=int(reviews_data.total_reviews) if reviews_data.total_reviews else 0,
            average_rating=float(reviews_data.average_rating) if reviews_data.average_rating else 0.0,
            popular_items=popular_items
        )

class CustomerBusinessLogic:
    """Business logic for customer operations"""
    
    @staticmethod
    async def get_customer_analytics(db: AsyncSession, customer_id: int) -> CustomerAnalytics:
        """Get comprehensive analytics for a customer"""
        # Total orders and spending
        orders_query = select(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent'),
            func.avg(Order.total_amount).label('average_order_value')
        ).where(
            and_(
                Order.customer_id == customer_id,
                Order.order_status.in_([OrderStatus.DELIVERED, OrderStatus.OUT_FOR_DELIVERY])
            )
        )
        
        orders_result = await db.execute(orders_query)
        orders_data = orders_result.fetchone()
        
        # Favorite restaurants
        favorite_restaurants_query = select(
            Restaurant.id,
            Restaurant.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_spent')
        ).join(Order, Restaurant.id == Order.restaurant_id)\
         .where(
            and_(
                Order.customer_id == customer_id,
                Order.order_status.in_([OrderStatus.DELIVERED, OrderStatus.OUT_FOR_DELIVERY])
            )
        ).group_by(Restaurant.id, Restaurant.name)\
         .order_by(desc('order_count'))\
         .limit(5)
        
        favorite_result = await db.execute(favorite_restaurants_query)
        favorite_restaurants = []
        
        for row in favorite_result.fetchall():
            favorite_restaurants.append({
                'restaurant_id': row.id,
                'restaurant_name': row.name,
                'order_count': int(row.order_count),
                'total_spent': float(row.total_spent)
            })
        
        # Order history (last 10 orders)
        order_history_query = select(
            Order.id,
            Order.order_date,
            Order.total_amount,
            Order.order_status,
            Restaurant.name.label('restaurant_name')
        ).join(Restaurant, Order.restaurant_id == Restaurant.id)\
         .where(Order.customer_id == customer_id)\
         .order_by(desc(Order.order_date))\
         .limit(10)
        
        history_result = await db.execute(order_history_query)
        order_history = []
        
        for row in history_result.fetchall():
            order_history.append({
                'order_id': row.id,
                'order_date': row.order_date.isoformat(),
                'total_amount': float(row.total_amount),
                'order_status': row.order_status.value,
                'restaurant_name': row.restaurant_name
            })
        
        return CustomerAnalytics(
            total_orders=int(orders_data.total_orders) if orders_data.total_orders else 0,
            total_spent=Decimal(str(orders_data.total_spent)) if orders_data.total_spent else Decimal('0.00'),
            average_order_value=Decimal(str(orders_data.average_order_value)) if orders_data.average_order_value else Decimal('0.00'),
            favorite_restaurants=favorite_restaurants,
            order_history=order_history
        )

class SearchBusinessLogic:
    """Business logic for search and filtering operations"""
    
    @staticmethod
    async def search_restaurants(
        db: AsyncSession,
        cuisine_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Restaurant]:
        """Search restaurants with multiple criteria"""
        query = select(Restaurant)
        conditions = []
        
        if cuisine_type:
            conditions.append(Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
        
        if min_rating is not None:
            conditions.append(Restaurant.rating >= min_rating)
        
        if max_rating is not None:
            conditions.append(Restaurant.rating <= max_rating)
        
        if is_active is not None:
            conditions.append(Restaurant.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def filter_orders(
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
        query = select(Order)
        conditions = []
        
        if status:
            conditions.append(Order.order_status == status)
        
        if start_date:
            conditions.append(Order.order_date >= start_date)
        
        if end_date:
            conditions.append(Order.order_date <= end_date)
        
        if min_amount:
            conditions.append(Order.total_amount >= min_amount)
        
        if max_amount:
            conditions.append(Order.total_amount <= max_amount)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

class ValidationBusinessLogic:
    """Business logic for validation operations"""
    
    @staticmethod
    async def validate_customer_exists(db: AsyncSession, customer_id: int) -> bool:
        """Validate that a customer exists and is active"""
        query = select(Customer).where(
            and_(
                Customer.id == customer_id,
                Customer.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def validate_restaurant_exists(db: AsyncSession, restaurant_id: int) -> bool:
        """Validate that a restaurant exists and is active"""
        query = select(Restaurant).where(
            and_(
                Restaurant.id == restaurant_id,
                Restaurant.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def validate_menu_item_exists(db: AsyncSession, menu_item_id: int, restaurant_id: int) -> bool:
        """Validate that a menu item exists and belongs to the specified restaurant"""
        query = select(MenuItem).where(
            and_(
                MenuItem.id == menu_item_id,
                MenuItem.restaurant_id == restaurant_id,
                MenuItem.is_available == True
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def validate_order_exists(db: AsyncSession, order_id: int) -> bool:
        """Validate that an order exists"""
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def validate_review_not_exists(db: AsyncSession, order_id: int) -> bool:
        """Validate that no review exists for the order"""
        query = select(Review).where(Review.order_id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is None 