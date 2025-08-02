from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from models import (
    Customer, Restaurant, MenuItem, Order, OrderItem, 
    Notification, Campaign, AnalyticsReport, SystemHealth, TaskExecution
)
from schemas import (
    CustomerCreate, CustomerUpdate, RestaurantCreate, RestaurantUpdate,
    MenuItemCreate, MenuItemUpdate, OrderCreate, OrderUpdate,
    NotificationCreate, CampaignCreate, AnalyticsReportCreate
)

logger = logging.getLogger(__name__)

# ==================== CUSTOMER CRUD OPERATIONS ====================

def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    """Create a new customer"""
    try:
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        logger.info(f"Created customer: {db_customer.id}")
        return db_customer
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer: {e}")
        raise

def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    """Get customer by ID"""
    return db.query(Customer).filter(Customer.id == customer_id).first()

def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
    """Get all customers with pagination"""
    return db.query(Customer).offset(skip).limit(limit).all()

def update_customer(db: Session, customer_id: int, customer_update: CustomerUpdate) -> Optional[Customer]:
    """Update customer information"""
    try:
        db_customer = get_customer(db, customer_id)
        if not db_customer:
            return None
        
        update_data = customer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        
        db_customer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_customer)
        logger.info(f"Updated customer: {customer_id}")
        return db_customer
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating customer {customer_id}: {e}")
        raise

def delete_customer(db: Session, customer_id: int) -> bool:
    """Delete customer"""
    try:
        db_customer = get_customer(db, customer_id)
        if not db_customer:
            return False
        
        db.delete(db_customer)
        db.commit()
        logger.info(f"Deleted customer: {customer_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting customer {customer_id}: {e}")
        raise

# ==================== RESTAURANT CRUD OPERATIONS ====================

def create_restaurant(db: Session, restaurant: RestaurantCreate) -> Restaurant:
    """Create a new restaurant"""
    try:
        db_restaurant = Restaurant(**restaurant.dict())
        db.add(db_restaurant)
        db.commit()
        db.refresh(db_restaurant)
        logger.info(f"Created restaurant: {db_restaurant.id}")
        return db_restaurant
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating restaurant: {e}")
        raise

def get_restaurant(db: Session, restaurant_id: int) -> Optional[Restaurant]:
    """Get restaurant by ID"""
    return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

def get_all_restaurants(db: Session, skip: int = 0, limit: int = 100) -> List[Restaurant]:
    """Get all restaurants with pagination"""
    return db.query(Restaurant).filter(Restaurant.is_active == True).offset(skip).limit(limit).all()

def update_restaurant(db: Session, restaurant_id: int, restaurant_update: RestaurantUpdate) -> Optional[Restaurant]:
    """Update restaurant information"""
    try:
        db_restaurant = get_restaurant(db, restaurant_id)
        if not db_restaurant:
            return None
        
        update_data = restaurant_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_restaurant, field, value)
        
        db_restaurant.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_restaurant)
        logger.info(f"Updated restaurant: {restaurant_id}")
        return db_restaurant
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating restaurant {restaurant_id}: {e}")
        raise

def delete_restaurant(db: Session, restaurant_id: int) -> bool:
    """Delete restaurant (soft delete by setting is_active to False)"""
    try:
        db_restaurant = get_restaurant(db, restaurant_id)
        if not db_restaurant:
            return False
        
        db_restaurant.is_active = False
        db_restaurant.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Deactivated restaurant: {restaurant_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deactivating restaurant {restaurant_id}: {e}")
        raise

# ==================== MENU ITEM CRUD OPERATIONS ====================

def create_menu_item(db: Session, menu_item: MenuItemCreate) -> MenuItem:
    """Create a new menu item"""
    try:
        db_menu_item = MenuItem(**menu_item.dict())
        db.add(db_menu_item)
        db.commit()
        db.refresh(db_menu_item)
        logger.info(f"Created menu item: {db_menu_item.id}")
        return db_menu_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating menu item: {e}")
        raise

def get_menu_item(db: Session, menu_item_id: int) -> Optional[MenuItem]:
    """Get menu item by ID"""
    return db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()

def get_menu_items(db: Session, restaurant_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[MenuItem]:
    """Get menu items, optionally filtered by restaurant"""
    query = db.query(MenuItem)
    if restaurant_id:
        query = query.filter(MenuItem.restaurant_id == restaurant_id)
    return query.filter(MenuItem.is_available == True).offset(skip).limit(limit).all()

def update_menu_item(db: Session, menu_item_id: int, menu_item_update: MenuItemUpdate) -> Optional[MenuItem]:
    """Update menu item"""
    try:
        db_menu_item = get_menu_item(db, menu_item_id)
        if not db_menu_item:
            return None
        
        update_data = menu_item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_menu_item, field, value)
        
        db_menu_item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_menu_item)
        logger.info(f"Updated menu item: {menu_item_id}")
        return db_menu_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating menu item {menu_item_id}: {e}")
        raise

