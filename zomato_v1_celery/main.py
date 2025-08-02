from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from database import engine, get_db
from models import Base
from schemas import RestaurantCreate, Restaurant, TaskStatus, TaskCreate
from crud import (
    create_restaurant, get_restaurants, get_restaurant, 
    update_restaurant, delete_restaurant
)
from celery_app import celery_app
from tasks import (
    generate_restaurant_report, sync_restaurant_data, 
    send_restaurant_notifications
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zomato-like Food Delivery System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task storage (in production, use Redis or database)
task_store: Dict[str, TaskStatus] = {}

@app.get("/")
def read_root():
    return {"message": "Zomato-like Food Delivery System with Celery"}

# Restaurant endpoints
@app.post("/restaurants/", response_model=Restaurant)
def create_restaurant_endpoint(restaurant: RestaurantCreate, db=Depends(get_db)):
    return create_restaurant(db=db, restaurant=restaurant)

@app.get("/restaurants/", response_model=List[Restaurant])
def read_restaurants(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    restaurants = get_restaurants(db, skip=skip, limit=limit)
    return restaurants

@app.get("/restaurants/{restaurant_id}", response_model=Restaurant)
def read_restaurant(restaurant_id: int, db=Depends(get_db)):
    restaurant = get_restaurant(db, restaurant_id=restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.put("/restaurants/{restaurant_id}", response_model=Restaurant)
def update_restaurant_endpoint(restaurant_id: int, restaurant: RestaurantCreate, db=Depends(get_db)):
    updated_restaurant = update_restaurant(db, restaurant_id, restaurant)
    if updated_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated_restaurant

@app.delete("/restaurants/{restaurant_id}")
def delete_restaurant_endpoint(restaurant_id: int, db=Depends(get_db)):
    success = delete_restaurant(db, restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {"message": "Restaurant deleted successfully"}

# Celery task endpoints
@app.post("/tasks/generate-report/{cuisine_type}")
def start_report_generation(cuisine_type: str):
    task_id = str(uuid.uuid4())
    task = TaskStatus(
        task_id=task_id,
        status="PENDING",
        progress=0,
        started_at=datetime.utcnow()
    )
    task_store[task_id] = task
    
    # Start Celery task
    celery_task = generate_restaurant_report.delay(cuisine_type)
    task_store[task_id].result = {"celery_task_id": celery_task.id}
    
    return {"task_id": task_id, "message": "Report generation started"}

@app.get("/tasks/status/{task_id}")
def get_task_status(task_id: str):
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_store[task_id]

@app.get("/tasks/list")
def list_tasks():
    return list(task_store.values())

@app.delete("/tasks/cancel/{task_id}")
def cancel_task(task_id: str):
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_store[task_id]
    if task.status in ["SUCCESS", "FAILURE"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed task")
    
    # Cancel Celery task if it exists
    if task.result and "celery_task_id" in task.result:
        celery_app.control.revoke(task.result["celery_task_id"], terminate=True)
    
    task.status = "CANCELLED"
    task.completed_at = datetime.utcnow()
    
    return {"message": "Task cancelled successfully"}

@app.post("/restaurants/{restaurant_id}/sync")
def sync_restaurant_endpoint(restaurant_id: int):
    task_id = str(uuid.uuid4())
    task = TaskStatus(
        task_id=task_id,
        status="PENDING",
        progress=0,
        started_at=datetime.utcnow()
    )
    task_store[task_id] = task
    
    # Start Celery task
    celery_task = sync_restaurant_data.delay(restaurant_id)
    task_store[task_id].result = {"celery_task_id": celery_task.id}
    
    return {"task_id": task_id, "message": "Restaurant sync started"}

@app.get("/workers/status")
def get_worker_status():
    try:
        # Get active workers
        active_workers = celery_app.control.inspect().active()
        registered_workers = celery_app.control.inspect().registered()
        
        return {
            "active_workers": active_workers or {},
            "registered_workers": registered_workers or {},
            "total_workers": len(active_workers) if active_workers else 0
        }
    except Exception as e:
        return {"error": str(e), "workers": {}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 