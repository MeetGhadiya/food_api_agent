"""
AI Food Delivery Chatbot Agent - V2.0
Built with Google Gemini AI and Flask
Enhanced with Reviews, Multi-Item Orders, and Cuisine Search

This agent processes natural language queries and converts them to FastAPI calls.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional, List

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"])

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
pending_orders: Dict[str, Dict[str, Any]] = {}

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
        description="Search for restaurants that serve a specific type of cuisine (e.g., Italian, Chinese, Gujarati, North Indian, South Indian, Desserts). Use when user asks for food type or cuisine.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "cuisine": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The type of cuisine to search for (e.g., 'Italian', 'Gujarati', 'North Indian')"
                )
            },
            required=["cuisine"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="place_order",
        description="Place a food order with multiple items from a restaurant. Use when user wants to order, buy, or get food. Supports ordering multiple items in one order.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "restaurant_name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Name of the restaurant to order from"
                ),
                "items": genai.protos.Schema(
                    type=genai.protos.Type.ARRAY,
                    description="List of items to order with quantities and prices",
                    items=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "item_name": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Name of the food item"
                            ),
                            "quantity": genai.protos.Schema(
                                type=genai.protos.Type.INTEGER,
                                description="Quantity of this item"
                            ),
                            "price": genai.protos.Schema(
                                type=genai.protos.Type.NUMBER,
                                description="Price per unit of this item"
                            )
                        }
                    )
                ),
                "token": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="User authentication token"
                )
            },
            required=["restaurant_name", "items", "token"]
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
        name="add_review",
        description="Submit a review and rating for a restaurant. Rating must be 1-5 stars. Use when user wants to review, rate, or give feedback about a restaurant.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "restaurant_name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Name of the restaurant to review"
                ),
                "rating": genai.protos.Schema(
                    type=genai.protos.Type.INTEGER,
                    description="Rating from 1 to 5 stars (1=Poor, 5=Excellent)"
                ),
                "comment": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Optional review comment or feedback"
                ),
                "token": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="User authentication token"
                )
            },
            required=["restaurant_name", "rating", "token"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="get_reviews",
        description="Get all reviews for a specific restaurant. Use when user wants to see reviews, ratings, or feedback for a restaurant.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "restaurant_name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Name of the restaurant"
                )
            },
            required=["restaurant_name"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="get_review_stats",
        description="Get review statistics for a restaurant including average rating and rating distribution. Use when user wants to know overall rating or stats.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "restaurant_name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="Name of the restaurant"
                )
            },
            required=["restaurant_name"]
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
                return "No restaurants are currently available. 😔"
            
            # Format as a clean bulleted list
            result = f"🍽️ I found these restaurants for you! ({len(restaurants)} total)\n\n"
            for restaurant in restaurants:
                result += f"• **{restaurant['name']}** in {restaurant['area']} (Cuisine: {restaurant.get('cuisine', 'N/A')})\n"
            
            result += "\n💡 Want to know more? Just ask about any restaurant!"
            return result
        else:
            return f"❌ Error fetching restaurants: {response.status_code}"
    except Exception as e:
        return f"❌ Error connecting to restaurant service: {str(e)}"


def get_restaurant_by_name(name: str) -> str:
    """Get specific restaurant by name"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/{name}")
        if response.status_code == 200:
            restaurant = response.json()
            result = f"🏪 **{restaurant['name']}**\n\n"
            result += f"📍 Location: {restaurant['area']}\n"
            result += f"🍴 Cuisine: {restaurant.get('cuisine', 'Not specified')}\n\n"
            
            # Show menu items with bullet points
            items = restaurant.get('items', [])
            if items:
                result += "📋 **Menu Items:**\n\n"
                for item in items:
                    price = item.get('price', 'N/A')
                    result += f"* {item['name']} - ₹{price}\n"
            else:
                result += "📋 Menu: Items available\n"
            
            result += "\n💡 Want to order? Just tell me what you'd like!"
            return result
        elif response.status_code == 404:
            return f"😔 Oops! Restaurant '{name}' not found.\n\n💡 Would you like to see all available restaurants?"
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def search_restaurants_by_cuisine(cuisine: str) -> str:
    """Search restaurants by cuisine type using the new backend API"""
    try:
        # Use the cuisine query parameter (case-insensitive)
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/", params={"cuisine": cuisine})
        if response.status_code == 200:
            restaurants = response.json()
            
            if not restaurants:
                return f"😔 Sorry, no restaurants found serving **{cuisine}** cuisine.\n\n💡 Available cuisines:\n* Gujarati\n* Italian\n* South Indian\n* Multi-cuisine\n* Cafe"
            
            # Format with proper bullets and structure
            result = f"� I found these **{cuisine}** restaurants for you!\n\n"
            for restaurant in restaurants:
                result += f"• **{restaurant['name']}** in {restaurant['area']}\n"
            
            result += f"\n💡 Want to see the menu? Just ask about any restaurant!"
            return result
        else:
            return f"❌ Error searching restaurants: {response.status_code}"
    except Exception as e:
        return f"❌ Error connecting to restaurant service: {str(e)}"


