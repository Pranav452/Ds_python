#!/usr/bin/env python3
"""
Demo script for Redis Cached Restaurant System
Showcases caching features and performance improvements
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def make_request(session: aiohttp.ClientSession, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make HTTP request and return response"""
    url = f"{BASE_URL}{endpoint}"
    
    if method == "GET":
        async with session.get(url) as response:
            return await response.json()
    elif method == "POST":
        async with session.post(url, json=data) as response:
            return await response.json()
    elif method == "PUT":
        async with session.put(url, json=data) as response:
            return await response.json()
    elif method == "DELETE":
        async with session.delete(url) as response:
            return {"status": response.status}

async def demo_cache_performance():
    """Demonstrate cache performance improvements"""
    print("🎯 Cache Performance Demo")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Create sample data
        print("📝 Creating sample restaurants...")
        sample_data = await make_request(session, "POST", "/demo/sample-data")
        print(f"✅ Created {len(sample_data.get('restaurants', []))} restaurants")
        
        # Test restaurant list performance
        print("\n📋 Restaurant List Performance:")
        print("-" * 30)
        
        # First request (cache miss)
        start_time = time.time()
        restaurants = await make_request(session, "GET", "/restaurants/")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        restaurants_cached = await make_request(session, "GET", "/restaurants/")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        
        print(f"🔄 First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test individual restaurant performance
        if restaurants:
            restaurant_id = restaurants[0]['id']
            print(f"\n🏪 Individual Restaurant Performance (ID: {restaurant_id}):")
            print("-" * 50)
            
            # First request (cache miss)
            start_time = time.time()
            restaurant = await make_request(session, "GET", f"/restaurants/{restaurant_id}")
            first_time = (time.time() - start_time) * 1000
            
            # Second request (cache hit)
            start_time = time.time()
            restaurant_cached = await make_request(session, "GET", f"/restaurants/{restaurant_id}")
            second_time = (time.time() - start_time) * 1000
            
            improvement = ((first_time - second_time) / first_time) * 100
            
            print(f"🔄 First request (cache miss): {first_time:.2f}ms")
            print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
            print(f"🚀 Performance improvement: {improvement:.1f}%")

async def demo_cache_invalidation():
    """Demonstrate cache invalidation"""
    print("\n🔄 Cache Invalidation Demo")
    print("=" * 35)
    
    async with aiohttp.ClientSession() as session:
        # Get cache stats before update
        stats_before = await make_request(session, "GET", "/cache/stats")
        print(f"📊 Cache keys before update: {stats_before.get('restaurant_cache_keys', 0)}")
        
        # Update a restaurant
        restaurants = await make_request(session, "GET", "/restaurants/")
        if restaurants:
            restaurant_id = restaurants[0]['id']
            print(f"\n✏️  Updating restaurant {restaurant_id}...")
            
            update_data = {
                "name": f"Updated Restaurant {int(time.time())}",
                "rating": 4.9,
                "description": "This restaurant was updated to test cache invalidation"
            }
            
            await make_request(session, "PUT", f"/restaurants/{restaurant_id}", update_data)
            print("✅ Restaurant updated successfully")
            
            # Get cache stats after update
            stats_after = await make_request(session, "GET", "/cache/stats")
            print(f"📊 Cache keys after update: {stats_after.get('restaurant_cache_keys', 0)}")
            
            # Test that cache was invalidated
            print("\n🔄 Testing cache invalidation...")
            start_time = time.time()
            restaurant = await make_request(session, "GET", f"/restaurants/{restaurant_id}")
            request_time = (time.time() - start_time) * 1000
            print(f"⏱️  Request after invalidation: {request_time:.2f}ms")
            print("💡 This request was slower because the cache was cleared!")

async def demo_search_caching():
    """Demonstrate search caching"""
    print("\n🔍 Search Caching Demo")
    print("=" * 25)
    
    async with aiohttp.ClientSession() as session:
        # Test search by cuisine
        cuisine = "Italian"
        print(f"🔍 Searching for '{cuisine}' restaurants...")
        
        # First search (cache miss)
        start_time = time.time()
        search_results = await make_request(session, "GET", f"/restaurants/search?cuisine={cuisine}")
        first_time = (time.time() - start_time) * 1000
        
        # Second search (cache hit)
        start_time = time.time()
        search_results_cached = await make_request(session, "GET", f"/restaurants/search?cuisine={cuisine}")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        
        print(f"🔍 Found {len(search_results)} {cuisine} restaurants")
        print(f"🔄 First search (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second search (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")

async def demo_cache_management():
    """Demonstrate cache management features"""
    print("\n⚙️  Cache Management Demo")
    print("=" * 30)
    
    async with aiohttp.ClientSession() as session:
        # Get cache statistics
        stats = await make_request(session, "GET", "/cache/stats")
        print("📊 Current Cache Statistics:")
        print(f"   Total keys: {stats.get('total_keys', 0)}")
        print(f"   Restaurant cache keys: {stats.get('restaurant_cache_keys', 0)}")
        print(f"   Namespace counts: {stats.get('namespace_counts', {})}")
        
        # Clear restaurant cache
        print("\n🗑️  Clearing restaurant cache...")
        clear_result = await make_request(session, "DELETE", "/cache/clear/restaurants")
        print(f"✅ {clear_result.get('message', 'Cache cleared')}")
        
        # Get stats after clearing
        stats_after = await make_request(session, "GET", "/cache/stats")
        print(f"📊 Cache keys after clearing: {stats_after.get('restaurant_cache_keys', 0)}")
        
        # Test that cache was cleared
        print("\n🔄 Testing cache clearing...")
        start_time = time.time()
        restaurants = await make_request(session, "GET", "/restaurants/")
        request_time = (time.time() - start_time) * 1000
        print(f"⏱️  Request after cache clear: {request_time:.2f}ms")
        print("💡 This request was slower because the cache was cleared!")

async def demo_cache_test_endpoint():
    """Demonstrate the cache test endpoint"""
    print("\n🧪 Cache Test Endpoint Demo")
    print("=" * 35)
    
    async with aiohttp.ClientSession() as session:
        # Get a restaurant ID
        restaurants = await make_request(session, "GET", "/restaurants/")
        if restaurants:
            restaurant_id = restaurants[0]['id']
            print(f"🏪 Testing cache performance for restaurant {restaurant_id}...")
            
            # Use the cache test endpoint
            cache_test = await make_request(session, "GET", f"/demo/cache-test/{restaurant_id}")
            
            metrics = cache_test.get('performance_metrics', {})
            print("📊 Performance Metrics:")
            print(f"   First request time: {metrics.get('first_request_time_ms', 0):.2f}ms")
            print(f"   Second request time: {metrics.get('second_request_time_ms', 0):.2f}ms")
            print(f"   Performance improvement: {metrics.get('performance_improvement', 0):.1f}%")

async def main():
    """Run all demos"""
    print("🎬 Redis Cached Restaurant System Demo")
    print("=" * 50)
    print("This demo showcases the Redis caching features and performance improvements.")
    print()
    
    try:
        # Run all demos
        await demo_cache_performance()
        await demo_cache_invalidation()
        await demo_search_caching()
        await demo_cache_management()
        await demo_cache_test_endpoint()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("📊 Check the application logs for detailed cache performance metrics")
        print("🔗 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("💡 Make sure the application is running on http://localhost:8000")
        print("💡 Ensure Redis server is running")

if __name__ == "__main__":
    asyncio.run(main()) 