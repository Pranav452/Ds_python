# Complete Food Delivery System - Version 3.0

A comprehensive food delivery ecosystem with customers, orders, delivery tracking, and reviews. This system implements complex multi-table relationships including many-to-many associations and multiple foreign key relationships.

## 🚀 Features

### Core Features
- **Restaurant Management**: Full CRUD operations with menu management
- **Customer Management**: Customer profiles with order history
- **Order Management**: Complex order workflow with status tracking
- **Review System**: Customer reviews with rating calculations
- **Analytics**: Business intelligence and performance metrics
- **Advanced Search**: Multi-criteria search and filtering

### Advanced Features
- **Complex Relationships**: One-to-many and many-to-many with association objects
- **Business Logic**: Order status workflow, review validation, price calculations
- **Data Validation**: Comprehensive input validation with Pydantic
- **Error Handling**: Proper HTTP status codes and error messages
- **Performance**: Efficient database queries with proper indexing

## 📋 Requirements

### New Models Added

#### Customer Model
- `id` (Primary Key)
- `name` (Required, 2-100 characters)
- `email` (Required, unique, validated format)
- `phone_number` (Required, validated format)
- `address` (Required, 10-500 characters)
- `is_active` (Boolean, default True)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

#### Order Model
- `id` (Primary Key)
- `customer_id` (Foreign Key to Customer)
- `restaurant_id` (Foreign Key to Restaurant)
- `order_status` (Enum: placed, confirmed, preparing, out_for_delivery, delivered, cancelled)
- `total_amount` (Decimal, calculated from order items)
- `delivery_address` (Required, 10-500 characters)
- `special_instructions` (Optional)
- `order_date` (Timestamp)
- `delivery_time` (Optional timestamp)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

#### Order Item Model (Association Object)
- `id` (Primary Key)
- `order_id` (Foreign Key to Order)
- `menu_item_id` (Foreign Key to Menu Item)
- `quantity` (Required, positive integer)
- `item_price` (Decimal, price at time of order)
- `special_requests` (Optional)
- `created_at` (Timestamp)

#### Review Model
- `id` (Primary Key)
- `customer_id` (Foreign Key to Customer)
- `restaurant_id` (Foreign Key to Restaurant)
- `order_id` (Foreign Key to Order, unique)
- `rating` (Integer, 1-5 stars)
- `comment` (Optional, max 1000 characters)
- `created_at` (Timestamp)

## 🔗 Complex Relationships

### One-to-Many Relationships
- **Customer → Orders**: One customer can have many orders
- **Restaurant → Orders**: One restaurant can have many orders
- **Customer → Reviews**: One customer can have many reviews
- **Restaurant → Reviews**: One restaurant can have many reviews

### Many-to-Many Relationships
- **Order ↔ Menu Items**: Many-to-many with association object (OrderItem)
  - Additional data: quantity, item_price, special_requests

### Cascade Operations
- Delete restaurant → Delete all menu items, orders, and reviews
- Delete customer → Delete all orders and reviews
- Delete order → Delete all order items and review

## 🛠️ API Endpoints

### Restaurant Management
```
POST   /restaurants/                    # Create restaurant
GET    /restaurants/                    # List restaurants
GET    /restaurants/{id}                # Get restaurant
GET    /restaurants/{id}/with-menu      # Get restaurant with menu
PUT    /restaurants/{id}                # Update restaurant
DELETE /restaurants/{id}                # Delete restaurant
GET    /restaurants/search              # Search restaurants
GET    /restaurants/{id}/analytics      # Restaurant analytics
```

### Menu Item Management
```
POST   /menu-items/                     # Create menu item
GET    /menu-items/                     # List menu items
GET    /menu-items/{id}                 # Get menu item
PUT    /menu-items/{id}                 # Update menu item
DELETE /menu-items/{id}                 # Delete menu item
GET    /menu-items/restaurant/{id}      # Get restaurant menu
```

### Customer Management
```
POST   /customers/                      # Create customer
GET    /customers/                      # List customers
GET    /customers/{id}                  # Get customer
GET    /customers/{id}/with-orders      # Get customer with orders
PUT    /customers/{id}                  # Update customer
DELETE /customers/{id}                  # Delete customer
GET    /customers/{id}/analytics        # Customer analytics
```

### Order Management
```
POST   /orders/customers/{id}/orders/   # Place new order
GET    /orders/                         # List orders
GET    /orders/{id}                     # Get order
GET    /orders/{id}/with-details        # Get order with details
PUT    /orders/{id}/status              # Update order status
PUT    /orders/{id}                     # Update order
DELETE /orders/{id}                     # Delete order
GET    /orders/customers/{id}/orders    # Customer orders
GET    /orders/restaurants/{id}/orders  # Restaurant orders
```

### Review System
```
POST   /reviews/orders/{id}/review      # Add review after order
GET    /reviews/                        # List reviews
GET    /reviews/{id}                    # Get review
DELETE /reviews/{id}                    # Delete review
GET    /reviews/restaurants/{id}/reviews # Restaurant reviews
GET    /reviews/customers/{id}/reviews  # Customer reviews
```

### Search and Analytics
```
GET    /search/restaurants              # Search restaurants
GET    /search/orders                   # Search orders
GET    /restaurants/{id}/analytics      # Restaurant analytics
GET    /customers/{id}/analytics        # Customer analytics
```

## 🏗️ Business Logic

### Order Status Workflow
1. **placed** → Order is created
2. **confirmed** → Restaurant confirms order
3. **preparing** → Food is being prepared
4. **out_for_delivery** → Order is being delivered
5. **delivered** → Order completed
6. **cancelled** → Order cancelled (can happen from any status except delivered)

### Review Validation
- Reviews can only be added for **delivered** orders
- One review per order (unique constraint)
- Rating must be 1-5 stars
- Restaurant rating is automatically recalculated

### Order Total Calculation
- Calculated from menu item prices × quantities
- Validates menu item availability
- Stores item prices at time of order

### Analytics Features
- **Restaurant Analytics**: Total orders, revenue, average order value, reviews, popular items
- **Customer Analytics**: Total orders, spending, average order value, favorite restaurants, order history

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

### 3. Start Server
```bash
python main.py
```

### 4. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. Run Tests
```bash
python test_api.py
```

## 📊 Sample Data

The system comes with comprehensive sample data including:

### Restaurants (5)
- Spice Garden (Indian)
- Pizza Palace (Italian)
- Sushi Express (Japanese)
- Burger Joint (American)
- Thai Delight (Thai)

### Customers (5)
- John Smith, Sarah Johnson, Mike Davis, Emily Wilson, David Brown

### Menu Items (18)
- Various items across different categories (Appetizer, Main Course, Dessert, Side)
- Vegetarian and vegan options
- Different price points and preparation times

### Orders (5)
- Different statuses (delivered, out_for_delivery, preparing, confirmed)
- Various order items and special requests

### Reviews (2)
- Sample reviews for delivered orders

## 🔧 Technical Implementation

### Database Design
- **SQLite** with SQLAlchemy ORM
- **Async/await** for non-blocking operations
- **Proper indexing** for performance
- **Cascade deletes** for data integrity

### API Design
- **FastAPI** with automatic OpenAPI documentation
- **Pydantic** for data validation and serialization
- **CORS middleware** for cross-origin requests
- **Comprehensive error handling**

### Business Logic
- **Modular design** with separate business logic classes
- **Validation layers** for complex business rules
- **Analytics functions** for business intelligence
- **Search and filtering** with multiple criteria

### Code Organization
```
Complete Food Delivery System/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py             # Database operations
├── utils/
│   └── business_logic.py # Business logic
├── routes/
│   ├── restaurants.py   # Restaurant endpoints
│   ├── menu_items.py    # Menu item endpoints
│   ├── customers.py     # Customer endpoints
│   ├── orders.py        # Order endpoints
│   └── reviews.py       # Review endpoints
├── init_db.py          # Database initialization
├── test_api.py         # API testing
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

## 🎯 Key Features Demonstrated

### Complex Relationships
- **One-to-Many**: Customer → Orders, Restaurant → Orders
- **Many-to-Many**: Order ↔ Menu Items (with association object)
- **Cascade Operations**: Automatic cleanup of related data

### Advanced Querying
- **Joins across multiple tables**
- **Aggregation functions** (SUM, AVG, COUNT)
- **Complex filtering** with multiple criteria
- **Efficient relationship loading** with selectinload

### Business Logic
- **Order status workflow** with validation
- **Review system** with business rules
- **Price calculations** and validation
- **Analytics and reporting**

### Data Validation
- **Comprehensive input validation** with Pydantic
- **Business rule validation** (e.g., review timing)
- **Data integrity** with foreign key constraints
- **Error handling** with proper HTTP status codes

## 🔍 API Examples

### Create a Restaurant
```bash
curl -X POST "http://localhost:8000/restaurants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Restaurant",
    "description": "A great new restaurant",
    "cuisine_type": "International",
    "address": "123 New Street, City",
    "phone_number": "+1-555-0123",
    "rating": 4.5,
    "is_active": true,
    "opening_time": "10:00",
    "closing_time": "22:00"
  }'
```

### Place an Order
```bash
curl -X POST "http://localhost:8000/orders/customers/1/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "delivery_address": "100 Customer Street, City",
    "special_instructions": "Please deliver to front door",
    "order_items": [
      {
        "menu_item_id": 1,
        "quantity": 2,
        "special_requests": "Extra spicy"
      }
    ]
  }'
```

### Update Order Status
```bash
curl -X PUT "http://localhost:8000/orders/1/status?new_status=confirmed"
```

### Add a Review
```bash
curl -X POST "http://localhost:8000/reviews/orders/1/review" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent service and delicious food!"
  }'
```

### Get Restaurant Analytics
```bash
curl -X GET "http://localhost:8000/restaurants/1/analytics"
```

## 🚀 Future Enhancements

- **Payment Integration**: Stripe/PayPal integration
- **Real-time Updates**: WebSocket for order status updates
- **Push Notifications**: Order status notifications
- **Advanced Analytics**: Machine learning for recommendations
- **Mobile App**: React Native mobile application
- **Admin Dashboard**: React admin interface
- **Multi-language Support**: Internationalization
- **Advanced Search**: Elasticsearch integration
- **Caching**: Redis for performance optimization
- **Microservices**: Service decomposition

## 📝 License

This project is for educational purposes and demonstrates advanced backend engineering concepts with FastAPI, SQLAlchemy, and complex database relationships.

---

**Complete Food Delivery System v3.0** - A comprehensive food delivery ecosystem with complex multi-table relationships, business logic, and advanced features. 