from celery_app import celery_app
from database import SessionLocal
from models import Restaurant
from crud import get_restaurants_by_cuisine, get_restaurant
import time
import random
from datetime import datetime
from typing import Dict, Any

@celery_app.task(bind=True, name="generate_restaurant_report")
def generate_restaurant_report(self, cuisine_type: str):
    """
    Generate comprehensive restaurant analytics for a specific cuisine type
    """
    try:
        # Update progress: 0% -> 25% -> 50% -> 75% -> 100%
        self.update_state(state="PROGRESS", meta={"progress": 0})
        time.sleep(2)  # Simulate processing time
        
        # Get restaurants by cuisine type
        db = SessionLocal()
        restaurants = get_restaurants_by_cuisine(db, cuisine_type)
        
        self.update_state(state="PROGRESS", meta={"progress": 25})
        time.sleep(2)
        
        # Calculate analytics
        total_restaurants = len(restaurants)
        if total_restaurants == 0:
            return {
                "cuisine_type": cuisine_type,
                "total_restaurants": 0,
                "average_rating": 0,
                "popular_price_ranges": [],
                "message": "No restaurants found for this cuisine type"
            }
        
        # Calculate average rating
        total_rating = sum(r.rating for r in restaurants)
        average_rating = total_rating / total_restaurants
        
        self.update_state(state="PROGRESS", meta={"progress": 50})
        time.sleep(2)
        
        # Analyze price ranges
        price_ranges = {}
        for restaurant in restaurants:
            price_range = restaurant.price_range
            price_ranges[price_range] = price_ranges.get(price_range, 0) + 1
        
        popular_price_ranges = sorted(price_ranges.items(), key=lambda x: x[1], reverse=True)
        
        self.update_state(state="PROGRESS", meta={"progress": 75})
        time.sleep(2)
        
        # Generate report
        report = {
            "cuisine_type": cuisine_type,
            "total_restaurants": total_restaurants,
            "average_rating": round(average_rating, 2),
            "popular_price_ranges": popular_price_ranges,
            "top_restaurants": [
                {
                    "id": r.id,
                    "name": r.name,
                    "rating": r.rating,
                    "price_range": r.price_range
                }
                for r in sorted(restaurants, key=lambda x: x.rating, reverse=True)[:5]
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        self.update_state(state="PROGRESS", meta={"progress": 100})
        time.sleep(1)
        
        db.close()
        return report
        
    except Exception as e:
        db.close()
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(name="sync_restaurant_data")
def sync_restaurant_data(restaurant_id: int):
    """
    Sync restaurant information with external APIs
    """
    try:
        db = SessionLocal()
        restaurant = get_restaurant(db, restaurant_id)
        
        if not restaurant:
            db.close()
            return {"error": "Restaurant not found", "restaurant_id": restaurant_id}
        
        # Simulate external API calls
        time.sleep(3)  # Simulate API call delay
        
        # Simulate updating restaurant data from external sources
        # In a real implementation, this would call Google Maps API, Yelp API, etc.
        updated_data = {
            "restaurant_id": restaurant_id,
            "name": restaurant.name,
            "external_rating": round(random.uniform(3.0, 5.0), 1),
            "external_reviews_count": random.randint(10, 500),
            "last_synced": datetime.utcnow().isoformat(),
            "sync_status": "success"
        }
        
        # Simulate updating the restaurant with external data
        restaurant.rating = (restaurant.rating + updated_data["external_rating"]) / 2
        db.commit()
        
        db.close()
        return updated_data
        
    except Exception as e:
        db.close()
        return {"error": str(e), "restaurant_id": restaurant_id}

@celery_app.task(name="send_restaurant_notifications")
def send_restaurant_notifications(restaurant_data: Dict[str, Any], notification_type: str):
    """
    Send notifications about restaurant updates
    """
    try:
        # Simulate notification processing
        time.sleep(2)
        
        notification_result = {
            "restaurant_id": restaurant_data.get("id"),
            "restaurant_name": restaurant_data.get("name"),
            "notification_type": notification_type,
            "sent_at": datetime.utcnow().isoformat(),
            "recipients": [],
            "status": "sent"
        }
        
        # Simulate different notification types
        if notification_type == "new_restaurant":
            notification_result["recipients"] = ["subscribers@example.com", "admin@example.com"]
            notification_result["message"] = f"New restaurant added: {restaurant_data.get('name')}"
        elif notification_type == "restaurant_update":
            notification_result["recipients"] = ["subscribers@example.com"]
            notification_result["message"] = f"Restaurant updated: {restaurant_data.get('name')}"
        elif notification_type == "rating_update":
            notification_result["recipients"] = ["admin@example.com"]
            notification_result["message"] = f"Rating updated for: {restaurant_data.get('name')}"
        else:
            notification_result["status"] = "failed"
            notification_result["error"] = "Unknown notification type"
        
        return notification_result
        
    except Exception as e:
        return {
            "error": str(e),
            "restaurant_data": restaurant_data,
            "notification_type": notification_type,
            "status": "failed"
        }

@celery_app.task(name="cleanup_old_tasks")
def cleanup_old_tasks():
    """
    Cleanup old completed tasks from result backend
    """
    try:
        # This would typically clean up old task results from Redis
        # For this demo, we'll just return a success message
        return {
            "cleanup_status": "completed",
            "cleaned_tasks": random.randint(10, 50),
            "cleaned_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "cleanup_status": "failed"} 