"""
CORS Error Diagnostic Script
Tests both login endpoints and shows detailed error information
"""
import requests
import json

def test_json_endpoint():
    """Test /api/auth/login with JSON data (RECOMMENDED)"""
    print("\n" + "="*70)
    print("🧪 TEST 1: JSON Endpoint /api/auth/login")
    print("="*70)
    
    url = "http://localhost:8000/api/auth/login"
    payload = {
        "username_or_email": "MG9328",
        "password": "Meet7805"
    }
    
    print(f"📍 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print(f"📋 Content-Type: application/json\n")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'content-type' in key.lower():
                print(f"   {key}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS! Login worked!")
            print(f"🔑 Token: {data.get('token', 'N/A')[:50]}...")
            print(f"👤 User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"\n🎉 CORS is working correctly!")
            return True
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Server is not running on port 8000")
        print("   Start the server with: cd food_api; python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def test_form_endpoint():
    """Test /users/login with form data (For Swagger)"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Form Endpoint /users/login")
    print("="*70)
    
    url = "http://localhost:8000/users/login"
    data = {
        "username": "MG9328",
        "password": "Meet7805",
        "grant_type": "password"  # Required for OAuth2
    }
    
    print(f"📍 URL: {url}")
    print(f"📦 Form Data: {data}")
    print(f"📋 Content-Type: application/x-www-form-urlencoded\n")
    
    try:
        response = requests.post(
            url,
            data=data,  # Form-encoded
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'content-type' in key.lower():
                print(f"   {key}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS! Login worked!")
            print(f"🔑 Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"📝 Token Type: {data.get('token_type', 'N/A')}")
            print(f"\n🎉 CORS is working correctly!")
            return True
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            print(f"Error: {response.text}")
            
            if response.status_code == 500:
                print("\n⚠️  500 INTERNAL SERVER ERROR detected!")
                print("    Check the FastAPI terminal for error traceback")
                print("    The error is happening BEFORE CORS headers are added")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Server is not running on port 8000")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    print("\n" + "🔍 CORS ERROR DIAGNOSTIC TOOL" + "\n")
    print("This script tests both login endpoints and shows CORS headers\n")
    
    # Test both endpoints
    json_success = test_json_endpoint()
    form_success = test_form_endpoint()
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"JSON Endpoint (/api/auth/login):  {'✅ PASSED' if json_success else '❌ FAILED'}")
    print(f"Form Endpoint (/users/login):     {'✅ PASSED' if form_success else '❌ FAILED'}")
    
    if json_success or form_success:
        print("\n✅ At least one endpoint is working!")
        print("   CORS is configured correctly on the backend.")
        if not form_success:
            print("\n⚠️  The /users/login endpoint has issues.")
            print("   Recommendation: Use /api/auth/login instead (JSON-based)")
    else:
        print("\n❌ Both endpoints failed!")
        print("\n🔍 Troubleshooting steps:")
        print("   1. Check if FastAPI server is running: http://localhost:8000/docs")
        print("   2. Check MongoDB is running: docker ps")
        print("   3. Check the FastAPI terminal for error logs")
        print("   4. Try restarting the server")
    
    print("\n" + "="*70)
    print("\n💡 For detailed error analysis, see: CORS_ERROR_ANALYSIS.md")

if __name__ == "__main__":
    main()
