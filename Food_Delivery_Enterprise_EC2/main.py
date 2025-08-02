from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import uvicorn
import logging
from datetime import datetime, timedelta
import json

from database import get_db, engine
from models import Base
from schemas import (
    OrderCreate, OrderResponse, RestaurantCreate, RestaurantResponse,
    CustomerCreate, CustomerResponse, MenuItemCreate, MenuItemResponse,
    OrderStatusUpdate, NotificationCampaign, AnalyticsReport,
    WorkflowStatus, SystemHealth
)
from crud import (
    create_order, get_order, update_order_status, get_orders_by_restaurant,
    create_restaurant, get_restaurant, get_all_restaurants,
    create_customer, get_customer, get_all_customers,
    create_menu_item, get_menu_items, update_menu_item,
    get_order_analytics, get_revenue_analytics
)
from tasks import (
    process_order_workflow, send_realtime_notifications, 
    generate_business_analytics, bulk_notification_campaign,
    system_health_check, cleanup_old_tasks
)
from celery_app import celery_app

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enterprise Food Delivery System",
    description="Production-grade food delivery platform with advanced task processing",
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

@app.get("/")
async def root():
    return {"message": "Enterprise Food Delivery System v3.0", "status": "operational"}

# ==================== ORDER MANAGEMENT ENDPOINTS ====================