def delete_menu_item(db: Session, menu_item_id: int) -> bool:
    """Delete menu item (soft delete by setting is_available to False)"""
    try:
        db_menu_item = get_menu_item(db, menu_item_id)
        if not db_menu_item:
            return False
        
        db_menu_item.is_available = False
        db_menu_item.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Deactivated menu item: {menu_item_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deactivating menu item {menu_item_id}: {e}")
        raise

# ==================== ORDER CRUD OPERATIONS ====================

def create_order(db: Session, order: OrderCreate) -> Order:
    """Create a new order with order items"""
    try:
        # Calculate total amount
        total_amount = 0
        order_items_data = []
        
        for item in order.order_items:
            menu_item = get_menu_item(db, item.menu_item_id)
            if not menu_item:
                raise ValueError(f"Menu item {item.menu_item_id} not found")
            
            item_total = item.quantity * item.unit_price
            total_amount += item_total
            
            order_items_data.append({
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item_total,
                "special_instructions": item.special_instructions
            })
        
        # Create order
        order_data = order.dict(exclude={'order_items'})
        order_data['total_amount'] = total_amount
        db_order = Order(**order_data)
        db.add(db_order)
        db.flush()  # Get the order ID
        
        # Create order items
        for item_data in order_items_data:
            item_data['order_id'] = db_order.id
            db_order_item = OrderItem(**item_data)
            db.add(db_order_item)
        
        db.commit()
        db.refresh(db_order)
        logger.info(f"Created order: {db_order.id} with total: {total_amount}")
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating order: {e}")
        raise

def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID with related data"""
    return db.query(Order).filter(Order.id == order_id).first()

def get_orders_by_customer(db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders by customer"""
    return db.query(Order).filter(Order.customer_id == customer_id).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()

def get_orders_by_restaurant(db: Session, restaurant_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders by restaurant"""
    return db.query(Order).filter(Order.restaurant_id == restaurant_id).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()

def update_order_status(db: Session, order_id: int, status: str) -> Optional[Order]:
    """Update order status"""
    try:
        db_order = get_order(db, order_id)
        if not db_order:
            return None
        
        db_order.status = status
        db_order.updated_at = datetime.utcnow()
        
        # Update workflow status based on order status
        if status == "confirmed":
            db_order.workflow_status = "completed"
            db_order.workflow_progress = 100
        elif status in ["preparing", "ready", "out_for_delivery"]:
            db_order.workflow_status = "in_progress"
            db_order.workflow_progress = 80
        elif status == "delivered":
            db_order.workflow_status = "completed"
            db_order.workflow_progress = 100
        
        db.commit()
        db.refresh(db_order)
        logger.info(f"Updated order {order_id} status to: {status}")
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order status: {e}")
        raise

def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order information"""
    try:
        db_order = get_order(db, order_id)
        if not db_order:
            return None
        
        update_data = order_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        
        db_order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_order)
        logger.info(f"Updated order: {order_id}")
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order {order_id}: {e}")
        raise

# ==================== NOTIFICATION CRUD OPERATIONS ====================

def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    """Create a new notification"""
    try:
        db_notification = Notification(**notification.dict())
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        logger.info(f"Created notification: {db_notification.id}")
        return db_notification
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating notification: {e}")
        raise

def get_notifications_by_user(db: Session, user_id: int, user_type: str, skip: int = 0, limit: int = 100) -> List[Notification]:
    """Get notifications by user"""
    return db.query(Notification).filter(
        and_(Notification.user_id == user_id, Notification.user_type == user_type)
    ).order_by(desc(Notification.sent_at)).offset(skip).limit(limit).all()

def mark_notification_read(db: Session, notification_id: int) -> Optional[Notification]:
    """Mark notification as read"""
    try:
        db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not db_notification:
            return None
        
        db_notification.is_read = True
        db_notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking notification read: {e}")
        raise

# ==================== CAMPAIGN CRUD OPERATIONS ====================

def create_campaign(db: Session, campaign: CampaignCreate) -> Campaign:
    """Create a new notification campaign"""
    try:
        db_campaign = Campaign(**campaign.dict())
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        logger.info(f"Created campaign: {db_campaign.campaign_id}")
        return db_campaign
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating campaign: {e}")
        raise

def get_campaign(db: Session, campaign_id: str) -> Optional[Campaign]:
    """Get campaign by campaign_id"""
    return db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()

def update_campaign_status(db: Session, campaign_id: str, status: str) -> Optional[Campaign]:
    """Update campaign status"""
    try:
        db_campaign = get_campaign(db, campaign_id)
        if not db_campaign:
            return None
        
        db_campaign.status = status
        if status == "running" and not db_campaign.started_at:
            db_campaign.started_at = datetime.utcnow()
        elif status == "completed":
            db_campaign.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_campaign)
        logger.info(f"Updated campaign {campaign_id} status to: {status}")
        return db_campaign
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating campaign status: {e}")
        raise

