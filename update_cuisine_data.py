"""
Database Migration Script: Add Cuisine Field to Restaurants
============================================================
This script updates all 7 existing restaurants in MongoDB with their correct cuisine types.

Cuisine Mapping:
- Swati Snacks: "Gujarati"
- Agashiye The House of MG: "Gujarati"
- PATEL & SONS: "Gujarati"
- Manek Chowk Pizza: "Italian"
- Honest Restaurant: "Multi-cuisine"
- Sankalp Restaurant: "South Indian"
- The Chocolate Room: "Cafe"

Usage: python update_cuisine_data.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection - use the actual connection string from database.py
MONGODB_URL = "mongodb://localhost:27017/food_db.6z9sntm.mongodb.net/?retryWrites=true&w=majority&appName=FoodAPICluster"
DATABASE_NAME = "food_db"  # Correct database name

# Restaurant cuisine mapping
CUISINE_MAPPING = {
    "Swati Snacks": "Gujarati",
    "Agashiye The House of MG": "Gujarati",
    "PATEL & SONS": "Gujarati",
    "Manek Chowk Pizza": "Italian",
    "Honest Restaurant": "Multi-cuisine",
    "Sankalp Restaurant": "South Indian",
    "The Chocolate Room": "Cafe"
}


async def update_restaurant_cuisines():
    """Update all restaurants with their correct cuisine types"""
    print("=" * 60)
    print("🔄 Starting Database Migration: Adding Cuisine Field")
    print("=" * 60)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    restaurants_collection = db["restaurants"]
    
    try:
        # Get count before update
        total_restaurants = await restaurants_collection.count_documents({})
        print(f"\n📊 Total restaurants in database: {total_restaurants}")
        
        updated_count = 0
        skipped_count = 0
        
        # Update each restaurant
        for restaurant_name, cuisine_type in CUISINE_MAPPING.items():
            print(f"\n🔍 Processing: {restaurant_name}")
            
            # Check if restaurant exists
            restaurant = await restaurants_collection.find_one({"name": restaurant_name})
            
            if restaurant:
                # Update with cuisine
                result = await restaurants_collection.update_one(
                    {"name": restaurant_name},
                    {"$set": {"cuisine": cuisine_type}}
                )
                
                if result.modified_count > 0:
                    print(f"   ✅ Updated: {restaurant_name} → Cuisine: {cuisine_type}")
                    updated_count += 1
                else:
                    print(f"   ⚠️  Already has cuisine: {restaurant_name} (Cuisine: {restaurant.get('cuisine', 'N/A')})")
                    skipped_count += 1
            else:
                print(f"   ❌ Not found: {restaurant_name}")
        
        # Verify updates
        print("\n" + "=" * 60)
        print("🔍 Verification: Checking Updated Restaurants")
        print("=" * 60)
        
        all_restaurants = await restaurants_collection.find({}).to_list(length=None)
        
        for restaurant in all_restaurants:
            name = restaurant.get("name", "Unknown")
            cuisine = restaurant.get("cuisine", "NOT SET")
            area = restaurant.get("area", "Unknown")
            print(f"✓ {name} ({area}) - Cuisine: {cuisine}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📈 Migration Summary")
        print("=" * 60)
        print(f"✅ Successfully Updated: {updated_count}")
        print(f"⚠️  Already Had Cuisine: {skipped_count}")
        print(f"📊 Total Restaurants: {len(all_restaurants)}")
        print("=" * 60)
        print("🎉 Migration Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    print("\n🚀 Starting Cuisine Migration Script...")
    asyncio.run(update_restaurant_cuisines())
    print("\n✅ Script execution completed!\n")
