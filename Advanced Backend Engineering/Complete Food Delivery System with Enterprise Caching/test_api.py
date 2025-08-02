import asyncio
import aiohttp
import json
from datetime import datetime
from decimal import Decimal

BASE_URL = "http://localhost:8000"

async def test_api():
    """Comprehensive API testing for the Complete Food Delivery System"""
    
    async with aiohttp.ClientSession() as session:
        print("🚀 Starting Complete Food Delivery System API Tests")
        print("=" * 60)
        
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        async with session.get(f"{BASE_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data}")
            else:
                print(f"❌ Health check failed: {response.status}")
        
        # Test 2: System Info
        print("\n2. Testing System Info...")
        async with session.get(f"{BASE_URL}/system/info") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ System info retrieved: {data['system']} v{data['version']}")
            else:
                print(f"❌ System info failed: {response.status}")
        
        # Test 3: Create Restaurants
        print("\n3. Testing Restaurant Creation...")
        restaurants = []
        restaurant_data = [
            {
                "name": "Test Restaurant 1",
                "description": "A test restaurant for API testing",
                "cuisine_type": "Test Cuisine",
                "address": "123 Test Street, Test City",
                "phone_number": "+1-555-0001",
                "rating": 4.5,
                "is_active": True,
                "opening_time": "10:00",
                "closing_time": "22:00"
            },
            {
                "name": "Test Restaurant 2",
                "description": "Another test restaurant",
                "cuisine_type": "Test Cuisine 2",
                "address": "456 Test Avenue, Test City",
                "phone_number": "+1-555-0002",
                "rating": 4.0,
                "is_active": True,
                "opening_time": "11:00",
                "closing_time": "21:00"
            }
        ]
        
        for i, data in enumerate(restaurant_data):
            async with session.post(f"{BASE_URL}/restaurants/", json=data) as response:
                if response.status == 201:
                    restaurant = await response.json()
                    restaurants.append(restaurant)
                    print(f"✅ Restaurant {i+1} created: {restaurant['name']}")
                else:
                    print(f"❌ Restaurant {i+1} creation failed: {response.status}")
        
        # Test 4: Create Customers
        print("\n4. Testing Customer Creation...")
        customers = []
        customer_data = [
            {
                "name": "Test Customer 1",
                "email": "test1@example.com",
                "phone_number": "+1-555-1001",
                "address": "100 Test Customer Street, Test City",
                "is_active": True
            },
            {
                "name": "Test Customer 2",
                "email": "test2@example.com",
                "phone_number": "+1-555-1002",
                "address": "200 Test Customer Avenue, Test City",
                "is_active": True
            }
        ]
        
        for i, data in enumerate(customer_data):
            async with session.post(f"{BASE_URL}/customers/", json=data) as response:
                if response.status == 201:
                    customer = await response.json()
                    customers.append(customer)
                    print(f"✅ Customer {i+1} created: {customer['name']}")
                else:
                    print(f"❌ Customer {i+1} creation failed: {response.status}")
        
        # Test 5: Create Menu Items
        print("\n5. Testing Menu Item Creation...")
        menu_items = []
        if restaurants:
            menu_item_data = [
                {
                    "name": "Test Menu Item 1",
                    "description": "A delicious test menu item",
                    "price": 15.99,
                    "category": "Main Course",
                    "is_vegetarian": False,
                    "is_vegan": False,
                    "is_available": True,
                    "preparation_time": 20,
                    "restaurant_id": restaurants[0]['id']
                },
                {
                    "name": "Test Menu Item 2",
                    "description": "Another test menu item",
                    "price": 12.99,
                    "category": "Appetizer",
                    "is_vegetarian": True,
                    "is_vegan": True,
                    "is_available": True,
                    "preparation_time": 15,
                    "restaurant_id": restaurants[0]['id']
                }
            ]
            
            for i, data in enumerate(menu_item_data):
                async with session.post(f"{BASE_URL}/menu-items/", json=data) as response:
                    if response.status == 201:
                        menu_item = await response.json()
                        menu_items.append(menu_item)
                        print(f"✅ Menu item {i+1} created: {menu_item['name']}")
                    else:
                        print(f"❌ Menu item {i+1} creation failed: {response.status}")
        
        # Test 6: Create Orders
        print("\n6. Testing Order Creation...")
        orders = []
        if customers and restaurants and menu_items:
            order_data = {
                "restaurant_id": restaurants[0]['id'],
                "delivery_address": "100 Test Delivery Street, Test City",
                "special_instructions": "Please deliver to the front door",
                "order_items": [
                    {
                        "menu_item_id": menu_items[0]['id'],
                        "quantity": 2,
                        "special_requests": "Extra spicy"
                    },
                    {
                        "menu_item_id": menu_items[1]['id'],
                        "quantity": 1,
                        "special_requests": "Extra sauce"
                    }
                ]
            }
            
            async with session.post(f"{BASE_URL}/orders/customers/{customers[0]['id']}/orders/", json=order_data) as response:
                if response.status == 201:
                    order = await response.json()
                    orders.append(order)
                    print(f"✅ Order created: Order #{order['id']}")
                else:
                    print(f"❌ Order creation failed: {response.status}")
        
        # Test 7: Update Order Status
        print("\n7. Testing Order Status Update...")
        if orders:
            order_id = orders[0]['id']
            new_status = "confirmed"
            
            async with session.put(f"{BASE_URL}/orders/{order_id}/status?new_status={new_status}") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Order status updated: {result['message']}")
                else:
                    print(f"❌ Order status update failed: {response.status}")
        
        # Test 8: Create Reviews
        print("\n8. Testing Review Creation...")
        if orders:
            # First, update order to delivered status
            async with session.put(f"{BASE_URL}/orders/{orders[0]['id']}/status?new_status=delivered") as response:
                if response.status == 200:
                    print("✅ Order updated to delivered status")
                    
                    # Now create a review
                    review_data = {
                        "rating": 5,
                        "comment": "Excellent service and delicious food!"
                    }
                    
                    async with session.post(f"{BASE_URL}/reviews/orders/{orders[0]['id']}/review", json=review_data) as response:
                        if response.status == 201:
                            review = await response.json()
                            print(f"✅ Review created: Rating {review['rating']} stars")
                        else:
                            print(f"❌ Review creation failed: {response.status}")
                else:
                    print(f"❌ Order status update failed: {response.status}")
        
        # Test 9: Get Analytics
        print("\n9. Testing Analytics...")
        if restaurants:
            async with session.get(f"{BASE_URL}/restaurants/{restaurants[0]['id']}/analytics") as response:
                if response.status == 200:
                    analytics = await response.json()
                    print(f"✅ Restaurant analytics retrieved: {analytics['total_orders']} orders, ${analytics['total_revenue']} revenue")
                else:
                    print(f"❌ Restaurant analytics failed: {response.status}")
        
        if customers:
            async with session.get(f"{BASE_URL}/customers/{customers[0]['id']}/analytics") as response:
                if response.status == 200:
                    analytics = await response.json()
                    print(f"✅ Customer analytics retrieved: {analytics['total_orders']} orders, ${analytics['total_spent']} spent")
                else:
                    print(f"❌ Customer analytics failed: {response.status}")
        
        # Test 10: Search and Filter
        print("\n10. Testing Search and Filter...")
        
        # Search restaurants
        async with session.get(f"{BASE_URL}/search/restaurants?cuisine_type=Test&min_rating=4.0") as response:
            if response.status == 200:
                results = await response.json()
                print(f"✅ Restaurant search returned {len(results)} results")
            else:
                print(f"❌ Restaurant search failed: {response.status}")
        
        # Search orders
        async with session.get(f"{BASE_URL}/search/orders?status=delivered") as response:
            if response.status == 200:
                results = await response.json()
                print(f"✅ Order search returned {len(results)} results")
            else:
                print(f"❌ Order search failed: {response.status}")
        
        # Test 11: Get Relationships
        print("\n11. Testing Relationship Endpoints...")
        
        if restaurants:
            # Get restaurant with menu
            async with session.get(f"{BASE_URL}/restaurants/{restaurants[0]['id']}/with-menu") as response:
                if response.status == 200:
                    restaurant_with_menu = await response.json()
                    print(f"✅ Restaurant with menu retrieved: {len(restaurant_with_menu['menu_items'])} menu items")
                else:
                    print(f"❌ Restaurant with menu failed: {response.status}")
            
            # Get restaurant menu
            async with session.get(f"{BASE_URL}/restaurants/{restaurants[0]['id']}/menu") as response:
                if response.status == 200:
                    menu = await response.json()
                    print(f"✅ Restaurant menu retrieved: {len(menu)} items")
                else:
                    print(f"❌ Restaurant menu failed: {response.status}")
        
        if customers:
            # Get customer orders
            async with session.get(f"{BASE_URL}/customers/{customers[0]['id']}/orders") as response:
                if response.status == 200:
                    customer_orders = await response.json()
                    print(f"✅ Customer orders retrieved: {len(customer_orders)} orders")
                else:
                    print(f"❌ Customer orders failed: {response.status}")
        
        # Test 12: List Operations
        print("\n12. Testing List Operations...")
        
        # List restaurants
        async with session.get(f"{BASE_URL}/restaurants/") as response:
            if response.status == 200:
                restaurants_list = await response.json()
                print(f"✅ Restaurants list retrieved: {len(restaurants_list)} restaurants")
            else:
                print(f"❌ Restaurants list failed: {response.status}")
        
        # List customers
        async with session.get(f"{BASE_URL}/customers/") as response:
            if response.status == 200:
                customers_list = await response.json()
                print(f"✅ Customers list retrieved: {len(customers_list)} customers")
            else:
                print(f"❌ Customers list failed: {response.status}")
        
        # List menu items
        async with session.get(f"{BASE_URL}/menu-items/") as response:
            if response.status == 200:
                menu_items_list = await response.json()
                print(f"✅ Menu items list retrieved: {len(menu_items_list)} menu items")
            else:
                print(f"❌ Menu items list failed: {response.status}")
        
        # List orders
        async with session.get(f"{BASE_URL}/orders/") as response:
            if response.status == 200:
                orders_list = await response.json()
                print(f"✅ Orders list retrieved: {len(orders_list)} orders")
            else:
                print(f"❌ Orders list failed: {response.status}")
        
        # List reviews
        async with session.get(f"{BASE_URL}/reviews/") as response:
            if response.status == 200:
                reviews_list = await response.json()
                print(f"✅ Reviews list retrieved: {len(reviews_list)} reviews")
            else:
                print(f"❌ Reviews list failed: {response.status}")
        
        print("\n" + "=" * 60)
        print("🎉 Complete Food Delivery System API Tests Completed!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_api()) 