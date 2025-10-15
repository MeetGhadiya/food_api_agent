"""
Context Handling Test - Verify the agent remembers previous restaurant
This tests the HIGH PRIORITY fix for Test 3.2b
"""

import requests
import uuid
import time

AGENT_URL = "http://localhost:5000/chat"
USER_ID = f"context_test_{uuid.uuid4()}"

def send_message(message):
    """Send message to agent"""
    print(f"\n{'='*70}")
    print(f"📤 USER: {message}")
    print(f"{'='*70}")
    
    response = requests.post(
        AGENT_URL,
        json={"user_id": USER_ID, "message": message, "history": []},
        timeout=60
    )
    
    reply = response.json().get("response", "")
    print(f"🤖 AGENT: {reply[:300]}...")
    return reply

def test_context_handling():
    """Test if agent remembers the last restaurant mentioned"""
    print("\n" + "🔥"*35)
    print("CONTEXT HANDLING TEST - HIGH PRIORITY FIX")
    print("🔥"*35)
    print(f"Test User: {USER_ID}")
    print(f"Agent URL: {AGENT_URL}\n")
    
    # Step 1: Ask about specific restaurant
    print("\n[TEST 1] Establish Context - Ask about Swati Snacks")
    response1 = send_message("tell me about Swati Snacks")
    
    # Verify restaurant info was returned
    if "swati snacks" in response1.lower() and "menu" in response1.lower():
        print("✅ PASS: Agent returned Swati Snacks details")
    else:
        print("❌ FAIL: Agent didn't return proper restaurant details")
        return False
    
    time.sleep(1)
    
    # Step 2: Ask vague question that requires context
    print("\n[TEST 2] Context Test - Ask 'show me the menu' (no restaurant name)")
    response2 = send_message("show me the menu")
    
    # Verify agent used context (should show Swati Snacks menu, not search for "The Menu")
    if "swati snacks" in response2.lower():
        print("✅ PASS: Agent remembered context! Showed Swati Snacks menu")
        print("🎉 CONTEXT HANDLING IS WORKING!")
        return True
    elif "the menu" in response2.lower() or "couldn't find" in response2.lower():
        print("❌ FAIL: Agent searched for 'The Menu' restaurant (no context)")
        print("⚠️  Context handling still needs work")
        return False
    elif "which restaurant" in response2.lower():
        print("⚠️  PARTIAL: Agent asked for clarification (better than searching 'The Menu')")
        print("💡 TIP: Could be improved by using context automatically")
        return False
    else:
        print("❓ UNKNOWN: Unexpected response")
        return False

def test_multiple_context_switches():
    """Test if agent can switch context between restaurants"""
    print("\n" + "🔥"*35)
    print("ADVANCED CONTEXT TEST - Multiple Restaurants")
    print("🔥"*35)
    
    # Ask about first restaurant
    print("\n[TEST 3] Ask about Agashiye")
    response1 = send_message("tell me about Agashiye")
    
    if "agashiye" in response1.lower():
        print("✅ Context set to: Agashiye")
    
    time.sleep(1)
    
    # Ask vague question (should use Agashiye context)
    print("\n[TEST 4] Ask 'what else do they have'")
    response2 = send_message("what else do they have?")
    
    if "agashiye" in response2.lower():
        print("✅ EXCELLENT: Agent maintained Agashiye context")
        return True
    else:
        print("⚠️  Agent may have lost context")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 TESTING CONTEXT HANDLING FIX (HIGH PRIORITY)")
    print("="*70)
    
    # Test 1: Basic context handling
    test1_passed = test_context_handling()
    
    time.sleep(2)
    
    # Test 2: Advanced context switching
    test2_passed = test_multiple_context_switches()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"[TEST 3.2b] Basic Context: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"[TEST 8.x]  Advanced Context: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 SUCCESS: Context handling is working correctly!")
        print("✅ Tests 3.2b and 8.x should now pass")
    elif test1_passed:
        print("\n👍 GOOD: Basic context working, advanced needs refinement")
    else:
        print("\n⚠️  NEEDS WORK: Context handling requires more fixes")
    
    print("="*70)
