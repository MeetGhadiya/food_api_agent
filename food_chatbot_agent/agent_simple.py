"""
FoodieExpress AI Chatbot Agent - Ollama Edition
Simple version for immediate testing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# Session storage
chat_sessions = {}  # Stores conversation history
session_context = {}  # Stores context: last_restaurant, pending_order, etc.

print(f"✅ Agent starting with Ollama {OLLAMA_MODEL}")
print(f"✅ Backend: {FASTAPI_BASE_URL}")

# Helper functions for context management
def save_context(user_id, key, value):
    """Save context information for a user session"""
    if user_id not in session_context:
        session_context[user_id] = {}
    session_context[user_id][key] = value
    print(f"🔍 CONTEXT SAVED: {user_id} -> {key} = {value}")

def get_context(user_id, key, default=None):
    """Retrieve context information from user session"""
    if user_id not in session_context:
        return default
    value = session_context[user_id].get(key, default)
    print(f"🔍 CONTEXT RETRIEVED: {user_id} -> {key} = {value}")
    return value

def clear_context(user_id, key=None):
    """Clear specific context key or entire context for user"""
    if user_id in session_context:
        if key:
            session_context[user_id].pop(key, None)
            print(f"🔍 CONTEXT CLEARED: {user_id} -> {key}")
        else:
            del session_context[user_id]
            print(f"🔍 CONTEXT CLEARED: {user_id} -> ALL")

def call_ollama(messages, system_prompt):
    """Call Ollama API"""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return "Error communicating with AI"
    except Exception as e:
        return f"AI Error: {str(e)}"

def get_all_restaurants():
    """Get all restaurants from backend"""
    api_url = f"{FASTAPI_BASE_URL}/restaurants/"
    print(f"DEBUG: Calling API at URL: {api_url}")  # Debug logging
    try:
        response = requests.get(api_url, timeout=5)
        print(f"DEBUG: API Response Status Code: {response.status_code}")  # Debug logging
        response.raise_for_status()  # Raise error for 4xx/5xx responses
        
        restaurants = response.json()
        print(f"DEBUG: Received {len(restaurants)} restaurants")  # Debug logging
        
        if not restaurants:
            return "I couldn't find any restaurants available at the moment."
        
        # Format the data into a clear, bulleted list string
        result = "Here are the restaurants I found! 🏪\n\n"
        for i, r in enumerate(restaurants, 1):
            result += f"• **{r['name']}** in {r.get('area', 'N/A')} (Cuisine: {r.get('cuisine', 'N/A')})\n"
        return result
        
    except requests.exceptions.RequestException as e:
        # Print the REAL error to terminal
        print(f"🔴 FATAL ERROR in get_all_restaurants: {e}")
        print(f"🔴 Error Type: {type(e).__name__}")
        return "🔌 Sorry, I'm having trouble connecting to the restaurant service. Please try again later."

def search_by_cuisine(cuisine):
    """Search restaurants by cuisine"""
    api_url = f"{FASTAPI_BASE_URL}/restaurants/?cuisine={cuisine}"
    print(f"DEBUG: Calling API at URL: {api_url}")  # Debug logging
    try:
        response = requests.get(api_url, timeout=5)
        print(f"DEBUG: API Response Status Code: {response.status_code}")  # Debug logging
        response.raise_for_status()  # Raise error for 4xx/5xx responses
        
        restaurants = response.json()
        print(f"DEBUG: Found {len(restaurants)} {cuisine} restaurants")  # Debug logging
        
        if not restaurants:
            return f"I couldn't find any {cuisine} restaurants at the moment. Would you like to see all available cuisines?"
        
        # Format the data
        result = f"🔍 Here are the **{cuisine}** restaurants I found:\n\n"
        for i, r in enumerate(restaurants, 1):
            result += f"{i}. **{r['name']}** - 📍 {r.get('area', 'N/A')}\n"
        return result
        
    except requests.exceptions.RequestException as e:
        # Print the REAL error to terminal
        print(f"🔴 FATAL ERROR in search_by_cuisine: {e}")
        print(f"🔴 Error Type: {type(e).__name__}")
        return "🔌 Sorry, I'm having trouble connecting to the restaurant service. Please try again later."

def get_restaurant_by_name(name, user_id=None):
    """Get specific restaurant details"""
    api_url = f"{FASTAPI_BASE_URL}/restaurants/{name}"
    print(f"DEBUG: Calling API at URL: {api_url}")  # Debug logging
    try:
        response = requests.get(api_url, timeout=5)
        print(f"DEBUG: API Response Status Code: {response.status_code}")  # Debug logging
        response.raise_for_status()  # Raise error for 4xx/5xx responses
        
        r = response.json()
        restaurant_name = r.get('name')
        print(f"DEBUG: Retrieved restaurant: {restaurant_name}")  # Debug logging
        
        # 🔥 CONTEXT TRACKING: Save the last restaurant viewed
        if user_id:
            save_context(user_id, 'last_restaurant', restaurant_name)
            save_context(user_id, 'last_restaurant_data', r)
        
        # Format restaurant details
        result = f"🏪 **{r['name']}**\n"
        result += f"📍 Location: {r.get('area', 'N/A')}\n"
        result += f"🍴 Cuisine: {r.get('cuisine', 'N/A')}\n\n"
        result += "📋 **Menu:**\n"
        for item in r.get('menu', []):
            result += f"• {item.get('item_name', 'N/A')} - ₹{item.get('price', 0)}\n"
        return result
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"🔴 Restaurant '{name}' not found (404)")
            return f"I couldn't find a restaurant named '{name}'. Would you like me to list all available restaurants?"
        else:
            print(f"🔴 FATAL ERROR in get_restaurant_by_name: {e}")
            print(f"🔴 Error Type: {type(e).__name__}")
            return "🔌 Sorry, I'm having trouble connecting to the restaurant service. Please try again later."
    except requests.exceptions.RequestException as e:
        print(f"🔴 FATAL ERROR in get_restaurant_by_name: {e}")
        print(f"🔴 Error Type: {type(e).__name__}")
        return "🔌 Sorry, I'm having trouble connecting to the restaurant service. Please try again later."

def search_by_item(item_name):
    """Search which restaurants have specific item"""
    api_url = f"{FASTAPI_BASE_URL}/restaurants/search/item?item_name={item_name}"
    print(f"DEBUG: Calling API at URL: {api_url}")  # Debug logging
    try:
        response = requests.get(api_url, timeout=5)
        print(f"DEBUG: API Response Status Code: {response.status_code}")  # Debug logging
        response.raise_for_status()  # Raise error for 4xx/5xx responses
        
        restaurants = response.json()
        print(f"DEBUG: Found {len(restaurants)} restaurants with {item_name}")  # Debug logging
        
        if not restaurants:
            return f"I couldn't find any restaurants that serve {item_name}. Would you like to search for something else?"
        
        # Format the results
        result = f"🔍 Great news! Here are the restaurants serving **{item_name}**:\n\n"
        for i, r in enumerate(restaurants, 1):
            result += f"{i}. **{r['name']}** - 📍 {r.get('area', 'N/A')}\n"
        return result
        
    except requests.exceptions.RequestException as e:
        # Print the REAL error to terminal
        print(f"🔴 FATAL ERROR in search_by_item: {e}")
        print(f"🔴 Error Type: {type(e).__name__}")
        return "🔌 Sorry, I'm having trouble connecting to the restaurant service. Please try again later."

SYSTEM_INSTRUCTION = """You are a friendly FoodieExpress chatbot assistant. 🍕

