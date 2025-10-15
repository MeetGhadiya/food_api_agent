"""
Fallback chatbot that works WITHOUT Gemini API
Uses simple pattern matching to handle restaurant queries
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static', template_folder=STATIC_DIR)
CORS(app)

API_BASE_URL = "http://localhost:8000"

# Store session context (restaurant being discussed, etc.)
session_contexts = {}

# Simple pattern-based responses
def get_all_restaurants():
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_restaurant_by_name(name):
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/{name}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def place_order(restaurant_name, item, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"restaurant_name": restaurant_name, "item": item}
        response = requests.post(f"{API_BASE_URL}/orders/", json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        return None
    except Exception as e:
        return None

def process_message(message, token, session_id="default"):
    """Simple pattern matching for common queries with session context"""
    message_lower = message.lower()
    
    # Get or create session context
    if session_id not in session_contexts:
        session_contexts[session_id] = {"current_restaurant": None, "last_items": []}
    
    # List restaurants
    if any(word in message_lower for word in ['list', 'show', 'all', 'restaurants', 'available', 'menu']):
        restaurants = get_all_restaurants()
        if not restaurants:
            return "Sorry, I couldn't fetch the restaurants. Please make sure the backend is running."
        
        response = "🍽️ **Available Restaurants:**\n\n"
        for rest in restaurants:
            response += f"📍 **{rest['name']}** ({rest['area']})\n"
            if rest.get('items'):
                response += "   Menu:\n"
                for item in rest['items'][:5]:  # Show first 5 items
                    price = item.get('price', 'N/A')
                    response += f"   • {item['item_name']} - ₹{price}\n"
                if len(rest['items']) > 5:
                    response += f"   ... and {len(rest['items']) - 5} more items\n"
            response += "\n"
        
        response += "\n💡 To order, say: 'I want [item name] from [restaurant name]'"
        return response
    
    # Get specific restaurant
    for rest_name in ['swati', 'agashiye', 'patel', 'manek', 'honest', 'sankalp', 'chocolate']:
        if rest_name in message_lower:
            restaurants = get_all_restaurants()
            matching = [r for r in restaurants if rest_name in r['name'].lower()]
            if matching:
                rest = matching[0]
                # Store restaurant in session context
                session_contexts[session_id]["current_restaurant"] = rest['name']
                session_contexts[session_id]["last_items"] = [item['item_name'] for item in rest.get('items', [])]
                
                response = f"🍽️ **{rest['name']}** - {rest['area']}\n\n"
                response += "📋 **Menu:**\n"
                for item in rest.get('items', []):
                    price = item.get('price', 'N/A')
                    rating = item.get('rating', 'N/A')
                    response += f"• **{item['item_name']}** - ₹{price} ⭐{rating}\n"
                    if item.get('description'):
                        response += f"  _{item['description'][:80]}..._\n"
                
                response += "\n💡 Say 'I want [item name]' to order!"
                return response
    
    # Order food with restaurant name specified
    order_pattern_with_restaurant = r"(?:i want|order|get me|i'll have|give me)\s+(.+?)\s+(?:from|at)\s+(.+)"
    match = re.search(order_pattern_with_restaurant, message_lower)
    if match:
        if not token:
            return "🔒 **Please login first to place an order!**\n\nClick the Login button in the top right corner."
        
        item = match.group(1).strip()
        restaurant_input = match.group(2).strip()
        
        # Find the actual restaurant (fuzzy match)
        restaurants = get_all_restaurants()
        matched_restaurant = None
        for rest in restaurants:
            if restaurant_input.lower() in rest['name'].lower() or rest['name'].lower() in restaurant_input.lower():
                matched_restaurant = rest
                break
        
        if not matched_restaurant:
            return f"❌ **Restaurant '{restaurant_input}' not found.**\n\nSay 'show restaurants' to see all available restaurants."
        
        restaurant_name = matched_restaurant['name']
        
        # Fuzzy match the item from menu
        menu_items = matched_restaurant.get('items', [])
        matched_item = None
        for menu_item in menu_items:
            if item.lower() == menu_item['item_name'].lower():
                matched_item = menu_item['item_name']
                break
        
        if not matched_item:
            for menu_item in menu_items:
                if item.lower() in menu_item['item_name'].lower() or menu_item['item_name'].lower() in item.lower():
                    matched_item = menu_item['item_name']
                    break
        
        if not matched_item:
            items_list = "\n".join([f"   • {mi['item_name']}" for mi in menu_items[:10]])
            return f"❌ **'{item}' not found at {restaurant_name}.**\n\n📋 **Available items:**\n{items_list}\n\n💡 Try: 'I want [item name] from {restaurant_name}'"
        
        # Store restaurant in context for future orders
        session_contexts[session_id]["current_restaurant"] = restaurant_name
        session_contexts[session_id]["last_items"] = [mi['item_name'] for mi in menu_items]
        
        result = place_order(restaurant_name, matched_item, token)
        if result:
            return f"✅ **Order Placed Successfully!**\n\n📦 Item: {matched_item}\n🏪 Restaurant: {restaurant_name}\n\nYour order is being prepared! 🎉"
        else:
            return f"❌ **Order failed.** Please check:\n• Restaurant: '{restaurant_name}'\n• Item: '{matched_item}'\n• Make sure you're logged in"
    
    # Order food WITHOUT restaurant name (check if item exists in multiple restaurants)
    order_pattern_simple = r"(?:i want|order|get me|i'll have|give me)\s+(.+)"
    match_simple = re.search(order_pattern_simple, message_lower)
    if match_simple:
        item = match_simple.group(1).strip()
        
        # Search for this item across ALL restaurants
        all_restaurants = get_all_restaurants()
        restaurants_with_item = []
        
        for rest in all_restaurants:
            for menu_item in rest.get('items', []):
                # Fuzzy match the item
                if (item.lower() == menu_item['item_name'].lower() or 
                    item.lower() in menu_item['item_name'].lower() or 
                    menu_item['item_name'].lower() in item.lower()):
                    restaurants_with_item.append({
                        'restaurant': rest['name'],
                        'area': rest['area'],
                        'item_name': menu_item['item_name'],
                        'price': menu_item.get('price', 'N/A'),
                        'rating': menu_item.get('rating', 'N/A')
                    })
                    break  # Only add restaurant once even if multiple matches
        
        # If item found in multiple restaurants, show options
        if len(restaurants_with_item) > 1:
            response = f"🔍 **'{item}' is available at {len(restaurants_with_item)} restaurants:**\n\n"
            for idx, rest_info in enumerate(restaurants_with_item, 1):
                response += f"{idx}. 📍 **{rest_info['restaurant']}** ({rest_info['area']})\n"
                response += f"   • {rest_info['item_name']} - ₹{rest_info['price']} ⭐{rest_info['rating']}\n\n"
            response += "💡 **To order, say:**\n"
            response += f"   'I want {item} from [restaurant name]'\n\n"
            response += "Or tap on a restaurant to see their full menu!"
            return response
        
        # If found in exactly one restaurant
        elif len(restaurants_with_item) == 1:
            if not token:
                return "🔒 **Please login first to place an order!**\n\nClick the Login button in the top right corner."
            
            rest_info = restaurants_with_item[0]
            restaurant = rest_info['restaurant']
            final_item = rest_info['item_name']
            
            # Store in context
            session_contexts[session_id]["current_restaurant"] = restaurant
            
            result = place_order(restaurant, final_item, token)
            if result:
                session_contexts[session_id]["current_restaurant"] = None
                return f"✅ **Order Placed Successfully!**\n\n📦 Item: {final_item}\n🏪 Restaurant: {restaurant} ({rest_info['area']})\n💰 Price: ₹{rest_info['price']}\n\nYour order is being prepared! 🎉\n\nWant to order more? Say 'show restaurants'!"
            else:
                return f"❌ **Order failed.** Please try again or contact support."
        
        # If using context from previous conversation
        elif session_contexts[session_id].get("current_restaurant"):
            if not token:
                return "🔒 **Please login first to place an order!**\n\nClick the Login button in the top right corner."
            
            restaurant = session_contexts[session_id]["current_restaurant"]
            last_items = session_contexts[session_id].get("last_items", [])
            
            # Check in last viewed menu
            matched_item = None
            if last_items:
                for menu_item in last_items:
                    if item.lower() == menu_item.lower() or item.lower() in menu_item.lower() or menu_item.lower() in item.lower():
                        matched_item = menu_item
                        break
                
                if not matched_item:
                    items_list = "\n".join([f"   • {mi}" for mi in last_items])
                    return f"❌ **'{item}' is not available at {restaurant}.**\n\n📋 **Available items:**\n{items_list}\n\n💡 Try: 'I want [item name]'"
            
            final_item = matched_item if matched_item else item
            result = place_order(restaurant, final_item, token)
            if result:
                session_contexts[session_id]["current_restaurant"] = None
                return f"✅ **Order Placed Successfully!**\n\n📦 Item: {final_item}\n🏪 Restaurant: {restaurant}\n\nYour order is being prepared! 🎉\n\nWant to order more? Say 'show restaurants'!"
            else:
                return f"❌ **Order failed.** Please check if '{final_item}' exists at {restaurant}."
        
        # Item not found anywhere
        else:
            return f"❌ **'{item}' not found in any restaurant.**\n\n💡 Say 'show all restaurants' to browse menus\n💡 Or try a different item name"
    
    # Help
    if any(word in message_lower for word in ['help', 'what can you do', 'how']):
        return """🤖 **I can help you with:**

