from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import time, datetime
from decimal import Decimal
import re

# Restaurant Schemas
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

# MenuItem Schemas
class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Menu item name")
    description: Optional[str] = Field(None, description="Menu item description")
    price: Decimal = Field(..., gt=0, description="Price with 2 decimal places")
    category: str = Field(..., min_length=2, max_length=50, description="Menu category")
    is_vegetarian: bool = Field(default=False, description="Whether item is vegetarian")
    is_vegan: bool = Field(default=False, description="Whether item is vegan")
    is_available: bool = Field(default=True, description="Whether item is available")
    preparation_time: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class MenuItemCreate(MenuItemBase):
    restaurant_id: int = Field(..., description="Restaurant ID")

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, ge=0)
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v

class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

# Nested Schemas for Complex Responses
class MenuItemWithRestaurant(MenuItemResponse):
    restaurant: RestaurantResponse
    
    class Config:
        from_attributes = True

class RestaurantWithMenu(RestaurantResponse):
    menu_items: List[MenuItemResponse] = []
    
    class Config:
        from_attributes = True

# Search and Filter Schemas
class MenuItemSearch(BaseModel):
    category: Optional[str] = None
    vegetarian: Optional[bool] = None
    vegan: Optional[bool] = None
    available: Optional[bool] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    
    @validator('min_price', 'max_price')
    def validate_price_range(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('max_price')
    def validate_max_price(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('Max price must be greater than or equal to min price')
        return v 