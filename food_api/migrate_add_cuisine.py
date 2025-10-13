"""
Migration Script: Add Cuisine Field to Existing Restaurants
This script updates all 7 restaurants in the database to include a cuisine field.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Restaurant

# Restaurant name to cuisine mapping
CUISINE_MAPPING = {
    "Swati Snacks": "Gujarati",
    "Agashiye The House of MG": "Gujarati",
    "PATEL & SONS": "Gujarati",
    "Manek Chowk Pizza": "Italian",
    "Honest Restaurant": "North Indian",
    "Sankalp Restaurant": "South Indian",
    "The Chocolate Room": "Desserts & Beverages"
}

async def migrate_cuisines():
    """Add cuisine field to all existing restaurants"""
    
    # MongoDB connection - use the same URL as in database.py
    MONGODB_URL = "mongodb://localhost:27017/food_db.6z9sntm.mongodb.net/?retryWrites=true&w=majority&appName=FoodAPICluster"
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(
        MONGODB_URL,
        uuidRepresentation="standard",
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    database = client.food_db
    
    print("=" * 70)
    print("MIGRATION: Adding Cuisine Field to Restaurants")
    print("=" * 70)
    
    # Access the restaurants collection directly
    restaurants_collection = database.restaurants
    
    # Get all restaurants
    restaurants = await restaurants_collection.find({}).to_list(length=None)
    
    print(f"\nFound {len(restaurants)} restaurants to update.\n")
    
    updated_count = 0
    
    for restaurant in restaurants:
        restaurant_name = restaurant.get('name', 'Unknown')
        
        # Get cuisine from mapping
        cuisine = CUISINE_MAPPING.get(restaurant_name, "Multi-Cuisine")
        
        # Update the restaurant document
        await restaurants_collection.update_one(
            {'_id': restaurant['_id']},
            {'$set': {'cuisine': cuisine}}
        )
        
        updated_count += 1
        print(f"✅ Updated '{restaurant_name}' → Cuisine: {cuisine}")
    
    print("\n" + "=" * 70)
    print(f"Migration Complete! Updated {updated_count} restaurants.")
    print("=" * 70)
    
    # Now initialize Beanie with the updated model to verify
    print("\nVerifying updates with Beanie...\n")
    await init_beanie(database=database, document_models=[Restaurant])
    
    # Verify the update
    restaurants = await Restaurant.find_all().to_list()
    
    for restaurant in restaurants:
        print(f"🏪 {restaurant.name}")
        print(f"   📍 Location: {restaurant.area}")
        print(f"   🍽️  Cuisine: {restaurant.cuisine}")
        print(f"   📊 Items: {len(restaurant.items)}")
        print()

if __name__ == "__main__":
    print("\n🚀 Starting Migration...")
    asyncio.run(migrate_cuisines())
    print("\n✅ Migration finished successfully!")
