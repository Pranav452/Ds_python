#!/usr/bin/env python3
"""
Advanced Cache Test Script for Restaurant-Menu System
Tests multi-level caching, hierarchical invalidation, and business logic caching
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

async def test_multi_level_caching():
    """Test multi-level caching with different TTLs"""
    print("🎯 Testing Multi-Level Caching...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Create sample data first
        print("📝 Creating sample data...")
        sample_data = await make_request(session, "POST", "/demo/sample-data")
        print(f"✅ Created {len(sample_data.get('restaurants', []))} restaurants and {len(sample_data.get('menu_items', []))} menu items")
        
        # Test restaurant caching (10-minute TTL)
        print("\n🏪 Testing Restaurant Caching (10-min TTL):")
        print("-" * 40)
        
        # First request (cache miss)
        start_time = time.time()
        restaurant = await make_request(session, "GET", "/restaurants/1")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        restaurant_cached = await make_request(session, "GET", "/restaurants/1")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test menu item caching (8-minute TTL)
        print("\n🍕 Testing Menu Item Caching (8-min TTL):")
        print("-" * 40)
        
        # First request (cache miss)
        start_time = time.time()
        menu_item = await make_request(session, "GET", "/menu-items/1")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        menu_item_cached = await make_request(session, "GET", "/menu-items/1")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test restaurant-menu caching (15-minute TTL)
        print("\n🍽️  Testing Restaurant-Menu Caching (15-min TTL):")
        print("-" * 45)
        
        # First request (cache miss)
        start_time = time.time()
        restaurant_with_menu = await make_request(session, "GET", "/restaurants/1/with-menu")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        restaurant_with_menu_cached = await make_request(session, "GET", "/restaurants/1/with-menu")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")

async def test_category_specific_caching():
    """Test category-specific caching with different TTLs"""
    print("\n🥗 Testing Category-Specific Caching...")
    print("=" * 45)
    
    async with aiohttp.ClientSession() as session:
        # Test vegetarian caching (4-minute TTL)
        print("\n🥬 Testing Vegetarian Caching (4-min TTL):")
        print("-" * 40)
        
        # First request (cache miss)
        start_time = time.time()
        vegetarian_items = await make_request(session, "GET", "/menu-items/vegetarian")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        vegetarian_items_cached = await make_request(session, "GET", "/menu-items/vegetarian")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"🥬 Found {len(vegetarian_items)} vegetarian items")
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test vegan caching (4-minute TTL)
        print("\n🌱 Testing Vegan Caching (4-min TTL):")
        print("-" * 35)
        
        # First request (cache miss)
        start_time = time.time()
        vegan_items = await make_request(session, "GET", "/menu-items/vegan")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        vegan_items_cached = await make_request(session, "GET", "/menu-items/vegan")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"🌱 Found {len(vegan_items)} vegan items")
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test popular items caching (10-minute TTL)
        print("\n🔥 Testing Popular Items Caching (10-min TTL):")
        print("-" * 45)
        
        # First request (cache miss)
        start_time = time.time()
        popular_items = await make_request(session, "GET", "/menu-items/category/Pizza")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        popular_items_cached = await make_request(session, "GET", "/menu-items/category/Pizza")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"🔥 Found {len(popular_items)} Pizza items")
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")

async def test_analytics_caching():
    """Test analytics caching with business logic"""
    print("\n📊 Testing Analytics Caching...")
    print("=" * 35)
    
    async with aiohttp.ClientSession() as session:
        # Test popular cuisines caching (30-minute TTL)
        print("\n🍽️  Testing Popular Cuisines Caching (30-min TTL):")
        print("-" * 50)
        
        # First request (cache miss)
        start_time = time.time()
        popular_cuisines = await make_request(session, "GET", "/analytics/popular-cuisines")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        popular_cuisines_cached = await make_request(session, "GET", "/analytics/popular-cuisines")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"🍽️  Found {len(popular_cuisines)} cuisine types")
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test price range analytics caching (30-minute TTL)
        print("\n💰 Testing Price Range Analytics Caching (30-min TTL):")
        print("-" * 55)
        
        # First request (cache miss)
        start_time = time.time()
        price_range = await make_request(session, "GET", "/analytics/price-range")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        price_range_cached = await make_request(session, "GET", "/analytics/price-range")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"💰 Price range: ${price_range.get('min_price', 0):.2f} - ${price_range.get('max_price', 0):.2f}")
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test dietary preferences caching (30-minute TTL)
        print("\n🥗 Testing Dietary Preferences Caching (30-min TTL):")
        print("-" * 50)
        
        # First request (cache miss)
        start_time = time.time()
        dietary_prefs = await make_request(session, "GET", "/analytics/dietary-preferences")
        first_time = (time.time() - start_time) * 1000
        
        # Second request (cache hit)
        start_time = time.time()
        dietary_prefs_cached = await make_request(session, "GET", "/analytics/dietary-preferences")
        second_time = (time.time() - start_time) * 1000
        
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"🥗 Vegetarian: {dietary_prefs.get('vegetarian_items', 0)}, Vegan: {dietary_prefs.get('vegan_items', 0)}")
        print(f"⏱️  First request (cache miss): {first_time:.2f}ms")
        print(f"⚡ Second request (cache hit): {second_time:.2f}ms")
        print(f"🚀 Performance improvement: {improvement:.1f}%")

async def test_hierarchical_invalidation():
    """Test hierarchical cache invalidation"""
    print("\n🔄 Testing Hierarchical Cache Invalidation...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Get cache stats before updates
        stats_before = await make_request(session, "GET", "/cache/stats/detailed")
        print(f"📊 Cache keys before updates: {stats_before.get('restaurant_menu_cache_keys', 0)}")
        
        # Test restaurant update invalidation
        print("\n🏪 Testing Restaurant Update Invalidation:")
        print("-" * 40)
        
        # Update a restaurant
        update_data = {
            "name": f"Updated Restaurant {int(time.time())}",
            "rating": 4.9
        }
        
        await make_request(session, "PUT", "/restaurants/1", update_data)
        print("✅ Restaurant updated")
        
        # Get cache stats after restaurant update
        stats_after_restaurant = await make_request(session, "GET", "/cache/stats/detailed")
        print(f"📊 Cache keys after restaurant update: {stats_after_restaurant.get('restaurant_menu_cache_keys', 0)}")
        
        # Test that restaurant cache was invalidated
        print("🔄 Testing restaurant cache invalidation...")
        start_time = time.time()
        restaurant = await make_request(session, "GET", "/restaurants/1")
        request_time = (time.time() - start_time) * 1000
        print(f"⏱️  Request after restaurant invalidation: {request_time:.2f}ms (should be slower)")
        
        # Test menu item update invalidation
        print("\n🍕 Testing Menu Item Update Invalidation:")
        print("-" * 40)
        
        # Update a menu item
        menu_update_data = {
            "name": f"Updated Menu Item {int(time.time())}",
            "price": "15.99"
        }
        
        await make_request(session, "PUT", "/menu-items/1", menu_update_data)
        print("✅ Menu item updated")
        
        # Get cache stats after menu item update
        stats_after_menu = await make_request(session, "GET", "/cache/stats/detailed")
        print(f"📊 Cache keys after menu item update: {stats_after_menu.get('restaurant_menu_cache_keys', 0)}")
        
        # Test that menu cache was invalidated
        print("🔄 Testing menu cache invalidation...")
        start_time = time.time()
        menu_item = await make_request(session, "GET", "/menu-items/1")
        request_time = (time.time() - start_time) * 1000
        print(f"⏱️  Request after menu invalidation: {request_time:.2f}ms (should be slower)")

async def test_cache_management():
    """Test advanced cache management features"""
    print("\n⚙️  Testing Advanced Cache Management...")
    print("=" * 45)
    
    async with aiohttp.ClientSession() as session:
        # Get detailed cache statistics
        stats = await make_request(session, "GET", "/cache/stats/detailed")
        print("📊 Detailed Cache Statistics:")
        print(f"   Total keys: {stats.get('total_keys', 0)}")
        print(f"   Restaurant menu cache keys: {stats.get('restaurant_menu_cache_keys', 0)}")
        print(f"   Namespace counts: {stats.get('namespace_counts', {})}")
        print(f"   Cache hit ratio: {stats.get('cache_hit_ratio', 0):.2%}")
        print(f"   Memory usage: {stats.get('memory_usage', {}).get('percent', 0):.1f}%")
        
        # Get performance metrics
        performance = await make_request(session, "GET", "/cache/performance")
        print("\n📈 Cache Performance Metrics:")
        print(f"   Total requests: {performance.get('total_requests', 0)}")
        print(f"   Cache hits: {performance.get('cache_hits', 0)}")
        print(f"   Cache misses: {performance.get('cache_misses', 0)}")
        print(f"   Hit ratio: {performance.get('hit_ratio', 0):.2%}")
        print(f"   Miss ratio: {performance.get('miss_ratio', 0):.2%}")
        
        # Test cache clearing by namespace
        print("\n🗑️  Testing Cache Clearing by Namespace:")
        print("-" * 40)
        
        # Clear menu items cache
        clear_result = await make_request(session, "DELETE", "/cache/clear/menu-items")
        print(f"✅ {clear_result.get('message', 'Menu cache cleared')}")
        
        # Clear search cache
        clear_result = await make_request(session, "DELETE", "/cache/clear/search")
        print(f"✅ {clear_result.get('message', 'Search cache cleared')}")
        
        # Get stats after clearing
        stats_after = await make_request(session, "GET", "/cache/stats/detailed")
        print(f"📊 Cache keys after clearing: {stats_after.get('restaurant_menu_cache_keys', 0)}")

async def test_performance_comparison():
    """Test performance comparison endpoint"""
    print("\n📊 Testing Performance Comparison...")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Get performance comparison
        comparison = await make_request(session, "GET", "/demo/performance-comparison")
        
        print("📈 Performance Comparison Results:")
        print("-" * 35)
        
        for test_name, results in comparison.get('performance_comparison', {}).items():
            print(f"\n{test_name.replace('_', ' ').title()}:")
            print(f"   Database time: {results.get('database_time_ms', 0):.2f}ms")
            print(f"   Cache time: {results.get('cache_time_ms', 0):.2f}ms")
            print(f"   Improvement: {results.get('improvement_percent', 0):.1f}%")
        
        cache_perf = comparison.get('cache_performance', {})
        print(f"\n📊 Overall Cache Performance:")
        print(f"   Hit ratio: {cache_perf.get('hit_ratio', 0):.2%}")
        print(f"   Total requests: {cache_perf.get('total_requests', 0)}")

async def main():
    """Run all advanced cache tests"""
    print("🚀 Advanced Cache Testing for Restaurant-Menu System")
    print("=" * 65)
    print("This test suite validates multi-level caching, hierarchical invalidation,")
    print("and business logic caching features.")
    print()
    
    try:
        # Run all tests
        await test_multi_level_caching()
        await test_category_specific_caching()
        await test_analytics_caching()
        await test_hierarchical_invalidation()
        await test_cache_management()
        await test_performance_comparison()
        
        print("\n" + "=" * 65)
        print("✅ All advanced cache tests completed successfully!")
        print("📊 Check the application logs for detailed cache performance metrics")
        print("🔗 API Documentation: http://localhost:8000/docs")
        print("📈 Performance Dashboard: http://localhost:8000/cache/performance")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Make sure the application is running on http://localhost:8000")
        print("💡 Ensure Redis server is running")
        print("💡 Run '/demo/sample-data' first to create test data")

if __name__ == "__main__":
    asyncio.run(main()) 