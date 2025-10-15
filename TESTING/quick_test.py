"""
Quick Test Runner - Fast execution with progress tracking
Tests only critical functionality
"""

import requests
import json
import uuid
import time

AGENT_URL = "http://localhost:5000/chat"
USER_ID = f"test_user_{uuid.uuid4()}"
TIMEOUT = 60  # Increased timeout for Ollama

def test_agent(test_num, description, message, should_contain):
    """Run a single test with progress indicator"""
    print(f"\n[{test_num}] {description}")
    print(f"  📤 {message}")
    print(f"  ⏳ Waiting for response...", end="", flush=True)
    
    start = time.time()
    try:
        response = requests.post(
            AGENT_URL,
            json={"user_id": USER_ID, "message": message, "history": []},
            timeout=TIMEOUT
        )
        elapsed = time.time() - start
        
        reply = response.json().get("reply", "")
        short_reply = (reply[:150] + '...') if len(reply) > 150 else reply
        
        print(f"\r  ⏱️  Response time: {elapsed:.1f}s")
        print(f"  📥 {short_reply}")
        
        if any(word.lower() in reply.lower() for word in should_contain):
            print(f"  ✅ PASSED")
            return True
        else:
            print(f"  ❌ FAILED - Expected keywords: {should_contain}")
            return False
    except requests.exceptions.Timeout:
        print(f"\r  ⏱️  ❌ TIMEOUT after {TIMEOUT}s")
        return False
    except Exception as e:
        print(f"\r  ❌ ERROR: {e}")
        return False

def main():
    print("="*80)
    print("🚀 Quick Test Runner - FoodieExpress Agent")
    print("="*80)
    print(f"🌐 Agent URL: {AGENT_URL}")
    print(f"👤 Test User: {USER_ID}")
    print(f"⏱️  Timeout: {TIMEOUT}s per test")
    print("="*80)
    
    # Check health
    print("\n🔍 Health Check...", end="", flush=True)
    try:
        health = requests.get("http://localhost:5000/health", timeout=5)
        print(f"\r✅ Health Check: {health.json()}")
    except:
        print("\r❌ Health Check FAILED - Agent not running")
        return
    
    results = []
    
    # Core Tests
    print("\n" + "="*80)
    print("📋 CRITICAL TESTS")
    print("="*80)
    
    results.append(test_agent(
        "1", "Basic Greeting",
        "hello",
        ["foodie", "welcome", "help"]
    ))
    
    results.append(test_agent(
        "2", "Capabilities",
        "what can you do?",
        ["restaurant", "search"]
    ))
    
    results.append(test_agent(
        "3", "List All Restaurants",
        "list all restaurants",
        ["swati snacks", "agashiye"]
    ))
    
    results.append(test_agent(
        "4", "Cuisine Filter - Gujarati",
        "show me gujarati restaurants",
        ["swati snacks", "gujarati"]
    ))
    
    results.append(test_agent(
        "5", "Cuisine Filter - Italian",
        "I want italian food",
        ["italian", "pizza"]
    ))
    
    results.append(test_agent(
        "6", "Restaurant Details",
        "tell me about Swati Snacks",
        ["swati snacks", "menu"]
    ))
    
    results.append(test_agent(
        "7", "Search by Item",
        "which restaurant has bhel?",
        ["swati snacks"]
    ))
    
    results.append(test_agent(
        "8", "Invalid Restaurant",
        "tell me about XYZ Restaurant",
        ["not found", "couldn't find", "don't have"]
    ))
    
    # Summary
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    rate = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {rate:.1f}%")
    
    if rate >= 90:
        print("🎉 EXCELLENT - Production Ready!")
    elif rate >= 75:
        print("👍 GOOD - Minor improvements needed")
    elif rate >= 50:
        print("⚠️  NEEDS IMPROVEMENT")
    else:
        print("🔴 CRITICAL - Major fixes required")
    
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n🔴 Fatal error: {e}")
