# Restaurant-Menu System with Advanced Caching - Version 2.0

A sophisticated restaurant management system with advanced Redis caching strategies, multi-level caching, hierarchical invalidation, and business logic caching for optimal performance.

## Features

### Core Features
- Complete CRUD operations for restaurants and menu items
- Restaurant-menu relationships with proper foreign keys
- Advanced search and filtering capabilities
- Comprehensive analytics and business intelligence
- Input validation and error handling
- Proper API documentation with FastAPI

### Advanced Caching Features
- **Multi-Level Caching Strategy**: Different TTLs for different data types
- **Namespace Organization**: Organized caching with namespace-based structure
- **Hierarchical Cache Invalidation**: Smart invalidation based on data relationships
- **Business Logic Caching**: Cache calculated fields and expensive aggregations
- **Cache Warming**: Pre-populate cache with frequently accessed data
- **Performance Monitoring**: Comprehensive cache hit/miss tracking and memory usage

### Caching Strategy

#### Multi-Level TTL Configuration
- **Restaurant Data**: 10-minute cache (600 seconds)
- **Menu Items**: 8-minute cache (480 seconds) - more dynamic
- **Restaurant-with-Menu**: 15-minute cache (900 seconds) - expensive joins
- **Search Results**: 5-minute cache (300 seconds) - frequently changing
- **Analytics**: 30-minute cache (1800 seconds) - business intelligence

#### Category-Specific Caching
- **Vegetarian/Vegan**: 4-minute cache (240 seconds) - more dynamic
- **Popular Items**: 10-minute cache (600 seconds)
- **Expensive Items**: 15-minute cache (900 seconds)
- **Budget Items**: 5-minute cache (300 seconds)

#### Namespace Organization
- `restaurants` - Basic restaurant data
- `menu-items` - Individual menu items
- `restaurant-menus` - Complete restaurant-menu combinations
- `search-results` - Search and filter results
- `analytics` - Business intelligence and analytics

### Hierarchical Cache Invalidation

#### When Restaurant is Updated
```python
await FastAPICache.clear(namespace="restaurants", key=f"restaurant:{restaurant_id}")
await FastAPICache.clear(namespace="restaurant-menus", key=f"restaurant:{restaurant_id}")
```

#### When Menu Item is Updated
```python
await FastAPICache.clear(namespace="menu-items", key=f"item:{item_id}")
await FastAPICache.clear(namespace="restaurant-menus", key=f"restaurant:{restaurant_id}")
await FastAPICache.clear(namespace="search-results")  # Clear all searches
```

## Data Models

### Restaurant Model
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

### MenuItem Model
- `id` (Primary Key)
- `name` (Required, 3-100 characters)
- `description` (Optional text)
- `price` (Decimal, 2 decimal places)
- `category` (Required, e.g., "Pizza", "Sushi", "Tacos")
- `is_vegetarian` (Boolean, default False)
- `is_vegan` (Boolean, default False)
- `is_available` (Boolean, default True)
- `preparation_time` (Integer, minutes)
- `restaurant_id` (Foreign Key to Restaurant)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

## API Endpoints

### Restaurant Management
- `POST /restaurants/` - Create new restaurant
- `GET /restaurants/` - List all restaurants (cached, 10-min TTL)
- `GET /restaurants/{restaurant_id}` - Get specific restaurant (cached, 10-min TTL)
- `GET /restaurants/{restaurant_id}/with-menu` - Get restaurant with menu (cached, 15-min TTL)
- `PUT /restaurants/{restaurant_id}` - Update restaurant
- `DELETE /restaurants/{restaurant_id}` - Delete restaurant
- `GET /restaurants/search` - Search by cuisine (cached, 5-min TTL)
- `GET /restaurants/active` - List active restaurants (cached, 10-min TTL)

### Menu Item Management
- `POST /restaurants/{restaurant_id}/menu-items/` - Add menu item to restaurant
- `GET /menu-items/` - List all menu items (cached, 8-min TTL)
- `GET /menu-items/{item_id}` - Get specific menu item (cached, 8-min TTL)
- `GET /menu-items/{item_id}/with-restaurant` - Get menu item with restaurant (cached, 8-min TTL)
- `GET /restaurants/{restaurant_id}/menu` - Get restaurant menu (cached, 15-min TTL)
- `PUT /menu-items/{item_id}` - Update menu item
- `DELETE /menu-items/{item_id}` - Delete menu item

