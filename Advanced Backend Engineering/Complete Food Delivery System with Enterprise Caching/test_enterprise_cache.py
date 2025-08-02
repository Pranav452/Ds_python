#!/usr/bin/env python3
"""
Enterprise Caching System Test Suite
Tests all advanced enterprise caching features and patterns
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseCacheTester:
    """Comprehensive test suite for enterprise caching system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request and return response"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return await response.json()
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    return await response.json()
            else:
                raise ValueError(f"Unsupported method: {method}")
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}
    
    def log_test_result(self, test_name: str, success: bool, response_time: float, details: str = ""):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "response_time_ms": response_time,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name} - {response_time:.2f}ms - {details}")
    
    async def test_cache_health(self):
        """Test cache health endpoints"""
        logger.info("Testing cache health endpoints...")
        
        # Test basic health
        start_time = time.time()
        response = await self.make_request("GET", "/cache/health")
        response_time = (time.time() - start_time) * 1000
        
        success = "status" in response and response["status"] == "healthy"
        self.log_test_result("Cache Health Check", success, response_time, f"Status: {response.get('status', 'unknown')}")
        
        # Test detailed health
        start_time = time.time()
        response = await self.make_request("GET", "/cache/health/detailed")
        response_time = (time.time() - start_time) * 1000
        
        success = "status" in response and response["status"] == "healthy"
        self.log_test_result("Detailed Cache Health", success, response_time, f"Redis version: {response.get('redis_version', 'unknown')}")
    
    async def test_cache_statistics(self):
        """Test cache statistics endpoints"""
        logger.info("Testing cache statistics endpoints...")
        
        # Test basic stats
        start_time = time.time()
        response = await self.make_request("GET", "/cache/stats/namespaces")
        response_time = (time.time() - start_time) * 1000
        
        success = "namespaces" in response
        self.log_test_result("Cache Statistics", success, response_time, f"Namespaces: {len(response.get('namespaces', {}))}")
        
        # Test detailed stats
        start_time = time.time()
        response = await self.make_request("GET", "/cache/stats/detailed")
        response_time = (time.time() - start_time) * 1000
        
        success = "cache_overview" in response
        self.log_test_result("Detailed Cache Statistics", success, response_time, f"Total keys: {response.get('cache_overview', {}).get('total_keys', 0)}")
    
    async def test_cache_operations(self):
        """Test cache operations"""
        logger.info("Testing cache operations...")
        
        # Test memory usage
        start_time = time.time()
        response = await self.make_request("GET", "/cache/memory-usage")
        response_time = (time.time() - start_time) * 1000
        
        success = "memory_usage" in response
        self.log_test_result("Memory Usage", success, response_time, f"Usage: {response.get('memory_usage', {}).get('percent', 0):.1f}%")
        
        # Test clear expired
        start_time = time.time()
        response = await self.make_request("DELETE", "/cache/clear/expired")
        response_time = (time.time() - start_time) * 1000
        
        success = "message" in response
        self.log_test_result("Clear Expired Keys", success, response_time, response.get("message", ""))
    
    async def test_cache_warming(self):
        """Test cache warming functionality"""
        logger.info("Testing cache warming...")
        
        # Test restaurants cache warming
        start_time = time.time()
        response = await self.make_request("POST", "/cache/warm/restaurants")
        response_time = (time.time() - start_time) * 1000
        
        success = "message" in response and "warming started" in response["message"]
        self.log_test_result("Restaurants Cache Warming", success, response_time, response.get("message", ""))
        
        # Test menu items cache warming
        start_time = time.time()
        response = await self.make_request("POST", "/cache/warm/menu-items")
        response_time = (time.time() - start_time) * 1000
        
        success = "message" in response and "warming started" in response["message"]
        self.log_test_result("Menu Items Cache Warming", success, response_time, response.get("message", ""))
    
    async def test_enterprise_patterns(self):
        """Test enterprise caching patterns"""
        logger.info("Testing enterprise caching patterns...")
        
        # Test write-through pattern
        start_time = time.time()
        response = await self.make_request("GET", "/enterprise/patterns/write-through")
        response_time = (time.time() - start_time) * 1000
        
        success = "pattern" in response and response["pattern"] == "write-through"
        self.log_test_result("Write-Through Pattern", success, response_time, f"Pattern: {response.get('pattern', 'unknown')}")
        
        # Test cache-aside pattern
        start_time = time.time()
        response = await self.make_request("GET", "/enterprise/patterns/cache-aside")
        response_time = (time.time() - start_time) * 1000
        
        success = "pattern" in response and response["pattern"] == "cache-aside"
        self.log_test_result("Cache-Aside Pattern", success, response_time, f"Pattern: {response.get('pattern', 'unknown')}")
    
    async def test_cache_invalidation(self):
        """Test cache invalidation patterns"""
        logger.info("Testing cache invalidation...")
        
        # Test cascade invalidation
        start_time = time.time()
        response = await self.make_request("POST", "/enterprise/invalidation/cascade")
        response_time = (time.time() - start_time) * 1000
        
        success = "pattern" in response and response["pattern"] == "cascade_invalidation"
        self.log_test_result("Cascade Invalidation", success, response_time, f"Pattern: {response.get('pattern', 'unknown')}")
    
    async def test_predictive_warming(self):
        """Test predictive cache warming"""
        logger.info("Testing predictive cache warming...")
        
        start_time = time.time()
        response = await self.make_request("POST", "/enterprise/warming/predictive")
        response_time = (time.time() - start_time) * 1000
        
        success = "pattern" in response and response["pattern"] == "predictive_warming"
        self.log_test_result("Predictive Warming", success, response_time, f"Pattern: {response.get('pattern', 'unknown')}")
    
    async def test_cache_analytics(self):
        """Test cache analytics"""
        logger.info("Testing cache analytics...")
        
        # Test pattern analytics
        start_time = time.time()
        response = await self.make_request("GET", "/enterprise/analytics/patterns")
        response_time = (time.time() - start_time) * 1000
        
        success = "cache_patterns" in response
        self.log_test_result("Cache Pattern Analytics", success, response_time, f"Patterns analyzed: {len(response.get('cache_patterns', {}))}")
        
        # Test performance report
        start_time = time.time()
        response = await self.make_request("GET", "/enterprise/performance/report")
        response_time = (time.time() - start_time) * 1000
        
        success = "performance_report" in response
        self.log_test_result("Performance Report", success, response_time, f"Report generated: {response.get('performance_report', {}).get('summary', {}).get('status', 'unknown')}")
    
    async def test_cache_security(self):
        """Test cache security features"""
        logger.info("Testing cache security...")
        
        # Test access validation
        start_time = time.time()
        response = await self.make_request("GET", "/enterprise/security/validate/restaurants?user_id=1")
        response_time = (time.time() - start_time) * 1000
        
        success = "has_access" in response
        self.log_test_result("Cache Access Validation", success, response_time, f"Has access: {response.get('has_access', False)}")
        
        # Test secure key generation
        start_time = time.time()
        response = await self.make_request("POST", "/enterprise/security/secure-key", {
            "key": "test-key",
            "namespace": "test-namespace"
        })
        response_time = (time.time() - start_time) * 1000
        
        success = "secure_key" in response
        self.log_test_result("Secure Key Generation", success, response_time, f"Key generated: {bool(response.get('secure_key'))}")
    
    async def test_namespace_operations(self):
        """Test namespace-specific operations"""
        logger.info("Testing namespace operations...")
        
        # Test get keys by namespace
        start_time = time.time()
        response = await self.make_request("GET", "/cache/keys/restaurants")
        response_time = (time.time() - start_time) * 1000
        
        success = "namespace" in response
        self.log_test_result("Get Keys by Namespace", success, response_time, f"Namespace: {response.get('namespace', 'unknown')}, Keys: {response.get('total_keys', 0)}")
        
        # Test namespace performance
        start_time = time.time()
        response = await self.make_request("GET", "/cache/performance/namespace/restaurants")
        response_time = (time.time() - start_time) * 1000
        
        success = "namespace" in response
        self.log_test_result("Namespace Performance", success, response_time, f"Namespace: {response.get('namespace', 'unknown')}, Hit ratio: {response.get('hit_ratio', 0):.2%}")
    
    async def test_cache_clearing(self):
        """Test cache clearing operations"""
        logger.info("Testing cache clearing operations...")
        
        # Test clear menu items
        start_time = time.time()
        response = await self.make_request("DELETE", "/cache/clear/menu-items")
        response_time = (time.time() - start_time) * 1000
        
        success = "message" in response and "cleared successfully" in response["message"]
        self.log_test_result("Clear Menu Items Cache", success, response_time, response.get("message", ""))
        
        # Test clear restaurants
        start_time = time.time()
        response = await self.make_request("DELETE", "/cache/clear/restaurants")
        response_time = (time.time() - start_time) * 1000
        
        success = "message" in response and "cleared successfully" in response["message"]
        self.log_test_result("Clear Restaurants Cache", success, response_time, response.get("message", ""))
        
        # Test clear orders
        start_time = time.time()
        response = await self.make_request("DELETE", "/cache/clear/orders")
        response_time = (time.time() - start_time) * 1000
        
        success = "message" in response and "cleared successfully" in response["message"]
        self.log_test_result("Clear Orders Cache", success, response_time, response.get("message", ""))
        
        # Test clear analytics
        start_time = time.time()
        response = await self.make_request("DELETE", "/cache/clear/analytics")
        response_time = (time.time() - start_time) * 1000
        
        success = "message" in response and "cleared successfully" in response["message"]
        self.log_test_result("Clear Analytics Cache", success, response_time, response.get("message", ""))
    
    async def test_performance_monitoring(self):
        """Test performance monitoring endpoints"""
        logger.info("Testing performance monitoring...")
        
        # Test cache performance analytics
        start_time = time.time()
        response = await self.make_request("GET", "/analytics/cache-performance")
        response_time = (time.time() - start_time) * 1000
        
        success = "hit_ratio" in response
        self.log_test_result("Cache Performance Analytics", success, response_time, f"Hit ratio: {response.get('hit_ratio', 0):.2%}")
        
        # Test popular data
        start_time = time.time()
        response = await self.make_request("GET", "/analytics/popular-data")
        response_time = (time.time() - start_time) * 1000
        
        success = "popular_items" in response
        self.log_test_result("Popular Data Analytics", success, response_time, f"Popular items: {len(response.get('popular_items', []))}")
    
    async def test_load_performance(self):
        """Test load performance"""
        logger.info("Testing load performance...")
        
        # Test load test endpoint
        start_time = time.time()
        response = await self.make_request("GET", "/demo/load-test/restaurants")
        response_time = (time.time() - start_time) * 1000
        
        success = "performance_metrics" in response
        self.log_test_result("Load Performance Test", success, response_time, f"Test completed: {response.get('test_completed', False)}")
    
    async def run_all_tests(self):
        """Run all enterprise caching tests"""
        logger.info("🚀 Starting Enterprise Caching System Tests")
        logger.info("=" * 60)
        
        test_methods = [
            self.test_cache_health,
            self.test_cache_statistics,
            self.test_cache_operations,
            self.test_cache_warming,
            self.test_enterprise_patterns,
            self.test_cache_invalidation,
            self.test_predictive_warming,
            self.test_cache_analytics,
            self.test_cache_security,
            self.test_namespace_operations,
            self.test_cache_clearing,
            self.test_performance_monitoring,
            self.test_load_performance
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
                await asyncio.sleep(0.5)  # Small delay between tests
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed: {e}")
                self.log_test_result(test_method.__name__, False, 0, f"Error: {e}")
        
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        logger.info("=" * 60)
        logger.info("📊 ENTERPRISE CACHING SYSTEM TEST SUMMARY")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        # Calculate average response time
        response_times = [result["response_time_ms"] for result in self.test_results if result["response_time_ms"] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Average Response Time: {avg_response_time:.2f}ms")
        
        # Show failed tests
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['test_name']}: {result['details']}")
        
        # Show performance highlights
        logger.info("\n🏆 Performance Highlights:")
        fastest_test = min(self.test_results, key=lambda x: x["response_time_ms"])
        slowest_test = max(self.test_results, key=lambda x: x["response_time_ms"])
        
        logger.info(f"  Fastest: {fastest_test['test_name']} - {fastest_test['response_time_ms']:.2f}ms")
        logger.info(f"  Slowest: {slowest_test['test_name']} - {slowest_test['response_time_ms']:.2f}ms")
        
        logger.info("\n🎯 Enterprise Caching System Test Complete!")
        logger.info("=" * 60)

async def main():
    """Main test runner"""
    async with EnterpriseCacheTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    print("🧪 Enterprise Caching System Test Suite")
    print("Make sure the FastAPI application is running on http://localhost:8000")
    print("Make sure Redis is running and accessible")
    print("=" * 60)
    
    asyncio.run(main()) 