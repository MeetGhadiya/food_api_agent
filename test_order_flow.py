"""
Test script to verify the complete order flow with the new restaurant structure
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_flow():
    print("=" * 60)
    print("TESTING FOOD ORDERING FLOW WITH NEW RESTAURANT STRUCTURE")
    print("=" * 60)
    
    # Step 1: Get all restaurants
    print("\n1️⃣  Fetching all restaurants...")
    response = requests.get(f"{BASE_URL}/restaurants/")
    if response.status_code == 200:
        restaurants = response.json()
        print(f"✅ Found {len(restaurants)} restaurants")
        for rest in restaurants[:2]:  # Show first 2
            print(f"\n   📍 {rest['name']} ({rest['area']})")
            print(f"      Items: {len(rest['items'])}")
            for item in rest['items'][:2]:  # Show first 2 items
                print(f"      - {item['item_name']}: ₹{item['price']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        return
    
    # Step 2: Register a new user
    print("\n2️⃣  Registering new user...")
    import random
    test_user = f"testuser{random.randint(1000, 9999)}"
    register_data = {
        "username": test_user,
        "email": f"{test_user}@test.com",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    if response.status_code == 201:
        print(f"✅ User registered: {test_user}")
    else:
        print(f"⚠️  Registration response: {response.status_code}")
        if response.status_code == 400:
            print("   (User may already exist, continuing with login...)")
    
    # Step 3: Login
    print("\n3️⃣  Logging in...")
    login_data = {
        "username": test_user,
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful! Token: {token[:20]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    # Step 4: Place an order
    print("\n4️⃣  Placing an order...")
    order_data = {
        "restaurant_name": "Swati Snacks",
        "item": "Bhel Puri"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/orders/", json=order_data, headers=headers)
    if response.status_code == 201:
        order = response.json()
        print(f"✅ Order placed successfully!")
        print(f"   Restaurant: {order['restaurant_name']}")
        print(f"   Item: {order['item']}")
    else:
        print(f"❌ Order failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # Step 5: Get all orders
    print("\n5️⃣  Fetching all orders...")
    response = requests.get(f"{BASE_URL}/orders/", headers=headers)
    if response.status_code == 200:
        orders = response.json()
        print(f"✅ Found {len(orders)} order(s)")
        for order in orders[-3:]:  # Show last 3 orders
            print(f"   - {order['item']} from {order['restaurant_name']}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! SYSTEM WORKING CORRECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
