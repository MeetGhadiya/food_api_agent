"""
Test registration endpoint with various data formats
"""
import requests
import json

url = "http://localhost:8000/users/register"

# Test 1: Correct format
print("=" * 70)
print("TEST 1: Correct Format")
print("=" * 70)

data1 = {
    "username": "TestUser123",
    "email": "test@example.com",
    "password": "Password123",
    "first_name": "Test",
    "last_name": "User"
}

print(f"Sending: {json.dumps(data1, indent=2)}")

try:
    response = requests.post(url, json=data1)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Missing first_name
print("\n" + "=" * 70)
print("TEST 2: Missing first_name (should fail)")
print("=" * 70)

data2 = {
    "username": "TestUser456",
    "email": "test2@example.com",
    "password": "Password123",
    "last_name": "User"
}

print(f"Sending: {json.dumps(data2, indent=2)}")

try:
    response = requests.post(url, json=data2)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: firstName instead of first_name (common mistake)
print("\n" + "=" * 70)
print("TEST 3: firstName instead of first_name (should fail)")
print("=" * 70)

data3 = {
    "username": "TestUser789",
    "email": "test3@example.com",
    "password": "Password123",
    "firstName": "Test",  # Wrong field name
    "lastName": "User"    # Wrong field name
}

print(f"Sending: {json.dumps(data3, indent=2)}")

try:
    response = requests.post(url, json=data3)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
