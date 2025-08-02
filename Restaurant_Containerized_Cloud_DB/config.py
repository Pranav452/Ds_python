from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import structlog


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/restaurant_db"
    database_ssl_mode: str = "require"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    celery_timezone: str = "UTC"
    
    # Application Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    debug: bool = False
    environment: str = "production"
    log_level: str = "INFO"
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: Optional[str] = None
    
    # External API Keys
    maps_api_key: Optional[str] = None
    email_api_key: Optional[str] = None
    sms_api_key: Optional[str] = None
    
    # Monitoring and Logging
    prometheus_enabled: bool = True
    structlog_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    
    # Security
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["localhost"]
    
    # Performance
    worker_concurrency: int = 4
    max_connections: int = 20
    pool_size: int = 10
    
    # Database Pool Configuration
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get database URL with SSL configuration for cloud databases."""
    if settings.environment == "production":
        return f"{settings.database_url}?sslmode={settings.database_ssl_mode}"
    return settings.database_url


def get_redis_url() -> str:
    """Get Redis URL with proper configuration."""
    return settings.redis_url


def get_celery_config() -> dict:
    """Get Celery configuration."""
    return {
        "broker_url": settings.celery_broker_url,
        "result_backend": settings.celery_result_backend,
        "timezone": settings.celery_timezone,
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "task_track_started": True,
        "task_time_limit": 30 * 60,  # 30 minutes
        "task_soft_time_limit": 25 * 60,  # 25 minutes
        "worker_prefetch_multiplier": 1,
        "worker_max_tasks_per_child": 1000,
    }


def get_logging_config() -> dict:
    """Get structured logging configuration."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.dev.ConsoleRenderer(),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "structured",
                "level": settings.log_level,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": settings.log_level,
                "propagate": True,
            },
        },
    } 