from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

# ==================== ENUM CLASSES ====================

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class WorkflowStatus(str, Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

class SystemHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"

# ==================== BASE MODELS ====================

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ==================== CUSTOMER SCHEMAS ====================

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

class CustomerResponse(CustomerBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime

# ==================== RESTAURANT SCHEMAS ====================

class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    cuisine_type: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    cuisine_type: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    is_active: Optional[bool] = None

class RestaurantResponse(RestaurantBase, BaseSchema):
    id: int
    rating: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

# ==================== MENU ITEM SCHEMAS ====================

class MenuItemBase(BaseModel):
    restaurant_id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=50)
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    is_available: Optional[bool] = None

class MenuItemResponse(MenuItemBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime

# ==================== ORDER SCHEMAS ====================

class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    special_instructions: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase, BaseSchema):
    id: int
    total_price: float
    menu_item: MenuItemResponse

class OrderBase(BaseModel):
    customer_id: int
    restaurant_id: int
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None

class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate] = Field(..., min_items=1)
    
    @validator('order_items')
    def validate_order_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None

class OrderResponse(OrderBase, BaseSchema):
    id: int
    status: OrderStatus
    total_amount: float
    payment_status: PaymentStatus
    workflow_status: WorkflowStatus
    workflow_progress: int
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse]
    customer: CustomerResponse
    restaurant: RestaurantResponse

# ==================== ORDER STATUS UPDATE SCHEMAS ====================

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    metadata: Optional[Dict[str, Any]] = None

# ==================== NOTIFICATION SCHEMAS ====================

class NotificationBase(BaseModel):
    user_id: int
    user_type: str = Field(..., regex="^(customer|restaurant)$")
    type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    message: str
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase, BaseSchema):
    id: int
    is_read: bool
    sent_at: datetime
    read_at: Optional[datetime] = None

# ==================== CAMPAIGN SCHEMAS ====================

class NotificationCampaign(BaseModel):
    campaign_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_segments: List[str] = Field(..., min_items=1)
    message_template: str
    status: CampaignStatus = CampaignStatus.DRAFT
    scheduled_at: Optional[datetime] = None

class CampaignResponse(NotificationCampaign, BaseSchema):
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    total_targets: int
    sent_count: int
    success_count: int
    failure_count: int

# ==================== ANALYTICS SCHEMAS ====================

class AnalyticsReport(BaseModel):
    report_type: str = Field(..., max_length=50)
    date_range: Dict[str, Any]
    report_data: Dict[str, Any]

class AnalyticsReportResponse(AnalyticsReport, BaseSchema):
    id: int
    generated_at: datetime
    status: str

# ==================== WORKFLOW SCHEMAS ====================

class WorkflowStatus(BaseModel):
    order_id: int
    workflow_status: WorkflowStatus
    current_stage: str
    progress_percentage: int = Field(..., ge=0, le=100)
    estimated_completion: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# ==================== SYSTEM HEALTH SCHEMAS ====================

class SystemHealth(BaseModel):
    status: SystemHealthStatus
    timestamp: datetime
    metrics: Dict[str, Any]
    critical_issues: List[str] = []
    component_health: Dict[str, Any]

class SystemHealthResponse(SystemHealth, BaseSchema):
    id: int

# ==================== TASK EXECUTION SCHEMAS ====================

class TaskExecution(BaseModel):
    task_id: str
    task_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    queue_name: Optional[str] = None
    priority: int = 5

class TaskExecutionResponse(TaskExecution, BaseSchema):
    id: int

# ==================== API RESPONSE SCHEMAS ====================

class APIResponse(BaseModel):
    message: str
    status: str = "success"
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==================== WORKFLOW MANAGEMENT SCHEMAS ====================

class WorkflowTrigger(BaseModel):
    order_id: int
    force_restart: bool = False

class WorkflowCancel(BaseModel):
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ==================== MONITORING SCHEMAS ====================

class WorkerHealth(BaseModel):
    name: str
    status: str
    active_tasks: int
    processed_tasks: int
    failed_tasks: int

class QueueMetrics(BaseModel):
    queue_name: str
    depth: int
    rate: float
    avg_processing_time: float

class SystemMetrics(BaseModel):
    workers: List[WorkerHealth]
    queues: List[QueueMetrics]
    total_tasks_processed: int
    system_load: float

class FailedTask(BaseModel):
    task_id: str
    task_name: str
    error: str
    retry_count: int
    timestamp: datetime

class FailedTasksResponse(BaseModel):
    failed_tasks: List[FailedTask]
    total_failed: int
    failure_rate: float

# ==================== SCALING SCHEMAS ====================

class WorkerScaling(BaseModel):
    queue_name: str
    count: int = Field(..., gt=0, le=10)
    reason: Optional[str] = None

# ==================== VALIDATION SCHEMAS ====================

class ValidationError(BaseModel):
    field: str
    message: str
    value: Any

class ValidationResponse(BaseModel):
    is_valid: bool
    errors: List[ValidationError] = []
    warnings: List[str] = [] 