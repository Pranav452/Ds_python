# Zomato-like Restaurant Management System - Version 1

A basic restaurant management system built with FastAPI, SQLAlchemy, and SQLite. This is the foundation of a progressive food delivery application.

## Features

- Complete CRUD operations for restaurants
- Restaurant data validation and error handling
- Proper API documentation with FastAPI
- Search functionality by cuisine type
- Pagination support
- Active restaurant filtering
- Input validation (phone number format, rating range, time validation)
- Error handling for duplicate restaurant names

## Restaurant Model Fields

- `id` (Primary Key)
- `name` (Required, 3-100 characters, unique)
- `description` (Optional text)
- `cuisine_type` (Required, e.g., "Italian", "Chinese", "Indian")
- `address` (Required)
- `phone_number` (Required, with validation)
- `rating` (Float, 0.0-5.0, default 0.0)
- `is_active` (Boolean, default True)
- `opening_time` (Time)
- `closing_time` (Time)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

## API Endpoints

### Restaurant Management

- `POST /restaurants/` - Create new restaurant
- `GET /restaurants/` - List all restaurants (with pagination)
- `GET /restaurants/{restaurant_id}` - Get specific restaurant
- `PUT /restaurants/{restaurant_id}` - Update restaurant
- `DELETE /restaurants/{restaurant_id}` - Delete restaurant

### Search and Filter

- `GET /restaurants/search?cuisine={cuisine_type}` - Search by cuisine
- `GET /restaurants/active` - List only active restaurants

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

Create a Python script to initialize the database:

```python
import asyncio
from database import create_tables

async def init_db():
    await create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
```

Run it:
```bash
python init_db.py
```

### 4. Run the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## Usage Examples

### Create a Restaurant

```bash
curl -X POST "http://localhost:8000/restaurants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pizza Palace",
    "description": "Best pizza in town",
    "cuisine_type": "Italian",
    "address": "123 Main St, City",
    "phone_number": "+1234567890",
    "rating": 4.5,
    "opening_time": "10:00",
    "closing_time": "22:00"
  }'
```

### Get All Restaurants

```bash
curl "http://localhost:8000/restaurants/?skip=0&limit=10"
```

### Search by Cuisine

```bash
curl "http://localhost:8000/restaurants/search?cuisine=Italian"
```

### Update Restaurant

```bash
curl -X PUT "http://localhost:8000/restaurants/1" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4.8,
    "description": "Updated description"
  }'
```

### Delete Restaurant

```bash
curl -X DELETE "http://localhost:8000/restaurants/1"
```

## Validation Rules

- **Name**: 3-100 characters, must be unique
- **Phone Number**: Must be a valid phone number format
- **Rating**: 0.0-5.0 range
- **Times**: Closing time must be after opening time
- **Address**: 5-200 characters
- **Cuisine Type**: 2-50 characters

## Error Handling

The API includes comprehensive error handling for:

- Duplicate restaurant names
- Invalid input data
- Non-existent resources
- Validation errors
- Database errors

## Project Structure

```
Advanced Backend Engineering/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas for validation
├── crud.py             # CRUD operations
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **SQLite**: Lightweight database
- **aiosqlite**: Async SQLite driver
- **Uvicorn**: ASGI server

## Next Steps

This is Version 1 of the progressive food delivery application. Future versions will include:

- Version 2: Menu management and order processing
- Version 3: User authentication and advanced features

## License

This project is for educational purposes. 