# Quick Start Guide - Redis Cached Restaurant System

This guide will help you get the Redis Cached Restaurant System up and running in minutes.

## Prerequisites

- Python 3.8 or higher
- Redis server
- Git (optional)

## Step 1: Install Redis

### macOS
```bash
brew install redis
brew services start redis
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Windows
Download and install Redis from https://redis.io/download

## Step 2: Verify Redis Installation

```bash
redis-cli ping
```
Should return: `PONG`

## Step 3: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Initialize Database

```bash
python setup.py
```

This will:
- Check dependencies
- Verify Redis connection
- Initialize the database
- Provide startup instructions

## Step 5: Start the Application

```bash
python main.py
```

The API will be available at: http://localhost:8000

## Step 6: Test the System

### Option 1: Run the Demo
```bash
python demo.py
```

### Option 2: Run the Test Suite
```bash
python test_cache.py
```

### Option 3: Manual Testing

1. **Create sample data:**
   ```bash
   curl -X POST "http://localhost:8000/demo/sample-data"
   ```

2. **Test cache performance:**
   ```bash
   # First request (cache miss)
   curl "http://localhost:8000/restaurants/1"
   
   # Second request (cache hit)
   curl "http://localhost:8000/restaurants/1"
   ```

3. **View cache statistics:**
   ```bash
   curl "http://localhost:8000/cache/stats"
   ```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Features to Test

### 1. Cache Performance
- First request shows "CACHE MISS"
- Subsequent requests show "CACHE HIT" with <10ms response time
- Check application logs for performance metrics

### 2. Cache Invalidation
- Update a restaurant: `PUT /restaurants/{id}`
- Cache is automatically cleared
- Next request will be slower (cache miss)

### 3. Cache Management
- View stats: `GET /cache/stats`
- Clear all cache: `DELETE /cache/clear`
- Clear restaurant cache: `DELETE /cache/clear/restaurants`

### 4. Search Caching
- Search by cuisine: `GET /restaurants/search?cuisine=Italian`
- Results are cached for 180 seconds

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Check Redis configuration
redis-cli config get bind
redis-cli config get port
```

### Application Issues
```bash
# Check if all dependencies are installed
pip list | grep -E "(fastapi|redis|uvicorn)"

# Check application logs for errors
python main.py
```

### Database Issues
```bash
# Reinitialize database
python setup.py
```

## Performance Expectations

- **Cache Miss**: 50-200ms (database query)
- **Cache Hit**: <10ms (Redis lookup)
- **Performance Improvement**: 80-95% faster on cached requests

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Run the demo**: `python demo.py`
3. **Run tests**: `python test_cache.py`
4. **Monitor performance**: Check application logs
5. **Customize**: Modify cache TTL settings in `cache_config.py`

## Support

If you encounter issues:
1. Check the application logs for error messages
2. Verify Redis is running: `redis-cli ping`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Reinitialize the database: `python setup.py`

Happy caching! 🚀 