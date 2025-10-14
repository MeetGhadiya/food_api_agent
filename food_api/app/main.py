"""
FastAPI Main Application - FoodieExpress Backend
Enhanced with Reviews, Multi-Item Orders, Role-Based Access Control, and Cuisine Search
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import timedelta

# Local Imports
from .database import init_db
from .models import Restaurant, User, Order, Review, OrderItem
from .schemas import (
    RestaurantCreate, UserCreate, UserOut, OrderCreate, OrderOut,
    ReviewCreate, ReviewOut, RestaurantItem
)
from .security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .dependencies import get_current_user, get_current_admin_user

# Application Lifespan Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown events"""
    await init_db()
    print("✅ Database connection established.")
    yield
    print("🔌 Closing database connection.")

# Create FastAPI App
app = FastAPI(
    title="FoodieExpress API",
    description="AI-Powered Food Delivery Platform with Reviews & Advanced Features",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PUBLIC ENDPOINTS ====================

@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to FoodieExpress API!",
        "version": "2.0.0",
        "features": ["AI Chatbot", "Multi-Item Orders", "Reviews & Ratings", "Cuisine Search"]
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
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Submit a review for a restaurant (requires authentication).
    
    Parameters:
    - restaurant_name: Name of the restaurant
    - rating: 1-5 stars
    - comment: Review text
    """
    # Verify restaurant exists
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    # Validate rating
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check if user already reviewed this restaurant
    existing_review = await Review.find_one(
        Review.user_id == current_user.id,
        Review.restaurant_name == restaurant_name
    )
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this restaurant. Please update your existing review instead."
        )
    
    # Create review
    review = Review(
        user_id=current_user.id,
        restaurant_name=restaurant_name,
        rating=review_data.rating,
        comment=review_data.comment
    )
    await review.insert()
    
    return ReviewOut(
        id=review.id,
        user_id=review.user_id,
        restaurant_name=review.restaurant_name,
        rating=review.rating,
        comment=review.comment,
        review_date=review.review_date
    )

@app.get("/restaurants/{restaurant_name}/reviews", response_model=List[ReviewOut])
async def get_restaurant_reviews(restaurant_name: str):
    """
    Get all reviews for a specific restaurant (public endpoint).
    """
    # Verify restaurant exists
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    # Get all reviews
    reviews = await Review.find(Review.restaurant_name == restaurant_name).to_list()
    
    return [
        ReviewOut(
            id=review.id,
            user_id=review.user_id,
            restaurant_name=review.restaurant_name,
            rating=review.rating,
            comment=review.comment,
            review_date=review.review_date
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

@app.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user account"""
    # Check email uniqueness
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    
    # Check username uniqueness
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this username already exists")
    
    # Hash password
    hashed_pass = hash_password(user_data.password)
    
    # Create user with role (default: "user")
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pass,
        role=user_data.role if user_data.role else "user"
    )
    await user.insert()
    
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role
    )

@app.post("/users/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token"""
    user = await User.find_one(User.username == form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current logged-in user information"""
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role
    )

# ==================== ORDER MANAGEMENT ====================

@app.post("/orders/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new multi-item order (requires authentication).
    
    PHASE 2: ORDER PLACEMENT DEBUG & FIX
    
    Enhanced with detailed logging to debug order placement issues.
    """
    # PHASE 2: Detailed logging
    print("\n" + "="*60)
    print("🎯 FASTAPI: ORDER CREATION REQUEST")
    print("="*60)
    print(f"👤 User ID: {current_user.id}")
    print(f"👤 Username: {current_user.username}")
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
    
    # Create order
    order = Order(
        user_id=current_user.id,
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

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "connected"
    }
