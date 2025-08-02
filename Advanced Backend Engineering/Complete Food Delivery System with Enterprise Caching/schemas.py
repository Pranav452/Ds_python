from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime, time
from decimal import Decimal
import re
from models import OrderStatus

# Base Schemas
class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Restaurant name")
    description: Optional[str] = Field(None, description="Restaurant description")
    cuisine_type: str = Field(..., min_length=2, max_length=50, description="Type of cuisine")
    address: str = Field(..., min_length=5, max_length=200, description="Restaurant address")
    phone_number: str = Field(..., description="Contact phone number")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Restaurant rating (0.0-5.0)")
    is_active: bool = Field(default=True, description="Whether restaurant is active")
    opening_time: str = Field(..., description="Opening time (HH:MM)")
    closing_time: str = Field(..., description="Closing time (HH:MM)")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        if not re.match(phone_pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('opening_time', 'closing_time')
    def validate_time_format(cls, v):
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError('Time must be in HH:MM format')
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
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
            if not re.match(phone_pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                raise ValueError('Invalid phone number format')
        return v

class RestaurantResponse(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
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

# Customer Schemas
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Customer name")
    email: str = Field(..., description="Customer email")
    phone_number: str = Field(..., description="Customer phone number")
    address: str = Field(..., min_length=10, max_length=500, description="Customer address")
    is_active: bool = Field(default=True, description="Whether customer is active")
    
    @validator('email')
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        if not re.match(phone_pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            raise ValueError('Invalid phone number format')
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = Field(None, min_length=10, max_length=500)
    is_active: Optional[bool] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
            if not re.match(phone_pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                raise ValueError('Invalid phone number format')
        return v

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# OrderItem Schemas
class OrderItemBase(BaseModel):
    menu_item_id: int = Field(..., description="Menu item ID")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    special_requests: Optional[str] = Field(None, description="Special requests for this item")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    item_price: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

# Order Schemas
class OrderBase(BaseModel):
    restaurant_id: int = Field(..., description="Restaurant ID")
    delivery_address: str = Field(..., min_length=10, max_length=500, description="Delivery address")
    special_instructions: Optional[str] = Field(None, description="Special delivery instructions")
    order_items: List[OrderItemCreate] = Field(..., min_items=1, description="List of order items")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    order_status: Optional[OrderStatus] = None
    delivery_time: Optional[datetime] = None
    special_instructions: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    order_status: OrderStatus
    total_amount: Decimal
    delivery_address: str
    special_instructions: Optional[str]
    order_date: datetime
    delivery_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment")
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    customer_id: int
    restaurant_id: int
    order_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
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

class OrderWithDetails(OrderResponse):
    customer: CustomerResponse
    restaurant: RestaurantResponse
    
    class Config:
        from_attributes = True

class CustomerWithOrders(CustomerResponse):
    orders: List[OrderResponse] = []
    
    class Config:
        from_attributes = True

class RestaurantWithOrders(RestaurantResponse):
    orders: List[OrderResponse] = []
    
    class Config:
        from_attributes = True

class RestaurantWithReviews(RestaurantResponse):
    reviews: List[ReviewResponse] = []
    
    class Config:
        from_attributes = True

class CustomerWithReviews(CustomerResponse):
    reviews: List[ReviewResponse] = []
    
    class Config:
        from_attributes = True

# Search and Filter Schemas
class RestaurantSearch(BaseModel):
    cuisine_type: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    max_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_active: Optional[bool] = None
    
    @validator('max_rating')
    def validate_rating_range(cls, v, values):
        if v is not None and 'min_rating' in values and values['min_rating'] is not None:
            if v < values['min_rating']:
                raise ValueError('Max rating must be greater than or equal to min rating')
        return v

class OrderSearch(BaseModel):
    status: Optional[OrderStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = Field(None, gt=0)
    max_amount: Optional[Decimal] = Field(None, gt=0)
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError('Max amount must be greater than or equal to min amount')
        return v

# Analytics Schemas
class RestaurantAnalytics(BaseModel):
    total_orders: int
    total_revenue: Decimal
    average_order_value: Decimal
    total_reviews: int
    average_rating: float
    popular_items: List[dict]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class CustomerAnalytics(BaseModel):
    total_orders: int
    total_spent: Decimal
    average_order_value: Decimal
    favorite_restaurants: List[dict]
    order_history: List[dict]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        } 