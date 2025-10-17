"""
FastAPI Main Application - FoodieExpress Backend
Enhanced with Reviews, Multi-Item Orders, Role-Based Access Control, and Cuisine Search

SECURITY ENHANCEMENTS:
- [HIGH-002] Rate limiting on authentication endpoints
- [HIGH-003] Enhanced input validation via Pydantic schemas
- [MEDIUM-005] Environment-based CORS configuration
- Improved error handling and security headers
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import secrets
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import timedelta
import os
import uuid
from dotenv import load_dotenv

# Rate Limiting - HIGH-002 FIX
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Local Imports
from .database import init_db
from .models import Restaurant, User, Order, Review, OrderItem
from .schemas import (
    RestaurantCreate, UserCreate, UserOut, OrderCreate, OrderOut,
    ReviewCreate, ReviewUpdate, ReviewOut, RestaurantItem,
    PlatformStatsOut, PopularRestaurantOut, UserActivityOut
)
from .security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .dependencies import get_current_user, get_current_admin_user

# NEW: Authentication System
from .auth import AuthService
from .auth_schemas import (
    UserRegisterRequest, UserLoginRequest, 
    UserRegisterResponse, UserLoginResponse, UserLogoutResponse
)

# ==================== RATE LIMITING CONFIGURATION ====================
# HIGH-002 FIX: Prevent brute force attacks and API abuse
limiter = Limiter(key_func=get_remote_address)

# Application Lifespan Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown events"""
    await init_db()
    print("✅ Database connection established.")
    yield
    print("🔌 Closing database connection.")

