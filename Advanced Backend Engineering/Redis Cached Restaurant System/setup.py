#!/usr/bin/env python3
"""
Setup script for Redis Cached Restaurant System
Initializes database and provides setup instructions
"""

import asyncio
import sys
import subprocess
import platform
from database import create_tables

def check_redis_installation():
    """Check if Redis is installed and running"""
    try:
        # Try to connect to Redis
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print("❌ Redis is not running or not installed")
        print(f"Error: {e}")
        return False

def install_redis_instructions():
    """Provide Redis installation instructions based on OS"""
    system = platform.system().lower()
    
    print("\n📋 Redis Installation Instructions:")
    print("=" * 50)
    
    if system == "darwin":  # macOS
        print("On macOS (using Homebrew):")
        print("1. Install Redis: brew install redis")
        print("2. Start Redis: brew services start redis")
        print("3. Verify: redis-cli ping")
    elif system == "linux":
        print("On Ubuntu/Debian:")
        print("1. Install Redis: sudo apt update && sudo apt install redis-server")
        print("2. Start Redis: sudo systemctl start redis-server")
        print("3. Enable Redis: sudo systemctl enable redis-server")
        print("4. Verify: redis-cli ping")
    elif system == "windows":
        print("On Windows:")
        print("1. Download Redis from: https://redis.io/download")
        print("2. Install Redis following the installation guide")
        print("3. Start Redis server")
        print("4. Verify: redis-cli ping")
    else:
        print("Please install Redis following the official guide:")
        print("https://redis.io/download")

async def initialize_database():
    """Initialize the database with tables"""
    try:
        print("🗄️  Initializing database...")
        await create_tables()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'aiosqlite',
        'pydantic',
        'redis',
        'fastapi-cache2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install missing packages with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def print_startup_instructions():
    """Print startup instructions"""
    print("\n🚀 Startup Instructions:")
    print("=" * 30)
    print("1. Ensure Redis is running")
    print("2. Start the application: python main.py")
    print("3. Access the API at: http://localhost:8000")
    print("4. View documentation at: http://localhost:8000/docs")
    print("5. Run tests: python test_cache.py")

async def main():
    """Main setup function"""
    print("🔧 Redis Cached Restaurant System Setup")
    print("=" * 50)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        return
    
    # Check Redis
    print("\n🔍 Checking Redis installation...")
    if not check_redis_installation():
        install_redis_instructions()
        print("\n❌ Please install and start Redis, then run this script again")
        return
    
    # Initialize database
    print("\n🗄️  Setting up database...")
    if not await initialize_database():
        print("\n❌ Database setup failed")
        return
    
    # Print startup instructions
    print_startup_instructions()
    
    print("\n✅ Setup completed successfully!")
    print("🎉 You're ready to start the application!")

if __name__ == "__main__":
    asyncio.run(main()) 