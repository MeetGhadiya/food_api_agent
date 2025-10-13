from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from typing import Optional, List
from datetime import datetime

class RestaurantItem(BaseModel):
    item_name: str
    price: Optional[float] = None
    rating: Optional[float] = None
    total_ratings: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    calories: Optional[int] = None
    preparation_time: Optional[str] = None

class RestaurantCreate(BaseModel):
    name: str
    area: str
    cuisine: str  # NEW: Cuisine field
    items: list[RestaurantItem] = []

# --- User Schemas ---

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"  # NEW: Optional role field (default: "user")

class UserOut(BaseModel):
    id: PydanticObjectId
    username: str
    email: EmailStr
    role: str  # NEW: Include role in output

    class Config:
        from_attributes = True

# --- Order Schemas ---

class OrderItemCreate(BaseModel):
    item_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    restaurant_name: str
    items: List[OrderItemCreate]  # NEW: Support multiple items

class OrderOut(BaseModel):
    id: PydanticObjectId
    user_id: PydanticObjectId
    restaurant_name: str
    items: List[OrderItemCreate]
    total_price: float
    status: str
    order_date: datetime

    class Config:
        from_attributes = True

# --- Review Schemas ---

class ReviewCreate(BaseModel):
    rating: int  # 1-5 stars
    comment: str

class ReviewOut(BaseModel):
    id: PydanticObjectId
    user_id: PydanticObjectId
    restaurant_name: str
    rating: int
    comment: str
    review_date: datetime

    class Config:
        from_attributes = True
