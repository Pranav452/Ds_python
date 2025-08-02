from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import time, datetime
import re

class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Restaurant name")
    description: Optional[str] = Field(None, description="Restaurant description")
    cuisine_type: str = Field(..., min_length=2, max_length=50, description="Type of cuisine")
    address: str = Field(..., min_length=5, max_length=200, description="Restaurant address")
    phone_number: str = Field(..., description="Contact phone number")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Restaurant rating (0.0-5.0)")
    is_active: bool = Field(default=True, description="Whether restaurant is active")
    opening_time: time = Field(..., description="Opening time")
    closing_time: time = Field(..., description="Closing time")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Basic phone number validation (allows various formats)
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        if not re.match(phone_pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('closing_time')
    def validate_closing_time(cls, v, values):
        if 'opening_time' in values and v <= values['opening_time']:
            raise ValueError('Closing time must be after opening time')
        return v

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, min_length=2, max_length=50)
    address: Optional[str] = Field(None, min_length=5, max_length=200)
    phone_number: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_active: Optional[bool] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
            if not re.match(phone_pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                raise ValueError('Invalid phone number format')
        return v
    
    @validator('closing_time')
    def validate_closing_time(cls, v, values):
        if v is not None and 'opening_time' in values and values['opening_time'] is not None:
            if v <= values['opening_time']:
                raise ValueError('Closing time must be after opening time')
        return v

class RestaurantResponse(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            time: lambda v: v.strftime("%H:%M"),
            datetime: lambda v: v.isoformat()
        } 