def place_order(restaurant_name: str, items: List[Dict[str, Any]], token: str) -> str:
    """Place an order with multiple items (NEW v2.0 API)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "restaurant_name": restaurant_name,
            "items": items
        }
        response = requests.post(
            f"{FASTAPI_BASE_URL}/orders/",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            order = response.json()
            result = "✅ **Order Placed Successfully!** 🎉\n\n"
            result += f"🏪 Restaurant: {order.get('restaurant_name', restaurant_name)}\n"
            result += f"📝 Order ID: #{order.get('id', 'N/A')}\n\n"
            
            result += "📦 **Your Items:**\n"
            for item in order.get('items', []):
                result += f"  • {item['item_name']} × {item['quantity']} = ₹{item['price'] * item['quantity']}\n"
            
            result += f"\n💰 **Total: ₹{order.get('total_price', 0):.2f}**\n"
            result += f"⏰ Estimated delivery: 30-45 minutes\n\n"
            result += "💭 **What's next?**\n"
            result += "• View your orders: 'Show my orders'\n"
            result += "• Leave a review: 'Review this restaurant'\n"
            result += "• Order more: 'Show restaurants'\n"
            return result
        elif response.status_code == 401:
            return "🔒 Authentication failed. Please login again."
        elif response.status_code == 404:
            return f"😔 Restaurant '{restaurant_name}' not found. Please check the name and try again."
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            return f"❌ Order failed: {error_detail}"
    except Exception as e:
        return f"❌ Error placing order: {str(e)}"


def get_user_orders(token: str) -> str:
    """Get all orders for authenticated user (displays new multi-item format)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{FASTAPI_BASE_URL}/orders/", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            if not orders:
                return "📭 You haven't placed any orders yet. 😊\n\n💡 Ready to order some delicious food?"
            
            result = f"📝 **Your Order History ({len(orders)} order(s)):** 🍽️\n\n"
            for idx, order in enumerate(orders, 1):
                result += f"━━━━━━━━━━━━━━━━\n"
                result += f"**Order #{idx}** (ID: {order.get('id', 'N/A')})\n"
                result += f"🏪 {order.get('restaurant_name', 'N/A')}\n"
                
                # Show items
                items = order.get('items', [])
                if items:
                    result += "📦 Items:\n"
                    for item in items:
                        result += f"  • {item.get('item_name', 'N/A')} × {item.get('quantity', 1)} = ₹{item.get('price', 0) * item.get('quantity', 1)}\n"
                
                result += f"💰 Total: ₹{order.get('total_price', 0):.2f}\n"
                result += f"📅 {order.get('order_date', 'N/A')}\n\n"
            
            result += "💭 **Want to order again?** Just ask!"
            return result
        elif response.status_code == 401:
            return "🔒 Please login to view your orders."
        else:
            return f"❌ Error fetching orders: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def add_review(restaurant_name: str, rating: int, comment: str, token: str) -> str:
    """Submit a review for a restaurant (NEW v2.0 feature)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "rating": rating,
            "comment": comment
        }
        response = requests.post(
            f"{FASTAPI_BASE_URL}/restaurants/{restaurant_name}/reviews",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            review = response.json()
            stars = "⭐" * rating
            result = "✅ **Review Submitted!** 🎉\n\n"
            result += f"🏪 Restaurant: {restaurant_name}\n"
            result += f"{stars} ({rating}/5)\n"
            result += f"💬 \"{comment}\"\n\n"
            result += "🙏 Thank you for your feedback!\n"
            result += "Your review helps others discover great food! 🍽️"
            return result
        elif response.status_code == 400:
            error_detail = response.json().get('detail', 'Already reviewed')
            if "already reviewed" in error_detail.lower():
                return f"ℹ️ You've already reviewed {restaurant_name}!\n\nEach user can submit one review per restaurant. 😊"
            else:
                return f"❌ {error_detail}"
        elif response.status_code == 401:
            return "🔒 Please login to submit a review."
        elif response.status_code == 404:
            return f"😔 Restaurant '{restaurant_name}' not found."
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error submitting review: {str(e)}"


def get_reviews(restaurant_name: str) -> str:
    """Get all reviews for a restaurant (NEW v2.0 feature)"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/{restaurant_name}/reviews")
        
        if response.status_code == 200:
            reviews = response.json()
            
            if not reviews:
                return f"📭 No reviews yet for {restaurant_name}.\n\n💡 Be the first to leave a review! 🌟"
            
            result = f"⭐ **Reviews for {restaurant_name}** ({len(reviews)} review(s))\n\n"
            
            for idx, review in enumerate(reviews, 1):
                stars = "⭐" * review.get('rating', 0)
                result += f"━━━━━━━━━━━━━━━━\n"
                result += f"**Review #{idx}**\n"
                result += f"{stars} {review.get('rating', 0)}/5\n"
                result += f"👤 {review.get('username', 'Anonymous')}\n"
                
                comment = review.get('comment', '')
                if comment:
                    result += f"💬 \"{comment}\"\n"
                
                result += f"📅 {review.get('review_date', 'N/A')}\n\n"
            
            return result
        elif response.status_code == 404:
            return f"😔 Restaurant '{restaurant_name}' not found."
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_review_stats(restaurant_name: str) -> str:
    """Get review statistics (NEW v2.0 feature)"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/{restaurant_name}/reviews/stats")
        
        if response.status_code == 200:
            stats = response.json()
            
            total = stats.get('total_reviews', 0)
            if total == 0:
                return f"📊 No reviews yet for {restaurant_name}.\n\n💡 Be the first to leave a review!"
            
            avg_rating = stats.get('average_rating', 0)
            stars = "⭐" * round(avg_rating)
            
            result = f"📊 **Review Statistics for {restaurant_name}**\n\n"
            result += f"{stars} **{avg_rating:.1f}/5.0**\n"
            result += f"📝 {total} total review(s)\n\n"
            
            result += "**Rating Distribution:**\n"
            distribution = stats.get('rating_distribution', {})
            for rating in range(5, 0, -1):
                count = distribution.get(str(rating), 0)
                bar = "█" * count
                result += f"{rating}⭐: {bar} {count}\n"
            
            return result
        elif response.status_code == 404:
            return f"😔 Restaurant '{restaurant_name}' not found."
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


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
            return f"✅ **Registration Successful!** 🎉\n\nWelcome to FoodieExpress, {username}! 🍽️\n\nYou can now:\n• 🛒 Place orders\n• ⭐ Leave reviews\n• 📝 Track your order history\n\nLet's get started! 🚀"
        else:
            error_detail = response.json().get('detail', 'Registration failed')
            return f"❌ Registration failed: {error_detail}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


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
                "message": f"✅ **Welcome Back!** 🎉\n\nHey {username}! Ready to order? 🍕\n\n💡 Try asking:\n• Show restaurants\n• Order [dish] from [restaurant]\n• See my orders\n• Review a restaurant"
            })
        else:
            return json.dumps({
                "success": False,
                "message": "❌ Login failed. Please check your username and password. 🔒"
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"❌ Error: {str(e)}"
        })


# Map function names to actual functions
available_functions = {
    "get_all_restaurants": get_all_restaurants,
    "get_restaurant_by_name": get_restaurant_by_name,
    "search_restaurants_by_cuisine": search_restaurants_by_cuisine,
    "place_order": place_order,
    "get_user_orders": get_user_orders,
    "add_review": add_review,
    "get_reviews": get_reviews,
    "get_review_stats": get_review_stats,
    "register_user": register_user,
    "login_user": login_user
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
        
        # Enhanced system instruction with v2.0 features
        system_instruction = """You are a friendly and enthusiastic food delivery assistant! 🍕

