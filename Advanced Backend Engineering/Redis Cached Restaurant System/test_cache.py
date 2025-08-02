#!/usr/bin/env python3
"""
Test script for Redis Cached Restaurant System
Tests cache performance, invalidation, and functionality
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

async def test_cache_performance():
    """Test cache performance with timing"""
    print("🧪 Testing Cache Performance...")
    
    async with aiohttp.ClientSession() as session:
        # Create sample data first
        print("📝 Creating sample data...")
        sample_data = await make_request(session, "POST", "/demo/sample-data")
        print(f"✅ Created {len(sample_data.get('restaurants', []))} sample restaurants")
        
        # Test restaurant list endpoint
        print("\n📋 Testing restaurant list endpoint...")
        
        # First request (cache miss)
        start_time = time.time()
        restaurants = await make_request(session, "GET", "/restaurants/")
        first_request_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        restaurants_cached = await make_request(session, "GET", "/restaurants/")
        second_request_time = (time.time() - start_time) * 1000
        
        print(f"⏱️  First request (cache miss): {first_request_time:.2f}ms")
        print(f"⏱️  Second request (cache hit): {second_request_time:.2f}ms")
        print(f"🚀 Performance improvement: {((first_request_time - second_request_time) / first_request_time * 100):.1f}%")
        
        # Test individual restaurant endpoint
        if restaurants:
            restaurant_id = restaurants[0]['id']
            print(f"\n🏪 Testing individual restaurant endpoint (ID: {restaurant_id})...")
            
            # First request (cache miss)
            start_time = time.time()
            restaurant = await make_request(session, "GET", f"/restaurants/{restaurant_id}")
            first_request_time = (time.time() - start_time) * 1000
            
            # Second request (cache hit)
            start_time = time.time()
            restaurant_cached = await make_request(session, "GET", f"/restaurants/{restaurant_id}")
            second_request_time = (time.time() - start_time) * 1000
            
            print(f"⏱️  First request (cache miss): {first_request_time:.2f}ms")
            print(f"⏱️  Second request (cache hit): {second_request_time:.2f}ms")
            print(f"🚀 Performance improvement: {((first_request_time - second_request_time) / first_request_time * 100):.1f}%")

async def test_cache_invalidation():
    """Test cache invalidation on data changes"""
    print("\n🔄 Testing Cache Invalidation...")
    
    async with aiohttp.ClientSession() as session:
        # Get cache stats before update
        stats_before = await make_request(session, "GET", "/cache/stats")
        print(f"📊 Cache keys before update: {stats_before.get('restaurant_cache_keys', 0)}")
        
        # Update a restaurant
        restaurants = await make_request(session, "GET", "/restaurants/")
        if restaurants:
            restaurant_id = restaurants[0]['id']
            print(f"✏️  Updating restaurant {restaurant_id}...")
            
            update_data = {
                "name": f"Updated Restaurant {int(time.time())}",
                "rating": 4.9
            }
            
            await make_request(session, "PUT", f"/restaurants/{restaurant_id}", update_data)
            print("✅ Restaurant updated")
            
            # Get cache stats after update
            stats_after = await make_request(session, "GET", "/cache/stats")
            print(f"📊 Cache keys after update: {stats_after.get('restaurant_cache_keys', 0)}")
            
            # Test that cache was invalidated
            print("🔄 Testing cache invalidation...")
            start_time = time.time()
            restaurant = await make_request(session, "GET", f"/restaurants/{restaurant_id}")
            request_time = (time.time() - start_time) * 1000
            print(f"⏱️  Request after invalidation: {request_time:.2f}ms (should be slower)")

async def test_cache_management():
    """Test cache management endpoints"""
    print("\n⚙️  Testing Cache Management...")
    
    async with aiohttp.ClientSession() as session:
        # Get cache stats
        stats = await make_request(session, "GET", "/cache/stats")
        print(f"📊 Current cache stats:")
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

async def test_search_caching():
    """Test search endpoint caching"""
    print("\n🔍 Testing Search Caching...")
    
    async with aiohttp.ClientSession() as session:
        # First search request (cache miss)
        start_time = time.time()
        search_results = await make_request(session, "GET", "/restaurants/search?cuisine=Italian")
        first_request_time = (time.time() - start_time) * 1000
        
        # Second search request (cache hit)
        start_time = time.time()
        search_results_cached = await make_request(session, "GET", "/restaurants/search?cuisine=Italian")
        second_request_time = (time.time() - start_time) * 1000
        
        print(f"🔍 Search results: {len(search_results)} restaurants")
        print(f"⏱️  First search (cache miss): {first_request_time:.2f}ms")
        print(f"⏱️  Second search (cache hit): {second_request_time:.2f}ms")
        print(f"🚀 Performance improvement: {((first_request_time - second_request_time) / first_request_time * 100):.1f}%")

async def test_active_restaurants_caching():
    """Test active restaurants endpoint caching"""
    print("\n✅ Testing Active Restaurants Caching...")
    
    async with aiohttp.ClientSession() as session:
        # First request (cache miss)
        start_time = time.time()
        active_restaurants = await make_request(session, "GET", "/restaurants/active")
        first_request_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        active_restaurants_cached = await make_request(session, "GET", "/restaurants/active")
        second_request_time = (time.time() - start_time) * 1000
        
        print(f"✅ Active restaurants: {len(active_restaurants)} restaurants")
        print(f"⏱️  First request (cache miss): {first_request_time:.2f}ms")
        print(f"⏱️  Second request (cache hit): {second_request_time:.2f}ms")
        print(f"🚀 Performance improvement: {((first_request_time - second_request_time) / first_request_time * 100):.1f}%")

async def main():
    """Run all tests"""
    print("🚀 Starting Redis Cache Restaurant System Tests...")
    print("=" * 60)
    
    try:
        # Test cache performance
        await test_cache_performance()
        
        # Test cache invalidation
        await test_cache_invalidation()
        
        # Test cache management
        await test_cache_management()
        
        # Test search caching
        await test_search_caching()
        
        # Test active restaurants caching
        await test_active_restaurants_caching()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("📊 Check the application logs for detailed cache performance metrics")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Make sure the application is running on http://localhost:8000")
        print("💡 Ensure Redis server is running")

if __name__ == "__main__":
    asyncio.run(main()) 