### Search and Filtering
- `GET /menu-items/search` - Advanced search with filters (cached, 5-min TTL)
- `GET /menu-items/category/{category}` - Get by category (cached, 10-min TTL)
- `GET /menu-items/vegetarian` - Get vegetarian items (cached, 4-min TTL)
- `GET /menu-items/vegan` - Get vegan items (cached, 4-min TTL)
- `GET /menu-items/available` - Get available items (cached, 8-min TTL)

### Analytics and Business Intelligence
- `GET /analytics/average-menu-prices` - Average prices per restaurant (cached, 30-min TTL)
- `GET /analytics/restaurants-with-stats` - Restaurants with menu statistics (cached, 30-min TTL)
- `GET /analytics/popular-cuisines` - Popular cuisines with counts (cached, 30-min TTL)
- `GET /analytics/price-range` - Price range analytics (cached, 30-min TTL)
- `GET /analytics/dietary-preferences` - Dietary preference statistics (cached, 30-min TTL)

### Advanced Cache Management
- `GET /cache/stats/detailed` - Detailed cache statistics by namespace
- `GET /cache/performance` - Cache performance metrics
- `DELETE /cache/clear` - Clear entire cache
- `DELETE /cache/clear/menu-items` - Clear menu-related caches
- `DELETE /cache/clear/search` - Clear search result caches
- `POST /cache/reset-stats` - Reset cache statistics

### Demo and Performance Testing
- `GET /demo/performance-comparison` - Compare cached vs non-cached performance
- `POST /demo/sample-data` - Create sample restaurants and menu items

## Performance Requirements

### Cache Performance
- **First Request**: Shows "CACHE MISS" behavior
- **Subsequent Requests**: Shows "CACHE HIT" with <10ms response time
- **Cache Hit Ratio**: Target >80% for optimal performance
- **Memory Usage**: Monitor cache memory consumption

### Business Logic Caching
- **Calculated Fields**: Cache average ratings, total menu items
- **Expensive Aggregations**: Cache popular cuisines, price ranges
- **Smart Refresh**: Automatic refresh for frequently accessed data

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

```bash
python setup.py
```

### 5. Start the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Testing the Advanced Caching System

### 1. Create Sample Data

```bash
curl -X POST "http://localhost:8000/demo/sample-data"
```

### 2. Test Multi-Level Caching

```bash
# Test restaurant caching (10-min TTL)
curl "http://localhost:8000/restaurants/1"

# Test menu item caching (8-min TTL)
curl "http://localhost:8000/menu-items/1"

# Test restaurant-menu caching (15-min TTL)
curl "http://localhost:8000/restaurants/1/with-menu"

# Test search caching (5-min TTL)
curl "http://localhost:8000/menu-items/search?category=Pizza"
```

### 3. Test Category-Specific Caching

```bash
# Test vegetarian caching (4-min TTL)
curl "http://localhost:8000/menu-items/vegetarian"

# Test vegan caching (4-min TTL)
curl "http://localhost:8000/menu-items/vegan"

# Test popular items caching (10-min TTL)
curl "http://localhost:8000/menu-items/category/Pizza"
```

### 4. Test Analytics Caching

```bash
# Test analytics caching (30-min TTL)
curl "http://localhost:8000/analytics/popular-cuisines"
curl "http://localhost:8000/analytics/price-range"
curl "http://localhost:8000/analytics/dietary-preferences"
```

### 5. Test Hierarchical Invalidation

```bash
# Update a restaurant (clears restaurant and restaurant-menu caches)
curl -X PUT "http://localhost:8000/restaurants/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Restaurant Name"}'

# Update a menu item (clears menu-item, restaurant-menu, and search caches)
curl -X PUT "http://localhost:8000/menu-items/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Menu Item"}'
```

### 6. View Cache Statistics

```bash
# Detailed cache statistics
curl "http://localhost:8000/cache/stats/detailed"

# Performance metrics
curl "http://localhost:8000/cache/performance"

# Performance comparison
curl "http://localhost:8000/demo/performance-comparison"
```

