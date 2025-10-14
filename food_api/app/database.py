"""
Database Configuration Module
Enhanced with environment variable security and proper error handling

SECURITY FIXES:
- [CRITICAL-001] Removed hardcoded MongoDB credentials
- [CRITICAL-003] Removed insecure TLS configuration (tlsAllowInvalidCertificates)
- Added proper environment variable validation
- Enhanced error handling and startup checks
"""

import motor.motor_asyncio
from beanie import init_beanie
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== SECURITY: ENVIRONMENT VARIABLES ====================
# CRITICAL-001 FIX: Load database URL from environment
MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL")

if not MONGO_DATABASE_URL:
    raise ValueError(
        "❌ CRITICAL ERROR: MONGO_DATABASE_URL not found in environment variables!\n"
        "Please set MONGO_DATABASE_URL in your .env file.\n"
        "See .env.example for the required format."
    )

# ==================== DATABASE CONNECTION ====================
# CRITICAL-003 FIX: Removed tlsAllowInvalidCertificates=True (insecure!)
# If you encounter SSL certificate issues:
# 1. Update certifi package: pip install --upgrade certifi
# 2. Ensure you're using the correct MongoDB Atlas connection string
# 3. Only use tlsAllowInvalidCertificates in local development (never production)

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGO_DATABASE_URL, 
        uuidRepresentation="standard",
        serverSelectionTimeoutMS=5000
    )
    database = client.food_db
    print("✅ MongoDB client initialized successfully")
except Exception as e:
    print(f"❌ WARNING: Could not connect to MongoDB: {e}")
    print("⚠️  Application will start with limited functionality")
    client = None
    database = None

async def init_db():
    if database is not None:
        try:
            await init_beanie(
                database=database,
                document_models=[
                    "app.models.User",
                    "app.models.Restaurant",
                    "app.models.Order",
                    "app.models.Review",  # NEW: Add Review model
                ]
            )
            print("✅ Database connection established.")
        except Exception as e:
            print(f"⚠️  WARNING: Could not initialize database: {e}")
            print("⚠️  Running without database - API will have limited functionality")
    else:
        print("⚠️  WARNING: Running without database - API will have limited functionality")
