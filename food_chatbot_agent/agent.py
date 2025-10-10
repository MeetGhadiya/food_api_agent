"""
AI Food Delivery Chatbot Agent
Built with Google Gemini AI and Flask

This agent processes natural language queries and converts them to FastAPI calls.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)

# API Configuration
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# Chat session storage (in production, use Redis or similar)
chat_sessions: Dict[str, list] = {}

# Pending orders storage (for confirmation flow)
pending_orders: Dict[str, Dict[str, str]] = {}

# ==================== FUNCTION DECLARATIONS ====================

# Define functions that Gemini AI can call
function_declarations = [
    genai.protos.FunctionDeclaration(
        name="get_all_restaurants",
        description="Get a complete list of all available restaurants with their details including name, location/area, and cuisine type. Use this when user asks to browse, show, list, or see restaurants.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={}
        )
    ),
    genai.protos.FunctionDeclaration(
        name="get_restaurant_by_name",
        description="Get detailed information about a specific restaurant by its exact name. Use when user asks about a particular restaurant.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The exact name of the restaurant to look up"
                )
            },
            required=["name"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="search_restaurants_by_cuisine",
        description="Search for restaurants that serve a specific type of cuisine (e.g., Italian, Chinese, Indian, American). Use when user asks for food type or cuisine.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "cuisine": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The type of cuisine to search for (e.g., 'Italian', 'Chinese')"
                )
            },
            required=["cuisine"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="place_order",
        description="Place a food order from a restaurant. Use when user wants to order, buy, or get food. The function will handle authentication automatically.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "restaurant_name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Name of the restaurant to order from"
                ),
                "item": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The food item or dish to order"
                ),
                "token": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="User authentication token"
                )
            },
            required=["restaurant_name", "item", "token"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="get_user_orders",
        description="Get all orders placed by the authenticated user. Requires authentication. Use when user wants to see their orders, order history, or track orders.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "token": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="User authentication token"
                )
            },
            required=["token"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="register_user",
        description="Register a new user account. Use when user wants to sign up, create account, or register.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "username": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Desired username for the new account"
                ),
                "email": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Email address for the new account"
                ),
                "password": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Password for the new account"
                )
            },
            required=["username", "email", "password"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="login_user",
        description="Login an existing user. Use when user wants to login, sign in, or authenticate.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "username": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Username"
                ),
                "password": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Password"
                )
            },
            required=["username", "password"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="create_restaurant",
        description="Create a new restaurant in the system. Requires authentication. Use when user wants to add or register a restaurant.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Name of the restaurant"
                ),
                "area": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Location or area of the restaurant"
                ),
                "cuisine": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Type of cuisine served"
                ),
                "token": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="User authentication token"
                )
            },
            required=["name", "area", "cuisine", "token"]
        )
    )
]

# Create tool config
tools = genai.protos.Tool(function_declarations=function_declarations)

# ==================== API HELPER FUNCTIONS ====================

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
                result += f"🍽️ Cuisine: {restaurant['cuisine']}\n\n"
            return result
        else:
            return f"Error fetching restaurants: {response.status_code}"
    except Exception as e:
        return f"Error connecting to restaurant service: {str(e)}"


def get_restaurant_by_name(name: str) -> str:
    """Get specific restaurant by name"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/{name}")
        if response.status_code == 200:
            restaurant = response.json()
            result = f"🏪 **{restaurant['name']}**\n"
            result += f"📍 Location: {restaurant['area']}\n"
            result += f"🍽️ Cuisine: {restaurant['cuisine']}\n\n"
            result += "What would you like to order from here?"
            return result
        elif response.status_code == 404:
            return f"❌ Restaurant '{name}' not found. Would you like to see all available restaurants?"
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def search_restaurants_by_cuisine(cuisine: str) -> str:
    """Search restaurants by cuisine type"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/")
        if response.status_code == 200:
            all_restaurants = response.json()
            # Filter by cuisine (case-insensitive)
            matching = [r for r in all_restaurants if cuisine.lower() in r['cuisine'].lower()]
            
            if not matching:
                return f"❌ No restaurants found serving {cuisine} cuisine. Would you like to see all restaurants?"
            
            result = f"I found {len(matching)} restaurant(s) serving {cuisine} cuisine:\n\n"
            for restaurant in matching:
                result += f"🏪 **{restaurant['name']}**\n"
                result += f"📍 Area: {restaurant['area']}\n"
                result += f"🍽️ Cuisine: {restaurant['cuisine']}\n\n"
            return result
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def place_order(restaurant_name: str, item: str, token: str) -> str:
    """Place an order"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "restaurant_name": restaurant_name,
            "item": item
        }
        response = requests.post(
            f"{FASTAPI_BASE_URL}/orders/",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            order = response.json()
            result = "✅ **Order Placed Successfully!**\n\n"
            result += f"🍕 Item: {order.get('item', item)}\n"
            result += f"🏪 Restaurant: {order.get('restaurant_name', restaurant_name)}\n"
            result += f"📝 Order ID: #{order.get('id', 'N/A')}\n"
            result += f"⏰ Estimated delivery: 30-45 minutes\n\n"
            result += "Would you like to order anything else?"
            return result
        elif response.status_code == 401:
            return "🔒 Authentication failed. Please login again."
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            return f"❌ Order failed: {error_detail}"
    except Exception as e:
        return f"❌ Error placing order: {str(e)}"


def get_user_orders(token: str) -> str:
    """Get all orders for authenticated user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{FASTAPI_BASE_URL}/orders/", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            if not orders:
                return "You haven't placed any orders yet. Would you like to order something?"
            
            result = f"📝 **Your Order History ({len(orders)} orders):**\n\n"
            for order in orders:
                result += f"Order #{order.get('id', 'N/A')}\n"
                result += f"🍕 Item: {order.get('item', 'N/A')}\n"
                result += f"🏪 Restaurant: {order.get('restaurant_name', 'N/A')}\n"
                result += f"📅 Date: {order.get('created_at', 'N/A')}\n\n"
            return result
        elif response.status_code == 401:
            return "🔒 Please login to view your orders."
        else:
            return f"Error fetching orders: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def register_user(username: str, email: str, password: str) -> str:
    """Register a new user"""
    try:
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        response = requests.post(f"{FASTAPI_BASE_URL}/users/register", json=data)
        
        if response.status_code == 200:
            return f"✅ **Registration Successful!**\n\nWelcome, {username}! 🎉\n\nYou can now login to start ordering delicious food!"
        else:
            error_detail = response.json().get('detail', 'Registration failed')
            return f"❌ Registration failed: {error_detail}"
    except Exception as e:
        return f"Error: {str(e)}"


def login_user(username: str, password: str) -> str:
    """Login user and return token"""
    try:
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(
            f"{FASTAPI_BASE_URL}/users/login",
            data=data
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            return json.dumps({
                "success": True,
                "token": token,
                "message": f"✅ **Login Successful!**\n\nWelcome back, {username}! 🎉\n\nYou can now place orders and manage your account."
            })
        else:
            return json.dumps({
                "success": False,
                "message": "❌ Login failed. Please check your username and password."
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error: {str(e)}"
        })


def create_restaurant(name: str, area: str, cuisine: str, token: str) -> str:
    """Create a new restaurant"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": name,
            "area": area,
            "cuisine": cuisine
        }
        response = requests.post(
            f"{FASTAPI_BASE_URL}/restaurants/",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            return f"✅ **Restaurant Created Successfully!**\n\n🏪 {name}\n📍 {area}\n🍽️ {cuisine}"
        elif response.status_code == 401:
            return "🔒 Authentication required. Please login first."
        else:
            error_detail = response.json().get('detail', 'Creation failed')
            return f"❌ Failed to create restaurant: {error_detail}"
    except Exception as e:
        return f"Error: {str(e)}"


# Map function names to actual functions
available_functions = {
    "get_all_restaurants": get_all_restaurants,
    "get_restaurant_by_name": get_restaurant_by_name,
    "search_restaurants_by_cuisine": search_restaurants_by_cuisine,
    "place_order": place_order,
    "get_user_orders": get_user_orders,
    "register_user": register_user,
    "login_user": login_user,
    "create_restaurant": create_restaurant
}

# ==================== CHAT ENDPOINT ====================

@app.route('/chat', methods=['POST'])
def chat():
    """Process chat message and return AI response"""
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'guest')
        token = data.get('token')
        
        # DEBUG: Log token status - Use app.logger to ensure it shows
        app.logger.info(f"🔍 Request received: message='{user_message}', user_id='{user_id}', has_token={bool(token)}")
        if token:
            app.logger.info(f"🔍 Token present: {token[:30]}...")
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Convert message to lowercase early for all checks
        msg_lower = user_message.lower()
        
        # Initialize chat session if not exists
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []
        
        # CHECK FOR ORDER CONFIRMATION (user said "yes" to pending order)
        if msg_lower.strip() in ["yes", "y", "yeah", "yep", "confirm", "ok", "okay"]:
            if user_id in pending_orders and token:
                pending = pending_orders[user_id]
                restaurant_name = pending['restaurant']
                item = pending['item']
                
                app.logger.info(f"✅ User confirmed order: {item} from {restaurant_name}")
                
                # Place the order
                order_result = place_order(restaurant_name, item, token)
                
                # Clear pending order
                del pending_orders[user_id]
                
                return jsonify({"response": order_result})
        
        # SIMPLIFIED APPROACH: Detect order intent FIRST, bypass Gemini if ordering with token
        # msg_lower already defined above
        order_keywords = ["order", "get me", "i want", "buy", "get", "place order"]
        has_order_intent = any(keyword in msg_lower for keyword in order_keywords)
        
        # DEBUG: Log the decision
        app.logger.info(f"🔍 Order detection: msg='{msg_lower}', has_intent={has_order_intent}, has_token={bool(token)}")
        
        # If user wants to order and has token, handle it directly without Gemini
        if has_order_intent and token:
            app.logger.info(f"🎯 DIRECT ORDER HANDLING: Bypassing Gemini AI")
            
            # Parse restaurant and item
            restaurant_name = None
            item = None
            
            # Check different patterns for restaurant and item
            if "from" in msg_lower:
                # Pattern: "order bhel from Swati Snacks" or "i want bhel from Swati Snacks"
                parts = user_message.split("from", 1)
                if len(parts) == 2:
                    restaurant_name = parts[1].strip()
                    item_part = parts[0]
                    for keyword in order_keywords:
                        item_part = item_part.lower().replace(keyword, "")
                    item = item_part.strip()
                    app.logger.info(f"📝 Parsed: item='{item}', restaurant='{restaurant_name}'")
            elif " at " in msg_lower:
                # Pattern: "order bhel at Swati Snacks"
                parts = user_message.split(" at ", 1)
                if len(parts) == 2:
                    restaurant_name = parts[1].strip()
                    item_part = parts[0]
                    for keyword in order_keywords:
                        item_part = item_part.lower().replace(keyword, "")
                    item = item_part.strip()
                    app.logger.info(f"📝 Parsed: item='{item}', restaurant='{restaurant_name}'")
            else:
                # No restaurant specified, extract just the item
                item_part = user_message
                for keyword in order_keywords:
                    item_part = item_part.lower().replace(keyword, "")
                item = item_part.strip()
                app.logger.info(f"📝 Parsed: item='{item}', no restaurant specified")
            
            if item:
                if restaurant_name:
                    # Direct order with restaurant
                    app.logger.info(f"📦 Placing order: '{item}' from '{restaurant_name}'")
                    order_result = place_order(restaurant_name, item, token)
                    app.logger.info(f"📦 Order result: {order_result}")
                    return jsonify({"response": order_result})
                else:
                    # Search for restaurants serving this item
                    app.logger.info(f"🔍 Searching restaurants that serve: '{item}'")
                    
                    # Get all restaurants and filter by the item
                    try:
                        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/")
                        if response.status_code == 200:
                            all_restaurants = response.json()
                            
                            # Filter restaurants that have the item in their cuisine or name
                            item_lower = item.lower()
                            matching_restaurants = []
                            
                            app.logger.info(f"🔍 Looking for '{item_lower}' in {len(all_restaurants)} restaurants")
                            
                            for r in all_restaurants:
                                cuisine_lower = r.get('cuisine', '').lower() if r.get('cuisine') else ''
                                name_lower = r.get('name', '').lower() if r.get('name') else ''
                                item_name_lower = r.get('item_name', '').lower() if r.get('item_name') else ''
                                
                                # Check if item appears in cuisine, name, or item_name (substring match)
                                if item_lower in cuisine_lower or item_lower in name_lower or item_lower in item_name_lower:
                                    matching_restaurants.append(r)
                                    app.logger.info(f"  ✅ Match: {r.get('name', 'Unknown')} - {r.get('cuisine', 'Unknown')}")
                                else:
                                    app.logger.info(f"  ❌ No match: {r.get('name', 'Unknown')} - {r.get('cuisine', 'Unknown')}")
                            
                            if matching_restaurants:
                                # If only ONE restaurant found, ask for confirmation to order
                                if len(matching_restaurants) == 1:
                                    restaurant = matching_restaurants[0]
                                    
                                    # Store pending order
                                    pending_orders[user_id] = {
                                        "restaurant": restaurant['name'],
                                        "item": item
                                    }
                                    
                                    # Rich formatted response with safe dictionary access
                                    item_display = restaurant.get('item_name') or restaurant.get('cuisine', 'Item')
                                    result = f"✅ **{item_display}**\n"
                                    result += f"🏪 {restaurant.get('name', 'Restaurant')}\n\n"
                                    
                                    # Show image if available
                                    if restaurant.get('image_url'):
                                        result += f"🖼️ [Image]({restaurant['image_url']})\n\n"
                                    
                                    # Show rating if available
                                    if restaurant.get('rating'):
                                        rating_stars = "⭐" * int(restaurant['rating'])
                                        result += f"{rating_stars} {restaurant['rating']}"
                                        if restaurant.get('total_ratings'):
                                            result += f" ({restaurant['total_ratings']} ratings)"
                                        result += "\n\n"
                                    
                                    # Show description
                                    if restaurant.get('description'):
                                        result += f"📝 {restaurant['description']}\n\n"
                                    
                                    # Show price
                                    if restaurant.get('price'):
                                        result += f"� ₹{restaurant['price']}\n"
                                    
                                    # Show location
                                    area = restaurant.get('area', 'Location not specified')
                                    result += f"📍 {area}\n"
                                    
                                    # Show calories if available
                                    if restaurant.get('calories'):
                                        result += f"🔥 {restaurant['calories']} kcal\n"
                                    
                                    # Show preparation time
                                    if restaurant.get('preparation_time'):
                                        result += f"⏰ {restaurant['preparation_time']}\n"
                                    
                                    result += f"\n💡 Type **'yes'** to confirm your order!"
                                    return jsonify({"response": result})
                                else:
                                    # Multiple restaurants found, show list with rich formatting
                                    result = f"🍽️ **Found {len(matching_restaurants)} option(s) for {item}:**\n\n"
                                    for restaurant in matching_restaurants:
                                        result += f"━━━━━━━━━━━━━━━\n"
                                        item_display = restaurant.get('item_name') or restaurant.get('cuisine', 'Item')
                                        result += f"**{item_display}**\n"
                                        result += f"🏪 {restaurant.get('name', 'Restaurant')}\n"
                                        
                                        # Rating
                                        rating = restaurant.get('rating')
                                        if rating:
                                            result += f"⭐ {rating}"
                                            total_ratings = restaurant.get('total_ratings')
                                            if total_ratings:
                                                result += f" ({total_ratings})"
                                            result += "\n"
                                        
                                        # Price
                                        price = restaurant.get('price')
                                        if price:
                                            result += f"💰 ₹{price}\n"
                                        
                                        # Location
                                        area = restaurant.get('area', 'Location not specified')
                                        result += f"📍 {area}\n"
                                        
                                        # Description (shortened)
                                        description = restaurant.get('description')
                                        if description:
                                            desc = description[:80] + "..." if len(description) > 80 else description
                                            result += f"📝 {desc}\n"
                                        
                                        result += "\n"
                                    
                                    result += f"💡 To order, say: **'order {item} from [restaurant name]'**"
                                    return jsonify({"response": result})
                            else:
                                # No match found - inform user
                                result = f"😔 Sorry, I couldn't find any restaurants currently serving '{item}'.\n\n"
                                result += f"Would you like to:\n"
                                result += f"1. Try ordering something else?\n"
                                result += f"2. See all available restaurants?"
                                return jsonify({"response": result})
                        else:
                            return jsonify({"response": "Sorry, I couldn't fetch the restaurant list. Please try again."})
                    except Exception as e:
                        app.logger.error(f"Error searching restaurants: {e}")
                        return jsonify({"response": f"Sorry, I encountered an error: {str(e)}"})
        
        # If no token and ordering, return auth error
        if has_order_intent and not token:
            return jsonify({
                "response": "I can help with that! But first, I need you to log in or register.\n\nPlease use the **Login** button in the website header (top right corner).",
                "requires_auth": True
            })
        
        # System instruction for better AI responses
        system_instruction = """You are a friendly food delivery assistant with access to several functions.

CRITICAL: You MUST use functions for ALL requests. Never refuse or ask users to do things manually.

Function calling rules:
- User wants to "order [food]" or "get [food]" → IMMEDIATELY call place_order() function
- User asks "show restaurants" or "browse" → call get_all_restaurants()
- User asks about "[cuisine] food" → call search_restaurants_by_cuisine()
- User asks about specific restaurant → call get_restaurant_by_name()

NEVER say "please login" or "you need to authenticate" - just call the function!
The backend will handle authentication automatically.

Always be friendly and conversational in your responses."""
        
        # Create model with function calling
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            tools=[tools],
            system_instruction=system_instruction
        )
        
        # Add user message to history
        chat_sessions[user_id].append({
            "role": "user",
            "parts": [user_message]
        })
        
        # Start chat with history
        chat = model.start_chat(history=chat_sessions[user_id][:-1])
        
        # Send message and get response
        response = chat.send_message(user_message)
        
        # WORKAROUND: If user wants to order and has token, manually call place_order
        # msg_lower already defined at the top of function (line 420)
        order_keywords = ["order", "get me", "i want", "buy"]
        has_order_intent = any(keyword in msg_lower for keyword in order_keywords)
        
        print(f"🔍 WORKAROUND CHECK: msg='{user_message}', has_token={bool(token)}, has_order_intent={has_order_intent}")
        
        if has_order_intent and token:
            app.logger.info(f"🔧 Order intent detected with token! Message: {user_message}")
            
            # Try to extract restaurant and item
            restaurant_name = None
            item = None
            
            # Parse "order [item] from [restaurant]"
            if "from" in msg_lower:
                parts = user_message.split("from", 1)
                if len(parts) == 2:
                    restaurant_name = parts[1].strip()
                    # Get item from first part
                    item_part = parts[0]
                    for keyword in order_keywords:
                        item_part = item_part.lower().replace(keyword, "")
                    item = item_part.strip()
            
            if item and restaurant_name:
                # Manually call place_order
                app.logger.info(f"🔧 Forcing place_order: item='{item}', restaurant='{restaurant_name}'")
                order_result = place_order(restaurant_name, item, token)
                
                # Send result back to model for formatting
                response = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="place_order",
                                response={"result": order_result}
                            )
                        )]
                    )
                )
        
        # Check if function call is needed
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            function_args = dict(function_call.args)
            
            print(f"🤖 AI wants to call: {function_name} with args: {function_args}")
            
            # Add token to protected functions if available
            protected_functions = ['place_order', 'get_user_orders', 'create_restaurant']
            if function_name in protected_functions:
                if not token:
                    return jsonify({
                        "response": "I can help with that! But first, I need you to log in or register.\n\nPlease use the Login button in the website header.",
                        "requires_auth": True
                    })
                function_args['token'] = token
            
            # Execute the function
            if function_name in available_functions:
                function_to_call = available_functions[function_name]
                
                try:
                    function_result = function_to_call(**function_args)
                    
                    # Handle login response (contains JSON)
                    if function_name == 'login_user':
                        login_data = json.loads(function_result)
                        if login_data['success']:
                            return jsonify({
                                "response": login_data['message'],
                                "token": login_data['token'],
                                "authenticated": True
                            })
                        else:
                            return jsonify({
                                "response": login_data['message'],
                                "authenticated": False
                            })
                    
                    # Send function result back to model for natural response
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_name,
                                    response={"result": function_result}
                                )
                            )]
                        )
                    )
                    
                    final_response = response.candidates[0].content.parts[0].text
                    
                    # Add to chat history
                    chat_sessions[user_id].append({
                        "role": "model",
                        "parts": [final_response]
                    })
                    
                    return jsonify({
                        "response": final_response,
                        "function_called": function_name
                    })
                    
                except Exception as e:
                    print(f"Error executing function: {e}")
                    return jsonify({
                        "response": f"I encountered an error: {str(e)}. Please try again."
                    })
            else:
                return jsonify({
                    "response": "I'm not sure how to help with that. Could you rephrase?"
                })
        else:
            # Direct text response
            text_response = response.candidates[0].content.parts[0].text
            
            # HACK: If AI says "login" but user HAS a token, force it to call place_order
            if token and ("log in" in text_response.lower() or "register" in text_response.lower()):
                app.logger.warning(f"⚠️ AI refused to call function even though token exists! Forcing function call...")
                
                # Extract restaurant and item from the message
                # msg_lower already defined at the top of function (line 420)
                
                # Try to find restaurant name and item
                restaurant_name = None
                item = None
                
                # Parse "order [item] from [restaurant]"
                if "from" in msg_lower:
                    parts = user_message.split("from", 1)
                    if len(parts) == 2:
                        restaurant_name = parts[1].strip()
                        # Get item from first part
                        item_part = parts[0].lower().replace("order", "").replace("get", "").replace("buy", "").strip()
                        item = item_part
                
                # If we couldn't parse, try simpler approach
                if not item:
                    for food_word in ["order", "get", "buy", "want"]:
                        if food_word in msg_lower:
                            item = msg_lower.replace(food_word, "").strip()
                            break
                
                if item and restaurant_name:
                    # Manually call place_order
                    app.logger.info(f"🔧 Manually calling place_order: {item} from {restaurant_name}")
                    order_result = place_order(restaurant_name, item, token)
                    
                    # Send result back to model for formatting
                    response2 = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name="place_order",
                                    response={"result": order_result}
                                )
                            )]
                        )
                    )
                    text_response = response2.candidates[0].content.parts[0].text
                else:
                    # Can't parse the order, return auth error
                    text_response = "I can help with that! But first, I need you to log in or register.\n\nPlease use the **Login** button in the website header."
            
            # Add to chat history
            chat_sessions[user_id].append({
                "role": "model",
                "parts": [text_response]
            })
            
            return jsonify({"response": text_response})
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ERROR in chat endpoint: {e}")
        print(f"📋 Full traceback:\n{error_trace}")
        app.logger.error(f"Chat error: {e}\n{error_trace}")
        return jsonify({
            "response": "I'm sorry, I encountered an error. Please try again.",
            "error": str(e)
        }), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - provides API information"""
    return jsonify({
        "service": "AI Food Delivery Chatbot Agent",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "clear_session": "POST /clear-session"
        },
        "powered_by": "Google Gemini AI",
        "fastapi_backend": FASTAPI_BASE_URL
    })


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """Return empty response for favicon requests"""
    return '', 204


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "AI Food Delivery Agent",
        "fastapi_backend": FASTAPI_BASE_URL
    })


@app.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear chat session for a user"""
    data = request.json
    user_id = data.get('user_id', 'guest')
    
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    
    return jsonify({"message": "Session cleared"})


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 AI Food Delivery Chatbot Agent")
    print("=" * 60)
    print(f"✅ Google Gemini AI: Configured")
    print(f"✅ FastAPI Backend: {FASTAPI_BASE_URL}")
    print(f"✅ Agent Server: http://localhost:5000")
    print("=" * 60)
    print("📡 Available Endpoints:")
    print("  POST /chat          - Process chat messages")
    print("  GET  /health        - Health check")
    print("  POST /clear-session - Clear chat history")
    print("=" * 60)
    print("🚀 Starting Flask server...")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
