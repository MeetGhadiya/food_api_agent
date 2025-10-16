"""
Check FoodieExpress API Status
Verifies that all required services are running before executing tests

Usage:
    python check_api_status.py
"""

import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("food_api/.env")


def check_api():
    """Check if FastAPI is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ FastAPI is running - {data.get('name', 'FoodieExpress')} v{data.get('version', '?')}")
            return True
        else:
            print(f"⚠️  FastAPI responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI is NOT running - Cannot connect to http://localhost:8000/")
        print("   → Start the API with: cd food_api && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error checking FastAPI: {str(e)}")
        return False


def check_mongodb():
    """Check if MongoDB is configured and accessible"""
    # Get MongoDB URL from environment
    mongo_url = os.getenv("MONGODB_URI") or os.getenv("MONGO_DATABASE_URL")
    
    if not mongo_url:
        print("❌ MongoDB connection string not found in environment variables")
        print("   → Set MONGODB_URI in food_api/.env file")
        return False
    
    # Check if using placeholder credentials
    if "{{" in mongo_url or "YOUR_PASSWORD" in mongo_url or "%7B%7B" in mongo_url:
        print("⚠️  MongoDB connection string contains placeholder credentials")
        print("   → Update MONGODB_URI in food_api/.env with actual credentials")
        print("   → Current: MONGODB_URI contains {{Your_Database_Password}}")
        print("   → Replace with your actual MongoDB Atlas password")
        return False
    
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        print("✅ MongoDB is running and accessible")
        
        # Check databases
        try:
            databases = client.list_database_names()
            if "food_db" in databases:
                print("   → Production database 'food_db' exists")
            if "test_foodie_express" in databases:
                print("   → Test database 'test_foodie_express' exists")
        except:
            pass  # Permission issues are OK
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed")
        print(f"   Error: {str(e)}")
        print("   → Verify MongoDB Atlas credentials in food_api/.env")
        print("   → Check network connectivity to MongoDB Atlas")
        return False


def check_all_services():
    """Check all required services"""
    print("\n" + "="*80)
    print("  FOODIEEXPRESS - SERVICE STATUS CHECK")
    print("="*80 + "\n")
    
    api_ok = check_api()
    print()
    mongodb_ok = check_mongodb()
    
    print("\n" + "="*80)
    if api_ok and mongodb_ok:
        print("  ✅ ALL SERVICES RUNNING - Ready to run tests")
        print("="*80 + "\n")
        print("Next steps:")
        print("  1. Run smoke tests:        python quick_smoke_test.py")
        print("  2. Run all tests:          python run_comprehensive_tests_v3.py")
        print("  3. Run with coverage:      python run_comprehensive_tests_v3.py --coverage")
        return 0
    else:
        print("  ❌ SOME SERVICES NOT RUNNING - Fix issues before running tests")
        print("="*80 + "\n")
        
        if not mongodb_ok:
            print("To start MongoDB:")
            print("  - Windows: net start MongoDB")
            print("  - Or use MongoDB Compass")
            print()
        
        if not api_ok:
            print("To start the API:")
            print("  cd food_api")
            print("  uvicorn app.main:app --reload")
            print()
        
        return 1


if __name__ == "__main__":
    sys.exit(check_all_services())
