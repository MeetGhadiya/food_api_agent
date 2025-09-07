from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId # Import this

class RestaurantCreate(BaseModel):
    name: str
    area: str
    cuisine: str

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
