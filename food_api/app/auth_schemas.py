"""
Pydantic Schemas for Authentication
====================================
Request and response models for auth endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    first_name: Optional[str] = Field(default="", min_length=0, max_length=50, description="First name (optional)")
    last_name: Optional[str] = Field(default="", min_length=0, max_length=50, description="Last name (optional)")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Ensure username is alphanumeric with underscores/hyphens only"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "first_name": "John",
                "last_name": "Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request"""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username_or_email": "john_doe",
                "password": "SecurePass123"
            }
        }


class UserRegisterResponse(BaseModel):
    """User registration response"""
    message: str
    user_id: str
    username: str
    email: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Registration successful! Welcome to FoodieExpress!",
                "user_id": "507f1f77bcf86cd799439011",
                "username": "john_doe",
                "email": "john@example.com"
            }
        }


class UserLoginResponse(BaseModel):
    """User login response"""
    message: str
    token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds
    user: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Login successful! Welcome back!",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "user_id": "507f1f77bcf86cd799439011",
                    "username": "john_doe",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            }
        }


class UserLogoutResponse(BaseModel):
    """User logout response"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Logout successful! See you soon!"
            }
        }


class TokenData(BaseModel):
    """Decoded token data"""
    user_id: str
    username: str
    exp: datetime
    iat: datetime
    type: str


class AuthErrorResponse(BaseModel):
    """Authentication error response"""
    detail: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials. Please check your username and password."
            }
        }
