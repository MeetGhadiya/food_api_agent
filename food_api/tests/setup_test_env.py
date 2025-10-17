"""
Test Database Management Helper Script
=======================================

Purpose:
- Manually initialize or drop the test database
- Reset test environment to clean state
- Debug database connection issues
- Verify Beanie initialization

Usage:
    python tests/setup_test_env.py --init    # Initialize test database
    python tests/setup_test_env.py --drop    # Drop test database
    python tests/setup_test_env.py --reset   # Drop and reinitialize
    python tests/setup_test_env.py --check   # Check database status

Author: FoodieExpress Development Team
Date: October 2025
"""

import asyncio
import argparse
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import User, Restaurant, Order, Review


class TestDatabaseManager:
    """Manage test database lifecycle"""
    
    def __init__(self, mongodb_uri: str = None):
        """
        Initialize database manager.
        
        Args:
            mongodb_uri: MongoDB connection string (defaults to localhost)
        """
        self.mongodb_uri = mongodb_uri or os.getenv(
            "MONGODB_URI", 
            "mongodb://localhost:27017"
        )
        self.db_name = "food_db_test"
        self.client = None
        self.database = None
    
    async def connect(self):
        """Establish database connection"""
        print(f"🔗 Connecting to MongoDB: {self.mongodb_uri}")
        self.client = AsyncIOMotorClient(self.mongodb_uri)
        self.database = self.client[self.db_name]
        print(f"✅ Connected to database: {self.db_name}")
    
    async def initialize_beanie(self):
        """Initialize Beanie ODM with all models"""
        print("🔧 Initializing Beanie ODM...")
        
        await init_beanie(
            database=self.database,
            document_models=[User, Restaurant, Order, Review]
        )
        
        print("✅ Beanie initialized with models:")
        print("   - User")
        print("   - Restaurant")
        print("   - Order")
        print("   - Review")
    
    async def drop_database(self):
        """Drop the test database"""
        print(f"🗑️  Dropping database: {self.db_name}")
        await self.client.drop_database(self.db_name)
        print("✅ Database dropped successfully")
    
    async def check_status(self):
        """Check database and collection status"""
        print("\n📊 Database Status:")
        print(f"   Database: {self.db_name}")
        
        # List all collections
        collections = await self.database.list_collection_names()
        print(f"   Collections: {len(collections)}")
        
        if collections:
            for collection_name in collections:
                count = await self.database[collection_name].count_documents({})
                print(f"      - {collection_name}: {count} documents")
        else:
            print("      (No collections found)")
        
        # Check Beanie initialization
        try:
            await self.initialize_beanie()
            
            # Count documents in each model
            user_count = await User.count()
            restaurant_count = await Restaurant.count()
            order_count = await Order.count()
            review_count = await Review.count()
            
            print(f"\n📈 Document Counts:")
            print(f"   - Users: {user_count}")
            print(f"   - Restaurants: {restaurant_count}")
            print(f"   - Orders: {order_count}")
            print(f"   - Reviews: {review_count}")
            
            print("\n✅ Beanie ODM is properly initialized")
        except Exception as e:
            print(f"\n❌ Beanie initialization failed: {e}")
    
    async def reset_database(self):
        """Drop and reinitialize database"""
        print("🔄 Resetting test database...")
        await self.drop_database()
        await self.initialize_beanie()
        print("✅ Database reset complete")
    
    async def create_sample_data(self):
        """Create sample test data"""
        print("\n📝 Creating sample test data...")
        
        await self.initialize_beanie()
        
        # Create sample restaurant
        restaurant = Restaurant(
            name="Test Restaurant",
            area="Test Area",
            cuisine="Test Cuisine",
            items=[
                {"item_name": "Test Pizza", "price": 250},
                {"item_name": "Test Pasta", "price": 300}
            ]
        )
        await restaurant.insert()
        print("   ✅ Created sample restaurant")
        
        # Create sample user
        from app.security import hash_password
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("testpass123"),
            first_name="Test",
            last_name="User",
            role="user"
        )
        await user.insert()
        print("   ✅ Created sample user")
        
        print("\n✅ Sample data created successfully")
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Database connection closed")


async def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="Test Database Management Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_test_env.py --init           # Initialize database
  python setup_test_env.py --drop           # Drop database
  python setup_test_env.py --reset          # Drop and reinitialize
  python setup_test_env.py --check          # Check status
  python setup_test_env.py --sample         # Create sample data
  python setup_test_env.py --reset --sample # Reset and add sample data
        """
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize Beanie and create collections"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop the test database"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and reinitialize database"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check database status and document counts"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Create sample test data"
    )
    parser.add_argument(
        "--uri",
        type=str,
        help="MongoDB connection URI (default: mongodb://localhost:27017)"
    )
    
    args = parser.parse_args()
    
    # If no action specified, show help
    if not any([args.init, args.drop, args.reset, args.check, args.sample]):
        parser.print_help()
        return
    
    manager = TestDatabaseManager(mongodb_uri=args.uri)
    
    try:
        await manager.connect()
        
        if args.drop:
            await manager.drop_database()
        
        if args.reset:
            await manager.reset_database()
        
        if args.init:
            await manager.initialize_beanie()
        
        if args.sample:
            await manager.create_sample_data()
        
        if args.check:
            await manager.check_status()
        
        print("\n✅ All operations completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        manager.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Test Database Management Helper")
    print("FoodieExpress Agent Bot - Test Suite")
    print("=" * 60)
    print()
    
    asyncio.run(main())
