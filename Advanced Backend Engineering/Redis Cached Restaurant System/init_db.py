import asyncio
from database import create_tables

async def init_db():
    """Initialize the database by creating all tables"""
    try:
        await create_tables()
        print("Database initialized successfully!")
        print("Tables created: restaurants")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    asyncio.run(init_db()) 