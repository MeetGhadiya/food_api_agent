from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId # Import this
from typing import Optional

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
    items: list[RestaurantItem] = []

# --- Add the User Schemas Below ---

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: PydanticObjectId
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # This allows the model to work with database objects

class OrderCreate(BaseModel):
    restaurant_name: str
    item: str
