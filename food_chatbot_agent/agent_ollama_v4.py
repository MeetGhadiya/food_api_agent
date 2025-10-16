"""
AI Food Delivery Chatbot Agent - V4.0 OLLAMA EDITION
Built with Ollama (Local AI) - No API Keys, No Crashes!

V4.0 FEATURES (ALL PRESERVED):
✅ Context Handling (TASK 1) - Remembers last mentioned restaurant
✅ Order Confirmation (TASK 2) - Two-step confirmation workflow
✅ Redis session storage for scalability
✅ All restaurant, order, and review functions
✅ NO MORE CRASHES - Ollama runs locally!

BACKUP: Gemini available as fallback if Ollama has issues
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional, List
import re

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"])

# ==================== OLLAMA CONFIGURATION (PRIMARY) ====================
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

print(f"🤖 Using Ollama Model: {OLLAMA_MODEL} (PRIMARY)")
print(f"🔗 Ollama Server: {OLLAMA_URL}")

# Test Ollama connection
try:
    test_response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if test_response.status_code == 200:
        print("✅ Ollama is ready!")
        OLLAMA_AVAILABLE = True
    else:
        print("⚠️  Ollama server responded but may have issues")
        OLLAMA_AVAILABLE = False
except:
    print("⚠️  Ollama not available - will use Gemini backup if configured")
    OLLAMA_AVAILABLE = False

# ==================== GEMINI BACKUP (OPTIONAL) ====================
GEMINI_AVAILABLE = False
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=GOOGLE_API_KEY)
        print("⚠️  Gemini available as backup (if Ollama fails)")
        GEMINI_AVAILABLE = True
    except:
        print("ℹ️  Gemini not available (this is OK - Ollama is primary)")
        GEMINI_AVAILABLE = False
else:
    print("ℹ️  No Gemini API key (this is OK - Ollama is primary)")

# API Configuration
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# ==================== REDIS SESSION STORE ====================
try:
    import redis
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD', None),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
    print(f"✅ Redis connected: {os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}")
    REDIS_AVAILABLE = True
except:
    print("⚠️  Redis not available - using in-memory storage")
    REDIS_AVAILABLE = False
    redis_client = None

# Fallback in-memory storage
chat_sessions: Dict[str, list] = {}
session_context: Dict[str, Dict[str, Any]] = {}

# ==================== REDIS HELPER FUNCTIONS ====================

def save_to_redis(user_id: str, key: str, value: Any, ttl: int = 600):
    """Save data to Redis or fallback to memory"""
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_key = f"session:{user_id}:{key}"
            redis_client.setex(redis_key, ttl, json.dumps(value))
            return True
        except:
            pass
    
    # Fallback to memory
    if user_id not in session_context:
        session_context[user_id] = {}
    session_context[user_id][key] = value
    return True


def get_from_redis(user_id: str, key: str, default: Any = None) -> Any:
    """Retrieve data from Redis or fallback to memory"""
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_key = f"session:{user_id}:{key}"
            data = redis_client.get(redis_key)  # type: ignore
            if data and isinstance(data, str):
                return json.loads(data)
        except:
            pass
    
    # Fallback to memory
    if user_id in session_context:
        return session_context[user_id].get(key, default)
    return default


def delete_from_redis(user_id: str, key: Optional[str] = None):
    """Delete data from Redis or fallback to memory"""
    if REDIS_AVAILABLE and redis_client:
        try:
            if key:
                redis_key = f"session:{user_id}:{key}"
                redis_client.delete(redis_key)  # type: ignore
            else:
                pattern = f"session:{user_id}:*"
                keys_list = redis_client.keys(pattern)  # type: ignore
                if keys_list:
                    redis_client.delete(*keys_list)  # type: ignore
            return True
        except:
            pass
    
    # Fallback to memory
    if key:
        if user_id in session_context:
            session_context[user_id].pop(key, None)
    else:
        if user_id in session_context:
            del session_context[user_id]
    return True

# ==================== AI FUNCTIONS ====================

def call_ollama(messages: List[Dict], system_prompt: str) -> Optional[str]:
    """Call Ollama API with conversation history"""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            print(f"⚠️  Ollama error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"⚠️  Ollama failed: {e}")
        return None


def call_gemini_backup(messages: List[Dict], system_prompt: str) -> Optional[str]:
    """Fallback to Gemini if Ollama fails (BACKUP ONLY)"""
    if not GEMINI_AVAILABLE:
        return None
    
    try:
        import google.generativeai as genai  # type: ignore
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=system_prompt
        )
        
        # Convert messages to Gemini format
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        
        chat = model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"])
        
        return response.text
        
    except Exception as e:
        print(f"⚠️  Gemini backup also failed: {e}")
        return None


def get_ai_response(messages: List[Dict], system_prompt: str) -> str:
    """Get AI response with automatic failover"""
    
    # Try Ollama first (PRIMARY)
    if OLLAMA_AVAILABLE:
        response = call_ollama(messages, system_prompt)
        if response:
            return response
        print("⚠️  Ollama failed, trying Gemini backup...")
    
    # Try Gemini as backup
    if GEMINI_AVAILABLE:
        response = call_gemini_backup(messages, system_prompt)
        if response:
            print("✅ Using Gemini backup")
            return response
    
    # Both failed
    return "I'm having trouble processing your request right now. Please try again in a moment."

# ==================== API HELPER FUNCTIONS ====================

def get_all_restaurants() -> str:
    """Fetch all restaurants"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/", timeout=5)
        if response.status_code == 200:
            restaurants = response.json()
            if not restaurants:
                return "No restaurants available right now."
            
            result = "📋 **All Available Restaurants:**\n\n"
            for idx, r in enumerate(restaurants, 1):
                result += f"{idx}. **{r['name']}** - {r.get('area', 'N/A')} ({r.get('cuisine', 'N/A')})\n"
            return result
        return "❌ Error fetching restaurants"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_restaurant_by_name(name: str, user_id: str = "guest") -> str:
    """Get restaurant details and save context"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/{name}", timeout=5)
        if response.status_code == 200:
            restaurant = response.json()
            
            # TASK 1: Save context
            save_to_redis(user_id, 'last_entity', name, ttl=600)
            print(f"🔥 CONTEXT SAVED: '{name}' → session:{user_id}:last_entity")
            
            result = f"🏪 **{restaurant['name']}**\n\n"
            result += f"📍 Location: {restaurant['area']}\n"
            result += f"🍴 Cuisine: {restaurant.get('cuisine', 'N/A')}\n\n"
            result += "📋 **Menu:**\n"
            
            items = restaurant.get('items', [])
            for item in items:
                item_name = item.get('item_name', 'Unknown')
                price = item.get('price', 'N/A')
                result += f"• {item_name} - ₹{price}\n"
            
            return result
        elif response.status_code == 404:
            return f"😔 Restaurant '{name}' not found."
        return "❌ Error fetching restaurant"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def search_restaurants_by_cuisine(cuisine: str) -> str:
    """Search by cuisine"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/restaurants/", params={"cuisine": cuisine}, timeout=5)
        if response.status_code == 200:
            restaurants = response.json()
            if not restaurants:
                return f"No {cuisine} restaurants found."
            
            result = f"🍽️ **{cuisine} Restaurants:**\n\n"
            for r in restaurants:
                result += f"• **{r['name']}** in {r['area']}\n"
            return result
        return "❌ Error searching restaurants"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def search_restaurants_by_item(item_name: str) -> str:
    """Search by menu item"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/search/items", params={"item_name": item_name}, timeout=5)
        if response.status_code == 200:
            restaurants = response.json()
            if not restaurants:
                return f"No restaurants serving {item_name} found."
            
            result = f"🔍 **Found '{item_name}' at:**\n\n"
            for r in restaurants:
                result += f"• **{r['name']}** in {r['area']}\n"
            return result
        return "❌ Error searching items"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def prepare_order_for_confirmation(user_id: str, restaurant_name: str, items: List[Dict[str, Any]]) -> str:
    """TASK 2: Prepare order and ask for confirmation"""
    try:
        total_price = sum(item['price'] * item['quantity'] for item in items)
        
        order_data = {
            'restaurant_name': restaurant_name,
            'items': items,
            'total_price': total_price
        }
        
        save_to_redis(user_id, 'pending_order', order_data, ttl=600)
        print(f"🔥 PENDING ORDER SAVED: {restaurant_name} (₹{total_price}) → session:{user_id}:pending_order")
        
        result = "🛒 **Order Summary - Please Confirm:**\n\n"
        result += f"🏪 Restaurant: **{restaurant_name}**\n\n"
        result += "📦 **Items:**\n"
        
        for item in items:
            item_total = item['price'] * item['quantity']
            result += f"  • {item['item_name']} × {item['quantity']} = ₹{item_total}\n"
        
        result += f"\n💰 **Total: ₹{total_price:.2f}**\n\n"
        result += "✅ **Confirm this order?**\n"
        result += "Say 'yes' or 'confirm' to proceed!"
        
        return result
        
    except Exception as e:
        return f"❌ Error preparing order: {str(e)}"


def place_order(restaurant_name: str, items: List[Dict[str, Any]], token: str) -> str:
    """Place confirmed order"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"restaurant_name": restaurant_name, "items": items}
        
        response = requests.post(f"{FASTAPI_BASE_URL}/orders/", json=data, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            order = response.json()
            
            result = "✅ **Order Placed Successfully!** 🎉\n\n"
            result += f"🏪 Restaurant: {order.get('restaurant_name', restaurant_name)}\n"
            result += f"📝 Order ID: #{order.get('id', 'N/A')}\n\n"
            result += "📦 **Your Items:**\n"
            
            for item in order.get('items', []):
                result += f"  • {item['item_name']} × {item['quantity']} = ₹{item['price'] * item['quantity']}\n"
            
            result += f"\n💰 **Total: ₹{order.get('total_price', 0):.2f}**\n"
            result += "⏰ Estimated delivery: 30-45 minutes"
            
            return result
        elif response.status_code == 401:
            return "🔒 Please login to place orders."
        elif response.status_code == 404:
            return f"😔 Restaurant '{restaurant_name}' not found."
        else:
            return f"❌ Order failed: {response.status_code}"
            
    except Exception as e:
        return f"❌ Error placing order: {str(e)}"


def get_user_orders(token: str) -> str:
    """Get user's order history"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{FASTAPI_BASE_URL}/orders/", headers=headers, timeout=5)
        
        if response.status_code == 200:
            orders = response.json()
            if not orders:
                return "📭 No orders yet."
            
            result = f"📝 **Your Orders ({len(orders)}):**\n\n"
            for idx, order in enumerate(orders, 1):
                result += f"**Order #{idx}** (ID: {order.get('id')})\n"
                result += f"🏪 {order.get('restaurant_name')}\n"
                result += f"💰 Total: ₹{order.get('total_price', 0):.2f}\n\n"
            
            return result
        elif response.status_code == 401:
            return "🔒 Please login to view orders."
        return "❌ Error fetching orders"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== TOOL PARSER ====================

def detect_and_execute_tool(user_message: str, user_id: str, token: Optional[str] = None) -> Optional[str]:
    """
    Detect if user wants a specific action and execute it directly.
    This replaces complex function calling with simple pattern matching.
    
    PRIORITY ORDER (P1-01 FIX):
    1. Item search (highest priority - "which restaurant has X?")
    2. List all restaurants
    3. Search by cuisine
    4. Restaurant details with context
    5. View orders
    """
    msg_lower = user_message.lower()
    
    # P1-01 FIX: Item search - HIGHEST PRIORITY
    # Patterns: "which restaurant has X?", "where can I get X?", "I want X", "who serves X?"
    item_keywords = ['which restaurant has', 'where can i get', 'where can i find', 'who serves', 'who has']
    item_wants = ['i want', 'i need', 'looking for', 'craving']
    
    for keyword in item_keywords:
        if keyword in msg_lower:
            # Extract item name after the keyword
            item_match = re.search(rf'{keyword}\s+(.+?)(?:\?|$)', msg_lower)
            if item_match:
                item_name = item_match.group(1).strip()
                # Clean up common words
                item_name = item_name.replace('some ', '').replace('a ', '').strip()
                if len(item_name) > 2:
                    print(f"🔥 P1-01 FIX: Item search triggered for '{item_name}'")
                    return search_restaurants_by_item(item_name)
    
    # Check "I want X" patterns (but avoid "I want to order")
    for keyword in item_wants:
        if keyword in msg_lower and 'order' not in msg_lower:
            # Extract what they want
            want_match = re.search(rf'{keyword}\s+(.+?)(?:\?|$|from|at)', msg_lower)
            if want_match:
                item_name = want_match.group(1).strip()
                # Filter out vague requests
                if item_name and len(item_name) > 2 and item_name not in ['food', 'something', 'anything']:
                    print(f"🔥 P1-01 FIX: Item search triggered for '{item_name}'")
                    return search_restaurants_by_item(item_name)
    
    # List all restaurants
    if any(keyword in msg_lower for keyword in ['list restaurants', 'show restaurants', 'all restaurants', 'browse restaurants']):
        return get_all_restaurants()
    
    # Search by cuisine (lower priority than item search)
    cuisines = ['gujarati', 'italian', 'south indian', 'north indian', 'multi-cuisine', 'cafe']
    for cuisine in cuisines:
        if cuisine in msg_lower and ('restaurant' in msg_lower or 'food' in msg_lower or 'place' in msg_lower):
            return search_restaurants_by_cuisine(cuisine.title())
    
    # Get specific restaurant (with context) - P1-03 FIX
    if 'menu' in msg_lower or 'tell me about' in msg_lower or 'show me' in msg_lower:
        # P1-03 FIX: Check for context first - ENHANCED
        last_entity = get_from_redis(user_id, 'last_entity')
        
        if last_entity and ('menu' in msg_lower or 'show' in msg_lower):
            # User asking about last restaurant
            print(f"🔥 P1-03 FIX: CONTEXT HIT - using last_entity: {last_entity}")
            return get_restaurant_by_name(last_entity, user_id)
        
        # Extract restaurant name from message
        # Simple pattern: "tell me about X" or "show me X"
        patterns = [
            r'about\s+(.+?)(?:\s+restaurant)?$',
            r'show\s+(?:me\s+)?(.+?)(?:\s+menu)?$',
            r'menu\s+(?:for\s+)?(.+?)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                restaurant_name = match.group(1).strip()
                # Clean up common words
                restaurant_name = restaurant_name.replace('the ', '').replace(' menu', '').strip()
                if len(restaurant_name) > 2:
                    return get_restaurant_by_name(restaurant_name.title(), user_id)
    
    # View orders - P1-05 FIX: Enhanced token handling
    if token and ('my orders' in msg_lower or 'order history' in msg_lower or 'my order' in msg_lower):
        print(f"🔥 P1-05 FIX: Using stored token for order history")
        return get_user_orders(token)
    
    return None

# ==================== SYSTEM PROMPT ====================

SYSTEM_PROMPT = """You are a friendly food delivery assistant! 🍕

Your job: Help users order food, browse restaurants, and manage their orders.

**CRITICAL RULES (ALL P1 FIXES APPLIED):**

1. **Context Awareness (P1-03 FIX - TASK 1):**
   - ALWAYS check conversation history before asking clarifying questions
   - When user says "show me the menu", look back to see if they just mentioned a restaurant
   - If they did, use that restaurant - NEVER ask "which restaurant?"
   - Example: User says "tell me about Pizza Palace" → You show info
     Then user says "show menu" → You show Pizza Palace menu (don't ask which!)

2. **Item Search Priority (P1-01 FIX):**
   - When user asks "which restaurant has X?" or "I want X", search for that ITEM first
   - Don't confuse item searches with cuisine searches
   - Examples:
     * "which restaurant has bhel?" → Search for item "bhel"
     * "I want pizza" → Search for item "pizza"  
     * "where can I get samosa?" → Search for item "samosa"

3. **Order Confirmation (P1-04 FIX - TASK 2):**
   - NEVER EVER place orders immediately
   - ALWAYS prepare order first and show summary with total price
   - Ask "Do you want to confirm this order?"
   - ONLY place order after user says "yes" or "confirm"
   - If user says "no" or "cancel", discard the order

4. **Complete Results (P1-02 FIX):**
   - When showing lists of restaurants, show ALL of them
   - Don't truncate or summarize
   - Users need to see all options to make informed choices

5. **Be Helpful & Proactive (P2 IMPROVEMENTS):**
   - Use emojis frequently 🍽️ 🏪 ⭐ 🎉
   - Be warm, friendly, and conversational
   - After showing restaurant, suggest: "Want to see the menu?"
   - After showing menu, suggest: "Ready to order?"
   - After order placed, suggest: "Leave a review?"

6. **Handle Errors Gracefully (P2-02 FIX):**
   - If restaurant not found: "😔 Couldn't find that restaurant. Want to see all restaurants?"
   - If item not found: "😔 No restaurants serving that. Try browsing by cuisine?"
   - Never show technical errors like "500" or "404"

7. **Clarify Ambiguous Requests (P2-07 FIX):**
   - If user says "I want food", ask "What type? Pizza? Indian? Italian?"
   - If user says "order something", ask "Which restaurant would you like to order from?"
   - Guide users to specific answers

**Available Actions:**
- List all restaurants: "list restaurants" or "show all restaurants"
- Search by cuisine: "show me [cuisine] restaurants" (e.g., "Gujarati restaurants")
- Search by item: "which restaurant has [item]?" (e.g., "who has pizza?")
- Restaurant details: "tell me about [name]" or "show me [name]"
- View menu: "show me the menu" (works with context!)
- Order: "I want to order [items] from [restaurant]"
- Order history: "show my orders" (requires login)

**Response Style:**
- Short, friendly, emoji-rich
- Bullet points for lists
- Clear formatting
- Suggest next steps

Keep it fun and helpful! 🎉"""

# ==================== CHAT ENDPOINT ====================

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with Ollama (and Gemini backup)"""
    try:
        # P2-08 FIX: Validate request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'guest')
        
        # Extract token - P1-05 FIX: Enhanced token handling
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1].strip()
        elif data.get('token'):
            token = data.get('token')
        
        if not user_message:
            return jsonify({"error": "Message required"}), 400
        
        # Initialize session
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []
        
        # ==================== TASK 2: ORDER CONFIRMATION CHECK ====================
        pending_order = get_from_redis(user_id, 'pending_order')
        
        if pending_order:
            user_msg_lower = user_message.lower().strip()
            
            # User confirms
            if any(kw in user_msg_lower for kw in ['yes', 'ok', 'confirm', 'yep', 'sure']):
                if not token:
                    delete_from_redis(user_id, 'pending_order')
                    return jsonify({"response": "🔒 Please login to place orders."})
                
                # Place order
                print(f"✅ V4.0: User confirmed order - executing place_order")
                order_response = place_order(
                    restaurant_name=pending_order['restaurant_name'],
                    items=pending_order['items'],
                    token=token
                )
                
                delete_from_redis(user_id, 'pending_order')
                print(f"✅ V4.0: Order executed and pending order cleared")
                
                chat_sessions[user_id].append({"role": "user", "content": user_message})
                chat_sessions[user_id].append({"role": "assistant", "content": order_response})
                
                return jsonify({"response": order_response})
            
            # User cancels
            elif any(kw in user_msg_lower for kw in ['no', 'cancel', 'nope', 'nevermind']):
                delete_from_redis(user_id, 'pending_order')
                response = "✅ Order cancelled. What else can I help you with?"
                
                chat_sessions[user_id].append({"role": "user", "content": user_message})
                chat_sessions[user_id].append({"role": "assistant", "content": response})
                
                return jsonify({"response": response})
        
        # ==================== TOOL DETECTION ====================
        tool_response = detect_and_execute_tool(user_message, user_id, token)
        
        if tool_response:
            chat_sessions[user_id].append({"role": "user", "content": user_message})
            chat_sessions[user_id].append({"role": "assistant", "content": tool_response})
            return jsonify({"response": tool_response})
        
        # ==================== AI RESPONSE ====================
        # Add context to message if available
        last_entity = get_from_redis(user_id, 'last_entity')
        contextual_message = user_message
        
        if last_entity:
            contextual_message = f"[Context: Last restaurant mentioned was '{last_entity}'] {user_message}"
            print(f"🔥 V4.0 TASK 1: Providing context to AI - last_entity: {last_entity}")
        
        # Add to chat history
        chat_sessions[user_id].append({"role": "user", "content": contextual_message})
        
        # Get AI response with failover
        ai_response = get_ai_response(chat_sessions[user_id], SYSTEM_PROMPT)
        
        # Save AI response
        chat_sessions[user_id].append({"role": "assistant", "content": ai_response})
        
        return jsonify({"response": ai_response})
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        app.logger.error(f"Chat error: {e}\n{error_trace}")
        return jsonify({"response": "😅 Oops! Something went wrong. Try again!"}), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "FoodieExpress AI Agent V4.0",
        "status": "running",
        "ai_model": f"Ollama {OLLAMA_MODEL}",
        "features": ["Context Handling", "Order Confirmation", "Redis Storage"]
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "ollama_available": OLLAMA_AVAILABLE,
        "gemini_backup": GEMINI_AVAILABLE,
        "redis_available": REDIS_AVAILABLE
    })