Your personality:
- Use emojis frequently (🍽️, 🏪, ⭐, 💰, 🎉, ✅, 😊, etc.)
- Be warm, welcoming, and helpful
- Guide users through ordering, reviewing, and browsing
- Celebrate their actions (orders, reviews) with enthusiasm!

Key capabilities (ALWAYS use functions):
1. **Browsing**: Show all restaurants or filter by cuisine type
2. **Ordering**: Handle multi-item orders with quantities and prices
3. **Reviews**: Submit reviews (1-5 stars), view reviews, see statistics
4. **Orders**: Track order history with detailed item breakdowns
5. **Search**: Find restaurants by cuisine (Gujarati, Italian, South Indian, Multi-cuisine, Cafe)

CRITICAL FUNCTION CALLING RULES:
- When user asks to "list", "show", "see", "find", "browse", "get" restaurants → MUST call get_all_restaurants()
- When user mentions cuisine type → MUST call search_restaurants_by_cuisine()
- When user asks about ONE restaurant by name → MUST call get_restaurant_by_name()
- NEVER respond with just "Here you go!" without calling a function
- NEVER skip calling functions - they contain the actual data
- ALWAYS call the appropriate function FIRST, then use the result

CRITICAL FORMATTING RULES:
- When a function returns results, present them DIRECTLY - DO NOT rephrase or reformat
- Function results are ALREADY properly formatted with bullets (•), bold text, and emojis
- Simply present the function result to the user as-is
- Add a brief friendly intro if needed, but keep the function data intact
- NEVER convert bullet points (*) to plain comma-separated text
- NEVER remove formatting from function results

