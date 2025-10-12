"""
Script to populate the database with proper restaurant data using the new model structure
"""
import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Restaurant

MONGODB_URL = "mongodb+srv://foodapi_user:Meet7805@foodapicluster.6z9sntm.mongodb.net/?retryWrites=true&w=majority&appName=FoodAPICluster"

# Restaurant data with items grouped by restaurant
restaurants_data = [
    {
        "name": "Swati Snacks",
        "area": "Ashram Road, Ahmedabad",
        "items": [
            {
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
                "item_name": "Dabeli",
                "price": 40.0,
                "rating": 4.6,
                "total_ratings": 380,
                "description": "Spiced potato mixture in a bun, topped with pomegranate, peanuts, and sev. A Gujarati specialty!",
                "image_url": "https://images.unsplash.com/photo-1626074353765-517a681e40be?w=400",
                "calories": 220,
                "preparation_time": "10-15 mins"
            },
            {
                "item_name": "Sev Puri",
                "price": 70.0,
                "rating": 4.4,
                "total_ratings": 310,
                "description": "Crispy puris topped with potatoes, onions, chutneys, and lots of sev. Crunchy and flavorful!",
                "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400",
                "calories": 280,
                "preparation_time": "10-15 mins"
            }
        ]
    },
    {
        "name": "Agashiye The House of MG",
        "area": "Lal Darwaja, Ahmedabad",
        "items": [
            {
                "item_name": "Gujarati Thali",
                "price": 450.0,
                "rating": 4.9,
                "total_ratings": 1200,
                "description": "Authentic rooftop dining experience with traditional Gujarati thali featuring 20+ dishes.",
                "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400",
                "calories": 850,
                "preparation_time": "30-40 mins"
            },
            {
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
                "item_name": "Khaman Dhokla",
                "price": 100.0,
                "rating": 4.7,
                "total_ratings": 520,
                "description": "Soft, spongy steamed cake made from gram flour, tempered with mustard seeds and curry leaves.",
                "image_url": "https://images.unsplash.com/photo-1626074353765-517a681e40be?w=400",
                "calories": 180,
                "preparation_time": "15-20 mins"
            }
        ]
    },
    {
        "name": "PATEL & SONS",
        "area": "Maninagar, Ahmedabad",
        "items": [
            {
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
                "item_name": "Kathiyawadi Thali",
                "price": 300.0,
                "rating": 4.9,
                "total_ratings": 650,
                "description": "Spicy Kathiyawadi cuisine with bajra rotla, traditional vegetables, and buttermilk.",
                "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400",
                "calories": 900,
                "preparation_time": "35-45 mins"
            },
            {
                "item_name": "South Indian Thali",
                "price": 220.0,
                "rating": 4.6,
                "total_ratings": 490,
                "description": "Authentic South Indian meal with sambar, rasam, rice, dosa, and filter coffee.",
                "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400",
                "calories": 700,
                "preparation_time": "25-35 mins"
            }
        ]
    },
    {
        "name": "Manek Chowk Pizza",
        "area": "Manek Chowk, Ahmedabad",
        "items": [
            {
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
                "item_name": "Cheese Burst Pizza",
                "price": 220.0,
                "rating": 4.5,
                "total_ratings": 410,
                "description": "Loaded with gooey cheese that bursts in your mouth! Topped with vegetables and special sauce.",
                "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400",
                "calories": 850,
                "preparation_time": "30-35 mins"
            }
        ]
    },
    {
        "name": "Honest Restaurant",
        "area": "CG Road, Ahmedabad",
        "items": [
            {
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
                "item_name": "Hyderabadi Biryani",
                "price": 280.0,
                "rating": 4.8,
                "total_ratings": 980,
                "description": "Aromatic basmati rice layered with spiced chicken/mutton, cooked in dum style. Served with raita.",
                "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400",
                "calories": 650,
                "preparation_time": "40-50 mins"
            }
        ]
    },
    {
        "name": "Sankalp Restaurant",
        "area": "Satellite, Ahmedabad",
        "items": [
            {
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
                "item_name": "Idli Sambar",
                "price": 80.0,
                "rating": 4.6,
                "total_ratings": 650,
                "description": "Soft, fluffy steamed rice cakes served with lentil sambar and coconut chutney.",
                "image_url": "https://images.unsplash.com/photo-1626074353765-517a681e40be?w=400",
                "calories": 180,
                "preparation_time": "10-15 mins"
            }
        ]
    },
    {
        "name": "The Chocolate Room",
        "area": "SG Highway, Ahmedabad",
        "items": [
            {
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
    }
]

async def populate_data():
    client = AsyncIOMotorClient(MONGODB_URL, tlsAllowInvalidCertificates=True)
    db = client["food_db"]
    await init_beanie(database=db, document_models=[Restaurant])
    
    # Clear existing data
    print("🗑️  Clearing existing restaurant data...")
    all_restaurants = await Restaurant.find_all().to_list()
    for r in all_restaurants:
        await r.delete()
    
    # Insert new data
    print(f"\n📝 Adding {len(restaurants_data)} restaurants with grouped items...")
    for rest_data in restaurants_data:
        restaurant = Restaurant(**rest_data)
        await restaurant.insert()
        print(f"  ✅ Added '{rest_data['name']}' in {rest_data['area']} with {len(rest_data['items'])} items")
    
    print(f"\n✅ Successfully populated {len(restaurants_data)} restaurants!")

if __name__ == "__main__":
    asyncio.run(populate_data())
