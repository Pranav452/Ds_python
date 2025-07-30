import asyncio
import aiohttp
import json
from datetime import time

# Sample restaurant data for testing
SAMPLE_RESTAURANTS = [
    {
        "name": "Pizza Palace",
        "description": "Best pizza in town with authentic Italian recipes",
        "cuisine_type": "Italian",
        "address": "123 Main Street, Downtown",
        "phone_number": "+1234567890",
        "rating": 4.5,
        "is_active": True,
        "opening_time": "10:00",
        "closing_time": "22:00"
    },
    {
        "name": "Golden Dragon",
        "description": "Authentic Chinese cuisine with fresh ingredients",
        "cuisine_type": "Chinese",
        "address": "456 Oak Avenue, Chinatown",
        "phone_number": "+1987654321",
        "rating": 4.2,
        "is_active": True,
        "opening_time": "11:00",
        "closing_time": "23:00"
    },
    {
        "name": "Spice Garden",
        "description": "Traditional Indian spices and flavors",
        "cuisine_type": "Indian",
        "address": "789 Spice Lane, Little India",
        "phone_number": "+1555123456",
        "rating": 4.8,
        "is_active": True,
        "opening_time": "12:00",
        "closing_time": "21:00"
    }
]

async def test_api():
    """Test the restaurant API endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("Testing Restaurant Management API...")
        print("=" * 50)
        
        # Test 1: Create restaurants
        print("\n1. Creating sample restaurants...")
        created_restaurants = []
        
        for restaurant_data in SAMPLE_RESTAURANTS:
            async with session.post(
                f"{base_url}/restaurants/",
                json=restaurant_data
            ) as response:
                if response.status == 201:
                    restaurant = await response.json()
                    created_restaurants.append(restaurant)
                    print(f"✓ Created: {restaurant['name']}")
                else:
                    error = await response.text()
                    print(f"✗ Failed to create {restaurant_data['name']}: {error}")
        
        # Test 2: Get all restaurants
        print("\n2. Getting all restaurants...")
        async with session.get(f"{base_url}/restaurants/") as response:
            if response.status == 200:
                restaurants = await response.json()
                print(f"✓ Found {len(restaurants)} restaurants")
            else:
                print(f"✗ Failed to get restaurants: {await response.text()}")
        
        # Test 3: Get specific restaurant
        if created_restaurants:
            restaurant_id = created_restaurants[0]['id']
            print(f"\n3. Getting restaurant with ID {restaurant_id}...")
            async with session.get(f"{base_url}/restaurants/{restaurant_id}") as response:
                if response.status == 200:
                    restaurant = await response.json()
                    print(f"✓ Found restaurant: {restaurant['name']}")
                else:
                    print(f"✗ Failed to get restaurant: {await response.text()}")
        
        # Test 4: Search by cuisine
        print("\n4. Searching for Italian restaurants...")
        async with session.get(f"{base_url}/restaurants/search?cuisine=Italian") as response:
            if response.status == 200:
                restaurants = await response.json()
                print(f"✓ Found {len(restaurants)} Italian restaurants")
            else:
                print(f"✗ Failed to search: {await response.text()}")
        
        # Test 5: Get active restaurants
        print("\n5. Getting active restaurants...")
        async with session.get(f"{base_url}/restaurants/active") as response:
            if response.status == 200:
                restaurants = await response.json()
                print(f"✓ Found {len(restaurants)} active restaurants")
            else:
                print(f"✗ Failed to get active restaurants: {await response.text()}")
        
        # Test 6: Update restaurant
        if created_restaurants:
            restaurant_id = created_restaurants[0]['id']
            update_data = {
                "rating": 4.9,
                "description": "Updated description - Even better pizza!"
            }
            print(f"\n6. Updating restaurant {restaurant_id}...")
            async with session.put(
                f"{base_url}/restaurants/{restaurant_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    restaurant = await response.json()
                    print(f"✓ Updated restaurant: {restaurant['name']} (Rating: {restaurant['rating']})")
                else:
                    print(f"✗ Failed to update restaurant: {await response.text()}")
        
        # Test 7: Test validation errors
        print("\n7. Testing validation errors...")
        invalid_data = {
            "name": "A",  # Too short
            "cuisine_type": "Italian",
            "address": "123 Test St",
            "phone_number": "invalid",
            "rating": 6.0,  # Too high
            "opening_time": "22:00",
            "closing_time": "10:00"  # Closing before opening
        }
        async with session.post(f"{base_url}/restaurants/", json=invalid_data) as response:
            if response.status == 422:
                print("✓ Validation errors caught correctly")
            else:
                print(f"✗ Expected validation error, got: {response.status}")
        
        print("\n" + "=" * 50)
        print("API testing completed!")

if __name__ == "__main__":
    print("Make sure the server is running on http://localhost:8000")
    print("Run: python main.py")
    print("\nPress Enter to start testing...")
    input()
    
    asyncio.run(test_api()) 