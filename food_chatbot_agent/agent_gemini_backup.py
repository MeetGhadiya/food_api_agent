"""
AI Food Delivery Chatbot Agent - V4.0
Built with Ollama (Local AI) and Flask
Enhanced with Personalized Recommendations & Business Intelligence

V4.0 FEATURES:
- Personalized AI greetings based on user history
- Proactive review requests after orders
- Admin dashboard integration
- Enhanced user engagement
- LOCAL AI with Ollama (no API keys needed!)

PREVIOUS ENHANCEMENTS:
- Reviews, Multi-Item Orders, and Cuisine Search
- Redis session storage for scalability
- Environment variable validation
- Improved session management architecture

This agent processes natural language queries and converts them to FastAPI calls.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional, List
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("⚠️  WARNING: GOOGLE_API_KEY not found in environment variables")
    print("   AI functionality will be limited")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Google Gemini AI configured")

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"])

# ==================== OLLAMA CONFIGURATION ====================
# Local AI model - runs entirely on your machine!
# No API keys, no billing, completely free!

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")  # Default model
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

print(f"🤖 Using Ollama Model: {OLLAMA_MODEL}")
print(f"🔗 Ollama Server: {OLLAMA_URL}")

# API Configuration
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# ==================== SESSION STORAGE ====================
# HIGH-001 SECURITY CONCERN: In-memory storage is NOT production-ready!
# Current implementation stores sessions in Python dictionaries, which:
# - Are lost on server restart (data loss)
# - Don't scale across multiple server instances
# - Can cause memory leaks with long-running sessions
# - Don't support distributed deployments

# TEMPORARY: In-memory storage (for development only)
chat_sessions: Dict[str, list] = {}
pending_orders: Dict[str, Dict[str, Any]] = {}
# V4.0: Track recent orders for proactive review prompts
recent_orders: Dict[str, Dict[str, Any]] = {}  # {user_id: {restaurant_name, order_id, turns_since_order}}

# ==================== REDIS SESSION STORE (V4.0 PRODUCTION-READY) ====================
# V4.0: Redis integration for stateful, persistent sessions

try:
    import redis
    redis_available = True
    print("✅ Redis module imported successfully")
except ImportError:
    redis_available = False
    print("⚠️  Redis module not available - using fallback in-memory storage")
    print("   Install with: pip install redis")

# Initialize Redis client (if available)
redis_client = None
if redis_available:
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True,
            socket_connect_timeout=5
        )
        # Test connection
        redis_client.ping()
        print(f"✅ Redis connected: {os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Falling back to in-memory storage")
        redis_client = None

# Redis Helper Functions
def save_to_redis(user_id: str, key: str, value: Any, ttl: int = 600):
    """
    Save data to Redis with TTL (Time To Live).
    
    Args:
        user_id: User identifier
        key: Data key (e.g., 'last_entity', 'pending_order')
        value: Data to store (will be JSON serialized)
        ttl: Time to live in seconds (default 600 = 10 minutes)
    """
    if redis_client:
        try:
            redis_key = f"session:{user_id}:{key}"
            redis_client.setex(
                redis_key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"⚠️  Redis save failed: {e}")
            return False
    else:
        # Fallback to in-memory storage
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []
        # Store in a metadata dict
        if not hasattr(chat_sessions[user_id], '__dict__'):
            chat_sessions[user_id] = []
        # Use pending_orders dict as fallback
        fallback_key = f"{user_id}:{key}"
        pending_orders[fallback_key] = value
        return True

def get_from_redis(user_id: str, key: str, default: Any = None) -> Any:
    """
    Retrieve data from Redis.
    
    Args:
        user_id: User identifier
        key: Data key (e.g., 'last_entity', 'pending_order')
        default: Default value if key not found
    
    Returns:
        Stored value or default
    """
    if redis_client:
        try:
            redis_key = f"session:{user_id}:{key}"
            data = redis_client.get(redis_key)
            if data and isinstance(data, str):
                return json.loads(data)
            return default
        except Exception as e:
            print(f"⚠️  Redis get failed: {e}")
            return default
    else:
        # Fallback to in-memory storage
        fallback_key = f"{user_id}:{key}"
        return pending_orders.get(fallback_key, default)

def delete_from_redis(user_id: str, key: Optional[str] = None):
    """
    Delete data from Redis.
    
    Args:
        user_id: User identifier
        key: Specific key to delete, or None to delete all user data
    """
    if redis_client:
        try:
            if key:
                redis_key = f"session:{user_id}:{key}"
                redis_client.delete(redis_key)
            else:
                # Delete all keys for this user
                pattern = f"session:{user_id}:*"
                keys_list = redis_client.keys(pattern)
                if keys_list and isinstance(keys_list, list):
                    redis_client.delete(*keys_list)
            return True
        except Exception as e:
            print(f"⚠️  Redis delete failed: {e}")
            return False
    else:
        # Fallback to in-memory storage
        if key:
            fallback_key = f"{user_id}:{key}"
            pending_orders.pop(fallback_key, None)
        else:
            # Delete all keys for this user
            keys_to_delete = [k for k in pending_orders.keys() if k.startswith(f"{user_id}:")]
            for k in keys_to_delete:
                del pending_orders[k]
        return True

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
        description="Get detailed information about a specific restaurant by its exact name. Use when user asks about a particular restaurant. V4.0: This function saves the restaurant name to user's session context.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "name": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="The exact name of the restaurant to look up"
                ),
                "user_id": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="User identifier for context storage (REQUIRED for context saving)"
                )
            },
            required=["name", "user_id"]
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
        name="prepare_order_for_confirmation",
        description="V4.0: Prepare an order for user confirmation. ALWAYS call this FIRST before place_order. Calculates total price and saves order to Redis. Returns confirmation question with total. Use when user wants to order food.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "user_id": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                    description="User identifier"
                ),
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
                )
            },
            required=["user_id", "restaurant_name", "items"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="place_order",
        description="V4.0: Execute a CONFIRMED order. DO NOT call this directly - user must confirm first via prepare_order_for_confirmation. Only called after user explicitly confirms (says 'yes', 'confirm', 'ok', 'yep').",
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
    ),
    genai.protos.FunctionDeclaration(
        name="get_my_reviews",
        description="V4.0: Get all reviews written by the current authenticated user. Use when user wants to see their reviews, review history, or what they've reviewed.",
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
            result = "📋 SHOWING ALL Available RESTAURANTS:\n\n"
            
            for idx, restaurant in enumerate(restaurants, 1):
                result += "═══════════════════════════════════════\n"
                result += f"🔸#{idx} RESTAURANT\n"
                result += f"🏪 Name: {restaurant['name']}\n"
                result += f"📍 Area: {restaurant['area']}\n"
                result += f"🍴 Cuisine: {restaurant.get('cuisine', 'N/A')}\n"
            
            result += "═══════════════════════════════════════\n"
            result += "\n💡 Want to see the menu? Just ask about any restaurant!"

            return result
        else:
            return f"❌ Error fetching restaurants: {response.status_code}"
    except Exception as e:
        return f"❌ Error connecting to restaurant service: {str(e)}"


def get_restaurant_by_name(name: str, user_id: str = "guest") -> str:
    """
    Get specific restaurant by name.
    
    V4.0 TASK 1 FIX: Saves context to Redis for vague follow-up queries.
    This enables the agent to understand vague questions like "show me the menu"
    when the user previously asked about a specific restaurant.
    """
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/{name}")
        if response.status_code == 200:
            restaurant = response.json()
            
            # V4.0 TASK 1 FIX: Save restaurant as last mentioned entity to Redis
            # TTL = 600 seconds (10 minutes) - context expires after 10 min of inactivity
            save_to_redis(user_id, 'last_entity', name, ttl=600)
            
            print(f"🔥 CONTEXT SAVED: '{name}' → session:{user_id}:last_entity")
            
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


def prepare_order_for_confirmation(user_id: str, restaurant_name: str, items: List[Dict[str, Any]]) -> str:
    """
    V4.0: Prepare order for user confirmation.
    
    This function calculates the total price and saves the order to Redis
    with a TTL of 600 seconds (10 minutes). It returns a confirmation question
    that the AI will ask the user.
    
    Args:
        user_id: User identifier
        restaurant_name: Name of the restaurant
        items: List of items with item_name, quantity, and price
    
    Returns:
        Formatted confirmation message with total price
    """
    try:
        # Calculate total price
        total_price = sum(item['price'] * item['quantity'] for item in items)
        
        # Save to Redis with TTL=600 (10 minutes)
        order_data = {
            'restaurant_name': restaurant_name,
            'items': items,
            'total_price': total_price
        }
        
        save_to_redis(user_id, 'pending_order', order_data, ttl=600)
        
        print(f"🔥 PENDING ORDER SAVED: {restaurant_name} (₹{total_price}) → session:{user_id}:pending_order")
        
        # Build confirmation message
        result = "🛒 **Order Summary - Please Confirm** 🛒\n\n"
        result += f"🏪 Restaurant: **{restaurant_name}**\n\n"
        result += "📦 **Your Items:**\n"
        
        for item in items:
            item_total = item['price'] * item['quantity']
            result += f"  • {item['item_name']} × {item['quantity']} = ₹{item_total}\n"
        
        result += f"\n💰 **Total: ₹{total_price:.2f}**\n\n"
        result += "✅ **Would you like to confirm this order?**\n"
        result += "   Say 'yes', 'confirm', 'ok', or 'yep' to proceed!\n"
        result += "   Say 'no' or 'cancel' to cancel this order."
        
        return result
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ PREPARE ORDER EXCEPTION:")
        print(error_trace)
        return f"❌ Error preparing order: {str(e)}\n\nPlease try again or contact support."


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
            
            # V4.0: Store order info for proactive review prompts
            user_id = token[:16]  # Use token prefix as user identifier
            recent_orders[user_id] = {
                'restaurant_name': order.get('restaurant_name', restaurant_name),
                'order_id': order.get('id', 'N/A'),
                'turns_since_order': 0
            }
            
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


def get_my_reviews(token: str) -> str:
    """
    V4.0: Get all reviews written by the current user.
    Returns a formatted list of the user's review history.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{FASTAPI_BASE_URL}/users/me/reviews", headers=headers)
        
        if response.status_code == 200:
            reviews = response.json()
            
            if not reviews:
                return "📝 You haven't written any reviews yet.\n\n💡 After you order from a restaurant, I'll ask if you'd like to leave a review! ⭐"
            
            result = f"📝 **Your Review History** ({len(reviews)} review(s))\n\n"
            
            for idx, review in enumerate(reviews, 1):
                stars = "⭐" * review['rating']
                verified = " ✓ Verified Purchase" if review.get('is_verified_purchase') else ""
                result += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                result += f"**{idx}. {review['restaurant_name']}**{verified}\n"
                result += f"{stars} ({review['rating']}/5)\n"
                result += f"💬 \"{review['comment']}\"\n"
                result += f"📅 {review['review_date'][:10]}\n"
            
            result += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            return result
        elif response.status_code == 401:
            return "🔒 Please log in to see your reviews."
        else:
            return f"❌ Error fetching reviews: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Map function names to actual functions
