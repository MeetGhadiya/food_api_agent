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
        description="REQUIRED: Get complete list of ALL restaurants with name, location, and cuisine. MUST be called when user asks to: list, show, see, browse, get, display, or find restaurants (any variation). DO NOT respond without calling this function for restaurant lists.",
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
        name="search_restaurants_by_item",
        description="PRIORITY TOOL: Search for restaurants that serve a specific menu item (e.g., Pizza, Dhokla, Bhel, Pasta, Dosa). Use this FIRST when user wants to order or find a specific food item. This helps identify which restaurants offer that item.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "item_name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The name of the food item to search for (e.g., 'Pizza', 'Dhokla', 'Bhel')"
                )
            },
            required=["item_name"]
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
    """
    Fetch all restaurants from FastAPI.
    
    CRITICAL: This function returns the COMPLETE list of ALL restaurants.
    The AI MUST display every single restaurant returned - NO truncation allowed!
    """
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/")
        if response.status_code == 200:
            restaurants = response.json()
            if not restaurants:
                return "No restaurants are currently available. 😔"
            
            # CRITICAL: Count total restaurants
            total_count = len(restaurants)
            
            # Format as a DIRECT, non-paraphrasable list
            result = f"� SHOWING ALL Available RESTAURANTS:\n\n"
            
            for idx, restaurant in enumerate(restaurants, 1):
                result += f"═══════════════════════════════════════\n"
                result += f"🔸#{idx} RESTAURANT \n"
                result += f"🏪 Name: {restaurant['name']}\n"
                result += f"📍 Area: {restaurant['area']}\n"
                result += f"🍴 Cuisine: {restaurant.get('cuisine', 'N/A')}\n"
            
            result += f"═══════════════════════════════════════\n"
            result += f"\n💡 Want to see the menu? Just ask about any restaurant!"

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
                    # Use 'item_name' instead of 'name' - that's the correct key
                    item_name = item.get('item_name', item.get('name', 'Unknown Item'))
                    price = item.get('price', 'N/A')
                    result += f"• **{item_name}** - ₹{price}\n"
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


def search_restaurants_by_item(item_name: str) -> str:
    """
    Search for restaurants that serve a specific menu item.
    
    This function calls the new FastAPI endpoint GET /search/items
    to find all restaurants that have the specified item on their menu.
    
    Args:
        item_name: The name of the food item to search for (e.g., "Pizza", "Dhokla", "Bhel")
    
    Returns:
        A formatted string with the list of restaurants serving that item,
        or a friendly message if no restaurants are found.
    """
    try:
        # Call the new FastAPI endpoint with proper error handling
        response = requests.get(
            f"{FASTAPI_BASE_URL}/search/items",
            params={"item_name": item_name},
            timeout=5  # 5 second timeout to prevent hanging
        )
        
        # Handle successful response
        if response.status_code == 200:
            restaurants = response.json()
            
            # No restaurants found with this item
            if not restaurants:
                return f"😔 Sorry, I couldn't find any restaurants that serve **{item_name}**.\n\n💡 Try:\n• Checking the spelling\n• Searching for similar items\n• Browsing all restaurants with 'show restaurants'"
            
            # Format the results in a user-friendly way
            result = f"🔍 Great news! I found **{item_name}** at these restaurants:\n\n"
            
            for restaurant in restaurants:
                result += f"• **{restaurant['name']}** in {restaurant['area']}"
                
                # Add cuisine info if available
                if restaurant.get('cuisine'):
                    result += f" (Cuisine: {restaurant['cuisine']})"
                
                result += "\n"
            
            result += f"\n💡 **Next steps:**\n"
            result += f"• Ask 'Show menu for [restaurant name]' to see full menu\n"
            result += f"• Say 'Order {item_name} from [restaurant name]' to place an order\n"
            
            return result
        
        # Handle not found error
        elif response.status_code == 404:
            return f"😔 Sorry, I couldn't find any restaurants that serve **{item_name}**."
        
        # Handle other HTTP errors
        else:
            return f"❌ Error searching for {item_name}: Server returned status {response.status_code}"
    
    # Handle network/connection errors
    except requests.exceptions.Timeout:
        return f"⏱️ The search for {item_name} timed out. Please try again!"
    except requests.exceptions.ConnectionError:
        return f"🔌 Cannot connect to the restaurant database. Please check if the backend service is running."
    except Exception as e:
        return f"❌ An unexpected error occurred while searching for {item_name}: {str(e)}"


