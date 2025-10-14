"""
AI Food Delivery Chatbot Agent - V3.0 SCALABLE ARCHITECTURE
Built with Google Gemini AI and Flask

🚀 MAJOR UPGRADE: Scalable & Highly Maintainable Architecture
=============================================================

ARCHITECTURAL IMPROVEMENTS:
---------------------------
✅ [PHASE 1] Redis Session Management - Distributed, persistent sessions
✅ [PHASE 2] Modular Code Structure - Refactored 350+ line function into focused modules
✅ [PHASE 3] Enhanced Observability - Request ID tracking across services
✅ [PHASE 4] Specific Error Handling - Granular exception handling with user-friendly messages

SCALABILITY FEATURES:
- Horizontal scaling across multiple server instances
- Session persistence across restarts
- Automatic session expiry (1-hour TTL)
- High-performance Redis backend

MAINTAINABILITY FEATURES:
- Single Responsibility Principle for all functions
- Clear separation of concerns
- Comprehensive error handling
- Request tracing for debugging

Author: Senior Software Engineer
Version: 3.0
Date: October 14, 2025
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import json
import redis
from datetime import timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging
import uuid

# Load environment variables
load_dotenv()

# ==================== LOGGING CONFIGURATION ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== FLASK APP INITIALIZATION ====================
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"])

# ==================== ENVIRONMENT CONFIGURATION ====================
# Google Gemini AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ CRITICAL: GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)

# FastAPI Backend
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

# Session TTL Configuration
SESSION_TTL = int(os.getenv("SESSION_TTL", 3600))  # 1 hour default
PENDING_ORDER_TTL = int(os.getenv("PENDING_ORDER_TTL", 600))  # 10 minutes default

# ==================== REDIS SESSION STORE ====================
"""
PHASE 1: DISTRIBUTED SESSION MANAGEMENT WITH REDIS

Benefits:
- ✅ Persistent storage across server restarts
- ✅ Horizontal scaling across multiple instances
- ✅ Automatic session expiry with TTL
- ✅ High performance (sub-millisecond operations)
- ✅ Production-ready reliability

