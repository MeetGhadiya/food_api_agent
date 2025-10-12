"""
Script to reorganize restaurants in the database:
1. Group restaurants by name and area
2. Each restaurant should have multiple items (not multiple entries)
3. Rename 'cuisine' to 'item_name'
"""
import asyncio
import sys
sys.path.insert(0, 'e:/agent workspace/agent/food_api_agent/food_api')

from motor.motor_asyncio import AsyncIOMotorClient
from collections import defaultdict

MONGO_URL = "mongodb+srv://foodapi_user:Meet7805@foodapicluster.6z9sntm.mongodb.net/?retryWrites=true&w=majority&appName=FoodAPICluster"

async def reorganize_restaurants():
    """Reorganize restaurant data to avoid duplicates"""
    
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
    db = client.food_db
    collection = db.restaurants
    
    print("Fetching all restaurants...")
    restaurants = await collection.find().to_list(length=None)
    print(f"Found {len(restaurants)} restaurant entries")
    
    # Group by restaurant name and area
    grouped = defaultdict(list)
    for rest in restaurants:
        key = (rest.get('name', ''), rest.get('area', ''))
        grouped[key].append(rest)
    
    print(f"\nGrouped into {len(grouped)} unique restaurants")
    
    # Show what we found
    print("\n--- Restaurant Groups ---")
    for (name, area), items in grouped.items():
        if len(items) > 1:
            print(f"\n🏪 {name} ({area}) - {len(items)} items:")
            for item in items:
                cuisine = item.get('cuisine') or item.get('item_name', 'Unknown')
                print(f"   • {cuisine}")
    
    # Ask for confirmation
    print("\n" + "="*60)
    response = input("Do you want to reorganize the database? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("\n🔄 Reorganizing database...")
    
    # Clear existing data
    await collection.delete_many({})
    print("✅ Cleared old data")
    
    # Create new organized structure
    new_restaurants = []
    for (name, area), items in grouped.items():
        # Take the first item's complete data as base
        base = items[0].copy()
        
        # If there's only one item
        if len(items) == 1:
            item = items[0]
            new_doc = {
                'name': name,
                'area': area,
                'item_name': item.get('item_name') or item.get('cuisine', 'Unknown'),
                'price': item.get('price'),
                'rating': item.get('rating'),
                'total_ratings': item.get('total_ratings'),
                'description': item.get('description'),
                'image_url': item.get('image_url'),
                'calories': item.get('calories'),
                'preparation_time': item.get('preparation_time')
            }
            new_restaurants.append(new_doc)
        else:
            # Multiple items - create separate documents with proper item_name
            for item in items:
                new_doc = {
                    'name': name,
                    'area': area,
                    'item_name': item.get('item_name') or item.get('cuisine', 'Unknown'),
                    'price': item.get('price'),
                    'rating': item.get('rating'),
                    'total_ratings': item.get('total_ratings'),
                    'description': item.get('description'),
                    'image_url': item.get('image_url'),
                    'calories': item.get('calories'),
                    'preparation_time': item.get('preparation_time')
                }
                new_restaurants.append(new_doc)
    
    # Insert new data
    if new_restaurants:
        result = await collection.insert_many(new_restaurants)
        print(f"✅ Inserted {len(result.inserted_ids)} restaurant items")
    
    # Show final structure
    print("\n--- Final Restaurant Structure ---")
    final = await collection.find().to_list(length=None)
    
    by_name = defaultdict(list)
    for rest in final:
        by_name[rest['name']].append(rest)
    
    for name, items in sorted(by_name.items()):
        areas = set(item['area'] for item in items)
        print(f"\n🏪 {name} ({', '.join(areas)})")
        for item in items:
            print(f"   • {item['item_name']}")
            if item.get('price'):
                print(f"     ₹{item['price']} | {item.get('rating', 'N/A')}⭐")
    
    print(f"\n✅ Database reorganization complete!")
    print(f"Total items: {len(final)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(reorganize_restaurants())
