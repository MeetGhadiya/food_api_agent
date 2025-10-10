# app/models.py
from beanie import Document
from pydantic import EmailStr

# app/models.py
from beanie import Document
from pydantic import EmailStr
from typing import Optional

class Restaurant(Document):
    name: str
    area: str
    cuisine: str  # This will be renamed to item_name in future
    item_name: Optional[str] = None  # New field for item name
    price: Optional[float] = None  # Price in rupees
    rating: Optional[float] = None  # Rating out of 5
    total_ratings: Optional[int] = None  # Number of ratings
    description: Optional[str] = None  # Item description
    image_url: Optional[str] = None  # Image URL
    calories: Optional[int] = None  # Calories
    preparation_time: Optional[str] = None  # e.g., "30-40 mins"
    
    class Settings:
        name = "restaurants" # This is the collection name in MongoDB

class User(Document):
    username: str
    email: EmailStr
    hashed_password: str

    class Settings:
        name = "users"
    
class Order(Document):
    restaurant_name: str
    item: str
    quantity: int = 1
    status: str = "placed"

    class Settings:
        name = "orders"