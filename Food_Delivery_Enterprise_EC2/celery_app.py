import os
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

# Configure Redis URL (for production, use environment variable)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "food_delivery_enterprise",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)

# Enterprise-level Celery configuration
celery_app.conf.update(
    # Task routing for different queues
    task_routes={
        'process_order_workflow': {'queue': 'orders'},
        'update_order_status': {'queue': 'orders'},
        'send_realtime_notifications': {'queue': 'notifications'},
        'bulk_notification_campaign': {'queue': 'notifications'},
        'generate_business_analytics': {'queue': 'analytics'},
        'ml_recommendation_training': {'queue': 'ml_processing'},
        'sync_payment_gateway': {'queue': 'payments'},
        'update_delivery_tracking': {'queue': 'delivery'},
        'system_health_check': {'queue': 'monitoring'},
        'cleanup_old_tasks': {'queue': 'maintenance'}
    },
    
    # Task prioritization
    task_default_priority=5,
    worker_prefetch_multiplier=1,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker configuration
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'system-health-check': {
            'task': 'system_health_check',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'cleanup-old-tasks': {
            'task': 'cleanup_old_tasks',
            'schedule': crontab(hour='*/2'),  # Every 2 hours
        },
        'generate-daily-analytics': {
            'task': 'generate_business_analytics',
            'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
            'args': ('daily_report', {'start_date': 'yesterday', 'end_date': 'today'})
        },
        'ml-model-retraining': {
            'task': 'ml_recommendation_training',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        }
    },
    
    # Task execution settings
    task_always_eager=False,
    task_eager_propagates=True,
    
    # Error handling
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Monitoring and logging
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security settings
    security_key=os.getenv("CELERY_SECURITY_KEY", "your-secret-key"),
    security_certificate=os.getenv("CELERY_CERTIFICATE", None),
    security_cert_store=os.getenv("CELERY_CERT_STORE", None),
)

# Configure logging
logger = get_task_logger(__name__)

# Queue definitions with priorities
celery_app.conf.task_routes = {
    'process_order_workflow': {'queue': 'orders', 'priority': 10},
    'update_order_status': {'queue': 'orders', 'priority': 8},
    'send_realtime_notifications': {'queue': 'notifications', 'priority': 6},
    'bulk_notification_campaign': {'queue': 'notifications', 'priority': 4},
    'generate_business_analytics': {'queue': 'analytics', 'priority': 2},
    'ml_recommendation_training': {'queue': 'ml_processing', 'priority': 1},
    'sync_payment_gateway': {'queue': 'payments', 'priority': 9},
    'update_delivery_tracking': {'queue': 'delivery', 'priority': 7},
    'system_health_check': {'queue': 'monitoring', 'priority': 5},
    'cleanup_old_tasks': {'queue': 'maintenance', 'priority': 3}
}

# Task error handling and retry configuration
celery_app.conf.task_annotations = {
    'process_order_workflow': {
        'rate_limit': '10/m',
        'time_limit': 300,
        'soft_time_limit': 240,
        'autoretry_for': (Exception,),
        'retry_kwargs': {'max_retries': 3, 'countdown': 60},
        'retry_backoff': True,
        'retry_backoff_max': 600,
    },
    'send_realtime_notifications': {
        'rate_limit': '100/m',
        'time_limit': 60,
        'soft_time_limit': 45,
        'autoretry_for': (Exception,),
        'retry_kwargs': {'max_retries': 5, 'countdown': 30},
    },
    'generate_business_analytics': {
        'rate_limit': '2/h',
        'time_limit': 1800,
        'soft_time_limit': 1500,
        'autoretry_for': (Exception,),
        'retry_kwargs': {'max_retries': 2, 'countdown': 300},
    },
    'ml_recommendation_training': {
        'rate_limit': '1/h',
        'time_limit': 3600,
        'soft_time_limit': 3300,
        'autoretry_for': (Exception,),
        'retry_kwargs': {'max_retries': 1, 'countdown': 600},
    }
}

# Worker pool configuration
celery_app.conf.worker_pool = 'prefork'
celery_app.conf.worker_concurrency = 4

# Result backend configuration
celery_app.conf.result_backend_transport_options = {
    'master_name': "mymaster",
    'visibility_timeout': 3600,
    'fanout_prefix': True,
    'fanout_patterns': True,
    'sentinel_kwargs': {},
}

# Task compression
celery_app.conf.task_compression = 'gzip'
celery_app.conf.result_compression = 'gzip'

# Task routing for different environments
if os.getenv("ENVIRONMENT") == "production":
    celery_app.conf.task_routes.update({
        'process_order_workflow': {'queue': 'orders_prod'},
        'send_realtime_notifications': {'queue': 'notifications_prod'},
        'generate_business_analytics': {'queue': 'analytics_prod'},
    })

# Monitoring and metrics
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True
celery_app.conf.event_queue_expires = 60
celery_app.conf.event_queue_ttl = 5.0

# Security settings for production
if os.getenv("ENVIRONMENT") == "production":
    celery_app.conf.security_key = os.getenv("CELERY_SECURITY_KEY")
    celery_app.conf.security_certificate = os.getenv("CELERY_CERTIFICATE")
    celery_app.conf.security_cert_store = os.getenv("CELERY_CERT_STORE")

# Task result expiration
celery_app.conf.result_expires = 3600  # 1 hour
celery_app.conf.task_ignore_result = False
celery_app.conf.task_store_errors_even_if_ignored = True

# Worker process settings
celery_app.conf.worker_max_tasks_per_child = 1000
celery_app.conf.worker_max_memory_per_child = 200000  # 200MB
celery_app.conf.worker_disable_rate_limits = False

# Task execution settings
celery_app.conf.task_always_eager = False
celery_app.conf.task_eager_propagates = True
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1

# Logging configuration
celery_app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
celery_app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Task routing for load balancing
celery_app.conf.task_routes = {
    'process_order_workflow': {'queue': 'orders'},
    'update_order_status': {'queue': 'orders'},
    'send_realtime_notifications': {'queue': 'notifications'},
    'bulk_notification_campaign': {'queue': 'notifications'},
    'generate_business_analytics': {'queue': 'analytics'},
    'ml_recommendation_training': {'queue': 'ml_processing'},
    'sync_payment_gateway': {'queue': 'payments'},
    'update_delivery_tracking': {'queue': 'delivery'},
    'system_health_check': {'queue': 'monitoring'},
    'cleanup_old_tasks': {'queue': 'maintenance'}
}

if __name__ == '__main__':
    celery_app.start() 