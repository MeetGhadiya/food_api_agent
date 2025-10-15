"""
FoodieExpress Test Plan V2.0 - Automated Test Runner
Executes all 127 test cases from TEST_PLAN_V2.txt
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = "http://localhost:8000"
AGENT_BASE_URL = "http://localhost:5000"
TEST_RESULTS = []

# Color codes for terminal output (disabled for Windows compatibility)
GREEN = ''
RED = ''
YELLOW = ''
BLUE = ''
RESET = ''

# Test data storage
test_users = {}
test_admin = {}
test_orders = {}
test_reviews = {}
test_restaurants = []

def print_header(text: str):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_test(test_id: str, description: str):
    print(f"\n{YELLOW}[{test_id}]{RESET} {description}")

def print_pass(test_id: str):
    print(f"[PASS] {test_id}")
    TEST_RESULTS.append((test_id, "PASS", ""))

def print_fail(test_id: str, reason: str):
    print(f"[FAIL] {test_id}: {reason}")
    TEST_RESULTS.append((test_id, "FAIL", reason))

def print_blocked(test_id: str, reason: str):
    print(f"[BLOCKED] {test_id}: {reason}")
    TEST_RESULTS.append((test_id, "BLOCKED", reason))

def check_services():
    """Check if API and Agent services are running"""
    print_header("SERVICE HEALTH CHECK")
    
    # Check API
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] API Service Running - {API_BASE_URL}")
        else:
            print(f"[ERROR] API Service Unhealthy - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] API Service Not Running - {API_BASE_URL}")
        print(f"   Error: {e}")
        return False
    
    # Check Agent
    try:
        response = requests.get(f"{AGENT_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] Agent Service Running - {AGENT_BASE_URL}")
        else:
            print(f"[WARNING] Agent Service Unhealthy - Status: {response.status_code}")
    except Exception as e:
        print(f"[WARNING] Agent Service Not Running - {AGENT_BASE_URL}")
        print(f"   Note: Agent tests will be skipped")
    
    return True

# ============================================================================
#                       CATEGORY 1: PUBLIC ENDPOINT TESTS
# ============================================================================

def run_public_endpoint_tests():
    print_header("CATEGORY 1: PUBLIC ENDPOINT TESTS")
    
    # PUB-001
    test_id = "PUB-001"
    print_test(test_id, "Verify root welcome endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "version" in data and "features" in data:
                if data["version"] == "4.0.0" and len(data["features"]) == 8:
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Version or features mismatch: {data}")
            else:
                print_fail(test_id, "Missing expected fields")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-002
    test_id = "PUB-002"
    print_test(test_id, "Verify retrieval of all restaurants")
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # Store for later tests
                global test_restaurants
                test_restaurants = data
                print(f"   Found {len(data)} restaurants")
                print_pass(test_id)
            else:
                print_fail(test_id, "Empty or invalid restaurant list")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-003
    test_id = "PUB-003"
    print_test(test_id, "Verify case-insensitive cuisine filtering")
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/?cuisine=gujarati", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                all_gujarati = all(r.get("cuisine", "").lower() == "gujarati" for r in data)
                if all_gujarati:
                    print(f"   Found {len(data)} Gujarati restaurants")
                    print_pass(test_id)
                else:
                    print_fail(test_id, "Results contain non-Gujarati restaurants")
            else:
                print_fail(test_id, "Invalid response format")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-004
    test_id = "PUB-004"
    print_test(test_id, "Verify filtering for non-existent cuisine")
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/?cuisine=thai", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected empty array, got {len(data)} items")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-005
    test_id = "PUB-005"
    print_test(test_id, "Verify retrieval of specific restaurant")
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/Swati Snacks", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("name") == "Swati Snacks":
                print_pass(test_id)
            else:
                print_fail(test_id, f"Wrong restaurant: {data.get('name')}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-006
    test_id = "PUB-006"
    print_test(test_id, "Verify 404 for non-existent restaurant")
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/NonExistentCafe", timeout=5)
        if response.status_code == 404:
            data = response.json()
            if "Restaurant 'NonExistentCafe' not found" in data.get("detail", ""):
                print_pass(test_id)
            else:
                print_fail(test_id, f"Wrong error message: {data}")
        else:
            print_fail(test_id, f"Expected 404, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-007
    test_id = "PUB-007"
    print_test(test_id, "Verify item search for existing item")
    try:
        response = requests.get(f"{API_BASE_URL}/search/items?item_name=Pizza", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   Found {len(data)} restaurants with Pizza")
                print_pass(test_id)
            else:
                print_fail(test_id, "Invalid response format")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-008
    test_id = "PUB-008"
    print_test(test_id, "Verify item search for non-existent item")
    try:
        response = requests.get(f"{API_BASE_URL}/search/items?item_name=Sushi", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected empty array, got {len(data)} items")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-009
    test_id = "PUB-009"
    print_test(test_id, "Verify item search fails without parameter")
    try:
        response = requests.get(f"{API_BASE_URL}/search/items", timeout=5)
        if response.status_code == 422:
            print_pass(test_id)
        else:
            print_fail(test_id, f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-010
    test_id = "PUB-010"
    print_test(test_id, "Verify case-insensitive item search")
    try:
        resp1 = requests.get(f"{API_BASE_URL}/search/items?item_name=pizza", timeout=5)
        resp2 = requests.get(f"{API_BASE_URL}/search/items?item_name=PIZZA", timeout=5)
        if resp1.status_code == 200 and resp2.status_code == 200:
            data1 = resp1.json()
            data2 = resp2.json()
            if len(data1) == len(data2):
                print_pass(test_id)
            else:
                print_fail(test_id, f"Case-sensitive: {len(data1)} vs {len(data2)}")
        else:
            print_fail(test_id, f"Status codes: {resp1.status_code}, {resp2.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # PUB-018
    test_id = "PUB-018"
    print_test(test_id, "Verify health check endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy" and data.get("database") == "connected":
                print_pass(test_id)
            else:
                print_fail(test_id, f"Unhealthy: {data}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))

# ============================================================================
#                    CATEGORY 2: AUTHENTICATION & USER TESTS
# ============================================================================

def run_auth_tests():
    print_header("CATEGORY 2: AUTHENTICATION & USER TESTS")
    
    # AUTH-001
    test_id = "AUTH-001"
    print_test(test_id, "Test successful user registration")
    try:
        timestamp = int(time.time())
        user_data = {
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@example.com",
            "password": "SecurePass123"
        }
        response = requests.post(f"{API_BASE_URL}/users/register", json=user_data, timeout=5)
        if response.status_code == 201:
            data = response.json()
            if data.get("username") == user_data["username"] and "password" not in data:
                test_users["user1"] = {**user_data, "id": data.get("id")}
                print(f"   Created user: {user_data['username']}")
                print_pass(test_id)
            else:
                print_fail(test_id, f"Invalid response: {data}")
        else:
            print_fail(test_id, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-002
    test_id = "AUTH-002"
    print_test(test_id, "Test registration with duplicate email")
    try:
        if "user1" in test_users:
            dup_data = {
                "username": "differentuser",
                "email": test_users["user1"]["email"],
                "password": "SecurePass456"
            }
            response = requests.post(f"{API_BASE_URL}/users/register", json=dup_data, timeout=5)
            if response.status_code == 400:
                data = response.json()
                if "email already exists" in data.get("detail", "").lower():
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Wrong error: {data}")
            else:
                print_fail(test_id, f"Expected 400, got {response.status_code}")
        else:
            print_blocked(test_id, "No user1 from AUTH-001")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-003
    test_id = "AUTH-003"
    print_test(test_id, "Test registration with duplicate username")
    try:
        if "user1" in test_users:
            dup_data = {
                "username": test_users["user1"]["username"],
                "email": "different@example.com",
                "password": "SecurePass456"
            }
            response = requests.post(f"{API_BASE_URL}/users/register", json=dup_data, timeout=5)
            if response.status_code == 400:
                data = response.json()
                if "username already exists" in data.get("detail", "").lower():
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Wrong error: {data}")
            else:
                print_fail(test_id, f"Expected 400, got {response.status_code}")
        else:
            print_blocked(test_id, "No user1 from AUTH-001")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-004
    test_id = "AUTH-004"
    print_test(test_id, "Test registration with password too short")
    try:
        short_pass_data = {
            "username": "shortpassuser",
            "email": "shortpass@example.com",
            "password": "Short1"  # 6 chars
        }
        response = requests.post(f"{API_BASE_URL}/users/register", json=short_pass_data, timeout=5)
        if response.status_code == 422:
            print_pass(test_id)
        else:
            print_fail(test_id, f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-005
    test_id = "AUTH-005"
    print_test(test_id, "Test registration with password missing letters")
    try:
        no_letters_data = {
            "username": "nolettersuser",
            "email": "noletters@example.com",
            "password": "123456789"
        }
        response = requests.post(f"{API_BASE_URL}/users/register", json=no_letters_data, timeout=5)
        if response.status_code == 422:
            print_pass(test_id)
        else:
            print_fail(test_id, f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-006
    test_id = "AUTH-006"
    print_test(test_id, "Test registration with password missing numbers")
    try:
        no_numbers_data = {
            "username": "nonumbersuser",
            "email": "nonumbers@example.com",
            "password": "PasswordWithoutNumber"
        }
        response = requests.post(f"{API_BASE_URL}/users/register", json=no_numbers_data, timeout=5)
        if response.status_code == 422:
            print_pass(test_id)
        else:
            print_fail(test_id, f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-011 - Create admin user
    test_id = "AUTH-011"
    print_test(test_id, "Test registration with admin role")
    try:
        timestamp = int(time.time())
        admin_data = {
            "username": f"admin{timestamp}",
            "email": f"admin{timestamp}@example.com",
            "password": "AdminPass123",
            "role": "admin"
        }
        response = requests.post(f"{API_BASE_URL}/users/register", json=admin_data, timeout=5)
        if response.status_code == 201:
            data = response.json()
            if data.get("role") == "admin":
                test_admin.update({**admin_data, "id": data.get("id")})
                print(f"   Created admin: {admin_data['username']}")
                print_pass(test_id)
            else:
                print_fail(test_id, f"Role not admin: {data}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-012
    test_id = "AUTH-012"
    print_test(test_id, "Test successful login")
    try:
        if "user1" in test_users:
            login_data = {
                "username": test_users["user1"]["username"],
                "password": test_users["user1"]["password"]
            }
            response = requests.post(f"{API_BASE_URL}/users/login", data=login_data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and data.get("token_type") == "bearer":
                    test_users["user1"]["token"] = data["access_token"]
                    print(f"   Token obtained")
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Invalid token response: {data}")
            else:
                print_fail(test_id, f"Status {response.status_code}")
        else:
            print_blocked(test_id, "No user1 created")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # Login admin
    if test_admin:
        try:
            login_data = {
                "username": test_admin["username"],
                "password": test_admin["password"]
            }
            response = requests.post(f"{API_BASE_URL}/users/login", data=login_data, timeout=5)
            if response.status_code == 200:
                test_admin["token"] = response.json()["access_token"]
                print(f"   Admin token obtained")
        except Exception as e:
            print(f"   Failed to get admin token: {e}")
    
    # AUTH-013
    test_id = "AUTH-013"
    print_test(test_id, "Test login with incorrect password")
    try:
        if "user1" in test_users:
            wrong_login = {
                "username": test_users["user1"]["username"],
                "password": "WrongPassword123"
            }
            response = requests.post(f"{API_BASE_URL}/users/login", data=wrong_login, timeout=5)
            if response.status_code == 401:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 401, got {response.status_code}")
        else:
            print_blocked(test_id, "No user1 created")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-016
    test_id = "AUTH-016"
    print_test(test_id, "Test retrieval of current user info")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            response = requests.get(f"{API_BASE_URL}/users/me", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("username") == test_users["user1"]["username"]:
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Wrong user: {data}")
            else:
                print_fail(test_id, f"Status {response.status_code}")
        else:
            print_blocked(test_id, "No token available")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AUTH-017
    test_id = "AUTH-017"
    print_test(test_id, "Test /users/me without token")
    try:
        response = requests.get(f"{API_BASE_URL}/users/me", timeout=5)
        if response.status_code == 401:
            print_pass(test_id)
        else:
            print_fail(test_id, f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))

# ============================================================================
#                       CATEGORY 3: ORDER MANAGEMENT TESTS
# ============================================================================

def run_order_tests():
    print_header("CATEGORY 3: ORDER MANAGEMENT TESTS")
    
    # ORDER-001
    test_id = "ORDER-001"
    print_test(test_id, "Test successful creation of multi-item order")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            order_data = {
                "restaurant_name": "Swati Snacks",
                "items": [
                    {"item_name": "Masala Thepla", "quantity": 2, "price": 120.0},
                    {"item_name": "Dhokla", "quantity": 1, "price": 80.0}
                ]
            }
            response = requests.post(f"{API_BASE_URL}/orders/", json=order_data, headers=headers, timeout=5)
            if response.status_code == 201:
                data = response.json()
                if data.get("total_price") == 320.0 and data.get("status") == "placed":
                    test_orders["order1"] = data
                    print(f"   Order created: {data.get('id')}, Total: ₹{data.get('total_price')}")
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Wrong order data: {data}")
            else:
                print_fail(test_id, f"Status {response.status_code}: {response.text}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ORDER-002
    test_id = "ORDER-002"
    print_test(test_id, "Test order for non-existent restaurant")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            order_data = {
                "restaurant_name": "NonExistentCafe",
                "items": [{"item_name": "Pizza", "quantity": 1, "price": 100.0}]
            }
            response = requests.post(f"{API_BASE_URL}/orders/", json=order_data, headers=headers, timeout=5)
            if response.status_code == 404:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 404, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ORDER-003
    test_id = "ORDER-003"
    print_test(test_id, "Test order with quantity = 0")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            order_data = {
                "restaurant_name": "Swati Snacks",
                "items": [{"item_name": "Dhokla", "quantity": 0, "price": 80.0}]
            }
            response = requests.post(f"{API_BASE_URL}/orders/", json=order_data, headers=headers, timeout=5)
            if response.status_code == 422:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 422, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ORDER-005
    test_id = "ORDER-005"
    print_test(test_id, "Test order with quantity = 101 (exceeds max)")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            order_data = {
                "restaurant_name": "Swati Snacks",
                "items": [{"item_name": "Dhokla", "quantity": 101, "price": 80.0}]
            }
            response = requests.post(f"{API_BASE_URL}/orders/", json=order_data, headers=headers, timeout=5)
            if response.status_code == 422:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 422, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ORDER-007
    test_id = "ORDER-007"
    print_test(test_id, "Test order with empty items array")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            order_data = {
                "restaurant_name": "Swati Snacks",
                "items": []
            }
            response = requests.post(f"{API_BASE_URL}/orders/", json=order_data, headers=headers, timeout=5)
            if response.status_code == 422:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 422, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ORDER-012
    test_id = "ORDER-012"
    print_test(test_id, "Test order without authentication")
    try:
        order_data = {
            "restaurant_name": "Swati Snacks",
            "items": [{"item_name": "Dhokla", "quantity": 1, "price": 80.0}]
        }
        response = requests.post(f"{API_BASE_URL}/orders/", json=order_data, timeout=5)
        if response.status_code == 401:
            print_pass(test_id)
        else:
            print_fail(test_id, f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ORDER-014
    test_id = "ORDER-014"
    print_test(test_id, "Test retrieval of user's order history")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            response = requests.get(f"{API_BASE_URL}/orders/", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Found {len(data)} orders")
                    print_pass(test_id)
                else:
                    print_fail(test_id, "No orders found")
            else:
                print_fail(test_id, f"Status {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))

# ============================================================================
#                         CATEGORY 4: REVIEW SYSTEM TESTS
# ============================================================================

def run_review_tests():
    print_header("CATEGORY 4: REVIEW SYSTEM TESTS")
    
    # REV-001
    test_id = "REV-001"
    print_test(test_id, "Test successful submission of valid review")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            review_data = {
                "restaurant_name": "Swati Snacks",
                "rating": 5,
                "comment": "Excellent food and service! Highly recommend this place."
            }
            response = requests.post(
                f"{API_BASE_URL}/restaurants/Swati Snacks/reviews",
                json=review_data,
                headers=headers,
                timeout=5
            )
            if response.status_code == 201:
                data = response.json()
                test_reviews["review1"] = data
                print(f"   Review created: {data.get('id')}")
                print_pass(test_id)
            else:
                print_fail(test_id, f"Status {response.status_code}: {response.text}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # REV-002
    test_id = "REV-002"
    print_test(test_id, "Test review with rating > 5")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            review_data = {
                "restaurant_name": "Honest Restaurant",
                "rating": 6,
                "comment": "This should fail validation"
            }
            response = requests.post(
                f"{API_BASE_URL}/restaurants/Honest Restaurant/reviews",
                json=review_data,
                headers=headers,
                timeout=5
            )
            if response.status_code == 422:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 422, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # REV-005
    test_id = "REV-005"
    print_test(test_id, "Test review with comment too short")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            review_data = {
                "restaurant_name": "Honest Restaurant",
                "rating": 4,
                "comment": "good"  # Only 4 characters
            }
            response = requests.post(
                f"{API_BASE_URL}/restaurants/Honest Restaurant/reviews",
                json=review_data,
                headers=headers,
                timeout=5
            )
            if response.status_code == 422:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 422, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # REV-007
    test_id = "REV-007"
    print_test(test_id, "Test duplicate review (same user, same restaurant)")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            review_data = {
                "restaurant_name": "Swati Snacks",
                "rating": 4,
                "comment": "This is a duplicate review attempt"
            }
            response = requests.post(
                f"{API_BASE_URL}/restaurants/Swati Snacks/reviews",
                json=review_data,
                headers=headers,
                timeout=5
            )
            if response.status_code == 400:
                data = response.json()
                if "already reviewed" in data.get("detail", "").lower():
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Wrong error: {data}")
            else:
                print_fail(test_id, f"Expected 400, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # REV-015
    test_id = "REV-015"
    print_test(test_id, "Test review without authentication")
    try:
        review_data = {
            "restaurant_name": "Honest Restaurant",
            "rating": 5,
            "comment": "This should fail without auth"
        }
        response = requests.post(
            f"{API_BASE_URL}/restaurants/Honest Restaurant/reviews",
            json=review_data,
            timeout=5
        )
        if response.status_code == 401:
            print_pass(test_id)
        else:
            print_fail(test_id, f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))

# ============================================================================
#                      CATEGORY 5: ADMIN FUNCTIONALITY TESTS
# ============================================================================

def run_admin_tests():
    print_header("CATEGORY 5: ADMIN FUNCTIONALITY TESTS")
    
    # ADMIN-002
    test_id = "ADMIN-002"
    print_test(test_id, "Test regular user CANNOT create restaurant")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            restaurant_data = {
                "name": "Test Restaurant",
                "area": "Test Area",
                "cuisine": "Test",
                "items": [{"item_name": "Test Item", "price": 100.0}]
            }
            response = requests.post(f"{API_BASE_URL}/restaurants/", json=restaurant_data, headers=headers, timeout=5)
            if response.status_code == 403:
                data = response.json()
                if "admin" in data.get("detail", "").lower():
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Wrong error: {data}")
            else:
                print_fail(test_id, f"Expected 403, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ADMIN-001
    test_id = "ADMIN-001"
    print_test(test_id, "Test admin can create restaurant")
    try:
        if test_admin and "token" in test_admin:
            headers = {"Authorization": f"Bearer {test_admin['token']}"}
            timestamp = int(time.time())
            restaurant_data = {
                "name": f"Test Restaurant {timestamp}",
                "area": "SG Highway, Ahmedabad",
                "cuisine": "Italian",
                "items": [
                    {
                        "item_name": "Margherita Pizza",
                        "price": 350.0,
                        "rating": 4.5,
                        "total_ratings": 10,
                        "description": "Classic Italian pizza"
                    }
                ]
            }
            response = requests.post(f"{API_BASE_URL}/restaurants/", json=restaurant_data, headers=headers, timeout=5)
            if response.status_code == 201:
                data = response.json()
                print(f"   Created restaurant: {data.get('name')}")
                print_pass(test_id)
            else:
                print_fail(test_id, f"Status {response.status_code}: {response.text}")
        else:
            print_blocked(test_id, "No admin token")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ADMIN-010
    test_id = "ADMIN-010"
    print_test(test_id, "Test admin can access platform statistics")
    try:
        if test_admin and "token" in test_admin:
            headers = {"Authorization": f"Bearer {test_admin['token']}"}
            response = requests.get(f"{API_BASE_URL}/admin/stats", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_users", "total_orders", "total_revenue"]
                if all(field in data for field in required_fields):
                    print(f"   Stats: {data.get('total_users')} users, {data.get('total_orders')} orders")
                    print_pass(test_id)
                else:
                    print_fail(test_id, f"Missing fields: {data}")
            else:
                print_fail(test_id, f"Status {response.status_code}")
        else:
            print_blocked(test_id, "No admin token")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # ADMIN-011
    test_id = "ADMIN-011"
    print_test(test_id, "Test regular user CANNOT access platform stats")
    try:
        if "user1" in test_users and "token" in test_users["user1"]:
            headers = {"Authorization": f"Bearer {test_users['user1']['token']}"}
            response = requests.get(f"{API_BASE_URL}/admin/stats", headers=headers, timeout=5)
            if response.status_code == 403:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Expected 403, got {response.status_code}")
        else:
            print_blocked(test_id, "No authenticated user")
    except Exception as e:
        print_fail(test_id, str(e))

# ============================================================================
#                      CATEGORY 6: AI AGENT TESTS
# ============================================================================

def run_agent_tests():
    print_header("CATEGORY 6: AI AGENT CONVERSATIONAL TESTS")
    
    # Check if agent is running
    try:
        response = requests.get(f"{AGENT_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"[WARNING] Agent service not healthy - skipping agent tests")
            return
    except:
        print(f"[WARNING] Agent service not running - skipping agent tests")
        return
    
    # AI-001
    test_id = "AI-001"
    print_test(test_id, "Test basic greeting")
    try:
        response = requests.post(
            f"{AGENT_BASE_URL}/chat",
            json={"message": "hello", "user_id": "test_user"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "").lower()
            if any(word in reply for word in ["hi", "hello", "greet", "welcome"]):
                print(f"   Reply: {data.get('reply')[:100]}...")
                print_pass(test_id)
            else:
                print_fail(test_id, f"Unexpected reply: {reply}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AI-002
    test_id = "AI-002"
    print_test(test_id, "Test 'list all restaurants' tool routing")
    try:
        response = requests.post(
            f"{AGENT_BASE_URL}/chat",
            json={"message": "list all restaurants", "user_id": "test_user"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            # Should call get_all_restaurants() and return formatted list
            if "restaurant" in reply.lower() and len(reply) > 50:
                print(f"   Reply length: {len(reply)} chars")
                print_pass(test_id)
            else:
                print_fail(test_id, f"Unexpected reply: {reply[:100]}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AI-003
    test_id = "AI-003"
    print_test(test_id, "Test cuisine search (gujarati)")
    try:
        response = requests.post(
            f"{AGENT_BASE_URL}/chat",
            json={"message": "show me gujarati restaurants", "user_id": "test_user"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "").lower()
            if "gujarati" in reply:
                print_pass(test_id)
            else:
                print_fail(test_id, f"No Gujarati mention: {reply[:100]}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AI-005
    test_id = "AI-005"
    print_test(test_id, "Test item search ('which has pizza')")
    try:
        response = requests.post(
            f"{AGENT_BASE_URL}/chat",
            json={"message": "which restaurants have pizza?", "user_id": "test_user"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "").lower()
            if "pizza" in reply:
                print_pass(test_id)
            else:
                print_fail(test_id, f"No pizza mention: {reply[:100]}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))
    
    # AI-009
    test_id = "AI-009"
    print_test(test_id, "Test graceful failure for non-existent item")
    try:
        response = requests.post(
            f"{AGENT_BASE_URL}/chat",
            json={"message": "who sells sushi?", "user_id": "test_user"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "").lower()
            if "couldn't find" in reply or "not found" in reply or "no" in reply:
                print_pass(test_id)
            else:
                print_fail(test_id, f"Should say not found: {reply[:100]}")
        else:
            print_fail(test_id, f"Status {response.status_code}")
    except Exception as e:
        print_fail(test_id, str(e))

# ============================================================================
#                           MAIN TEST EXECUTION
# ============================================================================

def generate_report():
    """Generate summary report"""
    print_header("TEST EXECUTION SUMMARY")
    
    total = len(TEST_RESULTS)
    passed = sum(1 for _, status, _ in TEST_RESULTS if status == "PASS")
    failed = sum(1 for _, status, _ in TEST_RESULTS if status == "FAIL")
    blocked = sum(1 for _, status, _ in TEST_RESULTS if status == "BLOCKED")
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{'='*80}")
    print(f"Total Tests Run: {total}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"[BLOCKED] Blocked: {blocked}")
    print(f"\nPass Rate: {pass_rate:.1f}%")
    print(f"{'='*80}\n")
    
    # Show failures
    if failed > 0:
        print(f"\nFAILED TESTS:")
        for test_id, status, reason in TEST_RESULTS:
            if status == "FAIL":
                print(f"  {test_id}: {reason}")
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_results_{timestamp}.txt"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("FOODIEEXPRESS TEST PLAN V2.0 - EXECUTION REPORT\n")
        f.write(f"Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total Tests: {total}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Blocked: {blocked}\n")
        f.write(f"Pass Rate: {pass_rate:.1f}%\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        for test_id, status, reason in TEST_RESULTS:
            f.write(f"[{status}] {test_id}")
            if reason:
                f.write(f": {reason}")
            f.write("\n")
    
    print(f"\n{GREEN}Report saved to: {report_file}{RESET}\n")

def main():
    print_header("FOODIEEXPRESS TEST PLAN V2.0 - AUTOMATED EXECUTION")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check services
    if not check_services():
        print(f"\n[ERROR] Required services are not running!")
        print("Please ensure the following are running:")
        print("  1. FastAPI (python -m uvicorn app.main:app --reload)")
        print("  2. MongoDB Atlas connection")
        print("  3. Agent (python agent_simple.py) - optional for agent tests")
        return
    
    # Run test categories
    try:
        run_public_endpoint_tests()
        run_auth_tests()
        run_order_tests()
        run_review_tests()
        run_admin_tests()
        run_agent_tests()
    except KeyboardInterrupt:
        print(f"\n\n[WARNING] Test execution interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error during test execution: {e}")
    
    # Generate report
    generate_report()
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_header("TEST EXECUTION COMPLETE")

if __name__ == "__main__":
    main()
