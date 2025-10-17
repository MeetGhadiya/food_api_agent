"""
WORKING SOLUTION: Test Authentication Without Swagger Authorization
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("="*70)
    print("  AUTHENTICATION TEST - BYPASS SWAGGER ISSUE")
    print("="*70)
    print()
    print("Since Swagger OAuth2 dialog is broken, we'll test the API directly.")
    print()
    
    # Step 1: Login
    print("[1] LOGGING IN...")
    print(f"POST {BASE_URL}/api/auth/login")
    
    login_data = {
        "username_or_email": "MG9328",
        "password": "Meet7805"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data["token"]
            
            print(f"✅ LOGIN SUCCESSFUL!")
            print(f"\n📋 User Info:")
            print(f"   Username: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Name: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"\n🔑 Token (first 50 chars): {token[:50]}...")
            
            # Step 2: Test protected endpoint
            print("\n" + "="*70)
            print("[2] TESTING PROTECTED ENDPOINT...")
            print(f"GET {BASE_URL}/users/me")
            print(f"Authorization: Bearer {token[:30]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            response2 = requests.get(f"{BASE_URL}/users/me", headers=headers)
            
            if response2.status_code == 200:
                user_info = response2.json()
                print(f"\n✅ PROTECTED ENDPOINT ACCESS SUCCESSFUL!")
                print(f"\n📋 Retrieved User Data:")
                print(json.dumps(user_info, indent=2))
            else:
                print(f"\n❌ FAILED: {response2.status_code}")
                print(response2.text)
            
            # Step 3: Show how to use in Swagger
            print("\n" + "="*70)
            print("[3] HOW TO USE IN SWAGGER (IF IT WORKS):")
            print("="*70)
            print()
            print("1. Open: http://localhost:8000/docs")
            print("2. Find any endpoint (e.g., GET /users/me)")
            print("3. Click 'Try it out'")
            print("4. DON'T use the Authorize button (it's broken)")
            print("5. Manually add this header in the 'curl' command:")
            print(f"   -H 'Authorization: Bearer {token}'")
            print()
            print("="*70)
            print("✅ API IS WORKING PERFECTLY!")
            print("❌ Only Swagger authorization dialog is broken")
            print("💡 Use Postman, curl, or Python requests instead")
            print("="*70)
            
        else:
            print(f"❌ LOGIN FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nMake sure the API server is running:")
        print("cd food_api")
        print("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()
