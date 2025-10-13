import requests

FASTAPI_BASE_URL = "http://localhost:8000"

def get_all_restaurants() -> str:
    """Fetch all restaurants from FastAPI"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/")
        if response.status_code == 200:
            restaurants = response.json()
            if not restaurants:
                return "No restaurants are currently available."
            
            result = f"I found {len(restaurants)} restaurant(s):\n\n"
            for restaurant in restaurants:
                result += f"🏪 **{restaurant['name']}**\n"
                result += f"📍 Area: {restaurant['area']}\n"
                # Show number of items available
                item_count = len(restaurant.get('items', []))
                result += f"🍽️ Menu: {item_count} items available\n\n"
            return result
        else:
            return f"Error fetching restaurants: {response.status_code}"
    except Exception as e:
        return f"Error connecting to restaurant service: {str(e)}"

if __name__ == "__main__":
    print("Testing get_all_restaurants function:")
    print("=" * 60)
    result = get_all_restaurants()
    print(result)
