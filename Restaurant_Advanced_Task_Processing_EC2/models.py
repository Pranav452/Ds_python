from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    cuisine_type = Column(String(50))
    rating = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    analytics = relationship("MenuAnalytics", back_populates="restaurant")

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    is_available = Column(Boolean, default=True)
    image_urls = Column(JSON, default=list)
    popularity_score = Column(Float, default=0.0)
    preparation_time = Column(Integer, default=15)  # minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20))
    customer_email = Column(String(100))
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, confirmed, preparing, ready, delivered, cancelled
    order_time = Column(DateTime, default=datetime.utcnow)
    delivery_time = Column(DateTime)
    special_instructions = Column(Text)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    special_instructions = Column(Text)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

class MenuAnalytics(Base):
    __tablename__ = "menu_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    analysis_date = Column(DateTime, default=datetime.utcnow)
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    popularity_score = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    pricing_recommendation = Column(JSON)
    performance_metrics = Column(JSON)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="analytics")

class TaskWorkflow(Base):
    __tablename__ = "task_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(100), unique=True, index=True)
    workflow_type = Column(String(50), nullable=False)  # restaurant_setup, menu_batch_process, analytics
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    task_data = Column(JSON)
    result_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    restaurant = relationship("Restaurant")

class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True)
    task_name = Column(String(100), nullable=False)
    priority = Column(String(20), default="medium")  # high, medium, low
    status = Column(String(20), default="pending")  # pending, running, completed, failed, retrying
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    execution_time = Column(Float)  # seconds
    result_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime) 