"""
Test MongoDB Connection Script
Tests different connection string formats to find the correct one
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Test different connection strings
test_connections = [
    ("With auth to food_db", "mongodb://admin:secure_password_here@localhost:27017/food_db?authSource=admin"),
    ("With auth no db", "mongodb://admin:secure_password_here@localhost:27017/?authSource=admin"),
    ("Without auth", "mongodb://localhost:27017/food_db"),
]

async def test_connection(name, uri):
    """Test a single connection string"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URI: {uri}")
    print('='*60)
    
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        # Try to ping the server
        await client.admin.command('ping')
        print("✅ Connection successful!")
        
        # List databases
        dbs = await client.list_database_names()
        print(f"📚 Available databases: {dbs}")
        
        # Try to access food_db
        db = client.food_db
        collections = await db.list_collection_names()
        print(f"📦 Collections in food_db: {collections}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    """Test all connection strings"""
    print("\n🔍 MongoDB Connection Tester")
    print("=" * 60)
    
    for name, uri in test_connections:
        success = await test_connection(name, uri)
        if success:
            print(f"\n🎉 Working connection string found!")
            print(f"Use this in your .env file:")
            print(f'MONGODB_URI="{uri}"')
            break
    else:
        print(f"\n❌ No working connection string found.")
        print(f"Possible issues:")
        print(f"  1. MongoDB container is not running")
        print(f"  2. Wrong username/password")
        print(f"  3. MongoDB not accessible from localhost")

if __name__ == "__main__":
    asyncio.run(main())