available_functions = {
    "get_all_restaurants": get_all_restaurants,
    "get_restaurant_by_name": get_restaurant_by_name,
    "search_restaurants_by_cuisine": search_restaurants_by_cuisine,
    "search_restaurants_by_item": search_restaurants_by_item,
    "prepare_order_for_confirmation": prepare_order_for_confirmation,  # V4.0: New function
    "place_order": place_order,
    "get_user_orders": get_user_orders,
    "add_review": add_review,
    "get_reviews": get_reviews,
    "get_review_stats": get_review_stats,
    "register_user": register_user,
    "login_user": login_user,
    "get_my_reviews": get_my_reviews
}

# ==================== CHAT ENDPOINT ====================

@app.route('/chat', methods=['POST'])
def chat():
    """
    Process chat message and return AI response.
    
    PHASE 1.2 & 1.3: SEAMLESS SINGLE SIGN-ON IMPLEMENTATION
    PHASE 3 (V4.0): PERSONALIZED AI GREETINGS & RECOMMENDATIONS
    
    This endpoint now extracts the JWT token from the Authorization header,
    eliminating the need for users to log in twice (once on website, once in chat).
    
    V4.0 Enhancement: When authenticated users start a new session, the agent
    greets them by name and offers personalized suggestions based on their order history.
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
        
        # ==================== V4.0: PERSONALIZED GREETING ====================
        # When authenticated user starts a NEW session, provide personalized greeting
        is_new_session = len(chat_sessions[user_id]) == 0
        personalized_greeting = None
        
        if is_new_session and token:
            app.logger.info(f"🎉 V4.0: New authenticated session detected - generating personalized greeting")
            
            try:
                # Get user info from /users/me
                headers = {"Authorization": f"Bearer {token}"}
                user_response = requests.get(f"{FASTAPI_BASE_URL}/users/me", headers=headers, timeout=5)
                
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    username = user_info.get('username', 'Friend')
                    
                    # Get recent orders
                    orders_response = requests.get(f"{FASTAPI_BASE_URL}/orders/", headers=headers, timeout=5)
                    
                    if orders_response.status_code == 200:
                        orders = orders_response.json()
                        
                        if orders and len(orders) > 0:
                            # User has order history - personalized with last order
                            last_order = orders[-1]  # Most recent order
                            last_restaurant = last_order.get('restaurant_name', 'your favorite restaurant')
                            
                            personalized_greeting = f"""Welcome back, {username}! 👋✨