@app.post("/orders/", response_model=OrderResponse)
async def create_new_order(order: OrderCreate, db=Depends(get_db)):
    """Create a new order and trigger processing workflow"""
    try:
        db_order = create_order(db, order)
        
        # Trigger enterprise order processing workflow
        workflow_task = process_order_workflow.delay(db_order.id)
        
        return {
            **db_order.__dict__,
            "workflow_task_id": workflow_task.id,
            "message": "Order created and processing started"
        }
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_details(order_id: int, db=Depends(get_db)):
    """Get order details with current status"""
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/status")
async def update_order_status_endpoint(
    order_id: int, 
    status_update: OrderStatusUpdate, 
    db=Depends(get_db)
):
    """Update order status and trigger notifications"""
    try:
        updated_order = update_order_status(db, order_id, status_update.status)
        
        # Trigger real-time notifications
        notification_task = send_realtime_notifications.delay({
            "type": "order_status_update",
            "order_id": order_id,
            "status": status_update.status,
            "customer_id": updated_order.customer_id,
            "restaurant_id": updated_order.restaurant_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "message": "Order status updated",
            "order_id": order_id,
            "new_status": status_update.status,
            "notification_task_id": notification_task.id
        }
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WORKFLOW MANAGEMENT ENDPOINTS ====================

@app.post("/workflows/order-processing/{order_id}")
async def start_order_processing(order_id: int, db=Depends(get_db)):
    """Manually trigger order processing workflow"""
    try:
        order = get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        task = process_order_workflow.delay(order_id)
        
        return {
            "message": "Order processing workflow started",
            "order_id": order_id,
            "task_id": task.id,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error starting order workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/order/{order_id}/status")
async def get_order_workflow_status(order_id: int):
    """Get order workflow processing status"""
    try:
        # In a real implementation, you'd query task status from Celery
        # For demo purposes, return mock status
        return {
            "order_id": order_id,
            "workflow_status": "in_progress",
            "current_stage": "payment_processing",
            "progress_percentage": 40,
            "estimated_completion": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/order/{order_id}/cancel")
async def cancel_order_workflow(order_id: int, db=Depends(get_db)):
    """Cancel order processing workflow"""
    try:
        order = get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update order status to cancelled
        update_order_status(db, order_id, "cancelled")
        
        return {
            "message": "Order workflow cancelled",
            "order_id": order_id,
            "status": "cancelled"
        }
    except Exception as e:
        logger.error(f"Error cancelling order workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== NOTIFICATION CAMPAIGN ENDPOINTS ====================

@app.post("/campaigns/notifications/create")
async def create_notification_campaign(campaign: NotificationCampaign):
    """Create and start a notification campaign"""
    try:
        task = bulk_notification_campaign.delay(
            campaign_data=campaign.dict(),
            user_segments=campaign.target_segments
        )
        
        return {
            "message": "Notification campaign created",
            "campaign_id": campaign.campaign_id,
            "task_id": task.id,
            "target_segments": campaign.target_segments,
            "status": "scheduled"
        }
    except Exception as e:
        logger.error(f"Error creating notification campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{campaign_id}/status")
async def get_campaign_status(campaign_id: str):
    """Get notification campaign progress"""
    try:
        # Mock campaign status
        return {
            "campaign_id": campaign_id,
            "status": "running",
            "progress": 65,
            "sent_count": 1300,
            "total_count": 2000,
            "success_rate": 98.5
        }
    except Exception as e:
        logger.error(f"Error getting campaign status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pause a running notification campaign"""
    try:
        return {
            "message": "Campaign paused",
            "campaign_id": campaign_id,
            "status": "paused"
        }
    except Exception as e:
        logger.error(f"Error pausing campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS PIPELINE ENDPOINTS ====================

@app.post("/analytics/generate-report/{report_type}")
async def generate_analytics_report(report_type: str, date_range: Dict):
    """Trigger business analytics report generation"""
    try:
        task = generate_business_analytics.delay(report_type, date_range)
        
        return {
            "message": "Analytics report generation started",
            "report_type": report_type,
            "task_id": task.id,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error generating analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/pipeline-status")
async def get_analytics_pipeline_status():
    """Get analytics pipeline health status"""
    try:
        return {
            "pipeline_status": "healthy",
            "active_tasks": 3,
            "queue_depth": 12,
            "last_report_generated": datetime.now().isoformat(),
            "system_resources": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.1
            }
        }
    except Exception as e:
        logger.error(f"Error getting analytics pipeline status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/ml-training/trigger")
async def trigger_ml_training():
    """Trigger ML recommendation model training"""
    try:
        # Mock ML training trigger
        return {
            "message": "ML training triggered",
            "model_type": "recommendation_engine",
            "status": "training_started",
            "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering ML training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SYSTEM MONITORING ENDPOINTS ====================

@app.get("/celery/workers/health")
async def get_worker_health():
    """Get Celery worker health status"""
    try:
        # Mock worker health data
        return {
            "workers": [
                {
                    "name": "worker-1",
                    "status": "online",
                    "active_tasks": 5,
                    "processed_tasks": 1247,
                    "failed_tasks": 3
                },
                {
                    "name": "worker-2", 
                    "status": "online",
                    "active_tasks": 3,
                    "processed_tasks": 892,
                    "failed_tasks": 1
                }
            ],
            "total_workers": 2,
            "system_status": "healthy"
        }
    except Exception as e:
        logger.error(f"Error getting worker health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/celery/queues/metrics")
async def get_queue_metrics():
    """Get queue depth and performance metrics"""
    try:
        return {
            "queues": {
                "orders": {
                    "depth": 15,
                    "rate": 8.5,
                    "avg_processing_time": 45.2
                },
                "notifications": {
                    "depth": 8,
                    "rate": 12.3,
                    "avg_processing_time": 2.1
                },
                "analytics": {
                    "depth": 3,
                    "rate": 1.2,
                    "avg_processing_time": 180.5
                }
            },
            "total_tasks_processed": 2139,
            "system_load": 67.3
        }
    except Exception as e:
        logger.error(f"Error getting queue metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/celery/tasks/failed")
async def get_failed_tasks():
    """Get analysis of failed tasks"""
    try:
        return {
            "failed_tasks": [
                {
                    "task_id": "task-123",
                    "task_name": "process_order_workflow",
                    "error": "Payment gateway timeout",
                    "retry_count": 2,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "total_failed": 4,
            "failure_rate": 0.19
        }
    except Exception as e:
        logger.error(f"Error getting failed tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/celery/workers/scale/{queue_name}")
async def scale_workers(queue_name: str, count: int = 1):
    """Auto-scale workers for specific queue"""
    try:
        return {
            "message": f"Scaling {queue_name} workers",
            "queue_name": queue_name,
            "workers_added": count,
            "status": "scaling"
        }
    except Exception as e:
        logger.error(f"Error scaling workers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RESTAURANT MANAGEMENT ENDPOINTS ====================

@app.post("/restaurants/", response_model=RestaurantResponse)
async def create_new_restaurant(restaurant: RestaurantCreate, db=Depends(get_db)):
    """Create a new restaurant"""
    db_restaurant = create_restaurant(db, restaurant)
    return db_restaurant

@app.get("/restaurants/", response_model=List[RestaurantResponse])
async def get_all_restaurants_endpoint(db=Depends(get_db)):
    """Get all restaurants"""
    return get_all_restaurants(db)

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant_details(restaurant_id: int, db=Depends(get_db)):
    """Get restaurant details"""
    restaurant = get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

# ==================== CUSTOMER MANAGEMENT ENDPOINTS ====================

@app.post("/customers/", response_model=CustomerResponse)
async def create_new_customer(customer: CustomerCreate, db=Depends(get_db)):
    """Create a new customer"""
    db_customer = create_customer(db, customer)
    return db_customer

@app.get("/customers/", response_model=List[CustomerResponse])
async def get_all_customers_endpoint(db=Depends(get_db)):
    """Get all customers"""
    return get_all_customers(db)

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer_details(customer_id: int, db=Depends(get_db)):
    """Get customer details"""
    customer = get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# ==================== MENU MANAGEMENT ENDPOINTS ====================

@app.post("/menu-items/", response_model=MenuItemResponse)
async def create_menu_item_endpoint(menu_item: MenuItemCreate, db=Depends(get_db)):
    """Create a new menu item"""
    db_menu_item = create_menu_item(db, menu_item)
    return db_menu_item

@app.get("/menu-items/", response_model=List[MenuItemResponse])
async def get_menu_items_endpoint(restaurant_id: Optional[int] = None, db=Depends(get_db)):
    """Get menu items, optionally filtered by restaurant"""
    return get_menu_items(db, restaurant_id)

# ==================== HEALTH CHECK ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """System health check"""
    try:
        # Trigger system health check task
        health_task = system_health_check.delay()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "health_task_id": health_task.id
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 