"""
Test login with existing user credentials
Username: MG9328
Password: Meet7805
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login with MG9328 user"""
    print("="*70)
    print("  TESTING LOGIN WITH EXISTING USER")
    print("="*70)
    
    # Login data
    login_data = {
        "username_or_email": "MG9328",
        "password": "Meet7805"
    }
    
    print(f"\n📝 Login Request:")
    print(f"POST {BASE_URL}/api/auth/login")
    print(json.dumps(login_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"\n📊 Response:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            print(f"\n✅ LOGIN SUCCESSFUL!")
            print(f"\n🔑 Your Bearer Token (copy this for Swagger):")
            print(f"Bearer {data['token']}")
            print(f"\n📋 To use in Swagger:")
            print(f"1. Go to http://localhost:8000/docs")
            print(f"2. Click 'Authorize' button (top-right)")
            print(f"3. Paste this token: Bearer {data['token']}")
            print(f"4. Click 'Authorize' and then 'Close'")
            return data['token']
        else:
            print(json.dumps(response.json(), indent=2))
            print(f"\n❌ LOGIN FAILED!")
            
            # If user doesn't exist, check if we need to register
            if response.status_code == 401:
                print(f"\n💡 User might not exist in new database.")
                print(f"Let me try to register this user first...")
                register_user()
    
    except Exception as e:
        print(f"❌ Error: {e}")

def register_user():
    """Register MG9328 user if doesn't exist"""
    print("\n" + "="*70)
    print("  REGISTERING USER")
    print("="*70)
    
    register_data = {
        "username": "MG9328",
        "email": "mitg7805@gmail.com",
        "password": "Meet7805",
        "first_name": "Meet",
        "last_name": "Ghadiya"
    }
    
    print(f"\n📝 Registration Request:")
    print(f"POST {BASE_URL}/api/auth/register")
    print(json.dumps(register_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=register_data,
            timeout=10
        )
        
        print(f"\n📊 Response:")
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 201:
            print(f"\n✅ REGISTRATION SUCCESSFUL!")
            print(f"\nNow trying to login...")
            test_login()
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"\n⚠️  User already exists!")
            print(f"Password might be different in database.")
            print(f"Trying with the old hashed password from database...")
        else:
            print(f"\n❌ REGISTRATION FAILED!")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
