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
        description="Place a food order from a restaurant. Requires user to be authenticated. Use when user wants to order, buy, or get food.",
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
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Initialize chat session if not exists
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []
        
        # Create model with function calling
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[tools]
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
                        "response": "🔒 **Authentication Required**\n\nTo perform this action, you need to be logged in. Would you like to:\n\n1️⃣ Login to existing account\n2️⃣ Create a new account",
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
            
            # Add to chat history
            chat_sessions[user_id].append({
                "role": "model",
                "parts": [text_response]
            })
            
            return jsonify({"response": text_response})
            
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return jsonify({
            "response": "I'm sorry, I encountered an error. Please try again.",
            "error": str(e)
        }), 500


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
