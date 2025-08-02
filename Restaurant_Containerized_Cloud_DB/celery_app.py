from celery import Celery
from config import get_celery_config
import structlog

logger = structlog.get_logger()

# Create Celery instance
celery_app = Celery("restaurant_system")

# Configure Celery
celery_app.conf.update(get_celery_config())

# Auto-discover tasks
celery_app.autodiscover_tasks(["tasks"])

# Task routing
celery_app.conf.task_routes = {
    "tasks.process_order": {"queue": "orders"},
    "tasks.send_notification": {"queue": "notifications"},
    "tasks.update_restaurant_rating": {"queue": "analytics"},
    "tasks.process_payment": {"queue": "payments"},
    "tasks.assign_delivery_driver": {"queue": "delivery"},
    "tasks.cleanup_expired_orders": {"queue": "maintenance"},
}

# Task serialization
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

# Task execution settings
celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 30 * 60  # 30 minutes
celery_app.conf.task_soft_time_limit = 25 * 60  # 25 minutes

# Worker settings
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.worker_max_tasks_per_child = 1000
celery_app.conf.worker_disable_rate_limits = False

# Result backend settings
celery_app.conf.result_expires = 3600  # 1 hour
celery_app.conf.result_persistent = True

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-orders": {
        "task": "tasks.cleanup_expired_orders",
        "schedule": 3600.0,  # Every hour
    },
    "update-restaurant-ratings": {
        "task": "tasks.update_restaurant_rating",
        "schedule": 1800.0,  # Every 30 minutes
    },
    "send-delivery-reminders": {
        "task": "tasks.send_delivery_reminders",
        "schedule": 300.0,  # Every 5 minutes
    },
    "process-pending-payments": {
        "task": "tasks.process_pending_payments",
        "schedule": 600.0,  # Every 10 minutes
    },
}

# Task error handling
@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")


# Health check task
@celery_app.task
def health_check():
    """Periodic health check task."""
    try:
        # Check database connection
        from database import check_db_connection
        db_healthy = check_db_connection()
        
        # Check Redis connection
        from redis import Redis
        from config import get_redis_url
        redis_client = Redis.from_url(get_redis_url())
        redis_healthy = redis_client.ping()
        
        logger.info(
            "Health check completed",
            database=db_healthy,
            redis=redis_healthy,
        )
        
        return {
            "database": db_healthy,
            "redis": redis_healthy,
            "timestamp": "2024-01-01T00:00:00Z",
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "database": False,
            "redis": False,
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z",
        }


# Task monitoring
@celery_app.task
def monitor_task_execution():
    """Monitor task execution statistics."""
    try:
        stats = celery_app.control.inspect().stats()
        active_tasks = celery_app.control.inspect().active()
        registered_tasks = celery_app.control.inspect().registered()
        
        logger.info(
            "Task monitoring",
            stats=stats,
            active_tasks=active_tasks,
            registered_tasks=registered_tasks,
        )
        
        return {
            "stats": stats,
            "active_tasks": active_tasks,
            "registered_tasks": registered_tasks,
        }
    except Exception as e:
        logger.error("Task monitoring failed", error=str(e))
        return {"error": str(e)}


if __name__ == "__main__":
    celery_app.start() 