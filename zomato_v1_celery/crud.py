from sqlalchemy.orm import Session
from models import Restaurant
from schemas import RestaurantCreate

def get_restaurant(db: Session, restaurant_id: int):
    return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

def get_restaurants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Restaurant).offset(skip).limit(limit).all()

def create_restaurant(db: Session, restaurant: RestaurantCreate):
    db_restaurant = Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def update_restaurant(db: Session, restaurant_id: int, restaurant: RestaurantCreate):
    db_restaurant = get_restaurant(db, restaurant_id)
    if db_restaurant is None:
        return None
    
    for key, value in restaurant.dict().items():
        setattr(db_restaurant, key, value)
    
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def delete_restaurant(db: Session, restaurant_id: int):
    db_restaurant = get_restaurant(db, restaurant_id)
    if db_restaurant is None:
        return False
    
    db.delete(db_restaurant)
    db.commit()
    return True

def get_restaurants_by_cuisine(db: Session, cuisine_type: str):
    return db.query(Restaurant).filter(Restaurant.cuisine_type == cuisine_type).all()

def get_restaurants_by_rating(db: Session, min_rating: float):
    return db.query(Restaurant).filter(Restaurant.rating >= min_rating).all() 