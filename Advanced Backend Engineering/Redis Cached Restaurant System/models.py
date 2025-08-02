from sqlalchemy import Column, Integer, String, Float, Boolean, Time, DateTime, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    cuisine_type = Column(String(50), nullable=False, index=True)
    address = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False)
    rating = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Restaurant(id={self.id}, name='{self.name}', cuisine_type='{self.cuisine_type}')>" 