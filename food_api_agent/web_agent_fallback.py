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

def process_message(message, token):
    """Simple pattern matching for common queries"""
    message_lower = message.lower()
    
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
    
    # Order food
    order_pattern = r"(?:i want|order|get me|i'll have|give me)\s+(.+?)\s+(?:from|at)\s+(.+)"
    match = re.search(order_pattern, message_lower)
    if match:
        if not token:
            return "🔒 **Please login first to place an order!**\n\nClick the Login button in the top right corner."
        
        item = match.group(1).strip()
        restaurant = match.group(2).strip()
        
        result = place_order(restaurant, item, token)
        if result:
            return f"✅ **Order Placed Successfully!**\n\n📦 Item: {item}\n🏪 Restaurant: {restaurant}\n\nYour order is being prepared! 🎉"
        else:
            return f"❌ **Order failed.** Please check:\n• Restaurant name: '{restaurant}'\n• Item name: '{item}'\n• Make sure you're logged in"
    
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
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        response_text = process_message(user_message, token)
        
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