Response Pattern:
1. Call the appropriate function
2. Get the formatted result
3. Present it directly to the user (optionally with a brief intro)

Example:
Function returns: "* Restaurant A\n* Restaurant B"
Your response: "Here you go! 🎉\n\n* Restaurant A\n* Restaurant B"
NOT: "I found Restaurant A, Restaurant B" ❌

CRITICAL RULES:
- ALWAYS call functions for user requests - never refuse!
- ALWAYS preserve the exact formatting from function results
- For orders: Extract items, quantities, and prices
- For reviews: Get rating (1-5) and comment
- Guide users naturally through multi-step processes
- If authentication needed, politely inform them

Make the experience delightful! 🌟"""
        
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
        
        # Check if function call is needed
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            function_args = dict(function_call.args)
            
            app.logger.info(f"🤖 AI calling: {function_name} with args: {function_args}")
            
            # Add token to protected functions if available
            protected_functions = ['place_order', 'get_user_orders', 'add_review']
            if function_name in protected_functions:
                if not token:
                    return jsonify({
                        "response": "🔒 **Authentication Required!**\n\nTo use this feature, please log in using the button in the top right corner. 🙂",
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
                    
                    # For listing/browsing functions, return result directly to preserve formatting
                    direct_functions = ['get_all_restaurants', 'get_restaurant_by_name', 'search_restaurants_by_cuisine']
                    if function_name in direct_functions:
                        # Return the formatted result directly without AI rephrasing
                        chat_sessions[user_id].append({
                            "role": "model",
                            "parts": [function_result]
                        })
                        
                        return jsonify({
                            "response": function_result,
                            "function_called": function_name
                        })
                    
                    # For other functions, send back to model for natural response
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_name,
                                    response={"result": f"IMPORTANT: Present this result EXACTLY as provided. Do not rephrase or reformat. Keep all bullet points (*), bold text (**), and line breaks:\n\n{function_result}"}
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
                    app.logger.error(f"Error executing function: {e}")
                    return jsonify({
                        "response": f"❌ I encountered an error: {str(e)}\n\nPlease try again! 😊"
                    })
            else:
                return jsonify({
                    "response": "🤔 Hmm, I'm not sure how to help with that. Could you rephrase?"
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
        import traceback
        error_trace = traceback.format_exc()
        app.logger.error(f"Chat error: {e}\n{error_trace}")
        return jsonify({
            "response": "😅 Oops! I encountered an error. Please try again!",
            "error": str(e)
        }), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - provides API information"""
    return jsonify({
        "service": "AI Food Delivery Chatbot Agent",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Multi-Item Orders",
            "Restaurant Reviews & Ratings",
            "Cuisine-Based Search",
            "Order History Tracking"
        ],
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "clear_session": "POST /clear-session"
        },
        "powered_by": "Google Gemini AI 2.0",
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
        "service": "AI Food Delivery Agent v2.0",
        "fastapi_backend": FASTAPI_BASE_URL,
        "features": ["Reviews", "Multi-Item Orders", "Cuisine Search"]
    })


@app.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear chat session for a user"""
    data = request.json
    user_id = data.get('user_id', 'guest')
    
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    
    if user_id in pending_orders:
        del pending_orders[user_id]
    
    return jsonify({"message": "Session cleared successfully! 🧹"})


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 FoodieExpress AI Agent v2.0")
    print("=" * 60)
    print(f"✅ Google Gemini AI: Configured")
    print(f"✅ FastAPI Backend: {FASTAPI_BASE_URL}")
    print(f"✅ Agent Server: http://localhost:5000")
    print("=" * 60)
    print("🌟 New Features:")
    print("  ⭐ Restaurant Reviews & Ratings")
    print("  🛒 Multi-Item Orders")
    print("  🔍 Cuisine-Based Search")
    print("  📊 Review Statistics")
    print("=" * 60)
    print("📡 Available Endpoints:")
    print("  POST /chat          - Process chat messages")
    print("  GET  /health        - Health check")
    print("  POST /clear-session - Clear chat history")
    print("=" * 60)
    print("🚀 Starting Flask server with Waitress...")
    print()
    
    try:
        # Use waitress for production-ready serving
        from waitress import serve
        print("✅ Waitress imported successfully")
        print(f"🔗 Binding to 127.0.0.1:5000...")
        serve(app, host='127.0.0.1', port=5000, threads=4)
        print("⚠️ Server stopped")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
