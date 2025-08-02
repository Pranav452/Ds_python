from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class RestaurantBase(BaseModel):
    name: str
    cuisine_type: str
    address: str
    phone: str
    rating: Optional[float] = 0.0
    price_range: Optional[str] = "$$"
    description: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskStatus(BaseModel):
    task_id: str
    status: str  # PENDING, PROCESSING, SUCCESS, FAILURE, CANCELLED
    progress: Optional[int] = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskCreate(BaseModel):
    task_type: str
    parameters: Dict[str, Any] 