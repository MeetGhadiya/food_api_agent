"""
Diagnostic Script - Test Registration Issue
============================================
This script helps diagnose why registration is failing
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_backend_health():
    """Test if backend is accessible"""
    print("="*60)
    print("TEST 1: Backend Health Check")
    print("="*60)
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ Backend is running: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("\n" + "="*60)
    print("TEST 2: User Registration")
    print("="*60)
    
    # Test data
    user_data = {
        "username": "TestUser" + str(hash("test") % 1000),  # Random username
        "email": f"test{hash('test') % 1000}@example.com",
        "password": "TestPass123!"
    }
    
    print(f"Attempting to register user: {user_data['username']}")
    print(f"Email: {user_data['email']}")
    
    try:
        response = requests.post(
            f"{API_URL}/users/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return True
        elif response.status_code == 400:
            print("⚠️  User already exists or validation error")
            print(f"   Details: {response.json()}")
            return False
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return False

def test_existing_user_registration():
    """Test registering with username from screenshot"""
    print("\n" + "="*60)
    print("TEST 3: Registration with Your Credentials")
    print("="*60)
    
    user_data = {
        "username": "MG9328",
        "email": "mitg7805@gmail.com",
        "password": "Meet@123"
    }
    
    print(f"Testing registration with username: {user_data['username']}")
    
    try:
        response = requests.post(
            f"{API_URL}/users/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            print("\nYou can now log in with:")
            print(f"   Username: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
            return True
        elif response.status_code == 400:
            error_detail = response.json().get('detail', 'Unknown error')
            if 'already exists' in error_detail:
                print("✅ User already exists! You can try logging in instead.")
                print("\nTry these credentials:")
                print(f"   Username: {user_data['username']}")
                print(f"   Password: {user_data['password']}")
                return "EXISTS"
            else:
                print(f"⚠️  Registration failed: {error_detail}")
                return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            try:
                print(f"   Details: {response.json()}")
            except:
                print(f"   Raw: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """Test login with the credentials"""
    print("\n" + "="*60)
    print("TEST 4: Login Test")
    print("="*60)
    
    credentials = {
        "username": "MG9328",
        "password": "Meet@123"
    }
    
    print(f"Attempting login with username: {credentials['username']}")
    
    try:
        response = requests.post(
            f"{API_URL}/users/login",
            data=credentials  # OAuth2 expects form data, not JSON
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"\nAccess Token: {token_data.get('access_token', '')[:50]}...")
            return True
        else:
            print(f"❌ Login failed")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Raw: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during login: {e}")
        return False

def main():
    print("\n" + "🔍 " + "="*56)
    print("   FOODIEEXPRESS REGISTRATION DIAGNOSTIC TOOL")
    print("="*58 + "\n")
    
    # Run tests
    if not test_backend_health():
        print("\n⚠️  Backend is not running!")
        print("   Start it with: cd food_api && python -m uvicorn app.main:app --reload")
        return
    
    # Test registration with new user
    test_registration()
    
    # Test with user from screenshot
    result = test_existing_user_registration()
    
    # If user exists or just registered, test login
    if result == "EXISTS" or result == True:
        test_login()
    
    print("\n" + "="*58)
    print("📊 DIAGNOSIS COMPLETE")
    print("="*58 + "\n")
    
    print("💡 NEXT STEPS:")
    print("   1. If user already exists → Try logging in")
    print("   2. If registration works → Use the new credentials")
    print("   3. If errors persist → Check backend logs")
    print("\n")

if __name__ == "__main__":
    main()
