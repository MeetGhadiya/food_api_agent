# app/models.py
from beanie import Document
from pydantic import EmailStr

class Restaurant(Document):
    name: str
    area: str
    cuisine: str
    
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