# Create FastAPI App with Swagger Bearer Token Authorization
app = FastAPI(
    title="FoodieExpress API",
    description="AI-Powered Food Delivery Platform with Reviews, Admin Dashboard & Intelligence Features",
    version="4.0.0",
    lifespan=lifespan,
    # IMPORTANT: Set openapi_url to None initially to prevent auto-generation
    # We'll re-enable it after customizing the schema
    # openapi_url=None,  # Uncomment if needed
    # Define security schemes for OpenAPI documentation
    openapi_tags=[
        {"name": "Authentication", "description": "User registration, login, and logout"},
        {"name": "Restaurants", "description": "Restaurant management operations"},
        {"name": "Orders", "description": "Order creation and management"},
        {"name": "Reviews", "description": "Restaurant reviews and ratings"},
    ],
    # Disable automatic security scheme generation
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# NUCLEAR OPTION: Completely override OpenAPI schema generation
def custom_openapi():
    """
    Custom OpenAPI schema that FORCES removal of OAuth2 auto-detection.
    
    FastAPI automatically detects OAuth2PasswordBearer from dependencies,
    so we need to aggressively remove it and replace with HTTPBearer.
    """
    # Always regenerate to ensure we get the latest schema
    app.openapi_schema = None
    
    from fastapi.openapi.utils import get_openapi
    import copy
    
    # Generate the base schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    
    # CRITICAL: Initialize components if not exists
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    # NUCLEAR OPTION: Delete ALL existing security schemes
    if "securitySchemes" in openapi_schema["components"]:
        del openapi_schema["components"]["securitySchemes"]
    
    # Add ONLY HTTP Basic Auth (Simple username/password)
    openapi_schema["components"]["securitySchemes"] = {
        "BasicAuth": {
            "type": "http",
            "scheme": "basic",
            "description": "Admin access: Username=Meet, Password=Meet7805"
        }
    }
    
    # Aggressively replace ALL security references in ALL paths
    if "paths" in openapi_schema:
        for path_item in openapi_schema["paths"].values():
            if isinstance(path_item, dict):
                for operation in path_item.values():
                    if isinstance(operation, dict):
                        # Remove any existing security
                        if "security" in operation:
                            # Check if any security requirement exists
                            has_security = False
                            for sec_req in operation["security"]:
                                if any(key for key in sec_req.keys()):
                                    has_security = True
                                    break
                            
                            # If endpoint had security, replace with BasicAuth
                            if has_security:
                                operation["security"] = [{"BasicAuth": []}]
    
    # Save and return
    app.openapi_schema = openapi_schema
    return openapi_schema

# Apply custom OpenAPI
app.openapi = custom_openapi

# Force regeneration on startup
@app.on_event("startup")
async def regenerate_openapi():
    """Force OpenAPI schema regeneration on startup"""
    app.openapi_schema = None
    custom_openapi()

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ==================== SWAGGER BASIC AUTH ====================
# Single admin account for Swagger UI access
security = HTTPBasic()
SWAGGER_USERNAME = "Meet"
SWAGGER_PASSWORD = "Meet7805"

def verify_swagger_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify Swagger UI credentials (single admin account).
    
    Admin credentials:
    - Username: Meet
    - Password: Meet7805
    """
    correct_username = secrets.compare_digest(credentials.username, SWAGGER_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, SWAGGER_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ==================== VALIDATION ERROR HANDLER ====================
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors to provide detailed error messages
    """
    print(f"\n❌ VALIDATION ERROR on {request.method} {request.url.path}")
    print(f"Errors: {exc.errors()}")
    print(f"Body: {exc.body}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

# ==================== CORS MIDDLEWARE ====================
# MEDIUM-005 FIX: Load allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:3000")
allowed_origins_list = [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== REQUEST ID MIDDLEWARE (V3.0/V4.0) ====================
# Distributed tracing middleware for observability

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """
    Generate or propagate X-Request-ID for distributed tracing.
    
    V3.0 Feature: Enables end-to-end request tracking across services.
    This middleware:
    - Generates a unique request ID if not provided
    - Propagates the ID through all log entries
    - Returns the ID in response headers for client correlation
    """
    # Get Request ID from header or generate new one
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    # Log incoming request with ID
    print(f"📥 [{request_id}] {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Add Request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response

# ==================== PUBLIC ENDPOINTS ====================

@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to FoodieExpress API!",
        "version": "4.0.0",
        "features": [
            "AI Chatbot",
            "Multi-Item Orders",
            "Reviews & Ratings",
            "Cuisine Search",
            "Admin Dashboard",
            "Business Intelligence",
            "Personalized Recommendations",
            "Distributed Tracing"
        ]
    }

@app.get("/restaurants/", response_model=List[RestaurantCreate])
async def get_all_restaurants(cuisine: Optional[str] = Query(None, description="Filter by cuisine type")):
    """
    Retrieve all restaurants with optional cuisine filtering.
    
    Query Parameters:
    - cuisine: Optional filter by cuisine type (e.g., "Italian", "Gujarati", "South Indian")
              Filtering is case-insensitive.
    
    Examples:
    - GET /restaurants/ - Returns all restaurants
    - GET /restaurants/?cuisine=Gujarati - Returns only Gujarati restaurants
    - GET /restaurants/?cuisine=gujarati - Same as above (case-insensitive)
    """
    try:
        if cuisine:
            # Use MongoDB case-insensitive regex for efficient filtering
            query = {"cuisine": {"$regex": f"^{cuisine}$", "$options": "i"}}
            restaurants = await Restaurant.find(query).to_list()
        else:
            restaurants = await Restaurant.find_all().to_list()
        
        return [
            RestaurantCreate(
                name=r.name,
                area=r.area,
                cuisine=r.cuisine,
                items=r.items
            ) for r in restaurants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")

@app.get("/restaurants/{restaurant_name}", response_model=RestaurantCreate)
async def get_restaurant_by_name(restaurant_name: str):
    """Retrieve a specific restaurant by name"""
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    return RestaurantCreate(
        name=restaurant.name,
        area=restaurant.area,
        cuisine=restaurant.cuisine,
        items=restaurant.items
    )

@app.get("/search/items", response_model=List[RestaurantCreate])
async def search_restaurants_by_item(item_name: str = Query(..., description="Name of the menu item to search for")):
    """
    Search for restaurants that serve a specific menu item.
    
    This endpoint performs a case-insensitive search across all restaurant menus
    to find which restaurants offer the specified item.
    
    Query Parameters:
    - item_name: The name of the food item to search for (e.g., "Pizza", "Dhokla", "Bhel")
    
    Examples:
    - GET /search/items?item_name=Pizza
    - GET /search/items?item_name=dhokla (case-insensitive)
    
    Returns:
    - List of restaurants that have the item on their menu
    """
    try:
        # Use MongoDB $elemMatch with case-insensitive regex to search within items array
        # This efficiently finds documents where at least one item in the array matches
        query = {
            "items": {
                "$elemMatch": {
                    "item_name": {"$regex": f"^{item_name}$", "$options": "i"}
                }
            }
        }
        
        restaurants = await Restaurant.find(query).to_list()
        
        return [
            RestaurantCreate(
                name=r.name,
                area=r.area,
                cuisine=r.cuisine,
                items=r.items
            ) for r in restaurants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for item: {str(e)}")

# ==================== REVIEW ENDPOINTS ====================

@app.post("/restaurants/{restaurant_name}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(
    restaurant_name: str,
    review_data: ReviewCreate
):
    """
    Submit a review for a restaurant (NO AUTHENTICATION REQUIRED).
    
    Authentication system removed - anyone can leave reviews!
    """
    # Guest user ID
    guest_user_id = "guest_user"
    guest_username = "Anonymous"
    # Verify restaurant exists
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    # Validate that review_data.restaurant_name matches URL parameter
    if review_data.restaurant_name != restaurant_name:
        raise HTTPException(
            status_code=400,
            detail="Restaurant name in URL must match restaurant name in request body"
        )
    
    # Skip duplicate review check - removed authentication
    # Anyone can review multiple times now
    
    # Skip verified purchase check - no authentication
    is_verified = False
    
    # Create review with guest user
    review = Review(
        user_id=guest_user_id,
        username=guest_username,
        restaurant_name=restaurant_name,
        rating=review_data.rating,
        comment=review_data.comment,
        helpful_count=0,
        is_verified_purchase=is_verified
    )
    await review.insert()
    
    return ReviewOut(
        id=review.id,
        user_id=review.user_id,
        username=review.username,
        restaurant_name=review.restaurant_name,
        rating=review.rating,
        comment=review.comment,
        review_date=review.review_date,
        helpful_count=review.helpful_count,
        is_verified_purchase=review.is_verified_purchase
    )

@app.get("/restaurants/{restaurant_name}/reviews", response_model=List[ReviewOut])
async def get_restaurant_reviews(
    restaurant_name: str,
    limit: int = Query(10, ge=1, le=100, description="Number of reviews to return"),
    skip: int = Query(0, ge=0, description="Number of reviews to skip")
):
    """
    V4.0: Get all reviews for a specific restaurant (public endpoint with pagination).
    
    Query Parameters:
    - limit: Maximum number of reviews to return (1-100, default 10)
    - skip: Number of reviews to skip for pagination (default 0)
    
    Returns reviews sorted by date (newest first)
    """
    # Verify restaurant exists
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    # Get paginated reviews, sorted by date (newest first)
    reviews = await Review.find(
        Review.restaurant_name == restaurant_name
    ).sort(-Review.review_date).skip(skip).limit(limit).to_list()
    
    return [
        ReviewOut(
            id=review.id,
            user_id=review.user_id,
            username=review.username,
            restaurant_name=review.restaurant_name,
            rating=review.rating,
            comment=review.comment,
            review_date=review.review_date,
            helpful_count=review.helpful_count,
            is_verified_purchase=review.is_verified_purchase
        ) for review in reviews
    ]

@app.get("/restaurants/{restaurant_name}/reviews/stats")
async def get_restaurant_review_stats(restaurant_name: str):
    """
    Get aggregated review statistics for a restaurant.
    """
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    reviews = await Review.find(Review.restaurant_name == restaurant_name).to_list()
    
    if not reviews:
        return {
            "restaurant_name": restaurant_name,
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    total_reviews = len(reviews)
    average_rating = sum(r.rating for r in reviews) / total_reviews
    rating_distribution = {i: sum(1 for r in reviews if r.rating == i) for i in range(1, 6)}
    
    return {
        "restaurant_name": restaurant_name,
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2),
        "rating_distribution": rating_distribution
    }

@app.put("/reviews/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: str,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    V4.0: Update an existing review (owner only).
    
    Users can only update their own reviews.
    Can update rating and/or comment.
    """
    from beanie import PydanticObjectId
    
    # Find the review
    try:
        review = await Review.get(PydanticObjectId(review_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check ownership
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own reviews"
        )
    
    # Update fields if provided
    if update_data.rating is not None:
        review.rating = update_data.rating
    if update_data.comment is not None:
        review.comment = update_data.comment
    
    await review.save()
    
    return ReviewOut(
        id=review.id,
        user_id=review.user_id,
        username=review.username,
        restaurant_name=review.restaurant_name,
        rating=review.rating,
        comment=review.comment,
        review_date=review.review_date,
        helpful_count=review.helpful_count,
        is_verified_purchase=review.is_verified_purchase
    )

@app.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    V4.0: Delete an existing review (owner only).
    
    Users can only delete their own reviews.
    """
    from beanie import PydanticObjectId
    
    # Find the review
    try:
        review = await Review.get(PydanticObjectId(review_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check ownership
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own reviews"
        )
    
    await review.delete()
    return None

@app.get("/users/me/reviews", response_model=List[ReviewOut])
async def get_my_reviews(current_user: User = Depends(get_current_user)):
    """
    V4.0: Get all reviews by the current authenticated user.
    
    Returns reviews sorted by date (newest first).
    """
    reviews = await Review.find(
        Review.user_id == current_user.id
    ).sort(-Review.review_date).to_list()
    
    return [
        ReviewOut(
            id=review.id,
            user_id=review.user_id,
            username=review.username,
            restaurant_name=review.restaurant_name,
            rating=review.rating,
            comment=review.comment,
            review_date=review.review_date,
            helpful_count=review.helpful_count,
            is_verified_purchase=review.is_verified_purchase
        ) for review in reviews
    ]

# ==================== ADMIN-ONLY RESTAURANT MANAGEMENT ====================

@app.post("/restaurants/", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_admin: User = Depends(get_current_admin_user)  # ADMIN ONLY
):
    """
    Create a new restaurant (admin only).
    """
    # Check if restaurant already exists
    existing = await Restaurant.find_one(Restaurant.name == restaurant_data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Restaurant with this name already exists")
    
    restaurant = Restaurant(**restaurant_data.dict())
    await restaurant.insert()
    return restaurant

@app.put("/restaurants/{restaurant_name}", response_model=Restaurant)
async def update_restaurant_by_name(
    restaurant_name: str,
    update_data: RestaurantCreate,
    current_admin: User = Depends(get_current_admin_user)  # ADMIN ONLY
):
    """
    Update an existing restaurant (admin only).
    """
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    restaurant.name = update_data.name
    restaurant.area = update_data.area
    restaurant.cuisine = update_data.cuisine
    restaurant.items = update_data.items
    await restaurant.save()
    return restaurant

@app.delete("/restaurants/{restaurant_name}")
async def delete_restaurant_by_name(
    restaurant_name: str,
    current_admin: User = Depends(get_current_admin_user)  # ADMIN ONLY
):
    """
    Delete a restaurant (admin only).
    """
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    await restaurant.delete()
    return {"message": f"Restaurant '{restaurant_name}' deleted successfully"}

# ==================== USER AUTHENTICATION ====================
# COMPREHENSIVE AUTH SYSTEM - Supports Guest & Logged-In Users
# - CASE 1: Logged-in users can order seamlessly
# - CASE 2: Guest users can browse, but must login to order

@app.post("/api/auth/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user_data: UserRegisterRequest):
    """
    Register a new user account with comprehensive validation
    
    Requirements:
    - Unique username (3-50 chars, alphanumeric + underscore/hyphen only)
    - Valid email address
    - Strong password (8+ chars, uppercase, lowercase, number)
    - First name and last name (1-50 chars each)
    
    Returns:
    - Success message with user details
    - User ID for immediate login
    """
    print(f"\n🔐 REGISTRATION REQUEST: username={user_data.username}, email={user_data.email}")
    
    # Validate password strength
    try:
        AuthService.validate_password_strength(user_data.password)
    except ValueError as e:
        print(f"❌ Password validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    # Check email uniqueness
    existing_user = await User.find_one(User.email == user_data.email.lower())
    if existing_user:
        print(f"❌ Email already registered: {user_data.email}")
        raise HTTPException(
            status_code=400, 
            detail="This email is already registered. Please login instead or use a different email."
        )
    
    # Check username uniqueness (case-insensitive)
    existing_user = await User.find_one(User.username == user_data.username.lower())
    if existing_user:
        print(f"❌ Username already taken: {user_data.username}")
        raise HTTPException(
            status_code=400, 
            detail="This username is already taken. Please choose a different username or login if you already have an account."
        )
    
    # Hash password using bcrypt
    hashed_password = AuthService.hash_password(user_data.password)
    
    # Create user with all required fields
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="user"  # Default role
    )
    
    await user.insert()
    
    print(f"✅ User registered successfully: {user.username} (ID: {user.id})")
    
    return UserRegisterResponse(
        message="Registration successful! You can now login.",
        user_id=str(user.id),
        username=user.username,
        email=user.email
    )


# ==================== LEGACY REGISTRATION ENDPOINT ====================
@app.post("/users/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def legacy_register_for_compatibility(user_data: UserRegisterRequest):
    """
    Legacy registration endpoint for backward compatibility.
    
    This endpoint exists to support frontend code that calls /users/register.
    It accepts the same JSON data as /api/auth/register and returns the same response.
    
    RECOMMENDATION: Frontend should migrate to /api/auth/register for consistency.
    
    Required fields:
    - username: 3-50 chars, alphanumeric + underscore/hyphen
    - email: Valid email address
    - password: 8+ chars, uppercase, lowercase, number
    - first_name: User's first name
    - last_name: User's last name
    """
    try:
        print(f"\n🔐 LEGACY REGISTRATION: username={user_data.username}, email={user_data.email}")
        
        # Validate password strength
        try:
            AuthService.validate_password_strength(user_data.password)
        except ValueError as e:
            print(f"❌ Password validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Check email uniqueness (case-insensitive)
        existing_user = await User.find_one(User.email == user_data.email.lower())
        if existing_user:
            print(f"❌ Email already registered: {user_data.email}")
            raise HTTPException(
                status_code=400, 
                detail="This email is already registered. Please login instead or use a different email."
            )
        
        # Check username uniqueness (case-insensitive)
        existing_user = await User.find_one(User.username == user_data.username.lower())
        if existing_user:
            print(f"❌ Username already taken: {user_data.username}")
            raise HTTPException(
                status_code=400, 
                detail="This username is already taken. Please choose a different username or login if you already have an account."
            )
        
        # Hash password using bcrypt
        hashed_password = AuthService.hash_password(user_data.password)
        
        # Create user with all required fields
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role="user"  # Default role
        )
        
        await user.insert()
        
        print(f"✅ Legacy registration successful: {user.username} (ID: {user.id})")
        
        return UserRegisterResponse(
            message="Registration successful! You can now login.",
            user_id=str(user.id),
            username=user.username,
            email=user.email
        )
    except HTTPException:
        # Re-raise HTTP exceptions (400, etc.)
        raise
    except Exception as e:
        # Log unexpected errors
        print(f"❌ UNEXPECTED ERROR in /users/register: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/auth/login", response_model=UserLoginResponse, tags=["Authentication"])
@limiter.limit("5/minute")  # Rate limit to prevent brute force attacks
async def login_user(request: Request, login_data: UserLoginRequest):
    """
    Authenticate user and return JWT token (1-hour expiry)
    
    Features:
    - Login with username OR email
    - Rate limited (5 attempts/minute)
    - Returns JWT Bearer token
    - Token expires in 1 hour
    
    Security:
    - Bcrypt password verification
    - Generic error messages (no user enumeration)
    - Rate limiting prevents brute force
    """
    print(f"\n🔐 LOGIN REQUEST: {login_data.username_or_email}")
    
    # Find user by username or email (case-insensitive for username)
    user = await User.find_one(User.username == login_data.username_or_email.lower())
    if not user:
        user = await User.find_one(User.email == login_data.username_or_email.lower())
    
    # Verify credentials
    if not user or not AuthService.verify_password(login_data.password, user.hashed_password):
        print(f"❌ Invalid credentials for: {login_data.username_or_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token (1 hour expiry)
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "user_id": str(user.id)}
    )
    
    print(f"✅ Login successful: {user.username}")
    
    return UserLoginResponse(
        message="Login successful!",
        token=access_token,
        token_type="bearer",
        expires_in=3600,  # 1 hour in seconds
        user={
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    )


@app.post("/api/auth/logout", response_model=UserLogoutResponse, tags=["Authentication"])
async def logout_user(request: Request):
    """
    Logout user (client-side token deletion)
    
    Note: Since we use stateless JWT tokens, logout is handled client-side
    by deleting the token. This endpoint provides a consistent API interface
    and can be extended for token blacklisting in the future.
    """
    # Extract token for logging purposes
    auth_header = request.headers.get("Authorization", "")
    token = AuthService.extract_token_from_header(auth_header)
    
    if token:
        try:
            payload = AuthService.decode_token(token)
            username = payload.get("sub")
            print(f"🔓 LOGOUT: {username}")
        except Exception:
            pass
    
    return UserLogoutResponse(
        message="Logout successful! Please delete your token on the client side."
    )


# ==================== LEGACY ENDPOINT FOR SWAGGER OAUTH2 COMPATIBILITY ====================
@app.post("/users/login")
@limiter.limit("5/minute")
async def legacy_login_for_swagger(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Legacy login endpoint for Swagger OAuth2 compatibility.
    
    This endpoint accepts form data (username/password) and returns a token in OAuth2 format.
    
    IMPORTANT: Frontend should use /api/auth/login (JSON-based) instead.
    This endpoint is primarily for Swagger UI OAuth2 authorization flow.
    
    Required form fields:
    - username: Username or email
    - password: User password
    - grant_type: OAuth2 grant type (optional, defaults to "password")
    """
    try:
        print(f"\n🔐 LEGACY LOGIN (Form): {form_data.username}")
        
        # Find user by username or email (case-insensitive for username)
        user = await User.find_one(User.username == form_data.username.lower())
        if not user:
            user = await User.find_one(User.email == form_data.username.lower())
        
        # Verify credentials
        if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
            print(f"❌ Invalid credentials for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create JWT token
        access_token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": str(user.id)}
        )
        
        print(f"✅ Legacy login successful: {user.username}")
        
        # Return in OAuth2 format (required by OAuth2PasswordBearer)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        # Re-raise HTTP exceptions (401, etc.)
        raise
    except Exception as e:
        # Log unexpected errors
        print(f"❌ UNEXPECTED ERROR in /users/login: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get(
    "/users/me", 
    response_model=UserOut,
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        200: {"description": "Successfully retrieved user information"}
    },
    summary="Get Current User Info",
    description="Get information about the currently authenticated user. Requires Bearer token in Authorization header."
)
async def get_current_user_info(request: Request):
    """
    Get current logged-in user information
    
    **Authorization Required**: Bearer token in Authorization header
    
    Example:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    current_user = await get_current_user(request)
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role
    )

# ==================== ORDER MANAGEMENT ====================

@app.post("/orders/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate
):
    """
    Create a new multi-item order (NO AUTHENTICATION REQUIRED).
    
    Authentication system removed - orders work for everyone!
    """
    # Create a default guest user ID
    guest_user_id = "guest_user"
    
    print("\n" + "="*60)
    print("🎯 FASTAPI: ORDER CREATION REQUEST (NO AUTH)")
    print("="*60)
    print(f"👤 User: Guest")
    print(f"🏪 Restaurant: {order_data.restaurant_name}")
    print(f"📦 Number of items: {len(order_data.items)}")
    print(f"📋 Items:")
    for idx, item in enumerate(order_data.items, 1):
        print(f"   {idx}. {item.item_name} x {item.quantity} @ ₹{item.price}")
    
    # Verify restaurant exists
    restaurant = await Restaurant.find_one(Restaurant.name == order_data.restaurant_name)
    if not restaurant:
        print(f"❌ Restaurant '{order_data.restaurant_name}' not found in database")
        print("="*60 + "\n")
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    print(f"✅ Restaurant found: {restaurant.name}")
    
    # Calculate total price
    total_price = sum(item.price * item.quantity for item in order_data.items)
    print(f"💰 Calculated total: ₹{total_price:.2f}")
    
    # Create order items
    order_items = [
        OrderItem(
            item_name=item.item_name,
            quantity=item.quantity,
            price=item.price
        ) for item in order_data.items
    ]
    
    print(f"✅ Order items created: {len(order_items)}")
    
    # Create order with guest user ID
    order = Order(
        user_id=guest_user_id,
        restaurant_name=order_data.restaurant_name,
        items=order_items,
        total_price=total_price,
        status="placed"
    )
    
    print(f"📝 Attempting to save order to database...")
    
    try:
        await order.insert()
        print(f"✅ Order saved successfully! Order ID: {order.id}")
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Failed to save order to database: {str(e)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
    
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        restaurant_name=order.restaurant_name,
        items=order_data.items,
        total_price=order.total_price,
        status=order.status,
        order_date=order.order_date
    )

@app.get("/orders/", response_model=List[OrderOut])
async def get_user_orders(current_user: User = Depends(get_current_user)):
    """Get all orders for the current user"""
    orders = await Order.find(Order.user_id == current_user.id).to_list()
    
    return [
        OrderOut(
            id=order.id,
            user_id=order.user_id,
            restaurant_name=order.restaurant_name,
            items=[
                {"item_name": item.item_name, "quantity": item.quantity, "price": item.price}
                for item in order.items
            ],
            total_price=order.total_price,
            status=order.status,
            order_date=order.order_date
        ) for order in orders
    ]

@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order_by_id(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific order by ID"""
    from beanie import PydanticObjectId
    
    try:
        order = await Order.get(PydanticObjectId(order_id))
    except:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to current user
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to view this order")
    
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        restaurant_name=order.restaurant_name,
        items=[
            {"item_name": item.item_name, "quantity": item.quantity, "price": item.price}
            for item in order.items
        ],
        total_price=order.total_price,
        status=order.status,
        order_date=order.order_date
    )

# ==================== ADMIN DASHBOARD ENDPOINTS ====================

@app.get("/admin/stats", response_model=PlatformStatsOut)
async def get_admin_stats(current_admin: User = Depends(get_current_admin_user)):
    """
    V4.0: Get comprehensive business intelligence statistics (admin only).
    
    Returns:
    - Total users, orders, revenue
    - Today's orders and revenue
    - Active users (last 7 days)
    - Review statistics
    
    V4.0 Feature: Enhanced Business Intelligence Dashboard
    """
    try:
        from datetime import datetime, timedelta
        
        # Get total users
        total_users = await User.count()
        
        # Get all orders
        all_orders = await Order.find_all().to_list()
        total_orders = len(all_orders)
        total_revenue = sum(order.total_price for order in all_orders)
        
        # Calculate today's stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        orders_today = sum(1 for order in all_orders if order.order_date >= today_start)
        revenue_today = sum(order.total_price for order in all_orders if order.order_date >= today_start)
        
        # Calculate active users (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_user_ids = set(order.user_id for order in all_orders if order.order_date >= seven_days_ago)
        active_users_last_7_days = len(active_user_ids)
        
        # Get review statistics
        all_reviews = await Review.find_all().to_list()
        total_reviews = len(all_reviews)
        average_rating = sum(review.rating for review in all_reviews) / total_reviews if total_reviews > 0 else 0.0
        
        return PlatformStatsOut(
            total_users=total_users,
            total_orders=total_orders,
            total_revenue=round(total_revenue, 2),
            orders_today=orders_today,
            revenue_today=round(revenue_today, 2),
            active_users_last_7_days=active_users_last_7_days,
            total_reviews=total_reviews,
            average_rating=round(average_rating, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching admin stats: {str(e)}")

@app.get("/admin/orders", response_model=List[OrderOut])
async def get_all_orders_admin(current_admin: User = Depends(get_current_admin_user)):
    """
    Get all orders in the system (admin only).
    
    Returns complete order history for business analysis.
    
    V4.0 Feature: Admin Order Management
    """
    try:
        orders = await Order.find_all().to_list()
        
        return [
            OrderOut(
                id=order.id,
                user_id=order.user_id,
                restaurant_name=order.restaurant_name,
                items=[
                    {"item_name": item.item_name, "quantity": item.quantity, "price": item.price}
                    for item in order.items
                ],
                total_price=order.total_price,
                status=order.status,
                order_date=order.order_date
            ) for order in orders
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

@app.get("/admin/users")
async def get_all_users_admin(current_admin: User = Depends(get_current_admin_user)):
    """
    Get all registered users (admin only).
    
    Returns user list WITHOUT hashed passwords for security.
    
    V4.0 Feature: User Management Dashboard
    """
    try:
        users = await User.find_all().to_list()
        
        return [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            } for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """
    V4.0: API health check endpoint with database connectivity test.
    
    Used by Docker HEALTHCHECK and monitoring systems.
    """
    try:
        # Test database connection by counting users
        user_count = await User.count()
        database_status = "connected"
    except Exception as e:
        database_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "version": "4.0.0",
        "database": database_status,
        "features": ["reviews", "admin_dashboard", "ai_personalization", "docker"]
    }