## Cache Configuration

### TTL Settings
```python
CACHE_TTL = {
    "restaurants": 600,        # 10 minutes
    "menu_items": 480,         # 8 minutes
    "restaurant_menus": 900,   # 15 minutes
    "search_results": 300,     # 5 minutes
    "analytics": 1800,         # 30 minutes
    "vegetarian": 240,         # 4 minutes
    "vegan": 240,              # 4 minutes
    "popular": 600,            # 10 minutes
    "expensive": 900,          # 15 minutes
    "budget": 300              # 5 minutes
}
```

### Namespace Organization
- **restaurants**: Basic restaurant data
- **menu-items**: Individual menu items
- **restaurant-menus**: Complete restaurant-menu combinations
- **search-results**: Search and filter results
- **analytics**: Business intelligence and analytics

## Performance Monitoring

### Cache Hit/Miss Tracking
- Real-time cache hit/miss ratio monitoring
- Namespace-specific performance tracking
- Memory usage monitoring with psutil
- Response time logging for all endpoints

### Business Logic Caching
- **Calculated Fields**: Average ratings, total menu items
- **Expensive Aggregations**: Popular cuisines, price ranges
- **Smart Refresh**: Automatic refresh for frequently accessed data

### Cache Warming
- Pre-populate cache with frequently accessed data
- Warm restaurant and menu item caches on startup
- Warm analytics data for business intelligence

## Advanced Features

### Hierarchical Invalidation Logic
- **Restaurant Updates**: Clear restaurant and restaurant-menu caches
- **Menu Item Updates**: Clear menu-item, restaurant-menu, and search caches
- **Analytics Updates**: Clear analytics cache on data changes

### Category-Specific Caching
- **Vegetarian/Vegan**: Shorter TTL for dynamic dietary preferences
- **Popular Items**: Longer TTL for frequently accessed categories
- **Expensive Items**: Extended TTL for high-value items
- **Budget Items**: Shorter TTL for frequently changing budget options

### Business Intelligence Caching
- **Popular Cuisines**: Cache restaurant counts and average ratings
- **Price Range Analytics**: Cache min, max, and average prices
- **Dietary Preferences**: Cache vegetarian, vegan, and available item counts

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Redis Cache   │    │   SQLite DB     │
│                 │    │                 │    │                 │
│  - Multi-Level  │◄──►│  - Namespaces   │    │  - Data Store   │
│    Caching      │    │  - TTL Mgmt     │    │  - Persistence  │
│  - Hierarchical │    │  - Invalidation │    │  - ACID         │
│    Invalidation │    │  - Performance  │    │  - Relations    │
│  - Business     │    │    Monitoring   │    │                 │
│    Logic Cache  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Dependencies

- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `sqlalchemy==2.0.23` - ORM
- `aiosqlite==0.19.0` - Async SQLite
- `pydantic==2.5.0` - Data validation
- `redis==5.0.1` - Redis client
- `fastapi-cache2==0.2.1` - FastAPI caching
- `psutil==5.9.6` - System and process utilities

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Check Redis configuration
redis-cli config get bind
redis-cli config get port
```

### Cache Performance Issues
1. Monitor cache hit rates via `/cache/performance`
2. Check response time logs in application output
3. Verify TTL settings in `cache_config.py`
4. Monitor memory usage via `/cache/stats/detailed`

### Database Issues
```bash
# Reinitialize database
python setup.py
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Performance Expectations

- **Cache Miss**: 50-200ms (database query)
- **Cache Hit**: <10ms (Redis lookup)
- **Performance Improvement**: 80-95% faster on cached requests
- **Cache Hit Ratio**: Target >80% for optimal performance
- **Memory Usage**: Monitor via `/cache/stats/detailed`

## Future Enhancements

- **Cache Compression**: Implement cache compression for large datasets
- **Cache Analytics Dashboard**: Real-time cache performance visualization
- **Multi-Node Support**: Redis cluster support for scalability
- **Advanced Warming**: Predictive cache warming based on usage patterns
- **Health Checks**: Redis health monitoring endpoints

## License

This project demonstrates advanced caching strategies in FastAPI applications with restaurant-menu management systems. 