"""
Migration script to consolidate restaurant entries and update to new model structure.
- Groups items under single restaurant entry (by name+area)
- Renames 'cuisine' and 'item_name' fields to 'item_name' in items list
- Removes duplicate restaurant entries
"""
import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Restaurant
import os

# MongoDB connection - use environment variable for security
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

async def migrate_restaurants():
    client = AsyncIOMotorClient(MONGODB_URL, tlsAllowInvalidCertificates=True)
    db = client["food_db"]
    await init_beanie(database=db, document_models=[Restaurant])
    all_restaurants = await Restaurant.find_all().to_list()
    
    print(f"Found {len(all_restaurants)} restaurant entries to migrate...")
    
    grouped = {}
    for r in all_restaurants:
        key = (r.name, r.area)
        # Create item dict from old structure
        item = {
            "item_name": getattr(r, "item_name", getattr(r, "cuisine", "")),
            "price": getattr(r, "price", None),
            "rating": getattr(r, "rating", None),
            "total_ratings": getattr(r, "total_ratings", None),
            "description": getattr(r, "description", None),
            "image_url": getattr(r, "image_url", None),
            "calories": getattr(r, "calories", None),
            "preparation_time": getattr(r, "preparation_time", None),
        }
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    # Remove all old entries
    print(f"Removing {len(all_restaurants)} old entries...")
    for r in all_restaurants:
        await r.delete()
    
    # Insert grouped entries
    print(f"Creating {len(grouped)} consolidated restaurant entries...")
    for (name, area), items in grouped.items():
        new_restaurant = Restaurant(name=name, area=area, items=items)
        await new_restaurant.insert()
        print(f"  ✅ Created '{name}' in {area} with {len(items)} items")
    
    print(f"\n✅ Migration complete! Consolidated into {len(grouped)} restaurants.")

if __name__ == "__main__":
    asyncio.run(migrate_restaurants())
