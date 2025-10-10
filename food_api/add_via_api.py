"""
Add dummy data via FastAPI endpoints
This works by logging in first, then adding restaurants
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Login credentials
USERNAME = "demo_user"
PASSWORD = "demo_password"

# Dummy restaurant data with rich information
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

def get_auth_token():
    """Login and get JWT token"""
    print("🔐 Logging in to get authentication token...")
    try:
        response = requests.post(
            f"{BASE_URL}/users/login",
            data={
                "username": USERNAME,
                "password": PASSWORD
            }
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Login successful! Token obtained.\n")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error logging in: {str(e)}")
        return None

def add_restaurants():
    """Add restaurants via POST endpoint"""
    # Get authentication token first
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return 0
    
    print(f"🚀 Adding {len(dummy_restaurants)} restaurants via API...\n")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    success_count = 0
    for i, restaurant in enumerate(dummy_restaurants, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/restaurants/",
                json=restaurant,
                headers=headers
            )
            
            if response.status_code == 201:  # Changed to 201 CREATED
                result = response.json()
                success_count += 1
                print(f"✅ {i}. Added: {restaurant['name']} - {restaurant['item_name']} (₹{restaurant['price']})")
            else:
                print(f"❌ {i}. Failed: {restaurant['name']} - Status {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ {i}. Error adding {restaurant['name']}: {str(e)}")
    
    print(f"\n✅ Successfully added {success_count}/{len(dummy_restaurants)} restaurants!")
    return success_count

def check_restaurants():
    """Check current restaurants"""
    try:
        response = requests.get(f"{BASE_URL}/restaurants/")
        if response.status_code == 200:
            restaurants = response.json()
            print(f"\n📊 Total restaurants in database: {len(restaurants)}\n")
            for r in restaurants:
                price = f"₹{r.get('price', 'N/A')}" if r.get('price') else "No price"
                rating = f"⭐{r.get('rating', 'N/A')}" if r.get('rating') else "No rating"
                print(f"  • {r['name']} - {r.get('item_name', r['cuisine'])} - {price} - {rating}")
            return len(restaurants)
        else:
            print(f"❌ Failed to get restaurants: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Error checking restaurants: {str(e)}")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("  🍕 ADDING DUMMY RESTAURANT DATA VIA API")
    print("=" * 60)
    
    # Check existing restaurants
    print("\n📋 Checking existing restaurants...")
    existing_count = check_restaurants()
    
    # Add new restaurants
    print("\n" + "=" * 60)
    added_count = add_restaurants()
    
    # Verify
    print("\n" + "=" * 60)
    print("📋 Verifying updated database...")
    final_count = check_restaurants()
    
    print("\n" + "=" * 60)
    print(f"✅ DONE! Database now has {final_count} restaurants")
    print("=" * 60)
