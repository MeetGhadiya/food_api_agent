"""
Security Module - Password Hashing and JWT Token Management
Enhanced with environment variable security and proper configuration

SECURITY FIXES:
- [CRITICAL-002] Removed hardcoded JWT secret key
- [MEDIUM-001] Removed unused 'os' import (now used for environment variables)
- Added proper environment variable validation
- Enhanced security documentation
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== PASSWORD HASHING ====================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== JWT CONFIGURATION ====================
# CRITICAL-002 FIX: Load secret key from environment
# SECURITY: Never hardcode secrets! Generate with: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "❌ CRITICAL ERROR: SECRET_KEY not found in environment variables!\n"
        "Generate a secure key with: openssl rand -hex 32\n"
        "Then add it to your .env file: SECRET_KEY=<generated_key>\n"
        "See .env.example for more details."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hashes a plain-text password. Truncates to 72 bytes to comply with bcrypt limit."""
    # Bcrypt has a 72 byte limit, so we truncate if necessary
    # Encoding to bytes and truncating ensures we don't split a multi-byte character
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        plain_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt