import asyncio
from datetime import time, datetime
from decimal import Decimal
from database import create_tables, AsyncSessionLocal
from models import Restaurant, MenuItem, Customer, Order, OrderItem, Review, OrderStatus

async def init_database():
    """Initialize database with comprehensive sample data"""
    # Create tables
    await create_tables()
    
    # Create sample restaurants
    restaurants_data = [
        {
            "name": "Spice Garden",
            "description": "Authentic Indian cuisine with modern twists",
            "cuisine_type": "Indian",
            "address": "123 Main Street, Downtown",
            "phone_number": "+1-555-0123",
            "rating": 4.5,
            "is_active": True,
            "opening_time": "11:00",
            "closing_time": "22:00"
        },
        {
            "name": "Pizza Palace",
            "description": "Traditional Italian pizzas and pasta",
            "cuisine_type": "Italian",
            "address": "456 Oak Avenue, Midtown",
            "phone_number": "+1-555-0456",
            "rating": 4.2,
            "is_active": True,
            "opening_time": "10:30",
            "closing_time": "23:00"
        },
        {
            "name": "Sushi Express",
            "description": "Fresh sushi and Japanese cuisine",
            "cuisine_type": "Japanese",
            "address": "789 Pine Street, Uptown",
            "phone_number": "+1-555-0789",
            "rating": 4.7,
            "is_active": True,
            "opening_time": "12:00",
            "closing_time": "21:30"
        },
        {
            "name": "Burger Joint",
            "description": "Classic American burgers and fries",
            "cuisine_type": "American",
            "address": "321 Elm Street, Downtown",
            "phone_number": "+1-555-0321",
            "rating": 4.0,
            "is_active": True,
            "opening_time": "11:00",
            "closing_time": "22:00"
        },
        {
            "name": "Thai Delight",
            "description": "Authentic Thai cuisine with spicy flavors",
            "cuisine_type": "Thai",
            "address": "654 Maple Drive, Midtown",
            "phone_number": "+1-555-0654",
            "rating": 4.3,
            "is_active": True,
            "opening_time": "11:30",
            "closing_time": "21:00"
        }
    ]
    
    # Create sample customers
    customers_data = [
        {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone_number": "+1-555-0101",
            "address": "100 Customer Street, Downtown, City, State 12345",
            "is_active": True
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@email.com",
            "phone_number": "+1-555-0102",
            "address": "200 Customer Avenue, Midtown, City, State 12345",
            "is_active": True
        },
        {
            "name": "Mike Davis",
            "email": "mike.davis@email.com",
            "phone_number": "+1-555-0103",
            "address": "300 Customer Road, Uptown, City, State 12345",
            "is_active": True
        },
        {
            "name": "Emily Wilson",
            "email": "emily.wilson@email.com",
            "phone_number": "+1-555-0104",
            "address": "400 Customer Lane, Downtown, City, State 12345",
            "is_active": True
        },
        {
            "name": "David Brown",
            "email": "david.brown@email.com",
            "phone_number": "+1-555-0105",
            "address": "500 Customer Way, Midtown, City, State 12345",
            "is_active": True
        }
    ]
    
    async with AsyncSessionLocal() as session:
        # Create restaurants
        restaurants = []
        for data in restaurants_data:
            restaurant = Restaurant(**data)
            session.add(restaurant)
            restaurants.append(restaurant)
        
        await session.commit()
        
        # Refresh to get IDs
        for restaurant in restaurants:
            await session.refresh(restaurant)
        
        # Create customers
        customers = []
        for data in customers_data:
            customer = Customer(**data)
            session.add(customer)
            customers.append(customer)
        
        await session.commit()
        
        # Refresh to get IDs
        for customer in customers:
            await session.refresh(customer)
        
        # Create menu items for each restaurant
        menu_items_data = [
            # Spice Garden menu items
            {
                "name": "Butter Chicken",
                "description": "Creamy tomato-based curry with tender chicken",
                "price": Decimal("18.99"),
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 20,
                "restaurant_id": restaurants[0].id
            },
            {
                "name": "Paneer Tikka",
                "description": "Grilled cottage cheese with Indian spices",
                "price": Decimal("16.99"),
                "category": "Appetizer",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 15,
                "restaurant_id": restaurants[0].id
            },
            {
                "name": "Dal Makhani",
                "description": "Creamy black lentils cooked overnight",
                "price": Decimal("12.99"),
                "category": "Main Course",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 25,
                "restaurant_id": restaurants[0].id
            },
            {
                "name": "Gulab Jamun",
                "description": "Sweet milk dumplings in rose syrup",
                "price": Decimal("6.99"),
                "category": "Dessert",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 10,
                "restaurant_id": restaurants[0].id
            },
            
            # Pizza Palace menu items
            {
                "name": "Margherita Pizza",
                "description": "Classic tomato sauce with mozzarella and basil",
                "price": Decimal("14.99"),
                "category": "Main Course",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 18,
                "restaurant_id": restaurants[1].id
            },
            {
                "name": "Pepperoni Pizza",
                "description": "Spicy pepperoni with melted cheese",
                "price": Decimal("17.99"),
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 20,
                "restaurant_id": restaurants[1].id
            },
            {
                "name": "Garlic Bread",
                "description": "Crispy bread with garlic butter and herbs",
                "price": Decimal("5.99"),
                "category": "Appetizer",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 8,
                "restaurant_id": restaurants[1].id
            },
            {
                "name": "Tiramisu",
                "description": "Classic Italian dessert with coffee and mascarpone",
                "price": Decimal("8.99"),
                "category": "Dessert",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 5,
                "restaurant_id": restaurants[1].id
            },
            
            # Sushi Express menu items
            {
                "name": "California Roll",
                "description": "Crab, avocado, and cucumber roll",
                "price": Decimal("12.99"),
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 12,
                "restaurant_id": restaurants[2].id
            },
            {
                "name": "Avocado Roll",
                "description": "Fresh avocado roll with rice and nori",
                "price": Decimal("9.99"),
                "category": "Main Course",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 10,
                "restaurant_id": restaurants[2].id
            },
            {
                "name": "Miso Soup",
                "description": "Traditional Japanese soup with tofu and seaweed",
                "price": Decimal("4.99"),
                "category": "Appetizer",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 5,
                "restaurant_id": restaurants[2].id
            },
            {
                "name": "Green Tea Ice Cream",
                "description": "Smooth green tea flavored ice cream",
                "price": Decimal("6.99"),
                "category": "Dessert",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 3,
                "restaurant_id": restaurants[2].id
            },
            
            # Burger Joint menu items
            {
                "name": "Classic Burger",
                "description": "Juicy beef burger with fresh vegetables",
                "price": Decimal("15.99"),
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 15,
                "restaurant_id": restaurants[3].id
            },
            {
                "name": "Veggie Burger",
                "description": "Plant-based burger with fresh vegetables",
                "price": Decimal("13.99"),
                "category": "Main Course",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 12,
                "restaurant_id": restaurants[3].id
            },
            {
                "name": "French Fries",
                "description": "Crispy golden fries with sea salt",
                "price": Decimal("4.99"),
                "category": "Side",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 8,
                "restaurant_id": restaurants[3].id
            },
            
            # Thai Delight menu items
            {
                "name": "Pad Thai",
                "description": "Stir-fried rice noodles with shrimp and vegetables",
                "price": Decimal("16.99"),
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 18,
                "restaurant_id": restaurants[4].id
            },
            {
                "name": "Green Curry",
                "description": "Spicy green curry with coconut milk",
                "price": Decimal("17.99"),
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 20,
                "restaurant_id": restaurants[4].id
            },
            {
                "name": "Spring Rolls",
                "description": "Fresh vegetables wrapped in rice paper",
                "price": Decimal("8.99"),
                "category": "Appetizer",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 10,
                "restaurant_id": restaurants[4].id
            }
        ]
        
        # Create menu items
        menu_items = []
        for data in menu_items_data:
            menu_item = MenuItem(**data)
            session.add(menu_item)
            menu_items.append(menu_item)
        
        await session.commit()
        
        # Refresh to get IDs
        for menu_item in menu_items:
            await session.refresh(menu_item)
        
        # Create sample orders
        orders_data = [
            {
                "customer_id": customers[0].id,
                "restaurant_id": restaurants[0].id,
                "order_status": OrderStatus.DELIVERED,
                "total_amount": Decimal("25.98"),
                "delivery_address": "100 Customer Street, Downtown, City, State 12345",
                "special_instructions": "Please deliver to the front door",
                "order_date": datetime.now(),
                "delivery_time": datetime.now()
            },
            {
                "customer_id": customers[1].id,
                "restaurant_id": restaurants[1].id,
                "order_status": OrderStatus.DELIVERED,
                "total_amount": Decimal("22.98"),
                "delivery_address": "200 Customer Avenue, Midtown, City, State 12345",
                "special_instructions": "Extra cheese please",
                "order_date": datetime.now(),
                "delivery_time": datetime.now()
            },
            {
                "customer_id": customers[2].id,
                "restaurant_id": restaurants[2].id,
                "order_status": OrderStatus.OUT_FOR_DELIVERY,
                "total_amount": Decimal("18.98"),
                "delivery_address": "300 Customer Road, Uptown, City, State 12345",
                "special_instructions": "Please include extra soy sauce",
                "order_date": datetime.now(),
                "delivery_time": None
            },
            {
                "customer_id": customers[3].id,
                "restaurant_id": restaurants[3].id,
                "order_status": OrderStatus.PREPARING,
                "total_amount": Decimal("20.98"),
                "delivery_address": "400 Customer Lane, Downtown, City, State 12345",
                "special_instructions": "Well done burger please",
                "order_date": datetime.now(),
                "delivery_time": None
            },
            {
                "customer_id": customers[4].id,
                "restaurant_id": restaurants[4].id,
                "order_status": OrderStatus.CONFIRMED,
                "total_amount": Decimal("26.98"),
                "delivery_address": "500 Customer Way, Midtown, City, State 12345",
                "special_instructions": "Extra spicy please",
                "order_date": datetime.now(),
                "delivery_time": None
            }
        ]
        
        # Create orders
        orders = []
        for data in orders_data:
            order = Order(**data)
            session.add(order)
            orders.append(order)
        
        await session.commit()
        
        # Refresh to get IDs
        for order in orders:
            await session.refresh(order)
        
        # Create order items
        order_items_data = [
            # Order 1 - Spice Garden
            {
                "order_id": orders[0].id,
                "menu_item_id": menu_items[0].id,  # Butter Chicken
                "quantity": 1,
                "item_price": Decimal("18.99"),
                "special_requests": "Extra spicy"
            },
            {
                "order_id": orders[0].id,
                "menu_item_id": menu_items[3].id,  # Gulab Jamun
                "quantity": 1,
                "item_price": Decimal("6.99"),
                "special_requests": None
            },
            
            # Order 2 - Pizza Palace
            {
                "order_id": orders[1].id,
                "menu_item_id": menu_items[4].id,  # Margherita Pizza
                "quantity": 1,
                "item_price": Decimal("14.99"),
                "special_requests": "Extra cheese"
            },
            {
                "order_id": orders[1].id,
                "menu_item_id": menu_items[6].id,  # Garlic Bread
                "quantity": 1,
                "item_price": Decimal("5.99"),
                "special_requests": "Extra garlic"
            },
            {
                "order_id": orders[1].id,
                "menu_item_id": menu_items[7].id,  # Tiramisu
                "quantity": 1,
                "item_price": Decimal("8.99"),
                "special_requests": None
            },
            
            # Order 3 - Sushi Express
            {
                "order_id": orders[2].id,
                "menu_item_id": menu_items[8].id,  # California Roll
                "quantity": 1,
                "item_price": Decimal("12.99"),
                "special_requests": "Extra soy sauce"
            },
            {
                "order_id": orders[2].id,
                "menu_item_id": menu_items[10].id,  # Miso Soup
                "quantity": 1,
                "item_price": Decimal("4.99"),
                "special_requests": None
            },
            {
                "order_id": orders[2].id,
                "menu_item_id": menu_items[11].id,  # Green Tea Ice Cream
                "quantity": 1,
                "item_price": Decimal("6.99"),
                "special_requests": None
            },
            
            # Order 4 - Burger Joint
            {
                "order_id": orders[3].id,
                "menu_item_id": menu_items[12].id,  # Classic Burger
                "quantity": 1,
                "item_price": Decimal("15.99"),
                "special_requests": "Well done"
            },
            {
                "order_id": orders[3].id,
                "menu_item_id": menu_items[14].id,  # French Fries
                "quantity": 1,
                "item_price": Decimal("4.99"),
                "special_requests": "Extra crispy"
            },
            
            # Order 5 - Thai Delight
            {
                "order_id": orders[4].id,
                "menu_item_id": menu_items[15].id,  # Pad Thai
                "quantity": 1,
                "item_price": Decimal("16.99"),
                "special_requests": "Extra spicy"
            },
            {
                "order_id": orders[4].id,
                "menu_item_id": menu_items[17].id,  # Spring Rolls
                "quantity": 1,
                "item_price": Decimal("8.99"),
                "special_requests": "Extra peanut sauce"
            }
        ]
        
        # Create order items
        for data in order_items_data:
            order_item = OrderItem(**data)
            session.add(order_item)
        
        await session.commit()
        
        # Create reviews for delivered orders
        reviews_data = [
            {
                "customer_id": customers[0].id,
                "restaurant_id": restaurants[0].id,
                "order_id": orders[0].id,
                "rating": 5,
                "comment": "Excellent food! The butter chicken was amazing and the service was quick."
            },
            {
                "customer_id": customers[1].id,
                "restaurant_id": restaurants[1].id,
                "order_id": orders[1].id,
                "rating": 4,
                "comment": "Great pizza and garlic bread. Delivery was on time."
            }
        ]
        
        # Create reviews
        for data in reviews_data:
            review = Review(**data)
            session.add(review)
        
        await session.commit()
        
        print("Database initialized successfully!")
        print(f"Created {len(restaurants)} restaurants")
        print(f"Created {len(customers)} customers")
        print(f"Created {len(menu_items)} menu items")
        print(f"Created {len(orders)} orders")
        print(f"Created {len(order_items_data)} order items")
        print(f"Created {len(reviews_data)} reviews")

if __name__ == "__main__":
    asyncio.run(init_database()) 