"""
Test the Legacy /users/login Endpoint Fix
This tests that the OAuth2 Swagger dialog now works correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_legacy_login():
    """Test the /users/login endpoint that Swagger OAuth2 uses"""
    print("="*70)
    print("  TESTING /users/login ENDPOINT (OAuth2 Swagger)")
    print("="*70)
    print()
    
    # This is the format Swagger OAuth2 sends (form data, not JSON)
    form_data = {
        "username": "MG9328",
        "password": "Meet7805",
        "grant_type": "password"  # OAuth2 requirement
    }
    
    print(f"POST {BASE_URL}/users/login")
    print(f"Form Data: {form_data}")
    print()
    
    try:
        # Send as form data (application/x-www-form-urlencoded)
        response = requests.post(
            f"{BASE_URL}/users/login",
            data=form_data,  # Use 'data' not 'json' for form encoding
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! The /users/login endpoint works!")
            print()
            print("Response:")
            print(json.dumps(data, indent=2))
            print()
            print("="*70)
            print("  SWAGGER OAUTH2 SHOULD NOW WORK!")
            print("="*70)
            print()
            print("1. Go to: http://localhost:8000/docs")
            print("2. Click 'Authorize' button")
            print("3. Enter:")
            print("   - username: MG9328")
            print("   - password: Meet7805")
            print("4. Click 'Authorize'")
            print("5. It should work now!")
            print()
            return True
        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_new_login():
    """Test the new /api/auth/login endpoint"""
    print("="*70)
    print("  TESTING /api/auth/login ENDPOINT (New)")
    print("="*70)
    print()
    
    login_data = {
        "username_or_email": "MG9328",
        "password": "Meet7805"
    }
    
    print(f"POST {BASE_URL}/api/auth/login")
    print(f"JSON Data: {login_data}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,  # JSON format
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! The /api/auth/login endpoint works!")
            print()
            print("Response:")
            print(json.dumps(data, indent=2))
            print()
            return True
        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  COMPREHENSIVE LOGIN ENDPOINT TEST")
    print("="*70)
    print()
    
    # Test both endpoints
    legacy_works = test_legacy_login()
    print()
    new_works = test_new_login()
    
    print()
    print("="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"Legacy /users/login (OAuth2):  {'✅ PASS' if legacy_works else '❌ FAIL'}")
    print(f"New /api/auth/login (JSON):     {'✅ PASS' if new_works else '❌ FAIL'}")
    print("="*70)
    
    if legacy_works and new_works:
        print()
        print("🎉 ALL TESTS PASSED!")
        print("   - OAuth2 Swagger dialog should work now")
        print("   - New authentication system also works")
        print()
    else:
        print()
        print("⚠️  SOME TESTS FAILED - Check server logs")
        print()

if __name__ == "__main__":
    main()