# ==================== ANALYTICS CRUD OPERATIONS ====================

def create_analytics_report(db: Session, report: AnalyticsReportCreate) -> AnalyticsReport:
    """Create a new analytics report"""
    try:
        db_report = AnalyticsReport(**report.dict())
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        logger.info(f"Created analytics report: {db_report.id}")
        return db_report
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating analytics report: {e}")
        raise

def get_order_analytics(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get order analytics for date range"""
    try:
        # Total orders
        total_orders = db.query(func.count(Order.id)).filter(
            and_(Order.created_at >= start_date, Order.created_at <= end_date)
        ).scalar()
        
        # Orders by status
        orders_by_status = db.query(Order.status, func.count(Order.id)).filter(
            and_(Order.created_at >= start_date, Order.created_at <= end_date)
        ).group_by(Order.status).all()
        
        # Total revenue
        total_revenue = db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.created_at >= start_date, 
                Order.created_at <= end_date,
                Order.status.in_(["confirmed", "preparing", "ready", "out_for_delivery", "delivered"])
            )
        ).scalar() or 0
        
        return {
            "total_orders": total_orders,
            "orders_by_status": dict(orders_by_status),
            "total_revenue": float(total_revenue),
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting order analytics: {e}")
        raise

def get_revenue_analytics(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get revenue analytics for date range"""
    try:
        # Daily revenue
        daily_revenue = db.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.status.in_(["confirmed", "preparing", "ready", "out_for_delivery", "delivered"])
            )
        ).group_by(func.date(Order.created_at)).all()
        
        # Restaurant revenue
        restaurant_revenue = db.query(
            Restaurant.name,
            func.sum(Order.total_amount).label('revenue')
        ).join(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.status.in_(["confirmed", "preparing", "ready", "out_for_delivery", "delivered"])
            )
        ).group_by(Restaurant.id, Restaurant.name).order_by(desc('revenue')).limit(10).all()
        
        return {
            "daily_revenue": [{"date": str(row.date), "revenue": float(row.revenue)} for row in daily_revenue],
            "restaurant_revenue": [{"restaurant": row.name, "revenue": float(row.revenue)} for row in restaurant_revenue],
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise

# ==================== SYSTEM HEALTH CRUD OPERATIONS ====================

def create_system_health(db: Session, health_data: Dict[str, Any]) -> SystemHealth:
    """Create a new system health record"""
    try:
        db_health = SystemHealth(**health_data)
        db.add(db_health)
        db.commit()
        db.refresh(db_health)
        logger.info(f"Created system health record: {db_health.id}")
        return db_health
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating system health record: {e}")
        raise

def get_latest_system_health(db: Session) -> Optional[SystemHealth]:
    """Get the latest system health record"""
    return db.query(SystemHealth).order_by(desc(SystemHealth.check_time)).first()

# ==================== TASK EXECUTION CRUD OPERATIONS ====================

def create_task_execution(db: Session, task_data: Dict[str, Any]) -> TaskExecution:
    """Create a new task execution record"""
    try:
        db_task = TaskExecution(**task_data)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Created task execution record: {db_task.id}")
        return db_task
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating task execution record: {e}")
        raise

def update_task_execution(db: Session, task_id: str, update_data: Dict[str, Any]) -> Optional[TaskExecution]:
    """Update task execution record"""
    try:
        db_task = db.query(TaskExecution).filter(TaskExecution.task_id == task_id).first()
        if not db_task:
            return None
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating task execution: {e}")
        raise

def get_failed_tasks(db: Session, limit: int = 100) -> List[TaskExecution]:
    """Get failed task executions"""
    return db.query(TaskExecution).filter(TaskExecution.status == "failed").order_by(desc(TaskExecution.completed_at)).limit(limit).all() 