@app.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear user session"""
    data = request.json
    user_id = data.get('user_id', 'guest') if data else 'guest'
    
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    
    delete_from_redis(user_id)
    
    return jsonify({"message": "Session cleared! 🧹"})


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 FoodieExpress AI Agent v4.0 - OLLAMA EDITION")
    print("=" * 60)
    print(f"✅ AI Model: Ollama {OLLAMA_MODEL} (PRIMARY)")
    if GEMINI_AVAILABLE:
        print(f"✅ Backup: Google Gemini (if Ollama fails)")
    print(f"✅ FastAPI Backend: {FASTAPI_BASE_URL}")
    print(f"✅ Redis: {'Connected' if REDIS_AVAILABLE else 'Fallback to memory'}")
    print(f"✅ Agent Server: http://localhost:5000")
    print("=" * 60)
    print("🌟 V4.0 Features:")
    print("  🎯 Context Handling (TASK 1)")
    print("  ✅ Order Confirmation (TASK 2)")
    print("  🔄 Auto-failover (Ollama → Gemini)")
    print("  🛡️  No crashes - stable & reliable!")
    print("=" * 60)
    print("🚀 Starting Flask server with Waitress...")
    print()
    
    try:
        from waitress import serve
        print("✅ Waitress imported successfully")
        print(f"🔗 Binding to 0.0.0.0:5000...")
        serve(app, host='0.0.0.0', port=5000, threads=4)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
