# Zomato-like Restaurant Management System with Redis Cache - Version 2.0

A high-performance restaurant management system built with FastAPI, SQLAlchemy, and Redis caching for improved response times and scalability.

## Features

### Core Features
- Complete CRUD operations for restaurants
- Restaurant data validation and error handling
- Proper API documentation with FastAPI
- Search functionality by cuisine type
- Pagination support
- Active restaurant filtering
- Input validation (phone number format, rating range, time validation)
- Error handling for duplicate restaurant names

### Redis Caching Features
- **Redis Integration**: Full Redis caching with fastapi-cache2
- **Performance Monitoring**: Response time logging for cache hit/miss analysis
- **Cache Management**: Comprehensive cache statistics and management endpoints
- **Smart Invalidation**: Automatic cache invalidation on data changes
- **Namespace Organization**: Organized caching with namespace-based structure

### Caching Strategy
- **Restaurant List**: 300-second TTL with namespace "restaurants"
- **Individual Restaurant**: 600-second TTL with namespace "restaurants"
- **Search Results**: 180-second TTL with namespace "restaurants"
- **Active Restaurants**: 240-second TTL with namespace "restaurants"

### Cache Invalidation Rules
- **On Creation**: Clear entire restaurant namespace
- **On Update**: Clear specific restaurant cache + list caches
- **On Deletion**: Clear specific restaurant cache + list caches

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
- `GET /restaurants/` - List all restaurants (with pagination, cached)
- `GET /restaurants/{restaurant_id}` - Get specific restaurant (cached)
- `PUT /restaurants/{restaurant_id}` - Update restaurant
- `DELETE /restaurants/{restaurant_id}` - Delete restaurant

### Search and Filter

- `GET /restaurants/search?cuisine={cuisine_type}` - Search by cuisine (cached)
- `GET /restaurants/active` - List only active restaurants (cached)

### Cache Management

- `GET /cache/stats` - View cache statistics and keys
- `DELETE /cache/clear` - Clear entire cache
- `DELETE /cache/clear/restaurants` - Clear only restaurant-related caches

### Demo and Testing

- `GET /demo/cache-test/{restaurant_id}` - Demonstrate cache performance
- `POST /demo/sample-data` - Create sample restaurants for testing

## Performance Requirements

- **First Request**: Shows "CACHE MISS" behavior
- **Subsequent Requests**: Shows "CACHE HIT" with <10ms response time
- **Response Time Logging**: Comprehensive logging for cache hit/miss analysis

## Setup Instructions

### 1. Install Redis Server

#### On macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### On Windows:
Download and install Redis from https://redis.io/download

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

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

### 5. Start the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Testing the Cache System

### 1. Create Sample Data

```bash
curl -X POST "http://localhost:8000/demo/sample-data"
```

### 2. Test Cache Performance

```bash
# First request (cache miss)
curl "http://localhost:8000/restaurants/1"

# Second request (cache hit)
curl "http://localhost:8000/restaurants/1"
```

### 3. View Cache Statistics

```bash
curl "http://localhost:8000/cache/stats"
```

### 4. Test Cache Invalidation

```bash
# Update a restaurant (this will clear cache)
curl -X PUT "http://localhost:8000/restaurants/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Restaurant Name"}'

# Check cache stats again
curl "http://localhost:8000/cache/stats"
```

## Cache Configuration

The system uses the following cache configuration:

- **Redis URL**: `redis://localhost:6379`
- **Cache Prefix**: `restaurant-cache`
- **Namespace**: `restaurants`

### TTL Settings

- Restaurant List: 300 seconds (5 minutes)
- Individual Restaurant: 600 seconds (10 minutes)
- Search Results: 180 seconds (3 minutes)
- Active Restaurants: 240 seconds (4 minutes)

## Performance Monitoring

The system includes comprehensive performance monitoring:

- **Response Time Logging**: All endpoints log response times
- **Cache Hit/Miss Logging**: Clear indication of cache performance
- **Performance Metrics**: Available via `/demo/cache-test/{restaurant_id}`

## Error Handling

- **Redis Connection Errors**: Graceful handling of Redis connection issues
- **Cache Miss Fallback**: Automatic fallback to database when cache is unavailable
- **Validation Errors**: Comprehensive input validation with clear error messages
- **Duplicate Handling**: Proper handling of duplicate restaurant names

## Dependencies

- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `sqlalchemy==2.0.23` - ORM
- `aiosqlite==0.19.0` - Async SQLite
- `pydantic==2.5.0` - Data validation
- `redis==5.0.1` - Redis client
- `fastapi-cache2==0.2.1` - FastAPI caching

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Redis Cache   │    │   SQLite DB     │
│                 │    │                 │    │                 │
│  - Endpoints    │◄──►│  - Cache Store  │    │  - Data Store   │
│  - Validation   │    │  - TTL Mgmt     │    │  - Persistence  │
│  - Error Hand.  │    │  - Invalidation │    │  - ACID         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Monitoring and Logs

The application provides detailed logging for:

- Cache hits and misses
- Response times for all endpoints
- Cache invalidation events
- Redis connection status
- Performance metrics

## Future Enhancements

- **Cache Warming**: Pre-populate cache with frequently accessed data
- **Cache Analytics**: Detailed analytics dashboard
- **Multi-Node Support**: Redis cluster support
- **Advanced Caching**: Cache compression and optimization
- **Health Checks**: Redis health monitoring endpoints

## Troubleshooting

### Redis Connection Issues

1. Ensure Redis server is running:
   ```bash
   redis-cli ping
   ```

2. Check Redis configuration:
   ```bash
   redis-cli config get bind
   redis-cli config get port
   ```

### Cache Performance Issues

1. Monitor cache hit rates via `/cache/stats`
2. Check response time logs in application output
3. Verify TTL settings in `cache_config.py`

### Database Issues

1. Ensure database is initialized:
   ```bash
   python init_db.py
   ```

2. Check database file permissions and location

## API Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## License

This project is for educational purposes and demonstrates advanced caching strategies in FastAPI applications. 