"""
Simple script to update restaurant data
"""
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.food_delivery
restaurants = db.restaurants

# Clear old data
print("🗑️  Clearing old data...")
restaurants.delete_many({})

# Add new data
dummy_data = [
    {
        "name": "Swati Snacks", "area": "Ashram Road", "cuisine": "BHEL",
        "item_name": "Bhel Puri", "price": 80.0, "rating": 4.5, "total_ratings": 450,
        "description": "Crispy puffed rice with tangy tamarind chutney",
        "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400",
        "calories": 250, "preparation_time": "10-15 mins"
    },
    {
        "name": "Swati Snacks", "area": "Ashram Road", "cuisine": "PANI PURI",
        "item_name": "Pani Puri", "price": 60.0, "rating": 4.7, "total_ratings": 620,
        "description": "Crispy hollow puris with spicy tangy water",
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400",
        "calories": 200, "preparation_time": "10-15 mins"
    },
    {
        "name": "Agashiye The House of MG", "area": "Lal Darwaja", "cuisine": "DALPAKVAN",
        "item_name": "Dal Pakwan", "price": 150.0, "rating": 4.6, "total_ratings": 280,
        "description": "Sindhi breakfast - crispy bread with dal",
        "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400",
        "calories": 420, "preparation_time": "20-25 mins"
    },
    {
        "name": "PATEL & SONS", "area": "Maninagar", "cuisine": "GUJARATI THALI",
        "item_name": "Gujarati Thali", "price": 250.0, "rating": 4.8, "total_ratings": 890,
        "description": "Complete traditional Gujarati meal",
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400",
        "calories": 800, "preparation_time": "30-40 mins"
    },
    {
        "name": "Honest Restaurant", "area": "CG Road", "cuisine": "BUTTER CHICKEN",
        "item_name": "Butter Chicken", "price": 320.0, "rating": 4.9, "total_ratings": 1250,
        "description": "Tender chicken in rich creamy gravy",
        "image_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400",
        "calories": 720, "preparation_time": "30-40 mins"
    },
    {
        "name": "Manek Chowk Pizza", "area": "Manek Chowk", "cuisine": "MARGHERITA PIZZA",
        "item_name": "Margherita Pizza", "price": 180.0, "rating": 4.6, "total_ratings": 520,
        "description": "Classic Italian pizza with fresh mozzarella",
        "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400",
        "calories": 650, "preparation_time": "25-30 mins"
    },
]

print(f"📝 Adding {len(dummy_data)} restaurants...")
restaurants.insert_many(dummy_data)

print("✅ Done! Added restaurants:")
for r in restaurants.find():
    print(f"  • {r['name']} - {r['item_name']} (₹{r['price']})")

client.close()