Architecture:
- Session data stored in Redis with user_id as key
- Automatic cleanup via TTL (no manual garbage collection)
- Fallback to in-memory if Redis unavailable (development mode)
"""

# In-memory fallback (for development without Redis)
memory_chat_sessions: Dict[str, list] = {}
memory_pending_orders: Dict[str, Dict[str, Any]] = {}

# Initialize Redis client with connection pooling
redis_client = None
if REDIS_ENABLED:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test connection
        redis_client.ping()
        logger.info(f"✅ Redis connected: {REDIS_HOST}:{REDIS_PORT} (DB {REDIS_DB})")
    except redis.ConnectionError as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        logger.warning("📝 Falling back to in-memory session storage (development mode)")
        redis_client = None
    except Exception as e:
        logger.error(f"❌ Redis initialization error: {e}")
        redis_client = None


def get_session_from_redis(user_id: str) -> list:
    """
    Retrieve chat history from Redis.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        List of chat messages (conversation history)
        Empty list if session not found or Redis unavailable
    """
    if not redis_client:
        # Fallback to in-memory storage
        return memory_chat_sessions.get(user_id, [])
    
    try:
        session_key = f"chat_session:{user_id}"
        session_data = redis_client.get(session_key)
        
        if session_data:
            return json.loads(session_data)
        return []
    except redis.RedisError as e:
        logger.error(f"❌ Redis GET error for user {user_id}: {e}")
        return memory_chat_sessions.get(user_id, [])
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error for user {user_id}: {e}")
        return []


def save_session_to_redis(user_id: str, history: list, ttl: int = SESSION_TTL) -> bool:
    """
    Save chat history to Redis with TTL (automatic expiry).
    
    Args:
        user_id: Unique identifier for the user
        history: List of chat messages to save
        ttl: Time-to-live in seconds (default: 1 hour)
        
    Returns:
        True if saved successfully, False otherwise
    """
    if not redis_client:
        # Fallback to in-memory storage
        memory_chat_sessions[user_id] = history
        return True
    
    try:
        session_key = f"chat_session:{user_id}"
        redis_client.setex(
            session_key,
            timedelta(seconds=ttl),
            json.dumps(history)
        )
        return True
    except redis.RedisError as e:
        logger.error(f"❌ Redis SET error for user {user_id}: {e}")
        # Fallback to in-memory
        memory_chat_sessions[user_id] = history
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error saving session for user {user_id}: {e}")
        return False


def get_pending_order_from_redis(user_id: str) -> Optional[Dict]:
    """
    Retrieve pending order from Redis.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Pending order dictionary or None if not found
    """
    if not redis_client:
        return memory_pending_orders.get(user_id, None)
    
    try:
        order_key = f"pending_order:{user_id}"
        order_data = redis_client.get(order_key)
        
        if order_data:
            return json.loads(order_data)
        return None
    except redis.RedisError as e:
        logger.error(f"❌ Redis GET pending order error for user {user_id}: {e}")
        return memory_pending_orders.get(user_id, None)
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error for pending order user {user_id}: {e}")
        return None


def save_pending_order_to_redis(user_id: str, order: Dict, ttl: int = PENDING_ORDER_TTL) -> bool:
    """
    Save pending order to Redis with TTL (shorter expiry than sessions).
    
    Args:
        user_id: Unique identifier for the user
        order: Pending order dictionary
        ttl: Time-to-live in seconds (default: 10 minutes)
        
    Returns:
        True if saved successfully, False otherwise
    """
    if not redis_client:
        memory_pending_orders[user_id] = order
        return True
    
    try:
        order_key = f"pending_order:{user_id}"
        redis_client.setex(
            order_key,
            timedelta(seconds=ttl),
            json.dumps(order)
        )
        return True
    except redis.RedisError as e:
        logger.error(f"❌ Redis SET pending order error for user {user_id}: {e}")
        memory_pending_orders[user_id] = order
        return False


def delete_pending_order_from_redis(user_id: str) -> bool:
    """
    Delete pending order after completion/cancellation.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        True if deleted successfully, False otherwise
    """
    if not redis_client:
        if user_id in memory_pending_orders:
            del memory_pending_orders[user_id]
        return True
    
    try:
        order_key = f"pending_order:{user_id}"
        redis_client.delete(order_key)
        return True
    except redis.RedisError as e:
        logger.error(f"❌ Redis DELETE pending order error for user {user_id}: {e}")
        if user_id in memory_pending_orders:
            del memory_pending_orders[user_id]
        return False


# ==================== REQUEST ID MIDDLEWARE ====================
"""
PHASE 3: OBSERVABILITY - REQUEST ID TRACKING

Purpose:
- Generate unique ID for each request
- Trace requests across microservices
- Correlate logs for debugging
- Monitor request flow in distributed systems
"""

@app.before_request
def add_request_id():
    """Generate unique request ID for tracing"""
    request.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    logger.info(f"📥 Incoming request: {request.method} {request.path}")


@app.after_request
def add_request_id_header(response):
    """Add request ID to response headers"""
    response.headers['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
    return response


# ==================== HELPER FUNCTIONS - MODULAR ARCHITECTURE ====================
"""
PHASE 2: CODE REFACTORING FOR MAINTAINABILITY

The original chat() function was 350+ lines - a monolithic function that:
- Violated Single Responsibility Principle
- Was difficult to test
- Had poor error handling
- Mixed concerns (auth, session, AI, function calling)

