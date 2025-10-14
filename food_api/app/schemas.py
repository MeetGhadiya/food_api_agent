"""
Pydantic Schemas for Request/Response Validation
Enhanced with strict input validation and security controls

SECURITY FIXES:
- [HIGH-003] Added comprehensive input validation using Pydantic Field constraints
- Added length limits, range validation, and type constraints
- Enhanced security against XSS, injection, and data manipulation attacks
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from beanie import PydanticObjectId
from typing import Optional, List
from datetime import datetime
import re

class RestaurantItem(BaseModel):
    """Individual menu item schema with validation"""
    item_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the menu item"
    )
    price: Optional[float] = Field(
        None,
        ge=0,
        le=10000,
        description="Price in rupees (0-10000)"
    )
    rating: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Item rating (0-5 stars)"
    )
    total_ratings: Optional[int] = Field(
        None,
        ge=0,
        description="Total number of ratings"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Item description"
    )
    image_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to item image"
    )
    calories: Optional[int] = Field(
        None,
        ge=0,
        le=5000,
        description="Calorie count"
    )
    preparation_time: Optional[str] = Field(
        None,
        max_length=50,
        description="Estimated preparation time"
    )

class RestaurantCreate(BaseModel):
    """Restaurant creation/update schema with validation"""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Restaurant name"
    )
    area: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Restaurant location/area"
    )
    cuisine: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Type of cuisine"
    )
    items: list[RestaurantItem] = Field(
        default=[],
        max_length=200,
        description="Menu items (max 200)"
    )

# ==================== USER SCHEMAS ====================

class UserCreate(BaseModel):
    """User registration schema with strict validation"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Username (3-30 chars, alphanumeric, underscore, hyphen only)"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters)"
    )
    role: Optional[str] = Field(
        default="user",
        pattern="^(user|admin)$",
        description="User role (user or admin)"
    )
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements:
        - At least 8 characters
        - Contains at least one letter
        - Contains at least one number
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Za-z]', v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one number")
        return v

class UserOut(BaseModel):
    """User output schema (excludes sensitive data)"""
    id: PydanticObjectId
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

# ==================== ORDER SCHEMAS ====================

class OrderItemCreate(BaseModel):
    """Order item schema with validation to prevent manipulation"""
    item_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the item being ordered"
    )
    quantity: int = Field(
        ...,
        ge=1,
        le=100,
        description="Quantity (1-100 items)"
    )
    price: float = Field(
        ...,
        ge=0,
        le=10000,
        description="Price per item (0-10000 rupees)"
    )
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Ensure quantity is positive and reasonable"""
        if v <= 0:
            raise ValueError("Quantity must be at least 1")
        if v > 100:
            raise ValueError("Maximum quantity per item is 100")
        return v

class OrderCreate(BaseModel):
    """Order creation schema with validation"""
    restaurant_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the restaurant"
    )
    items: List[OrderItemCreate] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Order items (1-50 items per order)"
    )
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[OrderItemCreate]) -> List[OrderItemCreate]:
        """Ensure order has at least one item"""
        if not v:
            raise ValueError("Order must contain at least one item")
        return v

class OrderOut(BaseModel):
    """Order output schema"""
    id: PydanticObjectId
    user_id: PydanticObjectId
    restaurant_name: str
    items: List[OrderItemCreate]
    total_price: float
    status: str
    order_date: datetime

    class Config:
        from_attributes = True

# ==================== REVIEW SCHEMAS ====================

class ReviewCreate(BaseModel):
    """
    Review creation schema with strict validation
    
    SECURITY FIXES:
    - [HIGH-003] Added rating range validation (1-5)
    - Added maximum comment length to prevent abuse
    - Added XSS protection through field validation
    """
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating from 1 to 5 stars"
    )
    comment: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Review comment (10-500 characters)"
    )
    
    @field_validator('comment')
    @classmethod
    def sanitize_comment(cls, v: str) -> str:
        """
        Sanitize review comment to prevent XSS attacks
        Remove potentially dangerous HTML/script tags
        """
        # Remove common XSS patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
        ]
        
        sanitized = v
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags but keep the content
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        return sanitized.strip()

class ReviewOut(BaseModel):
    """Review output schema"""
    id: PydanticObjectId
    user_id: PydanticObjectId
    restaurant_name: str
    rating: int
    comment: str
    review_date: datetime

    class Config:
        from_attributes = True