Your capabilities:
- Help users browse and discover restaurants
- Search by cuisine or food item
- Show restaurant menus and details
- Assist with orders and provide information

CONTEXT AWARENESS RULES:
- Before processing a query, check if there's a "last_restaurant" in the session context
- If the user's query is vague (e.g., "show the menu", "what do they have", "tell me more"), 
  assume they are referring to the last_restaurant
- Vague queries include: "menu", "the menu", "what else", "more info", "details", "items"

When users ask about restaurants, USE THESE TOOLS:
- "list all restaurants" → call get_all_restaurants()
- "gujarati restaurants" → call search_by_cuisine(cuisine)
- "tell me about X" → call get_restaurant_by_name(name)
- "which has bhel?" → call search_by_item(item_name)
- "show menu" (vague) → use last_restaurant from context

Be friendly, use emojis, and be helpful!
"""

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400
        
        message = data.get('message', '')
        user_id = data.get('user_id', 'guest')
        
        if not message:
            return jsonify({"error": "Message required"}), 400
        
        # Initialize session
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []
        
        # Add user message
        chat_sessions[user_id].append({"role": "user", "content": message})
        
        # Check for tool calls (simple keyword matching)
        response_text = None
        message_lower = message.lower()
        
        # 🔥 CONTEXT-AWARE TOOL ROUTING
        # Check if user is asking about "the menu" or similar vague queries
        vague_menu_queries = ["show me the menu", "the menu", "what's on the menu", 
                             "menu please", "show menu", "what do they have",
                             "what else do they have", "tell me more", "more info",
                             "what items", "show items"]
        
        is_vague_query = any(vague in message_lower for vague in vague_menu_queries)
        
        # Tool selection logic with context awareness
        if "list" in message_lower and "restaurant" in message_lower:
            response_text = get_all_restaurants()
            
        elif "which" in message_lower and ("has" in message_lower or "have" in message_lower):
            # Extract item name (simplified)
            words = message.split()
            if len(words) > 3:
                item = words[-1].rstrip('?')
                response_text = search_by_item(item)
                
        elif "gujarati" in message_lower or "italian" in message_lower or "chinese" in message_lower:
            for cuisine in ["gujarati", "italian", "chinese", "mexican", "japanese"]:
                if cuisine in message_lower:
                    response_text = search_by_cuisine(cuisine.capitalize())
                    break
                    
        elif "tell me about" in message_lower:
            # Extract restaurant name
            name_part = message_lower.split("tell me about")[-1].strip()
            response_text = get_restaurant_by_name(name_part.title(), user_id)
            
        elif "menu" in message_lower or is_vague_query:
            # 🔥 CONTEXT-AWARE: Check if there's a last_restaurant
            last_restaurant = get_context(user_id, 'last_restaurant')
            
            if last_restaurant:
                # User is asking about the restaurant they just viewed
                print(f"🔥 CONTEXT HIT: Using last_restaurant = {last_restaurant}")
                response_text = get_restaurant_by_name(last_restaurant, user_id)
            else:
                # Try to extract restaurant name from message
                words = message.split()
                if len(words) > 2:
                    name = ' '.join(words[-2:]).title()
                    response_text = get_restaurant_by_name(name, user_id)
                else:
                    # No context and no restaurant name provided
                    response_text = "I'd be happy to show you a menu! Which restaurant would you like to know about?"
        
        # If no tool was called, use Ollama
        if not response_text:
            response_text = call_ollama(chat_sessions[user_id], SYSTEM_INSTRUCTION)
        
        # Add assistant response
        chat_sessions[user_id].append({"role": "assistant", "content": response_text})
        
        return jsonify({"response": response_text, "status": "success"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "healthy", "model": OLLAMA_MODEL})

@app.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear chat session and context"""
    data = request.get_json()
    if data:
        user_id = data.get('user_id', 'guest')
        if user_id in chat_sessions:
            del chat_sessions[user_id]
        if user_id in session_context:
            del session_context[user_id]
    return jsonify({"message": "Session and context cleared"})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 FoodieExpress Agent - Ollama Edition")
    print("="*60)
    print(f"✅ Model: {OLLAMA_MODEL}")
    print(f"✅ Backend: {FASTAPI_BASE_URL}")
    print(f"✅ Running on http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
