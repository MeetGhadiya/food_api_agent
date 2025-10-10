"""
Script to add dummy restaurant data with rich information
Run this after updating the models
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.food_delivery
restaurants_collection = db.restaurants

# Dummy data with rich information
dummy_restaurants = [
    {
        "name": "Swati Snacks",
        "area": "Ashram Road, Ahmedabad",
        "cuisine": "BHEL",
        "item_name": "Bhel Puri",
        "price": 80.0,
        "rating": 4.5,
        "total_ratings": 450,
        "description": "Crispy puffed rice mixed with tangy tamarind chutney, onions, tomatoes, and sev. A perfect street food snack!",
        "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400",
        "calories": 250,
        "preparation_time": "10-15 mins"
    },
    {
        "name": "Swati Snacks",
        "area": "Ashram Road, Ahmedabad",
        "cuisine": "PANI PURI",
        "item_name": "Pani Puri",
        "price": 60.0,
        "rating": 4.7,
        "total_ratings": 620,
        "description": "Crispy hollow puris filled with spicy tangy water, potatoes, and chickpeas. An absolute delight!",
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400",
        "calories": 200,
        "preparation_time": "10-15 mins"
    },
    {
        "name": "Agashiye The House of MG",
        "area": "Lal Darwaja, Ahmedabad",
        "cuisine": "DALPAKVAN",
        "item_name": "Dal Pakwan",
        "price": 150.0,
        "rating": 4.6,
        "total_ratings": 280,
        "description": "Traditional Sindhi breakfast - crispy fried flatbread served with flavorful chana dal curry.",
        "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400",
        "calories": 420,
        "preparation_time": "20-25 mins"
    },
    {
        "name": "Agashiye The House of MG",
        "area": "Lal Darwaja, Ahmedabad",
        "cuisine": "THEPLA",
        "item_name": "Methi Thepla",
        "price": 120.0,
        "rating": 4.4,
        "total_ratings": 195,
        "description": "Soft, flavorful flatbread made with fenugreek leaves and spices. Perfect with curd or pickle!",
        "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400",
        "calories": 280,
        "preparation_time": "15-20 mins"
    },
    {
        "name": "PATEL & SONS",
        "area": "Maninagar, Ahmedabad",
        "cuisine": "GUJARATI THALI",
        "item_name": "Gujarati Thali",
        "price": 250.0,
        "rating": 4.8,
        "total_ratings": 890,
        "description": "A complete traditional Gujarati meal with dal, kadhi, vegetables, roti, rice, farsan, and sweets.",
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400",
        "calories": 800,
        "preparation_time": "30-40 mins"
    },
    {
        "name": "PATEL & SONS",
        "area": "Maninagar, Ahmedabad",
        "cuisine": "PANJABI THALI",
        "item_name": "Punjabi Thali",
        "price": 280.0,
        "rating": 4.7,
        "total_ratings": 720,
        "description": "Rich and flavorful Punjabi meal with dal makhani, paneer curry, naan, rice, and dessert.",
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400",
        "calories": 950,
        "preparation_time": "35-45 mins"
    },
    {
        "name": "Manek Chowk Pizza",
        "area": "Manek Chowk, Ahmedabad",
        "cuisine": "MARGHERITA PIZZA",
        "item_name": "Margherita Pizza",
        "price": 180.0,
        "rating": 4.6,
        "total_ratings": 520,
        "description": "Classic Italian pizza with fresh mozzarella, tomato sauce, and basil. Simple yet delicious!",
        "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400",
        "calories": 650,
        "preparation_time": "25-30 mins"
    },
    {
        "name": "Manek Chowk Pizza",
        "area": "Manek Chowk, Ahmedabad",
        "cuisine": "CHEESE BURST PIZZA",
        "item_name": "Cheese Burst Pizza",
        "price": 220.0,
        "rating": 4.5,
        "total_ratings": 410,
        "description": "Loaded with gooey cheese that bursts in your mouth! Topped with vegetables and special sauce.",
        "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400",
        "calories": 850,
        "preparation_time": "30-35 mins"
    },
    {
        "name": "Honest Restaurant",
        "area": "CG Road, Ahmedabad",
        "cuisine": "BUTTER CHICKEN",
        "item_name": "Butter Chicken",
        "price": 320.0,
        "rating": 4.9,
        "total_ratings": 1250,
        "description": "Tender chicken pieces in rich, creamy tomato-based gravy. A North Indian classic!",
        "image_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400",
        "calories": 720,
        "preparation_time": "30-40 mins"
    },
    {
        "name": "Honest Restaurant",
        "area": "CG Road, Ahmedabad",
        "cuisine": "BIRYANI",
        "item_name": "Hyderabadi Biryani",
        "price": 280.0,
        "rating": 4.8,
        "total_ratings": 980,
        "description": "Aromatic basmati rice layered with spiced chicken/mutton, cooked in dum style. Served with raita.",
        "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400",
        "calories": 650,
        "preparation_time": "40-50 mins"
    },
    {
        "name": "Cafe Upper Crust",
        "area": "Vastrapur, Ahmedabad",
        "cuisine": "PASTA",
        "item_name": "Alfredo Pasta",
        "price": 240.0,
        "rating": 4.4,
        "total_ratings": 340,
        "description": "Creamy white sauce pasta with herbs and parmesan cheese. Comfort food at its best!",
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400",
        "calories": 580,
        "preparation_time": "20-25 mins"
    },
    {
        "name": "Cafe Upper Crust",
        "area": "Vastrapur, Ahmedabad",
        "cuisine": "SANDWICH",
        "item_name": "Club Sandwich",
        "price": 180.0,
        "rating": 4.3,
        "total_ratings": 290,
        "description": "Triple-layered sandwich with chicken, egg, veggies, and cheese. Served with fries!",
        "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400",
        "calories": 520,
        "preparation_time": "15-20 mins"
    },
    {
        "name": "Sankalp Restaurant",
        "area": "Satellite, Ahmedabad",
        "cuisine": "DOSA",
        "item_name": "Masala Dosa",
        "price": 120.0,
        "rating": 4.7,
        "total_ratings": 780,
        "description": "Crispy rice crepe filled with spiced potato filling. Served with sambar and chutney.",
        "image_url": "https://images.unsplash.com/photo-1630383249896-424e482df921?w=400",
        "calories": 350,
        "preparation_time": "15-20 mins"
    },
    {
        "name": "Sankalp Restaurant",
        "area": "Satellite, Ahmedabad",
        "cuisine": "IDLI",
        "item_name": "Idli Sambar",
        "price": 80.0,
        "rating": 4.6,
        "total_ratings": 650,
        "description": "Soft, fluffy steamed rice cakes served with lentil sambar and coconut chutney.",
        "image_url": "https://images.unsplash.com/photo-1626074353765-517a681e40be?w=400",
        "calories": 180,
        "preparation_time": "10-15 mins"
    },
    {
        "name": "The Chocolate Room",
        "area": "SG Highway, Ahmedabad",
        "cuisine": "CHOCOLATE CAKE",
        "item_name": "Chocolate Fudge Cake",
        "price": 150.0,
        "rating": 4.8,
        "total_ratings": 520,
        "description": "Rich, moist chocolate cake with chocolate ganache. A chocolate lover's dream!",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400",
        "calories": 480,
        "preparation_time": "5-10 mins"
    },
    {
        "name": "The Chocolate Room",
        "area": "SG Highway, Ahmedabad",
        "cuisine": "BROWNIE",
        "item_name": "Brownie with Ice Cream",
        "price": 180.0,
        "rating": 4.7,
        "total_ratings": 450,
        "description": "Warm, gooey chocolate brownie topped with vanilla ice cream and chocolate sauce.",
        "image_url": "https://images.unsplash.com/photo-1607920591413-4ec007e70023?w=400",
        "calories": 550,
        "preparation_time": "10-15 mins"
    }
]

async def clear_and_add_data():
    """Clear existing data and add dummy data"""
    print("🗑️  Clearing existing restaurant data...")
    await restaurants_collection.delete_many({})
    
    print(f"📝 Adding {len(dummy_restaurants)} restaurants with rich data...")
    result = await restaurants_collection.insert_many(dummy_restaurants)
    
    print(f"✅ Successfully added {len(result.inserted_ids)} restaurants!")
    print("\n📋 Added restaurants:")
    for restaurant in dummy_restaurants:
        print(f"  • {restaurant['name']} - {restaurant['item_name']} (₹{restaurant['price']})")

async def main():
    await clear_and_add_data()
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