def place_order(restaurant_name: str, items: List[Dict[str, Any]], token: str) -> str:
    """
    Place an order with multiple items (NEW v2.0 API).
    
    PHASE 2: ORDER PLACEMENT DEBUG & FIX
    
    This function now includes extensive logging to debug order placement failures.
    Every step of the order process is logged for troubleshooting.
    """
    try:
        # PHASE 2: Detailed logging for debugging
        print("\n" + "="*60)
        print("🛒 PHASE 2: ORDER PLACEMENT DEBUG")
        print("="*60)
        print(f"📝 Restaurant: {restaurant_name}")
        print(f"📦 Items to order: {len(items)}")
        print(f"🔐 Token present: {'Yes' if token else 'No'}")
        print(f"🔐 Token length: {len(token) if token else 0}")
        
        # Build headers
        headers = {"Authorization": f"Bearer {token}"}
        print(f"\n📋 Request Headers:")
        print(f"   Authorization: Bearer {token[:20]}...{token[-20:] if len(token) > 40 else token}")
        
        # Build payload - CRITICAL: Must match FastAPI OrderCreate schema
        data = {
            "restaurant_name": restaurant_name,
            "items": items
        }
        
        print(f"\n📤 Request Payload (JSON):")
        print(json.dumps(data, indent=2))
        
        # Validate items structure before sending
        for idx, item in enumerate(items):
            if 'item_name' not in item:
                error_msg = f"❌ Item {idx} missing 'item_name' field"
                print(error_msg)
                return error_msg
            if 'quantity' not in item:
                error_msg = f"❌ Item {idx} missing 'quantity' field"
                print(error_msg)
                return error_msg
            if 'price' not in item:
                error_msg = f"❌ Item {idx} missing 'price' field"
                print(error_msg)
                return error_msg
        
        print(f"\n✅ Items validation passed")
        print(f"🌐 Sending POST request to: {FASTAPI_BASE_URL}/orders/")
        
        # Make the API call
        response = requests.post(
            f"{FASTAPI_BASE_URL}/orders/",
            json=data,
            headers=headers,
            timeout=10  # Add timeout to prevent hanging
        )
        
        print(f"\n📥 Response Status Code: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📥 Response Body:")
            print(json.dumps(response_json, indent=2))
        except:
            print(f"📥 Response Body (raw): {response.text[:500]}")
        
        print("="*60 + "\n")
        
        # Handle response
        if response.status_code == 201 or response.status_code == 200:
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
            return "🔒 Authentication failed. Your session may have expired. Please refresh the page and try again."
        elif response.status_code == 404:
            return f"😔 Restaurant '{restaurant_name}' not found. Please check the name and try again."
        elif response.status_code == 422:
            # Validation error - provide detailed feedback
            error_detail = response.json().get('detail', 'Validation error')
            return f"❌ Order validation failed: {error_detail}\n\nPlease check your order details and try again."
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            return f"❌ Order failed (HTTP {response.status_code}): {error_detail}\n\nPlease try again or contact support."
    except requests.exceptions.Timeout:
        return "⏱️ Order request timed out. Please check your connection and try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Cannot connect to the order service. Please ensure the backend is running."
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ ORDER PLACEMENT EXCEPTION:")
        print(error_trace)
        return f"❌ Error placing order: {str(e)}\n\nPlease try again or contact support."


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
    "search_restaurants_by_item": search_restaurants_by_item,
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
    """
    Process chat message and return AI response.
    
    PHASE 1.2 & 1.3: SEAMLESS SINGLE SIGN-ON IMPLEMENTATION
    
    This endpoint now extracts the JWT token from the Authorization header,
    eliminating the need for users to log in twice (once on website, once in chat).
    
    The token is automatically passed to all tools that require authentication,
    enabling a seamless user experience.
    """
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'guest')
        
        # PHASE 1.2: Extract token from Authorization header (preferred) or body (fallback)
        # This is the KEY to seamless authentication!
        auth_header = request.headers.get('Authorization', '')
        token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            # Extract token from "Bearer <token>" format
            token = auth_header.split('Bearer ')[1].strip()
            app.logger.info(f"🔐 Token extracted from Authorization header for user: {user_id}")
        elif data.get('token'):
            # Fallback: token in request body (backward compatibility)
            token = data.get('token')
            app.logger.info(f"🔐 Token extracted from request body for user: {user_id}")
        else:
            app.logger.info(f"🔓 No token found - user is not authenticated: {user_id}")
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Initialize chat session if not exists
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []
        
        # PHASE 1.3 & 3: Enhanced system instruction with seamless auth + improved UX
        system_instruction = """You are a friendly and enthusiastic food delivery assistant! 🍕

Your personality:
- Use emojis frequently (🍽️, 🏪, ⭐, 💰, 🎉, ✅, 😊, 🔍, etc.)
- Be warm, welcoming, and helpful
- Guide users through ordering, reviewing, and browsing
- Celebrate their actions (orders, reviews) with enthusiasm!

Key capabilities (ALWAYS use functions to get real data):
1. **Item Search**: Find which restaurants serve a specific dish (NEW!)
2. **Browsing**: Show all restaurants or filter by cuisine type
3. **Ordering**: Handle multi-item orders with quantities and prices
4. **Reviews**: Submit reviews (1-5 stars), view reviews, see statistics
5. **Orders**: Track order history with detailed item breakdowns
6. **Search**: Find restaurants by cuisine (Gujarati, Italian, South Indian, Multi-cuisine, Cafe)

⚠️ CRITICAL: SEAMLESS AUTHENTICATION (Phase 1.3)
**YOU MUST NEVER ASK AUTHENTICATED USERS TO LOG IN!**

- If a user is already authenticated (a token is provided with their message), they are LOGGED IN
- NEVER ask them for their username or password
- NEVER tell them to "please login first"
- IMMEDIATELY proceed with their requested action (place order, view orders, etc.)
- The authentication system handles everything automatically behind the scenes

Example:
❌ WRONG: "Please log in first to place an order"
✅ CORRECT: "Great! Let me place that order for you..." [proceeds to place order]

⚠️ CRITICAL: PRIORITIZE USER INTENT (Phase 3.2 Enhancement)
Your PRIMARY goal is to solve the user's immediate request intelligently:

1. **When user wants to order/find a specific food item** (e.g., "order bhel", "find pizza", "I want pasta"):
   - IMMEDIATELY call search_restaurants_by_item(item_name) as your FIRST action
   - Do NOT ask for cuisine preference first
   - Do NOT ask which restaurant first
   - Find the item, then present options to the user
   
2. **When user asks about a specific restaurant that was JUST mentioned**:
   - Pay close attention to conversation history
   - If a restaurant was mentioned in previous turn, vague questions like:
     * "what is the menu?"
     * "yes menu please"
     * "show me their items"
     * "tell me more"
   - All refer to THAT SPECIFIC RESTAURANT - do NOT ask them to repeat the name
   - Call get_restaurant_by_name() with the restaurant from context

3. **Be Proactive and Helpful** (Phase 3 UX Enhancement):
   - If a specific search fails (e.g., "find bhel in Gujarati restaurants"), don't give up
   - Proactively suggest a broader search
   - Example: "I couldn't find bhel in any Gujarati restaurants, but I did find it at Honest Restaurant (Multi-cuisine). Would you like to see their menu?"
   - Always provide helpful next steps
   
   - **When user asks for something too broad** (e.g., "list all items"):
     * DO NOT simply refuse with "I can't do that"
     * Instead, acknowledge the limitation and offer helpful alternatives
     * Example: "That would be a very long list! 📋 To help you find what you're looking for, I can:
       • Show you the full menu for a specific restaurant
       • Search for a particular item (like pizza, dhokla, etc.)
       • Filter by cuisine type (Gujarati, Italian, etc.)
       What works best for you?"

4. **Maintain Conversation Context** (Phase 3.1):
   - Full conversation history is provided to you in every request
   - Use this context to understand follow-up questions
   - Track what restaurant, items, or topics were just discussed
   - Make the conversation flow naturally without repetition

⚠️ CRITICAL FUNCTION CALLING RULES:
- When user wants to ORDER or FIND a specific ITEM → MUST call search_restaurants_by_item() FIRST
- When user asks to "list", "show", "see", "browse" restaurants → MUST call get_all_restaurants()
- When user mentions a cuisine type (Gujarati, Italian, etc.) → MUST call search_restaurants_by_cuisine()
- When user asks about ONE specific restaurant → MUST call get_restaurant_by_name()
- ALWAYS call functions to get real data - NEVER make up restaurant information
- NEVER respond without calling a function when data is needed

🚀 INSTANT RESPONSE RULE - NO INTERMEDIATE MESSAGES:
When user asks to "list", "show all", or "browse" restaurants:
- DO NOT send a "waiting" or "let me get that" message first
- IMMEDIATELY call the function WITHOUT any prior response
- Only respond ONCE with the complete function results
- The user wants SPEED - don't make them wait for intermediate messages!

CORRECT Pattern (list requests):
User: "list all restaurants"
[IMMEDIATELY call get_all_restaurants() - NO MESSAGE BEFORE THIS]
You: [ONE response with full restaurant list]

WRONG Pattern (NEVER DO THIS):
User: "list all restaurants"  
You: "Okay! Let me get that for you! 🔍" ← WRONG! Don't send this!
[Call function]
You: [Restaurant list] ← Now user had to wait twice!

⚠️ CRITICAL RESPONSE RULES AFTER FUNCTION CALLS:
When you receive function results, you MUST present the data to the user.
- The function result contains the COMPLETE, FORMATTED list of restaurants/items
- Your job is to present this data naturally in your response
- Include the intro message AND the complete data from the function
- Keep ALL formatting: bullets (•), bold text (**), emojis
- NEVER say "Here you go!" without including the actual data

🚨🚨🚨 ABSOLUTELY CRITICAL - DISPLAY FUNCTION RESULTS VERBATIM 🚨🚨🚨
**YOU MUST COPY-PASTE THE ENTIRE FUNCTION RESULT INTO YOUR RESPONSE!**

MANDATORY RULES:
1. When a function returns data (especially lists), you MUST include THE COMPLETE, UNMODIFIED OUTPUT in your response
2. DO NOT summarize, paraphrase, or truncate ANY part of the function result
3. DO NOT say "here are the results" and then NOT show them
4. DO NOT show partial lists (e.g., showing 3 out of 7 items)
5. TREAT THE FUNCTION OUTPUT AS A LITERAL BLOCK OF TEXT TO QUOTE VERBATIM

🔴 IF THE FUNCTION SAYS "SHOWING ALL 7 RESTAURANTS", YOUR RESPONSE MUST CONTAIN ALL 7 RESTAURANTS
🔴 IF THE FUNCTION INCLUDES NUMBERED ITEMS 1-7, YOUR RESPONSE MUST SHOW ITEMS 1-7
🔴 DO NOT ADD YOUR OWN INTRO AND THEN TRUNCATE THE LIST

CORRECT Response Pattern:
User: "list all restaurants"
Function returns: "📋 SHOWING ALL 7 RESTAURANTS:\n\n═══...═══\n🔸 RESTAURANT #1 OF 7\n🏪 Name: Swati Snacks\n📍 Area: Ashram Road\n🍴 Cuisine: Gujarati\n═══...═══\n🔸 RESTAURANT #2 OF 7\n🏪 Name: Agashiye\n..." [continues through #7]
Your response: [Short intro] + [PASTE ENTIRE FUNCTION OUTPUT HERE UNMODIFIED]

WRONG Response Pattern (ABSOLUTELY FORBIDDEN):
User: "list all restaurants"  
Function returns: [7 restaurants]
Your response: "Okay! Here's a list of ALL the restaurants! 🎉" ← WRONG! WHERE IS THE LIST?!

For other operations:
- Orders: Extract items, quantities, and prices from conversation
- Reviews: Get rating (1-5) and comment text
- Guide users naturally through multi-step processes
- If authentication needed, politely inform them

EXAMPLE DESIRED CONVERSATION FLOW (Phase 4):
User: "order bhel"
You: "I can help with that! Let me find which restaurants serve bhel... 🔍" [Call search_restaurants_by_item]
You: "Okay, I found bhel at: • **Swati Snacks** in Ashram Road • **Honest Restaurant** in CG Road\n\nWhich one would you like to order from?"
User: "Swati Snacks"
You: "Excellent choice! Let me get the menu for Swati Snacks..." [Call get_restaurant_by_name]
You: "Here is the menu for **Swati Snacks**: ... (displays menu) ... What would you like to add to your order besides bhel?"

Make the experience delightful and intelligent! 🌟"""
        
        # Create model with function calling
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            tools=[tools],
            system_instruction=system_instruction
        )
        
        # REMOVED: Pre-detection logic that was causing issues
        # We'll let the AI decide when to call functions naturally
        
        # Normal AI processing for other queries
        # Add user message to history
        chat_sessions[user_id].append({
            "role": "user",
            "parts": [user_message]
        })
        
        # Start chat with history
        chat = model.start_chat(history=chat_sessions[user_id][:-1])
        
        # ==================== PHASE 1: Send message to AI ====================
        # The AI will decide if a function needs to be called
        response = chat.send_message(user_message)
        
        # ==================== PHASE 2: Check if AI wants to call a function ====================
        response_part = response.candidates[0].content.parts[0]
        
        # Check if this is a function call (not a direct text response)
        if hasattr(response_part, 'function_call') and response_part.function_call:
            function_call = response_part.function_call
            function_name = function_call.name
            function_args = dict(function_call.args)
            
            app.logger.info(f"🤖 AI decided to call function: {function_name}")
            app.logger.info(f"📋 Function arguments: {function_args}")
            
            # ==================== PHASE 3: Execute the Python function ====================
            # Add authentication token for protected functions
            protected_functions = ['place_order', 'get_user_orders', 'add_review']
            if function_name in protected_functions:
                if not token:
                    # User must log in first
                    chat_sessions[user_id].append({
                        "role": "model",
                        "parts": ["🔒 Authentication required"]
                    })
                    return jsonify({
                        "response": "🔒 **Authentication Required!**\n\nTo use this feature, please log in using the button in the top right corner. 🙂",
                        "requires_auth": True
                    })
                function_args['token'] = token
            
            # Execute the actual Python function
            if function_name not in available_functions:
                error_msg = f"🤔 Hmm, I tried to call an unknown function: {function_name}"
                chat_sessions[user_id].append({"role": "model", "parts": [error_msg]})
                return jsonify({"response": error_msg})
            
            try:
                function_to_call = available_functions[function_name]
                app.logger.info(f"⚙️ Executing: {function_name}(**{function_args})")
                
                # Call the function and get the result
                function_result = function_to_call(**function_args)
                
                app.logger.info(f"✅ Function returned: {function_result[:200]}...")  # Log first 200 chars
                
                # ==================== SPECIAL CASE: Login (returns JSON) ====================
                if function_name == 'login_user':
                    login_data = json.loads(function_result)
                    chat_sessions[user_id].append({
                        "role": "model",
                        "parts": [login_data['message']]
                    })
                    
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
                
                # ==================== CRITICAL FIX: BYPASS AI FOR LIST FUNCTIONS ====================
                # The AI keeps truncating restaurant lists, so we'll return raw data for these functions
                bypass_ai_functions = ['get_all_restaurants', 'search_restaurants_by_cuisine']
                
                if function_name in bypass_ai_functions:
                    app.logger.info(f"⚡ BYPASSING AI for {function_name} - returning raw function result to prevent truncation")
                    final_text = function_result  # Use raw function result directly
                    
                    # Add to chat history
                    chat_sessions[user_id].append({
                        "role": "model",
                        "parts": [final_text]
                    })
                    
                    return jsonify({
                        "response": final_text,
                        "function_called": function_name
                    })
                
                # ==================== PHASE 4: Send function result back to AI ====================
                # For other functions, we still use AI's natural language generation
                
                app.logger.info(f"📤 Sending function result back to AI for natural language generation...")
                
                # Send the function result back to the model
                second_response = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": function_result}
                            )
                        )]
                    )
                )
                
                # ==================== PHASE 5: Extract final natural language response ====================
                final_text = second_response.candidates[0].content.parts[0].text
                
                app.logger.info(f"💬 AI's final response: {final_text[:200]}...")
                
                # Add to chat history
                chat_sessions[user_id].append({
                    "role": "model",
                    "parts": [final_text]
                })
                
                return jsonify({
                    "response": final_text,
                    "function_called": function_name
                })
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                app.logger.error(f"❌ Error executing function {function_name}: {e}")
                app.logger.error(f"Stack trace:\n{error_trace}")
                
                error_msg = f"❌ I encountered an error while trying to {function_name.replace('_', ' ')}. Please try again! 😊"
                chat_sessions[user_id].append({"role": "model", "parts": [error_msg]})
                
                return jsonify({
                    "response": error_msg,
                    "error": str(e)
                })
        
        # ==================== NO FUNCTION CALL: Direct text response ====================
        else:
            # The AI responded directly without needing to call a function
            text_response = response_part.text
            
            app.logger.info(f"💬 Direct AI response (no function): {text_response[:200]}...")
            
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
