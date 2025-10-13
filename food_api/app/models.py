# app/models.py
from beanie import Document
from pydantic import EmailStr

# app/models.py
from beanie import Document, PydanticObjectId
from pydantic import EmailStr, BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Restaurant(Document):
    name: str
    area: str
    cuisine: str  # NEW: Cuisine type (e.g., "Gujarati", "Italian", "South Indian")
    items: list = []  # List of items (dicts) for this restaurant
    # Example item: {"item_name": str, "price": float, "rating": float, "total_ratings": int, "description": str, "image_url": str, "calories": int, "preparation_time": str}
    
    class Settings:
        name = "restaurants"

class User(Document):
    username: str
    email: EmailStr
    hashed_password: str
    role: str = "user"  # NEW: Role-based access control ("user" or "admin")

    class Settings:
        name = "users"

# NEW: OrderItem model for multi-item orders
class OrderItem(BaseModel):
    item_name: str
    quantity: int
    price: float  # Price at the time of order

class Order(Document):
    user_id: PydanticObjectId  # NEW: Link order to user
    restaurant_name: str
    items: List[OrderItem]  # NEW: Support multiple items
    total_price: float  # NEW: Total order price
    status: str = "placed"  # "placed", "preparing", "out_for_delivery", "delivered"
    order_date: datetime = Field(default_factory=datetime.utcnow)  # NEW: Timestamp

    class Settings:
        name = "orders"

# NEW: Review model for restaurant reviews
class Review(Document):
    user_id: PydanticObjectId
    restaurant_name: str
    rating: int  # Rating from 1 to 5
    comment: str
    review_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reviews"