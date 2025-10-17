"""
Direct test of /users/login endpoint to diagnose 500 error
"""
import requests

def test_login():
    """Test the /users/login endpoint with form data"""
    url = "http://localhost:8000/users/login"
    
    # Send as form data (what OAuth2PasswordRequestForm expects)
    data = {
        "username": "MG9328",
        "password": "Meet7805"
    }
    
    print("🧪 Testing /users/login endpoint...")
    print(f"📍 URL: {url}")
    print(f"📦 Data: {data}")
    
    try:
        response = requests.post(
            url,
            data=data,  # Form-encoded data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ LOGIN SUCCESSFUL!")
            json_data = response.json()
            print(f"🔑 Access Token: {json_data.get('access_token', 'N/A')[:50]}...")
        else:
            print(f"\n❌ LOGIN FAILED!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("Make sure the server is running on port 8000")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_login()
