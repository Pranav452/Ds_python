#!/usr/bin/env python3
"""
Demonstration script for Restaurant-Menu Management System
This script shows how to use the API with example calls
"""

import asyncio
import aiohttp
import json
from datetime import time

# API base URL
BASE_URL = "http://localhost:8000"

async def demonstrate_restaurant_operations():
    """Demonstrate restaurant operations"""
    print("🍽️  Restaurant Operations Demo")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Create a restaurant
        restaurant_data = {
            "name": "Demo Restaurant",
            "description": "A demonstration restaurant for testing",
            "cuisine_type": "International",
            "address": "123 Demo Street, Demo City",
            "phone_number": "+1-555-0123",
            "rating": 4.5,
            "is_active": True,
            "opening_time": "09:00",
            "closing_time": "22:00"
        }
        
        print("1. Creating a restaurant...")
        async with session.post(f"{BASE_URL}/restaurants/", json=restaurant_data) as response:
            if response.status == 201:
                restaurant = await response.json()
                restaurant_id = restaurant["id"]
                print(f"✅ Restaurant created with ID: {restaurant_id}")
                print(f"   Name: {restaurant['name']}")
                print(f"   Cuisine: {restaurant['cuisine_type']}")
                return restaurant_id
            else:
                print(f"❌ Failed to create restaurant: {response.status}")
                return None

async def demonstrate_menu_operations(restaurant_id):
    """Demonstrate menu operations"""
    print(f"\n🍕 Menu Operations Demo (Restaurant ID: {restaurant_id})")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Create menu items
        menu_items = [
            {
                "name": "Classic Burger",
                "description": "Juicy beef burger with fresh vegetables",
                "price": "15.99",
                "category": "Main Course",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 20,
                "restaurant_id": restaurant_id
            },
            {
                "name": "Caesar Salad",
                "description": "Fresh romaine lettuce with Caesar dressing",
                "price": "12.99",
                "category": "Appetizer",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 10,
                "restaurant_id": restaurant_id
            },
            {
                "name": "Chocolate Brownie",
                "description": "Rich chocolate brownie with vanilla ice cream",
                "price": "8.99",
                "category": "Dessert",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_available": True,
                "preparation_time": 5,
                "restaurant_id": restaurant_id
            }
        ]
        
        menu_item_ids = []
        for i, item in enumerate(menu_items, 1):
            print(f"{i}. Creating menu item: {item['name']}...")
            async with session.post(f"{BASE_URL}/restaurants/{restaurant_id}/menu-items/", json=item) as response:
                if response.status == 201:
                    menu_item = await response.json()
                    menu_item_ids.append(menu_item["id"])
                    print(f"   ✅ Created with ID: {menu_item['id']}")
                    print(f"   Price: ${menu_item['price']}")
                    print(f"   Category: {menu_item['category']}")
                else:
                    print(f"   ❌ Failed to create menu item: {response.status}")
        
        return menu_item_ids

async def demonstrate_search_and_filtering():
    """Demonstrate search and filtering capabilities"""
    print(f"\n🔍 Search and Filtering Demo")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Search vegetarian items
        print("1. Searching for vegetarian menu items...")
        async with session.get(f"{BASE_URL}/menu-items/search?vegetarian=true") as response:
            if response.status == 200:
                items = await response.json()
                print(f"   ✅ Found {len(items)} vegetarian items")
                for item in items[:3]:  # Show first 3
                    print(f"   - {item['name']} (${item['price']})")
            else:
                print(f"   ❌ Search failed: {response.status}")
        
        # Search by category
        print("\n2. Searching for main course items...")
        async with session.get(f"{BASE_URL}/menu-items/category/Main%20Course") as response:
            if response.status == 200:
                items = await response.json()
                print(f"   ✅ Found {len(items)} main course items")
                for item in items[:3]:  # Show first 3
                    print(f"   - {item['name']} (${item['price']})")
            else:
                print(f"   ❌ Category search failed: {response.status}")
        
        # Get available items
        print("\n3. Getting available menu items...")
        async with session.get(f"{BASE_URL}/menu-items/available") as response:
            if response.status == 200:
                items = await response.json()
                print(f"   ✅ Found {len(items)} available items")
            else:
                print(f"   ❌ Available items search failed: {response.status}")

