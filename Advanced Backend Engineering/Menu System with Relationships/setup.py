#!/usr/bin/env python3
"""
Setup script for Restaurant-Menu Management System
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"Python version: {sys.version}")

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ["logs", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("Directories created successfully!")

async def initialize_database():
    """Initialize the database with sample data"""
    print("Initializing database...")
    try:
        # Import and run the init_db module
        from init_db import init_database
        await init_database()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

def create_env_file():
    """Create environment file with configuration"""
    env_content = """# Restaurant-Menu Management System Configuration

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./restaurant_menu.db

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Development Settings
DEBUG=true
LOG_LEVEL=INFO

# API Configuration
API_TITLE=Restaurant-Menu Management System
API_VERSION=2.0.0
API_DESCRIPTION=A comprehensive restaurant management system with menu management and relationships
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("Environment file created successfully!")

def create_startup_script():
    """Create startup script for easy launching"""
    script_content = """#!/usr/bin/env python3
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
"""
    
    with open("start_server.py", "w") as f:
        f.write(script_content)
    
    # Make the script executable on Unix-like systems
    try:
        os.chmod("start_server.py", 0o755)
    except:
        pass
    
    print("Startup script created successfully!")

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("Restaurant-Menu Management System Setup Complete!")
    print("="*60)
    print("\nTo start the server:")
    print("  python main.py")
    print("  OR")
    print("  python start_server.py")
    print("\nTo run tests:")
    print("  python test_api.py")
    print("\nAPI Documentation:")
    print("  http://localhost:8000/docs")
    print("  http://localhost:8000/redoc")
    print("\nAPI Base URL:")
    print("  http://localhost:8000")
    print("\nSample API calls:")
    print("  # Get all restaurants")
    print("  curl http://localhost:8000/restaurants/")
    print("\n  # Get all menu items")
    print("  curl http://localhost:8000/menu-items/")
    print("\n  # Search vegetarian menu items")
    print("  curl http://localhost:8000/menu-items/search?vegetarian=true")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("Restaurant-Menu Management System Setup")
    print("="*40)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Create environment file
    create_env_file()
    
    # Create startup script
    create_startup_script()
    
    # Initialize database
    print("\nInitializing database...")
    asyncio.run(initialize_database())
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main() 