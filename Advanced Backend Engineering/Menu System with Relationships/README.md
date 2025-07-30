# Restaurant-Menu Management System

A comprehensive restaurant management system with menu management and relationships, built with FastAPI, SQLAlchemy, and Pydantic.

## Features

### Core Features
- **Restaurant Management**: Full CRUD operations for restaurants
- **Menu Management**: Complete menu item management with relationships
- **One-to-Many Relationships**: Proper SQLAlchemy relationships between restaurants and menu items
- **Advanced Querying**: Efficient relationship loading with selectinload
- **Cascade Operations**: Automatic deletion of menu items when restaurants are deleted

### Menu Item Features
- **Dietary Preferences**: Support for vegetarian and vegan options
- **Availability Management**: Track item availability
- **Price Management**: Decimal precision for accurate pricing
- **Category Organization**: Organize items by categories (Appetizer, Main Course, Dessert, Beverage)
- **Preparation Time**: Track preparation time in minutes

### Advanced Features
- **Search and Filtering**: Advanced search with multiple criteria
- **Analytics**: Menu price analytics and restaurant statistics
- **Pagination**: Efficient pagination for large datasets
- **Validation**: Comprehensive input validation with Pydantic
- **Error Handling**: Proper error handling and status codes

## API Endpoints

### Restaurant Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/restaurants/` | Create a new restaurant |
| GET | `/restaurants/` | List all restaurants (paginated) |
| GET | `/restaurants/{restaurant_id}` | Get specific restaurant |
| GET | `/restaurants/{restaurant_id}/with-menu` | Get restaurant with all menu items |
| PUT | `/restaurants/{restaurant_id}` | Update restaurant information |
| DELETE | `/restaurants/{restaurant_id}` | Delete restaurant (cascade delete menu items) |
| GET | `/restaurants/search` | Search restaurants by cuisine type |
| GET | `/restaurants/active` | List only active restaurants |

### Menu Item Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/restaurants/{restaurant_id}/menu-items/` | Add menu item to restaurant |
| GET | `/menu-items/` | List all menu items (paginated) |
| GET | `/menu-items/{item_id}` | Get specific menu item |
| GET | `/menu-items/{item_id}/with-restaurant` | Get menu item with restaurant details |
| GET | `/restaurants/{restaurant_id}/menu` | Get all menu items for a restaurant |
| PUT | `/menu-items/{item_id}` | Update menu item |
| DELETE | `/menu-items/{item_id}` | Delete menu item |

### Search and Filter Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/menu-items/search` | Search menu items with filters |
| GET | `/menu-items/category/{category}` | Get menu items by category |
| GET | `/menu-items/vegetarian` | Get all vegetarian menu items |
| GET | `/menu-items/vegan` | Get all vegan menu items |
| GET | `/menu-items/available` | Get all available menu items |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/average-menu-prices` | Get average menu price per restaurant |
| GET | `/analytics/restaurants-with-stats` | Get restaurants with menu statistics |

## Data Models

### Restaurant Model
```python
class Restaurant(Base):
    id: int (Primary Key)
    name: str (Required, 3-100 characters, unique)
    description: str (Optional)
    cuisine_type: str (Required, 2-50 characters)
    address: str (Required, 5-200 characters)
    phone_number: str (Required, validated format)
    rating: float (0.0-5.0, default 0.0)
    is_active: bool (default True)
    opening_time: time (Required)
    closing_time: time (Required)
    created_at: datetime (auto-generated)
    updated_at: datetime (auto-updated)
    menu_items: relationship (One-to-Many with MenuItem)
```

### MenuItem Model
```python
class MenuItem(Base):
    id: int (Primary Key)
    name: str (Required, 3-100 characters)
    description: str (Optional)
    price: Decimal (Required, 2 decimal places, positive)
    category: str (Required, 2-50 characters)
    is_vegetarian: bool (default False)
    is_vegan: bool (default False)
    is_available: bool (default True)
    preparation_time: int (Optional, minutes)
    restaurant_id: int (Foreign Key to Restaurant, cascade delete)
    created_at: datetime (auto-generated)
    updated_at: datetime (auto-updated)
    restaurant: relationship (Many-to-One with Restaurant)
```

## Installation and Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Advanced Backend Engineering/Menu System with Relationships"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python init_db.py
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Documentation: http://localhost:8000/redoc
   - API Base URL: http://localhost:8000

## Usage Examples

### Creating a Restaurant
```bash
curl -X POST "http://localhost:8000/restaurants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spice Garden",
    "description": "Authentic Indian cuisine",
    "cuisine_type": "Indian",
    "address": "123 Main Street",
    "phone_number": "+1-555-0123",
    "rating": 4.5,
    "opening_time": "11:00",
    "closing_time": "22:00"
  }'
```

### Adding a Menu Item
```bash
curl -X POST "http://localhost:8000/restaurants/1/menu-items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Butter Chicken",
    "description": "Creamy tomato-based curry",
    "price": "18.99",
    "category": "Main Course",
    "is_vegetarian": false,
    "is_vegan": false,
    "is_available": true,
    "preparation_time": 20,
    "restaurant_id": 1
  }'
```

### Searching Menu Items
```bash
curl "http://localhost:8000/menu-items/search?vegetarian=true&category=Main%20Course"
```

### Getting Restaurant with Menu
```bash
curl "http://localhost:8000/restaurants/1/with-menu"
```

## Testing

Run the comprehensive test suite:
```bash
python test_api.py
```

This will test all endpoints and demonstrate the system's functionality.

## Key Features Implementation

### 1. SQLAlchemy Relationships
- **One-to-Many**: Restaurant → MenuItem
- **Cascade Delete**: Menu items are automatically deleted when restaurant is deleted
- **Efficient Loading**: Uses `selectinload` for optimal relationship loading

### 2. Pydantic Validation
- **Input Validation**: Comprehensive validation for all inputs
- **Price Validation**: Ensures positive decimal values
- **Phone Number Validation**: Regex-based phone number validation
- **Time Validation**: Ensures closing time is after opening time

### 3. Advanced Querying
- **Filtering**: Multiple filter criteria support
- **Search**: Text-based search with ILIKE
- **Pagination**: Efficient pagination for large datasets
- **Analytics**: Aggregation queries for statistics

### 4. Error Handling
- **HTTP Status Codes**: Proper status codes for all operations
- **Validation Errors**: Detailed validation error messages
- **Not Found Handling**: Proper 404 responses
- **Database Errors**: Graceful handling of database constraints

## Database Schema

The system uses SQLite with the following schema:

### Restaurants Table
- Primary key with auto-increment
- Unique constraint on restaurant name
- Indexes on frequently queried fields

### Menu Items Table
- Primary key with auto-increment
- Foreign key to restaurants with cascade delete
- Indexes on restaurant_id, category, and dietary preferences
- Decimal field for precise price storage

## Performance Considerations

1. **Indexing**: Proper indexes on frequently queried fields
2. **Efficient Loading**: Uses selectinload for relationship loading
3. **Pagination**: Implements pagination to handle large datasets
4. **Async Operations**: All database operations are asynchronous

## Security Features

1. **Input Validation**: Comprehensive validation prevents injection attacks
2. **SQL Injection Protection**: Uses SQLAlchemy ORM with parameterized queries
3. **Data Sanitization**: All inputs are validated and sanitized

## Future Enhancements

1. **Authentication**: JWT-based authentication system
2. **Authorization**: Role-based access control
3. **Image Upload**: Menu item image management
4. **Order Management**: Complete ordering system
5. **Payment Integration**: Payment processing capabilities
6. **Real-time Updates**: WebSocket support for real-time updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. 