async def demonstrate_analytics():
    """Demonstrate analytics features"""
    print(f"\n📊 Analytics Demo")
    print("=" * 30)
    
    async with aiohttp.ClientSession() as session:
        # Get average menu prices
        print("1. Getting average menu prices per restaurant...")
        async with session.get(f"{BASE_URL}/analytics/average-menu-prices") as response:
            if response.status == 200:
                analytics = await response.json()
                print(f"   ✅ Found analytics for {len(analytics)} restaurants")
                for item in analytics:
                    print(f"   - {item['restaurant_name']}: ${item['average_price']:.2f} avg")
            else:
                print(f"   ❌ Analytics failed: {response.status}")
        
        # Get restaurant stats
        print("\n2. Getting restaurants with menu statistics...")
        async with session.get(f"{BASE_URL}/analytics/restaurants-with-stats") as response:
            if response.status == 200:
                stats = await response.json()
                print(f"   ✅ Found stats for {len(stats)} restaurants")
                for item in stats[:3]:  # Show first 3
                    restaurant = item['restaurant']
                    print(f"   - {restaurant['name']}: {item['menu_item_count']} items")
            else:
                print(f"   ❌ Restaurant stats failed: {response.status}")

async def demonstrate_relationship_queries(restaurant_id):
    """Demonstrate relationship queries"""
    print(f"\n🔗 Relationship Queries Demo")
    print("=" * 35)
    
    async with aiohttp.ClientSession() as session:
        # Get restaurant with menu
        print(f"1. Getting restaurant {restaurant_id} with complete menu...")
        async with session.get(f"{BASE_URL}/restaurants/{restaurant_id}/with-menu") as response:
            if response.status == 200:
                restaurant = await response.json()
                print(f"   ✅ Restaurant: {restaurant['name']}")
                print(f"   Menu items: {len(restaurant['menu_items'])}")
                for item in restaurant['menu_items'][:3]:  # Show first 3
                    print(f"   - {item['name']} (${item['price']})")
            else:
                print(f"   ❌ Failed to get restaurant with menu: {response.status}")
        
        # Get restaurant menu
        print(f"\n2. Getting menu for restaurant {restaurant_id}...")
        async with session.get(f"{BASE_URL}/restaurants/{restaurant_id}/menu") as response:
            if response.status == 200:
                menu_items = await response.json()
                print(f"   ✅ Found {len(menu_items)} menu items")
                for item in menu_items[:3]:  # Show first 3
                    print(f"   - {item['name']} (${item['price']})")
            else:
                print(f"   ❌ Failed to get restaurant menu: {response.status}")

async def demonstrate_update_operations(restaurant_id, menu_item_ids):
    """Demonstrate update operations"""
    print(f"\n✏️  Update Operations Demo")
    print("=" * 35)
    
    if not menu_item_ids:
        print("No menu items to update")
        return
    
    async with aiohttp.ClientSession() as session:
        # Update a menu item
        menu_item_id = menu_item_ids[0]
        update_data = {
            "price": "18.99",
            "description": "Updated description - now with premium ingredients"
        }
        
        print(f"1. Updating menu item {menu_item_id}...")
        async with session.put(f"{BASE_URL}/menu-items/{menu_item_id}", json=update_data) as response:
            if response.status == 200:
                updated_item = await response.json()
                print(f"   ✅ Updated successfully")
                print(f"   New price: ${updated_item['price']}")
                print(f"   New description: {updated_item['description']}")
            else:
                print(f"   ❌ Update failed: {response.status}")

async def main():
    """Main demonstration function"""
    print("🚀 Restaurant-Menu Management System Demo")
    print("=" * 50)
    print("This demo will show the key features of the system.")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    try:
        # Test server connection
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/") as response:
                if response.status != 200:
                    print("❌ Server is not running. Please start the server first:")
                    print("   python main.py")
                    return
                else:
                    data = await response.json()
                    print(f"✅ Server is running: {data['message']}")
        
        # Run demonstrations
        restaurant_id = await demonstrate_restaurant_operations()
        if restaurant_id:
            menu_item_ids = await demonstrate_menu_operations(restaurant_id)
            await demonstrate_search_and_filtering()
            await demonstrate_analytics()
            await demonstrate_relationship_queries(restaurant_id)
            await demonstrate_update_operations(restaurant_id, menu_item_ids)
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("Check the API documentation at: http://localhost:8000/docs")
        print("=" * 50)
        
    except aiohttp.ClientConnectorError:
        print("❌ Could not connect to server. Please make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 