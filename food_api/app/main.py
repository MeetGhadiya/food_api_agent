# Import necessary modules from FastAPI and standard Python libraries
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
from datetime import timedelta

# --- Local Imports ---
# Import components from other files in the application
from .database import init_db
from .models import Restaurant, User
from .schemas import RestaurantCreate, UserCreate, UserOut
from .security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .dependencies import get_current_user

from .models import Restaurant, User, Order
from .schemas import RestaurantCreate, UserCreate, UserOut, OrderCreate
from typing import List # Make sure List is imported from typing

# --- Application Lifespan (for startup and shutdown events) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    This function is executed when the application starts.
    """
    # Initialize the database connection when the app starts
    await init_db()
    print("Database connection established.")
    # The 'yield' keyword passes control back to the application to run
    yield
    # Code after 'yield' would run on application shutdown
    print("Closing database connection.")

# Create the main FastAPI application instance
# The lifespan manager is attached to handle startup/shutdown logic.
app = FastAPI(title="Food Delivery API", lifespan=lifespan)

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Public Endpoints (No Login Required) ---

@app.get("/")
def read_root():
    """Provides a simple welcome message at the root URL."""
    return {"message": "Welcome to the Food Delivery API!"}

from .schemas import RestaurantCreate, UserCreate, UserOut, OrderCreate, RestaurantItem

@app.get("/restaurants/", response_model=List[RestaurantCreate])
async def get_all_restaurants():
    """
    Retrieves and returns a list of all restaurants from the database.
    This endpoint is public and does not require authentication.
    """
    restaurants = await Restaurant.find_all().to_list()
    return [RestaurantCreate(name=r.name, area=r.area, items=r.items) for r in restaurants]

@app.get("/restaurants/{restaurant_name}", response_model=RestaurantCreate)
async def get_restaurant_by_name(restaurant_name: str):
    """
    Retrieves a single restaurant by its unique name using a path parameter.
    """
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return RestaurantCreate(name=restaurant.name, area=restaurant.area, items=restaurant.items)

# --- Protected Restaurant Endpoints (Login Required) ---

@app.post("/restaurants/", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate, 
    current_user: User = Depends(get_current_user) # Dependency: Enforces user authentication
):
    """
    Creates a new restaurant. A valid JWT is required to access this endpoint.
    The `get_current_user` dependency ensures only logged-in users can proceed.
    """
    # Create a new Restaurant model instance from the request data
    restaurant = Restaurant(**restaurant_data.dict())
    # Insert the new restaurant into the database
    await restaurant.insert()
    return restaurant

@app.put("/restaurants/{restaurant_name}", response_model=Restaurant)
async def update_restaurant_by_name(
    restaurant_name: str, 
    update_data: RestaurantCreate, 
    current_user: User = Depends(get_current_user) # Dependency: Enforces user authentication
):
    """
    Updates an existing restaurant's details. Requires authentication.
    """
    # Find the existing restaurant by its name
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant.name = update_data.name
    restaurant.area = update_data.area
    restaurant.items = update_data.items
    await restaurant.save()
    return restaurant

@app.delete("/restaurants/{restaurant_name}", response_model=dict)
async def delete_restaurant_by_name(
    restaurant_name: str, 
    current_user: User = Depends(get_current_user) # Dependency: Enforces user authentication
):
    """
    Deletes a restaurant by its name. Requires authentication.
    """
    # Find the restaurant to be deleted
    restaurant = await Restaurant.find_one(Restaurant.name == restaurant_name)
    # If not found, return a 404 error
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Delete the restaurant document from the database
    await restaurant.delete()
    return {"message": "Restaurant deleted successfully"}

# --- User Authentication Endpoints ---

@app.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Registers a new user account in the system.
    """
    # Check if a user with the same email already exists to prevent duplicates
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
  

    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(status_code=401, detail="An account with this username already exists.")
    

    # Hash the plain-text password before storing it
    hashed_pass = hash_password(user_data.password)
    # Create a new User model instance
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pass
    )
    # Insert the new user into the database
    await user.insert()
    # Return the user data (without the password) using the UserOut schema
    return user

@app.post("/users/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT access token upon success.
    """
    # Find the user by their username (as per previous instructions)
    user = await User.find_one(User.username == form_data.username)
    # If user doesn't exist or password doesn't match, raise a 401 Unauthorized error
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Set the token's expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create the JWT, embedding the username in the "sub" (subject) claim
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Return the token to the client
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/orders/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user) # This action requires a logged-in user
):
    """Creates a new food order."""
    # In a real app, you'd check if the restaurant and item exist
    order = Order(
        restaurant_name=order_data.restaurant_name,
        item=order_data.item,
        # You could add more logic here, like associating the order with the current_user
    )
    await order.insert()
    return order  

@app.get("/orders/", response_model=List[Order])
async def get_all_orders(current_user: User = Depends(get_current_user)):
    """Retrieve a list of all orders."""
    orders = await Order.find_all().to_list()
    return orders