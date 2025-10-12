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
    items: list = []  # List of items (dicts) for this restaurant
    # Example item: {"item_name": str, "price": float, "rating": float, "total_ratings": int, "description": str, "image_url": str, "calories": int, "preparation_time": str}
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