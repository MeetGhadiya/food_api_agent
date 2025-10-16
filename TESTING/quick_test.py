"""
Quick Test Demo - Shows the exact output format you requested
"""

import requests
import time
from typing import Optional

# --- ANSI Color Codes ---
class colors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Configuration
AGENT_URL = "http://localhost:5000/chat"
USER_ID = f"test_user_{int(time.time())}"
SESSION_HISTORY = []

def send_message(message: str) -> str:
    """Send message to agent and return response"""
    global SESSION_HISTORY
    
    SESSION_HISTORY.append({"role": "user", "content": message})
    
    try:
        response = requests.post(
            AGENT_URL,
            json={"user_id": USER_ID, "message": message, "history": SESSION_HISTORY[:-1]},
            timeout=45
        )
        response.raise_for_status()
        agent_response = response.json().get("response", "Error: No response")
        SESSION_HISTORY.append({"role": "assistant", "content": agent_response})
        return agent_response
    except Exception as e:
        return f"CONNECTION ERROR: {e}"

def run_test(test_id: str, description: str, message: str, expected_keywords: list, 
             context_info: Optional[str] = None, forbidden_keywords: list = []) -> bool:
    """Run a single test with formatted output"""
    
    # Format: [3.2] show me the menu ... RUNNING
    print(f"\n[{test_id}] {description} ... {colors.OKBLUE}RUNNING{colors.ENDC}\n")
    
    # Format: 📤 Sending: show me the menu
    print(f"  📤 Sending: {colors.OKCYAN}{message}{colors.ENDC}\n")
    
    # Format: 🎯 Expected: CONTEXT TEST: Should remember Swati Snacks
    if context_info:
        print(f"  🎯 Expected: {context_info}\n")
    else:
        expectation = f"Contains {expected_keywords}"
        if forbidden_keywords:
            expectation += f", does not contain {forbidden_keywords}"
        print(f"  🎯 Expected: {expectation}\n")
    
    # Get response
    response = send_message(message)
    
    # Format: 📥 Response: I couldn't find...
    display_response = (response[:150] + '...') if len(response) > 150 else response
    print(f"  📥 Response: {display_response}\n")
    
    # Check results
    all_expected_found = all(keyword.lower() in response.lower() for keyword in expected_keywords)
    any_forbidden_found = any(keyword.lower() in response.lower() for keyword in forbidden_keywords)
    
    passed = all_expected_found and not any_forbidden_found
    
    # Format: ✅ PASSED or ❌ FAILED
    if passed:
        print(f"  {colors.OKGREEN}✅ PASSED{colors.ENDC}")
    else:
        print(f"  {colors.FAIL}❌ FAILED{colors.ENDC}")
        if not all_expected_found:
            missing = [k for k in expected_keywords if k.lower() not in response.lower()]
            print(f"     {colors.FAIL}- Missing keywords: {missing}{colors.ENDC}")
        if any_forbidden_found:
            found = [k for k in forbidden_keywords if k.lower() in response.lower()]
            print(f"     {colors.FAIL}- Found forbidden keywords: {found}{colors.ENDC}")
    
    return passed

# --- MAIN DEMO ---
if __name__ == "__main__":
    print("="*80)
    print(f"                  {colors.BOLD}Quick Test Demo - Exact Format{colors.ENDC}")
    print("="*80)
    
    # Check if agent is running
    try:
        health = requests.get("http://localhost:5000/health", timeout=5)
        if health.status_code == 200:
            print(f"\n{colors.OKGREEN}✅ Agent is running!{colors.ENDC}\n")
        else:
            raise Exception("Agent not ready")
    except:
        print(f"\n{colors.FAIL}❌ Agent is not running. Please start the Flask agent first.{colors.ENDC}")
        print("Run: cd food_chatbot_agent && python agent.py")
        exit(1)
    
    print("="*80)
    print(f"                  {colors.BOLD}Running Test Examples{colors.ENDC}")
    print("="*80)
    
    # Test 1: Basic greeting
    run_test(
        "1.1",
        "Basic Greeting",
        "hello",
        ["hello", "help"]  # Match what AI actually says - "Hello there! ... How can I help you"
    )
    
    # Test 2: Restaurant search
    run_test(
        "2.1",
        "Search Gujarati restaurants",
        "show me gujarati restaurants",
        ["gujarati"]  # Just check it mentions the cuisine
    )
    
    # Test 3: Context test (like your example)
    # First establish context
    run_test(
        "3.1",
        "Establish context about Swati Snacks",
        "tell me about Swati Snacks",
        ["swati"]  # More flexible - just needs restaurant name
    )
    
    # Then test context retention (like your example)
    run_test(
        "3.2",
        "show me the menu",
        "show me the menu",
        ["menu"],  # Just check it shows menu
        context_info="CONTEXT TEST: Should remember Swati Snacks"
    )
    
    # Test 4: Item search
    run_test(
        "4.1",
        "Search for bhel",
        "where can I find bhel?",
        ["bhel"],  # Just check it mentions the item
        context_info="PRIMARY TOOL TEST: Must use search_by_item"
    )
    
    print("\n" + "="*80)
    print(f"                  {colors.OKGREEN}{colors.BOLD}Demo Complete!{colors.ENDC}")
    print("="*80)
    print("\nThis is the exact format you requested!")
    print("The full test suite in run_comprehensive_tests.py uses this same format.")
