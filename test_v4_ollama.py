"""
V4.0 OLLAMA VERIFICATION TESTS
Shows exactly what the agent says and thinks!
"""

import requests
import json
import time

def test_context_handling():
    """TEST 1: Context Handling - Agent should remember last restaurant"""
    
    print("=" * 70)
    print("🧪 TEST 1: CONTEXT HANDLING (TASK 1)")
    print("=" * 70)
    print("\nObjective: Verify agent remembers 'Thepla House' when user asks 'show me the menu'\n")
    
    user_id = "test_user_001"
    
    # Step 1: Mention restaurant
    print("📤 STEP 1: User mentions restaurant")
    print("USER: 'tell me about Thepla House'")
    print("-" * 70)
    
    response1 = requests.post(
        'http://localhost:5000/chat',
        json={'user_id': user_id, 'message': 'tell me about Thepla House'},
        headers={'Content-Type': 'application/json'}
    )
    
    agent_response_1 = response1.json()['response']
    print("\n📥 AGENT RESPONSE:")
    print(agent_response_1)
    
    # Check if context was saved
    if "Thepla House" in agent_response_1 and ("Menu" in agent_response_1 or "menu" in agent_response_1):
        print("\n✅ Restaurant details shown successfully")
    else:
        print("\n⚠️  Unexpected response format")
    
    time.sleep(1)
    
    # Step 2: Ask vague question
    print("\n" + "=" * 70)
    print("📤 STEP 2: User asks vague question (no restaurant name)")
    print("USER: 'show me the menu'")
    print("-" * 70)
    
    response2 = requests.post(
        'http://localhost:5000/chat',
        json={'user_id': user_id, 'message': 'show me the menu'},
        headers={'Content-Type': 'application/json'}
    )
    
    agent_response_2 = response2.json()['response']
    print("\n📥 AGENT RESPONSE (using context):")
    print(agent_response_2)
    
    # Verify context was used
    print("\n" + "=" * 70)
    print("🔍 VERIFICATION:")
    if "Thepla House" in agent_response_2 and ("Menu" in agent_response_2 or "menu" in agent_response_2 or "₹" in agent_response_2):
        print("✅ PASS: Agent remembered 'Thepla House' from context!")
        print("✅ Agent showed the menu WITHOUT asking 'which restaurant?'")
        return True
    else:
        print("❌ FAIL: Agent did NOT use context (would have asked 'which restaurant?')")
        return False


def test_order_confirmation():
    """TEST 2: Order Confirmation - Agent should ask for confirmation before ordering"""
    
    print("\n\n" + "=" * 70)
    print("🧪 TEST 2: ORDER CONFIRMATION (TASK 2)")
    print("=" * 70)
    print("\nObjective: Verify agent asks for confirmation before placing order\n")
    
    user_id = "test_user_002"
    
    # Step 1: Try to order
    print("📤 STEP 1: User tries to order")
    print("USER: 'I want to order 2 Masala Thepla from Thepla House'")
    print("-" * 70)
    
    response1 = requests.post(
        'http://localhost:5000/chat',
        json={'user_id': user_id, 'message': 'I want to order 2 Masala Thepla from Thepla House'},
        headers={'Content-Type': 'application/json'}
    )
    
    agent_response_1 = response1.json()['response']
    print("\n📥 AGENT RESPONSE:")
    print(agent_response_1)
    
    # Check if asking for confirmation
    confirmation_keywords = ['confirm', 'yes', 'proceed', 'total']
    has_confirmation = any(keyword in agent_response_1.lower() for keyword in confirmation_keywords)
    
    if has_confirmation:
        print("\n✅ Agent is asking for confirmation (not placing order immediately)")
    else:
        print("\n⚠️  Agent response unclear")
    
    time.sleep(1)
    
    # Step 2: Confirm order
    print("\n" + "=" * 70)
    print("📤 STEP 2: User confirms")
    print("USER: 'yes'")
    print("-" * 70)
    
    # For this test, we'll simulate without actual token
    response2 = requests.post(
        'http://localhost:5000/chat',
        json={'user_id': user_id, 'message': 'yes'},
        headers={'Content-Type': 'application/json'}
    )
    
    agent_response_2 = response2.json()['response']
    print("\n📥 AGENT RESPONSE:")
    print(agent_response_2)
    
    # Verify order flow
    print("\n" + "=" * 70)
    print("🔍 VERIFICATION:")
    if "login" in agent_response_2.lower() or "order placed" in agent_response_2.lower():
        print("✅ PASS: Two-step confirmation workflow working!")
        print("✅ Agent asked for confirmation first, then processed on 'yes'")
        return True
    else:
        print("❌ FAIL: Order confirmation flow not working correctly")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting V4.0 OLLAMA Verification Tests...")
    print("⏳ Waiting for agent to be ready...\n")
    
    time.sleep(2)
    
    # Run tests
    test1_pass = False
    test2_pass = False
    
    try:
        test1_pass = test_context_handling()
    except Exception as e:
        print(f"❌ TEST 1 ERROR: {e}")
    
    try:
        test2_pass = test_order_confirmation()
    except Exception as e:
        print(f"❌ TEST 2 ERROR: {e}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 70)
    print(f"TEST 1 (Context Handling): {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"TEST 2 (Order Confirmation): {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print("=" * 70)
    
    if test1_pass and test2_pass:
        print("\n🎉 ALL TESTS PASSED! V4.0 OLLAMA is working perfectly! 🎉\n")
    else:
        print("\n⚠️  Some tests failed - review output above\n")