New Architecture:
- Each function has ONE clear responsibility
- Easy to test in isolation
- Clear error boundaries
- Reusable across endpoints
"""

def _get_user_context(request_data: Dict[str, Any]) -> Tuple[str, str, Optional[str]]:
    """
    Extract user context from incoming request.
    
    RESPONSIBILITY: Parse and validate request payload
    
    Args:
        request_data: JSON payload from POST /chat
        
    Returns:
        Tuple of (user_message, user_id, auth_token)
        
    Raises:
        ValueError: If message is missing or invalid
    """
    user_message = request_data.get('message', '').strip()
    user_id = request_data.get('user_id', 'guest')
    
    if not user_message:
        raise ValueError("Message is required and cannot be empty")
    
    # Extract token from Authorization header (preferred) or body (fallback)
    auth_header = request.headers.get('Authorization', '')
    token = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1].strip()
        logger.info(f"🔐 Token extracted from Authorization header for user: {user_id}")
    elif request_data.get('token'):
        token = request_data.get('token')
        logger.info(f"🔐 Token extracted from request body for user: {user_id}")
    else:
        logger.info(f"🔓 No token found - user is not authenticated: {user_id}")
    
    return user_message, user_id, token


def _get_or_create_session(user_id: str) -> list:
    """
    Retrieve existing session or create new one.
    
    RESPONSIBILITY: Session management (Redis or in-memory)
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        List of chat messages (conversation history)
    """
    session = get_session_from_redis(user_id)
    
    if not session:
        logger.info(f"🆕 New session created for user: {user_id}")
    else:
        logger.info(f"📖 Loaded session with {len(session)} messages for user: {user_id}")
    
    return session


def _save_session(user_id: str, conversation_history: list) -> None:
    """
    Save updated conversation history to Redis.
    
    RESPONSIBILITY: Persist session data
    
    Args:
        user_id: Unique identifier for the user
        conversation_history: Updated list of chat messages
    """
    success = save_session_to_redis(user_id, conversation_history)
    
    if success:
        logger.info(f"💾 Session saved for user: {user_id} ({len(conversation_history)} messages)")
    else:
        logger.warning(f"⚠️ Session save failed for user: {user_id}, using in-memory fallback")


def _make_api_request(method: str, endpoint: str, auth_token: Optional[str] = None,
                      json_data: Optional[Dict] = None, params: Optional[Dict] = None,
                      timeout: int = 10) -> requests.Response:
    """
    Make HTTP request to FastAPI backend with comprehensive error handling.
    
    PHASE 3 & 4: Enhanced observability and specific error handling
    
    RESPONSIBILITY: HTTP communication with proper error boundaries
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        auth_token: Optional JWT token for authentication
        json_data: Optional JSON payload
        params: Optional query parameters
        timeout: Request timeout in seconds
        
    Returns:
        Response object from requests library
        
    Raises:
        requests.exceptions.Timeout: If request times out
        requests.exceptions.ConnectionError: If connection fails
        requests.exceptions.RequestException: For other request errors
    """
    url = f"{FASTAPI_BASE_URL}{endpoint}"
    headers = {}
    
    # Add authentication token if provided
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    # Add request ID for tracing
    if hasattr(request, 'request_id'):
        headers["X-Request-ID"] = request.request_id
    
    logger.info(f"🌐 {method} {url}")
    if params:
        logger.info(f"📋 Query params: {params}")
    if json_data:
        logger.info(f"📤 Request body: {json.dumps(json_data, indent=2)[:200]}...")
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            params=params,
            timeout=timeout
        )
        
        logger.info(f"📥 Response: {response.status_code}")
        return response
        
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Request timeout: {method} {url}")
        raise
    except requests.exceptions.ConnectionError:
        logger.error(f"🔌 Connection failed: {method} {url}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error: {method} {url} - {e}")
        raise


def _handle_function_call(function_call, auth_token: Optional[str]) -> str:
    """
    Execute a function called by Gemini AI.
    
    RESPONSIBILITY: Function call orchestration and execution
    
    Args:
        function_call: Gemini function call object
        auth_token: Optional JWT token for protected endpoints
        
    Returns:
        String result from the function execution
        
    Raises:
        ValueError: If function not found or authentication required but missing
    """
    function_name = function_call.name
    function_args = dict(function_call.args)
    
    logger.info(f"🤖 AI decided to call function: {function_name}")
    logger.info(f"📋 Function arguments: {function_args}")
    
    # Check if function requires authentication
    protected_functions = ['place_order', 'get_user_orders', 'add_review']
    if function_name in protected_functions:
        if not auth_token:
            raise ValueError("AUTHENTICATION_REQUIRED")
        function_args['token'] = auth_token
    
    # Verify function exists
    if function_name not in available_functions:
        raise ValueError(f"Unknown function: {function_name}")
    
    # Execute the function
    function_to_call = available_functions[function_name]
    logger.info(f"⚙️ Executing: {function_name}(**{function_args})")
    
    result = function_to_call(**function_args)
    logger.info(f"✅ Function returned: {result[:200]}...")
    
    return result


# ==================== FUNCTION DECLARATIONS (same as before) ====================

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

tools = genai.protos.Tool(function_declarations=function_declarations)

# ==================== API HELPER FUNCTIONS WITH ENHANCED ERROR HANDLING ====================
# Note: I'll continue this in the next part...