I see your last order was from **{last_restaurant}**. Are you in the mood for that again, or would you like to explore something new today? 🍽️

💡 I can help you:
• 🔍 Search for specific dishes
• 🏪 Browse restaurants by cuisine
• 📝 View your order history
• ⭐ Leave reviews

What sounds good today?"""
                        else:
                            # First-time orderer - welcome message
                            personalized_greeting = f"""Welcome to FoodieExpress, {username}! 👋🎉

I'm so excited to help you discover delicious food! As a new customer, I'd love to help you explore our restaurants. 🍽️

💡 Let's get started! You can:
• 🔍 Tell me what you're craving (e.g., "I want pizza")
• 🏪 Browse restaurants by cuisine
• ⭐ Check out reviews from other customers

What are you in the mood for today?"""
                    else:
                        # Could not fetch orders - generic welcome
                        personalized_greeting = f"""Welcome back, {username}! 👋

Ready to order some delicious food? Let me know what you're craving! 🍽️"""
                    
                    app.logger.info(f"✅ V4.0: Personalized greeting generated for {username}")
                else:
                    app.logger.warning(f"⚠️ V4.0: Could not fetch user info (status {user_response.status_code})")
            
            except Exception as e:
                app.logger.error(f"❌ V4.0: Error generating personalized greeting: {e}")
                # Fall back to normal chat flow if personalization fails
        
        # If we have a personalized greeting, return it immediately
        if personalized_greeting:
            chat_sessions[user_id].append({
                "role": "user",
                "parts": [user_message]
            })
            chat_sessions[user_id].append({
                "role": "model",
                "parts": [personalized_greeting]
            })
            
            return jsonify({
                "response": personalized_greeting,
                "personalized": True
            })
        
        # ==================== V4.0: ORDER CONFIRMATION CHECK ====================
        # Check if user has a pending order and is confirming
        pending_order = get_from_redis(user_id, 'pending_order')
        
        if pending_order:
            app.logger.info(f"🔥 V4.0: Pending order found for user {user_id}")
            
            # Check if user is confirming (yes, ok, confirm, yep, etc.)
            confirmation_keywords = ['yes', 'ok', 'confirm', 'yep', 'sure', 'proceed', 'go ahead', 'yeah']
            cancellation_keywords = ['no', 'cancel', 'nope', 'nevermind', 'stop']
            
            user_message_lower = user_message.lower().strip()
            
            # User confirms the order
            if any(keyword in user_message_lower for keyword in confirmation_keywords):
                app.logger.info(f"✅ V4.0: User confirmed order - executing place_order")
                
                # Check if user is authenticated
                if not token:
                    delete_from_redis(user_id, 'pending_order')
                    confirmation_response = "🔒 **Authentication Required!**\n\nTo place this order, please log in using the button in the top right corner. 🙂"
                    
                    chat_sessions[user_id].append({"role": "user", "parts": [user_message]})
                    chat_sessions[user_id].append({"role": "model", "parts": [confirmation_response]})
                    
                    return jsonify({
                        "response": confirmation_response,
                        "requires_auth": True
                    })
                
                # Execute the order
                try:
                    order_response = place_order(
                        restaurant_name=pending_order['restaurant_name'],
                        items=pending_order['items'],
                        token=token
                    )
                    
                    # Clear pending order
                    delete_from_redis(user_id, 'pending_order')
                    app.logger.info(f"✅ V4.0: Order executed and pending order cleared")
                    
                    # Add to chat history
                    chat_sessions[user_id].append({"role": "user", "parts": [user_message]})
                    chat_sessions[user_id].append({"role": "model", "parts": [order_response]})
                    
                    return jsonify({
                        "response": order_response,
                        "order_confirmed": True
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error executing order: {str(e)}\n\nPlease try again or contact support."
                    app.logger.error(f"❌ V4.0: Order execution failed: {e}")
                    
                    # Clear pending order on error
                    delete_from_redis(user_id, 'pending_order')
                    
                    chat_sessions[user_id].append({"role": "user", "parts": [user_message]})
                    chat_sessions[user_id].append({"role": "model", "parts": [error_msg]})
                    
                    return jsonify({"response": error_msg})
            
            # User cancels the order
            elif any(keyword in user_message_lower for keyword in cancellation_keywords):
                app.logger.info(f"❌ V4.0: User cancelled order")
                
                # Clear pending order
                delete_from_redis(user_id, 'pending_order')
                
                cancellation_response = "✅ **Order Cancelled**\n\nNo problem! Your order has been cancelled. 😊\n\n💡 Let me know if you'd like to order something else!"
                
                chat_sessions[user_id].append({"role": "user", "parts": [user_message]})
                chat_sessions[user_id].append({"role": "model", "parts": [cancellation_response]})
                
                return jsonify({
                    "response": cancellation_response,
                    "order_cancelled": True
                })
            
            # User said something else - remind them about pending order
            else:
                app.logger.info(f"ℹ️  V4.0: User has pending order but didn't confirm/cancel - reminding them")
                
                reminder = f"⏰ **You have a pending order!**\n\n"
                reminder += f"🏪 Restaurant: **{pending_order['restaurant_name']}**\n"
                reminder += f"💰 Total: ₹{pending_order['total_price']:.2f}\n\n"
                reminder += "Please confirm your order by saying **'yes'** or **'confirm'**, or cancel it by saying **'no'** or **'cancel'**."
                
                chat_sessions[user_id].append({"role": "user", "parts": [user_message]})
                chat_sessions[user_id].append({"role": "model", "parts": [reminder]})
                
                return jsonify({
                    "response": reminder,
                    "pending_order": True
                })
        
        # ==================== V4.0 TASK 1 FIX: CONTEXT-AWARE ROUTING ====================
        # Check if user is asking a vague question that needs context
        user_message_lower = user_message.lower()
        vague_menu_queries = [
            "show me the menu", "the menu", "what's on the menu", "menu please",
            "what do they have", "what do they serve", "what items", "show items",
            "what can i order", "what's available", "tell me more", "more info",
            "show the menu", "display menu", "see menu", "view menu"
        ]
        
        is_vague_query = any(vague in user_message_lower for vague in vague_menu_queries)
        
        # TASK 1 FIX: If user asks vague "menu" question, check if we have context
        if "menu" in user_message_lower or is_vague_query:
            last_entity = get_from_redis(user_id, 'last_entity')
            
            if last_entity:
                # Context exists - use it immediately
                restaurant_name = last_entity
                app.logger.info(f"🔥 V4.0 TASK 1: CONTEXT HIT - User asked vague question, using last_entity: {restaurant_name}")
                
                # Call get_restaurant_by_name with context
                restaurant_details = get_restaurant_by_name(restaurant_name, user_id)
                
                # Add to chat history
                chat_sessions[user_id].append({"role": "user", "parts": [user_message]})
                chat_sessions[user_id].append({"role": "model", "parts": [restaurant_details]})
                
                return jsonify({
                    "response": restaurant_details,
                    "context_used": True
                })
        
        # ==================== CONTINUE WITH NORMAL CHAT FLOW ====================
        
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

⚠️ CRITICAL: V4.0 ORDER CONFIRMATION WORKFLOW
**TWO-STEP ORDER PROCESS - ALWAYS CONFIRM BEFORE PLACING!**

When user wants to order food:
1. **STEP 1**: Call prepare_order_for_confirmation(user_id, restaurant_name, items)
   - This calculates total and asks for confirmation
   - DO NOT call place_order directly
   - The system will save the pending order and ask user to confirm

2. **STEP 2**: User confirms (handled automatically by system)
   - User says "yes", "ok", "confirm", "yep" → Order is placed automatically
   - User says "no", "cancel" → Order is cancelled
   - You don't need to handle confirmation - the system does it

Example Flow:
User: "order 2 Masala Thepla from Thepla House"
You: [Call prepare_order_for_confirmation with user_id, restaurant_name, items]
System: Shows confirmation message with total price
User: "yes"
System: Automatically executes place_order and shows success message

IMPORTANT:
- NEVER call place_order directly when user first requests an order
- ALWAYS use prepare_order_for_confirmation first
- The confirmation step is automatic - you just prepare the order
- This prevents accidental orders and builds user trust

⚠️ CRITICAL: V4.0 TASK 1 - CONTEXT AWARENESS (CONTEXT RULE)
**REMEMBER WHAT USER JUST VIEWED - NEVER ASK TWICE!**

**Context Rule:** When the user's request is vague (e.g., 'show the menu', 'what are the reviews?', 
'order one of those', 'tell me more', 'what's available'), you MUST FIRST check if a 'last_entity' 
(the last mentioned restaurant) has been provided to you in the contextual_prompt.

If a last_entity is present:
- IMMEDIATELY use it - DO NOT ask for the restaurant name again
- Call the appropriate function with that restaurant name
- Example: If user previously asked about "Swati Snacks" and now says "show the menu",
  IMMEDIATELY call get_restaurant_by_name("Swati Snacks", user_id)

When user views restaurant details (e.g., "tell me about Thepla House"), the system automatically 
saves this as context. Vague follow-up questions like:
- "show me the menu"
- "what do they have"
- "tell me more"
- "what's available"
- "get the reviews"
- "order from there"

ALL refer to the last mentioned restaurant. The context is automatically provided to you.
You don't need to ask "Which restaurant?" - USE THE CONTEXT IMMEDIATELY!

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
        
        # ==================== CRITICAL FIX: FORCE FUNCTION CALLING FOR LIST REQUESTS ====================
        # Pre-detect list requests and directly call the function, bypassing AI decision
        user_message_lower = user_message.lower()
        list_keywords = ['list', 'show all', 'browse', 'see all', 'get all', 'display all', 'all restaurant']
        
        if any(keyword in user_message_lower for keyword in list_keywords) and 'restaurant' in user_message_lower:
            app.logger.info(f"🎯 DETECTED LIST REQUEST - Directly calling get_all_restaurants() without AI")
            
            # Call the function directly
            function_result = get_all_restaurants()
            
            # Add to chat history
            chat_sessions[user_id].append({
                "role": "user",
                "parts": [user_message]
            })
            chat_sessions[user_id].append({
                "role": "model",
                "parts": [function_result]
            })
            
            return jsonify({
                "response": function_result,
                "function_called": "get_all_restaurants"
            })
        
        # Normal AI processing for other queries
        
        # ==================== V4.0 TASK 1 FIX: Fetch context and provide to AI ====================
        # Before calling the LLM, check for last_entity in Redis and provide it as context
        last_entity = get_from_redis(user_id, 'last_entity')
        
        # Build contextual prompt
        contextual_message = user_message
        if last_entity:
            # Prepend context information to the user's message
            contextual_message = f"[CONTEXT: The last restaurant the user was talking about was '{last_entity}'] {user_message}"
            app.logger.info(f"🔥 V4.0 TASK 1: Providing context to AI - last_entity: {last_entity}")
        
        # Add user message to history (with context if available)
        chat_sessions[user_id].append({
            "role": "user",
            "parts": [contextual_message]
        })
        
        # Start chat with history
        chat = model.start_chat(history=chat_sessions[user_id][:-1])
        
        # ==================== PHASE 1: Send message to AI ====================
        # The AI will decide if a function needs to be called
        response = chat.send_message(contextual_message)
        
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
            protected_functions = ['place_order', 'get_user_orders', 'add_review', 'get_my_reviews']
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
            
            # V4.0 TASK 1 FIX: Add user_id for context-aware functions
            context_aware_functions = ['get_restaurant_by_name', 'prepare_order_for_confirmation']
            if function_name in context_aware_functions and 'user_id' not in function_args:
                function_args['user_id'] = user_id
                app.logger.info(f"🔥 V4.0 TASK 1: Injecting user_id={user_id} for context-aware function {function_name}")
            
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
            
            # ==================== V4.0: PROACTIVE REVIEW PROMPTS ====================
            # After 2-3 turns since order, proactively ask for review
            if token and user_id in recent_orders:
                recent_order = recent_orders[user_id]
                recent_order['turns_since_order'] += 1
                
                # Prompt after 2 conversational turns
                if recent_order['turns_since_order'] == 2:
                    restaurant_name = recent_order['restaurant_name']
                    app.logger.info(f"🌟 V4.0: Proactive review prompt for {restaurant_name}")
                    
                    # Check if user already reviewed this restaurant
                    try:
                        headers = {"Authorization": f"Bearer {token}"}
                        check_response = requests.get(
                            f"{FASTAPI_BASE_URL}/reviews/user-restaurant-review/{restaurant_name}",
                            headers=headers,
                            timeout=5
                        )
                        
                        if check_response.status_code == 404:
                            # No review yet - add prompt
                            review_prompt = f"\n\n---\n\n💫 **By the way**, how was your experience with **{restaurant_name}**? I'd love to hear your feedback! ⭐\n\nYou can say something like: *'Rate {restaurant_name} 5 stars'* or *'Review {restaurant_name}'*"
                            text_response += review_prompt
                            app.logger.info(f"✅ V4.0: Added proactive review prompt")
                        else:
                            # Already reviewed - clear from tracking
                            del recent_orders[user_id]
                            app.logger.info(f"✅ V4.0: User already reviewed, skipping prompt")
                    except Exception as e:
                        app.logger.warning(f"⚠️ V4.0: Could not check review status: {e}")
                
                # Clear tracking after 5 turns to avoid repeated prompts
                elif recent_order['turns_since_order'] >= 5:
                    del recent_orders[user_id]
                    app.logger.info(f"🗑️ V4.0: Cleared order tracking after 5 turns")
            
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
        "version": "4.0.0",
        "status": "running",
        "features": [
            "Multi-Item Orders",
            "Restaurant Reviews & Ratings",
            "Cuisine-Based Search",
            "Order History Tracking",
            "Personalized Greetings",
            "Proactive Review Requests",
            "Admin Dashboard Support"
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
        "service": "AI Food Delivery Agent v4.0",
        "fastapi_backend": FASTAPI_BASE_URL,
        "features": ["Reviews", "Multi-Item Orders", "Cuisine Search", "Personalization", "Admin Dashboard"]
    })


@app.route('/clear-session', methods=['POST'])
def clear_session():
    """
    Clear chat session for a user.
    
    V4.0: Also clears Redis context data (last_entity, pending_order).
    """
    data = request.json
    user_id = data.get('user_id', 'guest') if data else 'guest'
    
    # Clear chat history
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    
    # Clear in-memory pending orders (fallback)
    if user_id in pending_orders:
        del pending_orders[user_id]
    
    # V4.0: Clear Redis context data
    delete_from_redis(user_id)  # Clears all session:{user_id}:* keys
    
    print(f"🧹 Session cleared for user: {user_id}")
    
    return jsonify({"message": "Session cleared successfully! 🧹"})


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 FoodieExpress AI Agent v4.0")
    print("=" * 60)
    print(f"✅ Google Gemini AI: Configured")
    print(f"✅ FastAPI Backend: {FASTAPI_BASE_URL}")
    print(f"✅ Agent Server: http://localhost:5000")
    print("=" * 60)
    print("🌟 V4.0 Features:")
    print("  🎯 Personalized AI Greetings")
    print("  ⭐ Restaurant Reviews & Ratings")
    print("  🛒 Multi-Item Orders")
    print("  🔍 Cuisine-Based Search")
    print("  📊 Review Statistics")
    print("  📈 Admin Dashboard Support")
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
        print(f"🔗 Binding to 0.0.0.0:5000...")
        serve(app, host='0.0.0.0', port=5000, threads=4)
        print("⚠️ Server stopped")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
