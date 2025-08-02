from celery_app import celery_app
from sqlalchemy.orm import Session
from database import SessionLocal, get_db_stats
from models import Order, OrderItem, Restaurant, User, Review, DeliveryDriver, Delivery
from schemas import OrderCreate, OrderStatus, PaymentStatus
from datetime import datetime, timedelta
import structlog
import time
from typing import List, Dict, Any
import json

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a new order with comprehensive workflow."""
    try:
        logger.info("Starting order processing", order_id=order_data.get("id"))
        
        # Simulate order processing steps
        steps = [
            "validating_order",
            "checking_inventory",
            "calculating_total",
            "processing_payment",
            "assigning_driver",
            "sending_notifications"
        ]
        
        for step in steps:
            logger.info(f"Processing step: {step}")
            time.sleep(1)  # Simulate processing time
            
            # Update order status based on step
            if step == "validating_order":
                update_order_status.delay(order_data["id"], OrderStatus.CONFIRMED)
            elif step == "checking_inventory":
                update_order_status.delay(order_data["id"], OrderStatus.PREPARING)
            elif step == "processing_payment":
                process_payment.delay(order_data["id"])
            elif step == "assigning_driver":
                assign_delivery_driver.delay(order_data["id"])
            elif step == "sending_notifications":
                send_order_notifications.delay(order_data["id"])
        
        logger.info("Order processing completed", order_id=order_data.get("id"))
        return {"status": "success", "order_id": order_data.get("id")}
        
    except Exception as e:
        logger.error("Order processing failed", error=str(e), order_id=order_data.get("id"))
        raise self.retry(countdown=60, max_retries=3)


@celery_app.task
def update_order_status(order_id: int, status: OrderStatus) -> Dict[str, Any]:
    """Update order status in database."""
    try:
        db = SessionLocal()
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            db.commit()
            logger.info("Order status updated", order_id=order_id, status=status)
            return {"status": "success", "order_id": order_id, "new_status": status}
        else:
            logger.error("Order not found", order_id=order_id)
            return {"status": "error", "message": "Order not found"}
    except Exception as e:
        logger.error("Failed to update order status", error=str(e), order_id=order_id)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def process_payment(self, order_id: int) -> Dict[str, Any]:
    """Process payment for an order."""
    try:
        logger.info("Processing payment", order_id=order_id)
        
        # Simulate payment processing
        time.sleep(2)
        
        # Update payment status
        db = SessionLocal()
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.payment_status = PaymentStatus.PAID
            order.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Payment processed successfully", order_id=order_id)
            return {"status": "success", "order_id": order_id, "payment_status": "paid"}
        else:
            logger.error("Order not found for payment", order_id=order_id)
            return {"status": "error", "message": "Order not found"}
            
    except Exception as e:
        logger.error("Payment processing failed", error=str(e), order_id=order_id)
        raise self.retry(countdown=30, max_retries=3)
    finally:
        db.close()


@celery_app.task
def assign_delivery_driver(order_id: int) -> Dict[str, Any]:
    """Assign a delivery driver to an order."""
    try:
        logger.info("Assigning delivery driver", order_id=order_id)
        
        db = SessionLocal()
        
        # Find available driver
        driver = db.query(DeliveryDriver).filter(
            DeliveryDriver.is_available == True
        ).first()
        
        if driver:
            # Create delivery record
            delivery = Delivery(
                order_id=order_id,
                driver_id=driver.id,
                status="assigned"
            )
            db.add(delivery)
            db.commit()
            
            logger.info("Driver assigned", order_id=order_id, driver_id=driver.id)
            return {
                "status": "success",
                "order_id": order_id,
                "driver_id": driver.id,
                "driver_name": driver.name
            }
        else:
            logger.warning("No available drivers", order_id=order_id)
            return {"status": "error", "message": "No available drivers"}
            
    except Exception as e:
        logger.error("Driver assignment failed", error=str(e), order_id=order_id)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def send_order_notifications(order_id: int) -> Dict[str, Any]:
    """Send notifications for order updates."""
    try:
        logger.info("Sending order notifications", order_id=order_id)
        
        db = SessionLocal()
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if order:
            # Send notification to customer
            send_customer_notification.delay(
                user_id=order.user_id,
                message=f"Your order #{order_id} has been confirmed and is being prepared."
            )
            
            # Send notification to restaurant
            send_restaurant_notification.delay(
                restaurant_id=order.restaurant_id,
                message=f"New order #{order_id} received."
            )
            
            logger.info("Notifications sent", order_id=order_id)
            return {"status": "success", "order_id": order_id}
        else:
            logger.error("Order not found for notifications", order_id=order_id)
            return {"status": "error", "message": "Order not found"}
            
    except Exception as e:
        logger.error("Notification sending failed", error=str(e), order_id=order_id)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def send_customer_notification(user_id: int, message: str) -> Dict[str, Any]:
    """Send notification to customer."""
    try:
        logger.info("Sending customer notification", user_id=user_id, message=message)
        
        # Simulate sending notification (email, SMS, push notification)
        time.sleep(1)
        
        logger.info("Customer notification sent", user_id=user_id)
        return {"status": "success", "user_id": user_id, "message": message}
        
    except Exception as e:
        logger.error("Customer notification failed", error=str(e), user_id=user_id)
        return {"status": "error", "message": str(e)}


@celery_app.task
def send_restaurant_notification(restaurant_id: int, message: str) -> Dict[str, Any]:
    """Send notification to restaurant."""
    try:
        logger.info("Sending restaurant notification", restaurant_id=restaurant_id, message=message)
        
        # Simulate sending notification
        time.sleep(1)
        
        logger.info("Restaurant notification sent", restaurant_id=restaurant_id)
        return {"status": "success", "restaurant_id": restaurant_id, "message": message}
        
    except Exception as e:
        logger.error("Restaurant notification failed", error=str(e), restaurant_id=restaurant_id)
        return {"status": "error", "message": str(e)}


@celery_app.task
def update_restaurant_rating(restaurant_id: int) -> Dict[str, Any]:
    """Update restaurant rating based on recent reviews."""
    try:
        logger.info("Updating restaurant rating", restaurant_id=restaurant_id)
        
        db = SessionLocal()
        
        # Calculate average rating from recent reviews
        recent_reviews = db.query(Review).filter(
            Review.restaurant_id == restaurant_id,
            Review.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if recent_reviews:
            avg_rating = sum(review.rating for review in recent_reviews) / len(recent_reviews)
            
            # Update restaurant rating
            restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
            if restaurant:
                restaurant.rating = round(avg_rating, 2)
                db.commit()
                
                logger.info("Restaurant rating updated", restaurant_id=restaurant_id, new_rating=avg_rating)
                return {"status": "success", "restaurant_id": restaurant_id, "new_rating": avg_rating}
        
        logger.info("No recent reviews to update rating", restaurant_id=restaurant_id)
        return {"status": "success", "message": "No recent reviews"}
        
    except Exception as e:
        logger.error("Rating update failed", error=str(e), restaurant_id=restaurant_id)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def cleanup_expired_orders() -> Dict[str, Any]:
    """Clean up expired orders (older than 24 hours with pending status)."""
    try:
        logger.info("Starting cleanup of expired orders")
        
        db = SessionLocal()
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Find expired pending orders
        expired_orders = db.query(Order).filter(
            Order.status == OrderStatus.PENDING,
            Order.created_at < cutoff_time
        ).all()
        
        cleaned_count = 0
        for order in expired_orders:
            order.status = OrderStatus.CANCELLED
            order.payment_status = PaymentStatus.FAILED
            cleaned_count += 1
        
        db.commit()
        
        logger.info("Cleanup completed", cleaned_count=cleaned_count)
        return {"status": "success", "cleaned_count": cleaned_count}
        
    except Exception as e:
        logger.error("Cleanup failed", error=str(e))
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def send_delivery_reminders() -> Dict[str, Any]:
    """Send delivery reminders for orders that are ready."""
    try:
        logger.info("Sending delivery reminders")
        
        db = SessionLocal()
        
        # Find orders that are ready for delivery
        ready_orders = db.query(Order).filter(
            Order.status == OrderStatus.READY
        ).all()
        
        reminder_count = 0
        for order in ready_orders:
            # Send reminder to assigned driver
            delivery = db.query(Delivery).filter(Delivery.order_id == order.id).first()
            if delivery:
                send_driver_reminder.delay(delivery.driver_id, order.id)
                reminder_count += 1
        
        logger.info("Delivery reminders sent", reminder_count=reminder_count)
        return {"status": "success", "reminder_count": reminder_count}
        
    except Exception as e:
        logger.error("Delivery reminders failed", error=str(e))
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def send_driver_reminder(driver_id: int, order_id: int) -> Dict[str, Any]:
    """Send reminder to delivery driver."""
    try:
        logger.info("Sending driver reminder", driver_id=driver_id, order_id=order_id)
        
        # Simulate sending reminder
        time.sleep(1)
        
        logger.info("Driver reminder sent", driver_id=driver_id, order_id=order_id)
        return {"status": "success", "driver_id": driver_id, "order_id": order_id}
        
    except Exception as e:
        logger.error("Driver reminder failed", error=str(e), driver_id=driver_id, order_id=order_id)
        return {"status": "error", "message": str(e)}


@celery_app.task
def process_pending_payments() -> Dict[str, Any]:
    """Process pending payments in batches."""
    try:
        logger.info("Processing pending payments")
        
        db = SessionLocal()
        
        # Find orders with pending payments
        pending_orders = db.query(Order).filter(
            Order.payment_status == PaymentStatus.PENDING,
            Order.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).all()
        
        processed_count = 0
        for order in pending_orders:
            # Simulate payment processing
            time.sleep(0.5)
            
            # Update payment status (simulate successful payment)
            order.payment_status = PaymentStatus.PAID
            processed_count += 1
        
        db.commit()
        
        logger.info("Pending payments processed", processed_count=processed_count)
        return {"status": "success", "processed_count": processed_count}
        
    except Exception as e:
        logger.error("Payment processing failed", error=str(e))
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def generate_analytics_report() -> Dict[str, Any]:
    """Generate analytics report for the system."""
    try:
        logger.info("Generating analytics report")
        
        db = SessionLocal()
        
        # Calculate various metrics
        total_orders = db.query(Order).count()
        total_revenue = db.query(Order).filter(Order.payment_status == PaymentStatus.PAID).with_entities(
            db.func.sum(Order.total_amount)
        ).scalar() or 0
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Get top restaurants
        top_restaurants = db.query(Restaurant).order_by(Restaurant.rating.desc()).limit(5).all()
        
        report = {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "avg_order_value": float(avg_order_value),
            "top_restaurants": [
                {"id": r.id, "name": r.name, "rating": r.rating}
                for r in top_restaurants
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info("Analytics report generated", report=report)
        return {"status": "success", "report": report}
        
    except Exception as e:
        logger.error("Analytics report generation failed", error=str(e))
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def monitor_system_health() -> Dict[str, Any]:
    """Monitor overall system health."""
    try:
        logger.info("Monitoring system health")
        
        # Get database stats
        db_stats = get_db_stats()
        
        # Check Redis connection
        from redis import Redis
        from config import get_redis_url
        redis_client = Redis.from_url(get_redis_url())
        redis_healthy = redis_client.ping()
        
        # Get Celery stats
        celery_stats = celery_app.control.inspect().stats()
        
        health_report = {
            "database": {
                "healthy": True,
                "stats": db_stats
            },
            "redis": {
                "healthy": redis_healthy
            },
            "celery": {
                "healthy": bool(celery_stats),
                "stats": celery_stats
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("System health monitored", health_report=health_report)
        return {"status": "success", "health": health_report}
        
    except Exception as e:
        logger.error("System health monitoring failed", error=str(e))
        return {"status": "error", "message": str(e)} 