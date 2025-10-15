"""
V4.0: Script to promote a user to admin role
Usage: python make_admin.py --email user@example.com
       python make_admin.py --username john_doe
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import User
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/food_db")

async def make_admin(email: str = None, username: str = None):
    """Promote a user to admin role"""
    
    # Connect to database
    client = AsyncIOMotorClient(MONGODB_URI)
    db_name = MONGODB_URI.split("/")[-1].split("?")[0]
    db = client[db_name]
    
    await init_beanie(database=db, document_models=[User])
    
    # Find user
    if email:
        user = await User.find_one(User.email == email)
        identifier = f"email '{email}'"
    elif username:
        user = await User.find_one(User.username == username)
        identifier = f"username '{username}'"
    else:
        print("❌ Error: Please provide either --email or --username")
        return
    
    if not user:
        print(f"❌ User with {identifier} not found")
        return
    
    if user.role == "admin":
        print(f"ℹ️  User {user.username} is already an admin")
        return
    
    # Promote to admin
    user.role = "admin"
    await user.save()
    
    print(f"✅ Successfully promoted user '{user.username}' ({user.email}) to admin role!")
    print(f"   User ID: {user.id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promote a user to admin role")
    parser.add_argument("--email", type=str, help="User's email address")
    parser.add_argument("--username", type=str, help="User's username")
    
    args = parser.parse_args()
    
    if not args.email and not args.username:
        print("❌ Error: Please provide either --email or --username")
        parser.print_help()
        sys.exit(1)
    
    asyncio.run(make_admin(email=args.email, username=args.username))
