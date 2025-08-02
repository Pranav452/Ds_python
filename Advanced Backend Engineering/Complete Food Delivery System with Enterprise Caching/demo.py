import asyncio
import aiohttp
import json
from datetime import datetime
from decimal import Decimal

BASE_URL = "http://localhost:8000"

async def run_demo():
    """Comprehensive demo of the Complete Food Delivery System"""
    
    async with aiohttp.ClientSession() as session:
        print("🍽️ Complete Food Delivery System - Version 3.0 Demo")
        print("=" * 70)
        
        # Check server health
        print("\n1. Checking server health...")
        async with session.get(f"{BASE_URL}/health") as response:
            if response.status == 200:
                health_data = await response.json()
                print(f"✅ Server is healthy: {health_data['status']}")
            else:
                print("❌ Server is not responding")
                return
        
        # Get system info
        print("\n2. System Information...")
        async with session.get(f"{BASE_URL}/system/info") as response:
            if response.status == 200:
                system_info = await response.json()
                print(f"✅ System: {system_info['system']} v{system_info['version']}")
                print(f"   Database: {system_info['database']}")
                print(f"   Framework: {system_info['framework']}")
            else:
                print("❌ Could not retrieve system info")
        
        # Demo 1: Restaurant Management
        print("\n" + "=" * 70)
        print("3. RESTAURANT MANAGEMENT DEMO")
        print("=" * 70)
        
        # Create a new restaurant
        new_restaurant = {
            "name": "Demo Restaurant",
            "description": "A fantastic demo restaurant with amazing food",
            "cuisine_type": "Fusion",
            "address": "789 Demo Street, Demo City",
            "phone_number": "+1-555-9999",
            "rating": 4.8,
            "is_active": True,
            "opening_time": "09:00",
            "closing_time": "23:00"
        }
        
        async with session.post(f"{BASE_URL}/restaurants/", json=new_restaurant) as response:
            if response.status == 201:
                restaurant = await response.json()
                restaurant_id = restaurant['id']
                print(f"✅ Created restaurant: {restaurant['name']} (ID: {restaurant_id})")
            else:
                print("❌ Failed to create restaurant")
                return
        
        # Get restaurant with menu
        async with session.get(f"{BASE_URL}/restaurants/{restaurant_id}/with-menu") as response:
            if response.status == 200:
                restaurant_with_menu = await response.json()
                print(f"✅ Retrieved restaurant with {len(restaurant_with_menu['menu_items'])} menu items")
            else:
                print("❌ Failed to get restaurant with menu")
        
        # Demo 2: Customer Management
        print("\n" + "=" * 70)
        print("4. CUSTOMER MANAGEMENT DEMO")
        print("=" * 70)
        
        # Create a new customer
        new_customer = {
            "name": "Demo Customer",
            "email": "demo@example.com",
            "phone_number": "+1-555-8888",
            "address": "456 Demo Customer Avenue, Demo City, State 12345",
            "is_active": True
        }
        
        async with session.post(f"{BASE_URL}/customers/", json=new_customer) as response:
            if response.status == 201:
                customer = await response.json()
                customer_id = customer['id']
                print(f"✅ Created customer: {customer['name']} (ID: {customer_id})")
            else:
                print("❌ Failed to create customer")
                return
        
        # Get customer with orders
        async with session.get(f"{BASE_URL}/customers/{customer_id}/with-orders") as response:
            if response.status == 200:
                customer_with_orders = await response.json()
                print(f"✅ Retrieved customer with {len(customer_with_orders['orders'])} orders")
            else:
                print("❌ Failed to get customer with orders")
        
        # Demo 3: Menu Item Management
        print("\n" + "=" * 70)
        print("5. MENU ITEM MANAGEMENT DEMO")
        print("=" * 70)
        
        # Create menu items
        menu_items = [
            {
                "name": "Demo Burger",
                "description": "Juicy beef burger with fresh vegetables",
                "price": 16.99,
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 15,
                "restaurant_id": restaurant_id
            },
            {
                "name": "Demo Salad",
                "description": "Fresh garden salad with vinaigrette",
                "price": 12.99,
                "category": "Appetizer",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 10,
                "restaurant_id": restaurant_id
            },
            {
                "name": "Demo Dessert",
                "description": "Chocolate lava cake with vanilla ice cream",
                "price": 8.99,
                "category": "Dessert",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 5,
                "restaurant_id": restaurant_id
            }
        ]
        
        created_menu_items = []
        for i, menu_item in enumerate(menu_items):
            async with session.post(f"{BASE_URL}/menu-items/", json=menu_item) as response:
                if response.status == 201:
                    created_item = await response.json()
                    created_menu_items.append(created_item)
                    print(f"✅ Created menu item: {created_item['name']} (ID: {created_item['id']})")
                else:
                    print(f"❌ Failed to create menu item {i+1}")
        
        # Demo 4: Order Management
        print("\n" + "=" * 70)
        print("6. ORDER MANAGEMENT DEMO")
        print("=" * 70)
        
        if created_menu_items:
            # Place an order
            order_data = {
                "restaurant_id": restaurant_id,
                "delivery_address": "456 Demo Customer Avenue, Demo City, State 12345",
                "special_instructions": "Please deliver to the front door and ring the bell",
                "order_items": [
                    {
                        "menu_item_id": created_menu_items[0]['id'],
                        "quantity": 2,
                        "special_requests": "Extra cheese and well done"
                    },
                    {
                        "menu_item_id": created_menu_items[1]['id'],
                        "quantity": 1,
                        "special_requests": "Extra dressing on the side"
                    },
                    {
                        "menu_item_id": created_menu_items[2]['id'],
                        "quantity": 1,
                        "special_requests": "Extra chocolate sauce"
                    }
                ]
            }
            
            async with session.post(f"{BASE_URL}/orders/customers/{customer_id}/orders/", json=order_data) as response:
                if response.status == 201:
                    order = await response.json()
                    order_id = order['id']
                    print(f"✅ Placed order: Order #{order_id}")
                    print(f"   Total amount: ${order['total_amount']}")
                    print(f"   Status: {order['order_status']}")
                else:
                    print("❌ Failed to place order")
                    return
            
            # Update order status through workflow
            status_workflow = ["confirmed", "preparing", "out_for_delivery", "delivered"]
            
            for status in status_workflow:
                async with session.put(f"{BASE_URL}/orders/{order_id}/status?new_status={status}") as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Order status updated to: {status}")
                    else:
                        print(f"❌ Failed to update order status to {status}")
                        break
            
            # Get order with details
            async with session.get(f"{BASE_URL}/orders/{order_id}/with-details") as response:
                if response.status == 200:
                    order_details = await response.json()
                    print(f"✅ Retrieved order details with {len(order_details['order_items'])} items")
                else:
                    print("❌ Failed to get order details")
        
        # Demo 5: Review System
        print("\n" + "=" * 70)
        print("7. REVIEW SYSTEM DEMO")
        print("=" * 70)
        
        if 'order_id' in locals():
            # Add a review for the delivered order
            review_data = {
                "rating": 5,
                "comment": "Amazing food and excellent service! The delivery was fast and the food was still hot. Highly recommend!"
            }
            
            async with session.post(f"{BASE_URL}/reviews/orders/{order_id}/review", json=review_data) as response:
                if response.status == 201:
                    review = await response.json()
                    print(f"✅ Added review: {review['rating']} stars")
                    print(f"   Comment: {review['comment']}")
                else:
                    print("❌ Failed to add review")
        
        # Demo 6: Analytics
        print("\n" + "=" * 70)
        print("8. ANALYTICS DEMO")
        print("=" * 70)
        
        # Restaurant analytics
        async with session.get(f"{BASE_URL}/restaurants/{restaurant_id}/analytics") as response:
            if response.status == 200:
                restaurant_analytics = await response.json()
                print("📊 Restaurant Analytics:")
                print(f"   Total orders: {restaurant_analytics['total_orders']}")
                print(f"   Total revenue: ${restaurant_analytics['total_revenue']}")
                print(f"   Average order value: ${restaurant_analytics['average_order_value']}")
                print(f"   Total reviews: {restaurant_analytics['total_reviews']}")
                print(f"   Average rating: {restaurant_analytics['average_rating']}")
                print(f"   Popular items: {len(restaurant_analytics['popular_items'])} items")
            else:
                print("❌ Failed to get restaurant analytics")
        
        # Customer analytics
        async with session.get(f"{BASE_URL}/customers/{customer_id}/analytics") as response:
            if response.status == 200:
                customer_analytics = await response.json()
                print("\n📊 Customer Analytics:")
                print(f"   Total orders: {customer_analytics['total_orders']}")
                print(f"   Total spent: ${customer_analytics['total_spent']}")
                print(f"   Average order value: ${customer_analytics['average_order_value']}")
                print(f"   Favorite restaurants: {len(customer_analytics['favorite_restaurants'])} restaurants")
                print(f"   Order history: {len(customer_analytics['order_history'])} orders")
            else:
                print("❌ Failed to get customer analytics")
        
        # Demo 7: Search and Filter
        print("\n" + "=" * 70)
        print("9. SEARCH AND FILTER DEMO")
        print("=" * 70)
        
        # Search restaurants
        async with session.get(f"{BASE_URL}/search/restaurants?cuisine_type=Fusion&min_rating=4.0") as response:
            if response.status == 200:
                search_results = await response.json()
                print(f"🔍 Restaurant search results: {len(search_results)} restaurants found")
                for restaurant in search_results:
                    print(f"   - {restaurant['name']} ({restaurant['cuisine_type']}) - Rating: {restaurant['rating']}")
            else:
                print("❌ Restaurant search failed")
        
        # Search orders
        async with session.get(f"{BASE_URL}/search/orders?status=delivered") as response:
            if response.status == 200:
                order_results = await response.json()
                print(f"🔍 Order search results: {len(order_results)} delivered orders found")
            else:
                print("❌ Order search failed")
        
        # Demo 8: Relationship Queries
        print("\n" + "=" * 70)
        print("10. RELATIONSHIP QUERIES DEMO")
        print("=" * 70)
        
        # Get restaurant menu
        async with session.get(f"{BASE_URL}/restaurants/{restaurant_id}/menu") as response:
            if response.status == 200:
                menu = await response.json()
                print(f"🍽️ Restaurant menu: {len(menu)} items")
                for item in menu:
                    print(f"   - {item['name']} (${item['price']}) - {item['category']}")
            else:
                print("❌ Failed to get restaurant menu")
        
        # Get customer orders
        async with session.get(f"{BASE_URL}/customers/{customer_id}/orders") as response:
            if response.status == 200:
                customer_orders = await response.json()
                print(f"📦 Customer orders: {len(customer_orders)} orders")
                for order in customer_orders:
                    print(f"   - Order #{order['id']}: ${order['total_amount']} - Status: {order['order_status']}")
            else:
                print("❌ Failed to get customer orders")
        
        # Get restaurant reviews
        async with session.get(f"{BASE_URL}/restaurants/{restaurant_id}/reviews") as response:
            if response.status == 200:
                restaurant_reviews = await response.json()
                print(f"⭐ Restaurant reviews: {len(restaurant_reviews)} reviews")
                for review in restaurant_reviews:
                    print(f"   - {review['rating']} stars: {review['comment']}")
            else:
                print("❌ Failed to get restaurant reviews")
        
        # Demo 9: List Operations
        print("\n" + "=" * 70)
        print("11. LIST OPERATIONS DEMO")
        print("=" * 70)
        
        # List all restaurants
        async with session.get(f"{BASE_URL}/restaurants/") as response:
            if response.status == 200:
                restaurants = await response.json()
                print(f"🏪 Total restaurants: {len(restaurants)}")
            else:
                print("❌ Failed to list restaurants")
        
        # List all customers
        async with session.get(f"{BASE_URL}/customers/") as response:
            if response.status == 200:
                customers = await response.json()
                print(f"👥 Total customers: {len(customers)}")
            else:
                print("❌ Failed to list customers")
        
        # List all menu items
        async with session.get(f"{BASE_URL}/menu-items/") as response:
            if response.status == 200:
                menu_items = await response.json()
                print(f"🍽️ Total menu items: {len(menu_items)}")
            else:
                print("❌ Failed to list menu items")
        
        # List all orders
        async with session.get(f"{BASE_URL}/orders/") as response:
            if response.status == 200:
                orders = await response.json()
                print(f"📦 Total orders: {len(orders)}")
            else:
                print("❌ Failed to list orders")
        
        # List all reviews
        async with session.get(f"{BASE_URL}/reviews/") as response:
            if response.status == 200:
                reviews = await response.json()
                print(f"⭐ Total reviews: {len(reviews)}")
            else:
                print("❌ Failed to list reviews")
        
        print("\n" + "=" * 70)
        print("🎉 Complete Food Delivery System Demo Completed!")
        print("=" * 70)
        print("\n📚 Key Features Demonstrated:")
        print("✅ Complex multi-table relationships")
        print("✅ Business logic and validation")
        print("✅ Order status workflow")
        print("✅ Review system with rating calculations")
        print("✅ Analytics and reporting")
        print("✅ Advanced search and filtering")
        print("✅ Comprehensive CRUD operations")
        print("✅ Error handling and validation")
        print("\n🌐 Access the API documentation at:")
        print("   Swagger UI: http://localhost:8000/docs")
        print("   ReDoc: http://localhost:8000/redoc")

if __name__ == "__main__":
    asyncio.run(run_demo()) 