import asyncio
import aiohttp
import json
from datetime import time
from decimal import Decimal

# API base URL
BASE_URL = "http://localhost:8000"

async def test_api():
    """Test all API endpoints"""
    async with aiohttp.ClientSession() as session:
        print("Testing Restaurant-Menu Management System API")
        print("=" * 50)
        
        # Test 1: Get root endpoint
        print("\n1. Testing root endpoint...")
        async with session.get(f"{BASE_URL}/") as response:
            data = await response.json()
            print(f"Status: {response.status}")
            print(f"Response: {data}")
        
        # Test 2: Create restaurants
        print("\n2. Creating restaurants...")
        restaurants = [
            {
                "name": "Test Restaurant 1",
                "description": "A test restaurant",
                "cuisine_type": "Test Cuisine",
                "address": "123 Test Street",
                "phone_number": "+1-555-0001",
                "rating": 4.0,
                "is_active": True,
                "opening_time": "09:00",
                "closing_time": "22:00"
            },
            {
                "name": "Test Restaurant 2",
                "description": "Another test restaurant",
                "cuisine_type": "Test Cuisine 2",
                "address": "456 Test Avenue",
                "phone_number": "+1-555-0002",
                "rating": 4.5,
                "is_active": True,
                "opening_time": "10:00",
                "closing_time": "23:00"
            }
        ]
        
        restaurant_ids = []
        for i, restaurant_data in enumerate(restaurants):
            async with session.post(f"{BASE_URL}/restaurants/", json=restaurant_data) as response:
                if response.status == 201:
                    data = await response.json()
                    restaurant_ids.append(data["id"])
                    print(f"Restaurant {i+1} created with ID: {data['id']}")
                else:
                    print(f"Failed to create restaurant {i+1}: {response.status}")
        
        # Test 3: List restaurants
        print("\n3. Listing restaurants...")
        async with session.get(f"{BASE_URL}/restaurants/") as response:
            data = await response.json()
            print(f"Found {len(data)} restaurants")
        
        # Test 4: Get specific restaurant
        if restaurant_ids:
            print(f"\n4. Getting restaurant {restaurant_ids[0]}...")
            async with session.get(f"{BASE_URL}/restaurants/{restaurant_ids[0]}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Restaurant: {data['name']}")
                else:
                    print(f"Failed to get restaurant: {response.status}")
        
        # Test 5: Add menu items
        print("\n5. Adding menu items...")
        menu_items = [
            {
                "name": "Test Burger",
                "description": "A delicious test burger",
                "price": "12.99",
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 15,
                "restaurant_id": restaurant_ids[0] if restaurant_ids else 1
            },
            {
                "name": "Veggie Salad",
                "description": "Fresh vegetable salad",
                "price": "8.99",
                "category": "Appetizer",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_available": True,
                "preparation_time": 10,
                "restaurant_id": restaurant_ids[0] if restaurant_ids else 1
            },
            {
                "name": "Chocolate Cake",
                "description": "Rich chocolate cake",
                "price": "6.99",
                "category": "Dessert",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 5,
                "restaurant_id": restaurant_ids[0] if restaurant_ids else 1
            }
        ]
        
        menu_item_ids = []
        for i, menu_item_data in enumerate(menu_items):
            restaurant_id = menu_item_data["restaurant_id"]
            async with session.post(f"{BASE_URL}/restaurants/{restaurant_id}/menu-items/", json=menu_item_data) as response:
                if response.status == 201:
                    data = await response.json()
                    menu_item_ids.append(data["id"])
                    print(f"Menu item {i+1} created with ID: {data['id']}")
                else:
                    print(f"Failed to create menu item {i+1}: {response.status}")
        
        # Test 6: List menu items
        print("\n6. Listing menu items...")
        async with session.get(f"{BASE_URL}/menu-items/") as response:
            data = await response.json()
            print(f"Found {len(data)} menu items")
        
        # Test 7: Get restaurant with menu
        if restaurant_ids:
            print(f"\n7. Getting restaurant {restaurant_ids[0]} with menu...")
            async with session.get(f"{BASE_URL}/restaurants/{restaurant_ids[0]}/with-menu") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Restaurant: {data['name']}")
                    print(f"Menu items: {len(data['menu_items'])}")
                else:
                    print(f"Failed to get restaurant with menu: {response.status}")
        
        # Test 8: Get restaurant menu
        if restaurant_ids:
            print(f"\n8. Getting menu for restaurant {restaurant_ids[0]}...")
            async with session.get(f"{BASE_URL}/restaurants/{restaurant_ids[0]}/menu") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Found {len(data)} menu items for this restaurant")
                else:
                    print(f"Failed to get restaurant menu: {response.status}")
        
        # Test 9: Search menu items
        print("\n9. Searching menu items...")
        async with session.get(f"{BASE_URL}/menu-items/search?vegetarian=true") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found {len(data)} vegetarian menu items")
            else:
                print(f"Failed to search menu items: {response.status}")
        
        # Test 10: Get menu items by category
        print("\n10. Getting menu items by category...")
        async with session.get(f"{BASE_URL}/menu-items/category/Main%20Course") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found {len(data)} main course items")
            else:
                print(f"Failed to get menu items by category: {response.status}")
        
        # Test 11: Get vegetarian menu items
        print("\n11. Getting vegetarian menu items...")
        async with session.get(f"{BASE_URL}/menu-items/vegetarian") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found {len(data)} vegetarian menu items")
            else:
                print(f"Failed to get vegetarian menu items: {response.status}")
        
        # Test 12: Get vegan menu items
        print("\n12. Getting vegan menu items...")
        async with session.get(f"{BASE_URL}/menu-items/vegan") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found {len(data)} vegan menu items")
            else:
                print(f"Failed to get vegan menu items: {response.status}")
        
        # Test 13: Get available menu items
        print("\n13. Getting available menu items...")
        async with session.get(f"{BASE_URL}/menu-items/available") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found {len(data)} available menu items")
            else:
                print(f"Failed to get available menu items: {response.status}")
        
        # Test 14: Update menu item
        if menu_item_ids:
            print(f"\n14. Updating menu item {menu_item_ids[0]}...")
            update_data = {
                "price": "15.99",
                "description": "Updated description"
            }
            async with session.put(f"{BASE_URL}/menu-items/{menu_item_ids[0]}", json=update_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Updated menu item: {data['name']} - New price: {data['price']}")
                else:
                    print(f"Failed to update menu item: {response.status}")
        
        # Test 15: Get menu item with restaurant
        if menu_item_ids:
            print(f"\n15. Getting menu item {menu_item_ids[0]} with restaurant details...")
            async with session.get(f"{BASE_URL}/menu-items/{menu_item_ids[0]}/with-restaurant") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Menu item: {data['name']}")
                    print(f"Restaurant: {data['restaurant']['name']}")
                else:
                    print(f"Failed to get menu item with restaurant: {response.status}")
        
        # Test 16: Analytics - Average menu prices
        print("\n16. Getting average menu prices per restaurant...")
        async with session.get(f"{BASE_URL}/analytics/average-menu-prices") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found analytics for {len(data)} restaurants")
                for item in data:
                    print(f"  {item['restaurant_name']}: ${item['average_price']:.2f} avg, {item['menu_item_count']} items")
            else:
                print(f"Failed to get analytics: {response.status}")
        
        # Test 17: Analytics - Restaurants with stats
        print("\n17. Getting restaurants with menu statistics...")
        async with session.get(f"{BASE_URL}/analytics/restaurants-with-stats") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found stats for {len(data)} restaurants")
                for item in data:
                    restaurant = item['restaurant']
                    print(f"  {restaurant['name']}: {item['menu_item_count']} items, ${item['average_price']:.2f} avg")
            else:
                print(f"Failed to get restaurant stats: {response.status}")
        
        # Test 18: Search restaurants by cuisine
        print("\n18. Searching restaurants by cuisine...")
        async with session.get(f"{BASE_URL}/restaurants/search?cuisine=Test") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found {len(data)} restaurants with 'Test' cuisine")
            else:
                print(f"Failed to search restaurants: {response.status}")
        
        # Test 19: Get active restaurants
        print("\n19. Getting active restaurants...")
        async with session.get(f"{BASE_URL}/restaurants/active") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Found {len(data)} active restaurants")
            else:
                print(f"Failed to get active restaurants: {response.status}")
        
        # Test 20: Delete menu item
        if menu_item_ids:
            print(f"\n20. Deleting menu item {menu_item_ids[-1]}...")
            async with session.delete(f"{BASE_URL}/menu-items/{menu_item_ids[-1]}") as response:
                if response.status == 204:
                    print("Menu item deleted successfully")
                else:
                    print(f"Failed to delete menu item: {response.status}")
        
        # Test 21: Delete restaurant (cascade delete will handle menu items)
        if restaurant_ids:
            print(f"\n21. Deleting restaurant {restaurant_ids[-1]}...")
            async with session.delete(f"{BASE_URL}/restaurants/{restaurant_ids[-1]}") as response:
                if response.status == 204:
                    print("Restaurant deleted successfully (menu items cascade deleted)")
                else:
                    print(f"Failed to delete restaurant: {response.status}")
        
        print("\n" + "=" * 50)
        print("API testing completed!")

if __name__ == "__main__":
    asyncio.run(test_api()) 