import asyncio
from datetime import time
from decimal import Decimal
from database import create_tables, AsyncSessionLocal
from models import Restaurant, MenuItem

async def init_database():
    """Initialize database with sample data"""
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
            "opening_time": time(11, 0),
            "closing_time": time(22, 0)
        },
        {
            "name": "Pizza Palace",
            "description": "Traditional Italian pizzas and pasta",
            "cuisine_type": "Italian",
            "address": "456 Oak Avenue, Midtown",
            "phone_number": "+1-555-0456",
            "rating": 4.2,
            "is_active": True,
            "opening_time": time(10, 30),
            "closing_time": time(23, 0)
        },
        {
            "name": "Sushi Express",
            "description": "Fresh sushi and Japanese cuisine",
            "cuisine_type": "Japanese",
            "address": "789 Pine Street, Uptown",
            "phone_number": "+1-555-0789",
            "rating": 4.7,
            "is_active": True,
            "opening_time": time(12, 0),
            "closing_time": time(21, 30)
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
        
        # Create sample menu items
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
            }
        ]
        
        # Create menu items
        for data in menu_items_data:
            menu_item = MenuItem(**data)
            session.add(menu_item)
        
        await session.commit()
        
        print("Database initialized successfully!")
        print(f"Created {len(restaurants)} restaurants and {len(menu_items_data)} menu items")

if __name__ == "__main__":
    asyncio.run(init_database()) 