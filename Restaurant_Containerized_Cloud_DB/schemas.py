from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
from models import OrderStatus, PaymentStatus


# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Restaurant schemas
class RestaurantBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    address: str = Field(..., min_length=1)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    cuisine_type: Optional[str] = None
    delivery_fee: float = Field(0.0, ge=0)
    minimum_order: float = Field(0.0, ge=0)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    cuisine_type: Optional[str] = None
    delivery_fee: Optional[float] = Field(None, ge=0)
    minimum_order: Optional[float] = Field(None, ge=0)


class Restaurant(RestaurantBase):
    id: int
    rating: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Category schemas
class CategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None


class Category(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime


# MenuItem schemas
class MenuItemBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    preparation_time: int = Field(15, ge=1)
    calories: Optional[int] = Field(None, ge=0)
    restaurant_id: int
    category_id: int


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    preparation_time: Optional[int] = Field(None, ge=1)
    calories: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None


class MenuItem(MenuItemBase):
    id: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    restaurant: Restaurant
    category: Category


# OrderItem schemas
class OrderItemBase(BaseSchema):
    menu_item_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    special_instructions: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    total_price: float
    created_at: datetime
    menu_item: MenuItem


# Order schemas
class OrderBase(BaseSchema):
    restaurant_id: int
    delivery_address: str = Field(..., min_length=1)
    delivery_instructions: Optional[str] = None


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]

    @validator('order_items')
    def validate_order_items(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v


class OrderUpdate(BaseSchema):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    delivery_address: Optional[str] = Field(None, min_length=1)
    delivery_instructions: Optional[str] = None


class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: float
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: User
    restaurant: Restaurant
    order_items: List[OrderItem]


# Review schemas
class ReviewBase(BaseSchema):
    restaurant_id: int
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseSchema):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class Review(ReviewBase):
    id: int
    user_id: int
    is_verified: bool
    created_at: datetime
    user: User
    restaurant: Restaurant


# Delivery schemas
class DeliveryDriverBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10)
    email: Optional[EmailStr] = None
    vehicle_number: Optional[str] = None


class DeliveryDriverCreate(DeliveryDriverBase):
    pass


class DeliveryDriverUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10)
    email: Optional[EmailStr] = None
    vehicle_number: Optional[str] = None
    current_location: Optional[str] = None
    is_available: Optional[bool] = None


class DeliveryDriver(DeliveryDriverBase):
    id: int
    is_available: bool
    current_location: Optional[str] = None
    rating: float
    created_at: datetime
    updated_at: Optional[datetime] = None


class DeliveryBase(BaseSchema):
    order_id: int
    driver_id: int


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseSchema):
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    status: Optional[str] = None


class Delivery(DeliveryBase):
    id: int
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    order: Order
    driver: DeliveryDriver


# Response schemas
class HealthCheck(BaseSchema):
    status: str
    timestamp: datetime
    database: bool
    redis: bool
    version: str = "3.0.0"


class PaginatedResponse(BaseSchema):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int


# Authentication schemas
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    username: Optional[str] = None


class LoginRequest(BaseSchema):
    username: str
    password: str 