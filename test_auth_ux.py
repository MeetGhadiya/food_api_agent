"""
Test Authentication Flow - Verify UX Improvements
=================================================
Quick test to verify that authenticated users don't get asked to log in again

Run this test after starting the chatbot agent to verify the fix.
"""

import requests
import json

# Configuration
AGENT_URL = "http://localhost:5001/chat"
FASTAPI_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_guest_browsing():
    """Test that guests can browse without login"""
    print_section("TEST 1: Guest Browsing (No Login Required)")
    
    # Test browsing restaurants as guest
    response = requests.post(AGENT_URL, json={
        "message": "list all restaurants",
        "user_id": "test_guest_001"
    })
    
    data = response.json()
    
    if "requires_auth" in data:
        print("❌ FAILED: Guest asked to login for browsing!")
        print(f"   Response: {data['response'][:100]}")
        return False
    else:
        print("✅ PASSED: Guest can browse without login")
        print(f"   Response preview: {data['response'][:100]}...")
        return True

def test_guest_ordering():
    """Test that guests are prompted to login when ordering"""
    print_section("TEST 2: Guest Ordering (Should Prompt Login)")
    
    # First, get menu
    response1 = requests.post(AGENT_URL, json={
        "message": "show menu for The Chocolate Room",
        "user_id": "test_guest_002"
    })
    
    # Try to order
    response2 = requests.post(AGENT_URL, json={
        "message": "order 2 Chocolate Fudge Cake",
        "user_id": "test_guest_002"
    })
    
    # Confirm order
    response3 = requests.post(AGENT_URL, json={
        "message": "yes",
        "user_id": "test_guest_002"
    })
    
    data = response3.json()
    
    if "requires_auth" in data or "Login Required" in data['response']:
        print("✅ PASSED: Guest prompted to login when ordering")
        print(f"   Response: {data['response'][:200]}...")
        return True
    else:
        print("❌ FAILED: Guest NOT prompted to login!")
        print(f"   Response: {data['response'][:200]}")
        return False

def test_authenticated_ordering():
    """Test that authenticated users can order without login prompt"""
    print_section("TEST 3: Authenticated User Ordering (No Login Prompt)")
    
    # First, login to get token
    print("   Step 1: Logging in...")
    login_response = requests.post(
        f"{FASTAPI_URL}/users/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    
    if login_response.status_code != 200:
        print("⚠️  SKIPPED: Could not login (user may not exist)")
        print("   Create test user: POST /users/register with username=testuser, password=testpass123")
        return None
    
    token = login_response.json()['access_token']
    print(f"   ✅ Logged in successfully (token: {token[:20]}...)")
    
    # View menu
    print("   Step 2: Viewing menu...")
    response1 = requests.post(
        AGENT_URL,
        json={
            "message": "show menu for The Chocolate Room",
            "user_id": "testuser"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Order
    print("   Step 3: Placing order...")
    response2 = requests.post(
        AGENT_URL,
        json={
            "message": "order 2 Chocolate Fudge Cake",
            "user_id": "testuser"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Confirm order
    print("   Step 4: Confirming order...")
    response3 = requests.post(
        AGENT_URL,
        json={
            "message": "yes",
            "user_id": "testuser"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    data = response3.json()
    
    # Check if authentication was requested
    if "requires_auth" in data or "Login Required" in data['response'] or "Authentication Required" in data['response']:
        print("❌ FAILED: Authenticated user asked to login again!")
        print(f"   Response: {data['response'][:200]}")
        return False
    elif "Order Placed Successfully" in data['response'] or "Order failed" in data['response']:
        print("✅ PASSED: Authenticated user ordered without login prompt!")
        print(f"   Response preview: {data['response'][:150]}...")
        return True
    else:
        print("⚠️  UNCLEAR: Unexpected response")
        print(f"   Response: {data['response'][:200]}")
        return None

def main():
    """Run all tests"""
    print("\n" + "🚀 " + "="*56)
    print("   AUTHENTICATION UX IMPROVEMENT TESTS")
    print("="*58)
    print("\nThese tests verify that:")
    print("  1. Guests can browse without login")
    print("  2. Guests are prompted to login when ordering")
    print("  3. Authenticated users can order without login prompts")
    print("\nStarting tests...")
    
    results = []
    
    # Run tests
    results.append(("Guest Browsing", test_guest_browsing()))
    results.append(("Guest Ordering", test_guest_ordering()))
    results.append(("Authenticated Ordering", test_authenticated_ordering()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result == True)
    failed = sum(1 for _, result in results if result == False)
    skipped = sum(1 for _, result in results if result is None)
    
    for name, result in results:
        if result == True:
            print(f"✅ {name}: PASSED")
        elif result == False:
            print(f"❌ {name}: FAILED")
        else:
            print(f"⚠️  {name}: SKIPPED")
    
    print(f"\n📊 Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0 and passed > 0:
        print("\n🎉 All tests passed! Authentication UX is working correctly!")
    elif failed > 0:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
    
    print("\n" + "="*58 + "\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to services!")
        print("   Make sure the following are running:")
        print("   - FastAPI backend: http://localhost:8000")
        print("   - Chatbot agent: http://localhost:5001")
        print("\nStart them with:")
        print("   1. cd food_api && python -m uvicorn app.main:app --reload")
        print("   2. cd food_chatbot_agent && python app.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
