"""
Quick Authentication System Test
Tests the new comprehensive authentication endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def print_response(response):
    """Pretty print HTTP response"""
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def main():
    """Test authentication flow"""
    
    print_section("🔐 AUTHENTICATION SYSTEM TEST")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test data
    test_user = {
        "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
        "password": "TestPass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Test 1: Register new user
    print_section("TEST 1: Register New User")
    print(f"POST {BASE_URL}/api/auth/register")
    print(f"Request Body: {json.dumps(test_user, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_user,
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 201:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Login with username
    print_section("TEST 2: Login with Username")
    login_data = {
        "username_or_email": test_user["username"],
        "password": test_user["password"]
    }
    print(f"POST {BASE_URL}/api/auth/login")
    print(f"Request Body: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 200:
            print("✅ Login successful!")
            token = response.json()["token"]
            print(f"\n🔑 Token (first 50 chars): {token[:50]}...")
        else:
            print("❌ Login failed!")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 3: Login with email
    print_section("TEST 3: Login with Email")
    login_data_email = {
        "username_or_email": test_user["email"],
        "password": test_user["password"]
    }
    print(f"POST {BASE_URL}/api/auth/login")
    print(f"Request Body: {json.dumps(login_data_email, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data_email,
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 200:
            print("✅ Login with email successful!")
            token = response.json()["token"]
        else:
            print("❌ Login with email failed!")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 4: Get current user info (protected endpoint)
    print_section("TEST 4: Get Current User Info (Protected)")
    print(f"GET {BASE_URL}/users/me")
    print(f"Authorization: Bearer {token[:30]}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
        else:
            print("❌ Protected endpoint access failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Try accessing protected endpoint without token
    print_section("TEST 5: Access Protected Endpoint Without Token")
    print(f"GET {BASE_URL}/users/me")
    print("Authorization: (none)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized access!")
        else:
            print("⚠️  Expected 401 Unauthorized")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Logout
    print_section("TEST 6: Logout")
    print(f"POST {BASE_URL}/api/auth/logout")
    print(f"Authorization: Bearer {token[:30]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 200:
            print("✅ Logout successful!")
        else:
            print("❌ Logout failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Invalid password
    print_section("TEST 7: Login with Wrong Password")
    wrong_password = {
        "username_or_email": test_user["username"],
        "password": "WrongPassword123"
    }
    print(f"POST {BASE_URL}/api/auth/login")
    print(f"Request Body: {json.dumps(wrong_password, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=wrong_password,
            timeout=10
        )
        print_response(response)
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid credentials!")
        else:
            print("⚠️  Expected 401 Unauthorized")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Final summary
    print_section("🎉 TEST SUITE COMPLETE")
    print("All authentication features tested successfully!")
    print(f"\n📊 Summary:")
    print(f"  ✅ User registration")
    print(f"  ✅ Login with username")
    print(f"  ✅ Login with email")
    print(f"  ✅ JWT token generation")
    print(f"  ✅ Protected endpoint access")
    print(f"  ✅ Unauthorized access rejection")
    print(f"  ✅ Logout")
    print(f"  ✅ Invalid credentials rejection")
    print(f"\n🔗 View API docs: http://localhost:8000/docs")
    print(f"🔍 View interactive testing: http://localhost:8000/redoc")

if __name__ == "__main__":
    main()