1. 📋 **Browse Restaurants**
   Say: "Show all restaurants" or "List restaurants"

2. 🔍 **View Menu**
   Say: "Show me Swati Snacks menu"

3. 🛒 **Place Orders**
   Say: "I want Bhel Puri from Swati Snacks"
   (You need to login first!)

4. 🔐 **Account**
   Use the Login/Register buttons at the top

What would you like to do?"""
    
    # Default response
    return """👋 Hi! I'm your food delivery assistant!

🍽️ Say **"show all restaurants"** to browse menus
🛒 Say **"I want [item] from [restaurant]"** to order
❓ Say **"help"** for more options"""

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        token = data.get('token')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        response_text = process_message(user_message, token, session_id)
        
        return jsonify({
            "response": response_text,
            "function_called": "pattern_matcher"
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "mode": "fallback"})

@app.route('/widget')
def widget():
    return send_from_directory(STATIC_DIR, 'popup_widget.html')

if __name__ == '__main__':
    print("🚀 Starting Food Delivery Chatbot (Fallback Mode)")
    print("⚠️  Running WITHOUT Gemini AI - using pattern matching")
    print("📡 Server: http://localhost:5000")
    print("🤖 Chat API: http://localhost:5000/chat")
    print("💾 Backend: http://localhost:8000")
    print("\n💡 This fallback works without any API key!")
    app.run(debug=True, port=5000)
