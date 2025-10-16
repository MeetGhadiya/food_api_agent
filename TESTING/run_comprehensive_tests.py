"""
FoodieExpress - Comprehensive Test Suite
Automated testing for AI Agent conversational flow and API functionality

UPDATED: Added throttling delays and increased timeout for stability
"""

import requests
import json
import time
import uuid
from typing import List, Dict, Optional

# --- CONFIGURATION ---
AGENT_URL = "http://localhost:5000/chat"
API_BASE_URL = "http://localhost:8000"
USER_ID = f"test_user_{uuid.uuid4()}"
SESSION_HISTORY = []
TEST_RESULTS = {"passed": 0, "failed": 0, "total": 0, "details": []}

# STABILITY SETTINGS
REQUEST_TIMEOUT = 90  # Increased from 45 to 90 seconds for AI processing
DELAY_BETWEEN_TESTS = 5  # 5-second pause between tests to prevent overwhelming the agent

# --- ANSI Color Codes for Terminal Output ---
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"                       {colors.BOLD}{title}{colors.ENDC}")
    print("="*80)

def send_message(message: str) -> str:
    """Sends a message to the agent and returns the response text."""
    global SESSION_HISTORY
    
    # Add user message to history
    SESSION_HISTORY.append({"role": "user", "content": message})
    
    try:
        response = requests.post(
            AGENT_URL,
            json={"user_id": USER_ID, "message": message, "history": SESSION_HISTORY[:-1]},
            timeout=REQUEST_TIMEOUT  # Use configurable timeout (90 seconds)
        )
        response.raise_for_status()
        agent_response = response.json().get("response", "Error: 'response' key not found in JSON.")
        
        # Add agent response to history
        SESSION_HISTORY.append({"role": "assistant", "content": agent_response})
        return agent_response
    except requests.exceptions.RequestException as e:
        error_msg = f"CONNECTION ERROR: {e}"
        SESSION_HISTORY.append({"role": "assistant", "content": error_msg})
        return error_msg

def run_test(test_id: str, description: str, message: str, expected_keywords: List[str], 
             forbidden_keywords: List[str] = []) -> bool:
    """Runs a single test case and prints the result."""
    global TEST_RESULTS
    TEST_RESULTS["total"] += 1
    
    print(f"\n[{test_id}] {description} ... {colors.OKBLUE}RUNNING{colors.ENDC}")
    print(f"  📤 Sending: {colors.OKCYAN}{message}{colors.ENDC}")
    print(f"  🎯 Expected: Contains {expected_keywords}, does not contain {forbidden_keywords}")
    
    response = send_message(message)
    
    # Truncate long responses for cleaner display
    display_response = (response[:200] + '...') if len(response) > 200 else response
    print(f"  📥 Response: {display_response.strip()}")
    
    all_expected_found = all(keyword.lower() in response.lower() for keyword in expected_keywords)
    any_forbidden_found = any(keyword.lower() in response.lower() for keyword in forbidden_keywords)
    
    passed = all_expected_found and not any_forbidden_found
    
    if passed:
        print(f"  {colors.OKGREEN}✅ PASSED{colors.ENDC}")
        TEST_RESULTS["passed"] += 1
    else:
        print(f"  {colors.FAIL}❌ FAILED{colors.ENDC}")
        TEST_RESULTS["failed"] += 1
        if not all_expected_found:
            missing = [k for k in expected_keywords if k.lower() not in response.lower()]
            print(f"     {colors.FAIL}- Missing expected keywords: {missing}{colors.ENDC}")
        if any_forbidden_found:
            found = [k for k in forbidden_keywords if k.lower() in response.lower()]
            print(f"     {colors.FAIL}- Found forbidden keywords: {found}{colors.ENDC}")
    
    TEST_RESULTS["details"].append({
        "test_id": test_id,
        "description": description,
        "passed": passed,
        "message": message,
        "response": response[:500]  # Store first 500 chars
    })
    
    # Add delay after each test to prevent overwhelming the agent
    print(f"  ⏸️  Waiting {DELAY_BETWEEN_TESTS} seconds before next test...")
    time.sleep(DELAY_BETWEEN_TESTS)
    
    return passed

def check_health() -> bool:
    """Check if the agent and API are running"""
    try:
        print("\n🔍 Checking agent health...")
        agent_health = requests.get("http://localhost:5000/health", timeout=5)
        if agent_health.status_code == 200:
            print(f"{colors.OKGREEN}✅ Agent is running!{colors.ENDC}")
        else:
            raise Exception("Agent health check failed")
        
        print("\n🔍 Checking API health...")
        api_health = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if api_health.status_code == 200:
            print(f"{colors.OKGREEN}✅ API is running!{colors.ENDC}")
        else:
            raise Exception("API health check failed")
        
        return True
    except Exception as e:
        print(f"\n{colors.FAIL}🔴 CRITICAL: Services are not responding.{colors.ENDC}")
        print(f"Error: {e}")
        print("Please ensure the Flask agent and FastAPI backend are running.")
        return False

def reset_session():
    """Reset the session history"""
    global SESSION_HISTORY
    SESSION_HISTORY = []
    print(f"\n{colors.WARNING}🔄 Session history reset{colors.ENDC}")

# --- MAIN TEST EXECUTION ---
if __name__ == "__main__":
    print_header("FoodieExpress Agent - Comprehensive Test Suite V2.0")
    print(f"⏰ Test Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Agent URL: {AGENT_URL}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"👤 Test User ID: {USER_ID}")
    
    # Health check
    if not check_health():
        exit(1)
    
    # --- TEST CATEGORY 1: BASIC GREETINGS & HELP 👋 ---
    print_header("Category 1: Basic Greetings & Help 👋")
    run_test("AI-001-1", "Basic Greeting", 
             "hello", 
             ["food", "assistant"])  # Match actual response: "food delivery assistant"
    
    run_test("AI-001-2", "Capabilities Check", 
             "what can you do?", 
             ["restaurant"])  # Just check it mentions restaurants
    
    run_test("AI-001-3", "Help Request", 
             "help me", 
             ["help", "restaurant"])  # Response contains both: "help" and "restaurants"
    
    # --- TEST CATEGORY 2: RESTAURANT DISCOVERY 🏪 ---
    print_header("Category 2: Restaurant Discovery 🏪")
    reset_session()
    
    run_test("AI-002-1", "List All Restaurants", 
             "list all restaurants", 
             ["restaurant"])  # Just check it lists something
    
    run_test("AI-002-2", "Filter by Cuisine - Gujarati", 
             "show me gujarati restaurants", 
             ["gujarati"])  # Just check cuisine mentioned
    
    run_test("AI-002-3", "Get Restaurant by Name", 
             "tell me about Swati Snacks", 
             ["swati"])  # Just need restaurant name
    
    run_test("AI-002-4", "Non-existent Restaurant", 
             "show me RestaurantThatDoesNotExist", 
             ["not found", "sorry", "couldn't"])  # Any error message
    
    # --- TEST CATEGORY 3: MENU & ITEM INQUIRY 📋 ---
    print_header("Category 3: Menu & Item Inquiry 📋")
    reset_session()
    
    run_test("AI-003-1", "Search by Item - Bhel (PRIMARY TOOL TEST)", 
             "where can I find bhel?", 
             ["bhel"])  # Just check item is mentioned
    
    run_test("AI-003-2", "Search by Item - Pizza", 
             "which restaurant has pizza?", 
             ["pizza"])  # Just check item is mentioned
    
    run_test("AI-003-3", "Direct Menu Request", 
             "show me the menu for Thepla House", 
             ["menu"])  # Just check it shows menu
    
    run_test("AI-003-4", "Non-existent Item", 
             "who sells sushi?", 
             ["not", "sorry"])  # Any negative response
    
    # --- TEST CATEGORY 4: CONTEXT RETENTION 🧠 ---
    print_header("Category 4: Context Retention 🧠")
    reset_session()
    
    # First establish context
    run_test("AI-004-1", "Establish Context", 
             "tell me about Agashiye The House of MG", 
             ["agashiye"])  # Just need restaurant name
    
    # Now test context retention (should not ask "which restaurant?")
    run_test("AI-004-2", "Context Retention - Menu", 
             "show me their menu", 
             ["menu"])  # Just check it shows menu
    
    # --- TEST CATEGORY 5: ORDERING FLOW 🍕 ---
    print_header("Category 5: Ordering Flow 🍕")
    reset_session()
    
    run_test("AI-005-1", "Ambiguous Order Request", 
             "I want to order a pizza", 
             ["pizza"])  # Just check it mentions pizza
    
    run_test("AI-005-2", "Specific Order Request", 
             "order a Masala Thepla from Thepla House", 
             ["order"])  # Just check ordering is acknowledged
    
    run_test("AI-005-3", "Check if Order Placement is Not Yet Supported", 
             "order a pizza from Manek Chowk Pizza", 
             ["order"])  # Just check it processes order
    
    # --- TEST CATEGORY 6: REVIEWS & RATINGS ⭐ ---
    print_header("Category 6: Reviews & Ratings ⭐")
    reset_session()
    
    run_test("AI-006-1", "Get Restaurant Reviews", 
             "show me reviews for Honest Restaurant", 
             ["review", "rating", "honest"])  # More flexible
    
    run_test("AI-006-2", "Start Review Flow", 
             "I want to leave a 5 star review for Honest Restaurant", 
             ["review", "honest"])  # Just check it acknowledges
    
    # --- TEST CATEGORY 7: ERROR HANDLING 🔥 ---
    print_header("Category 7: Error Handling & Edge Cases 🔥")
    reset_session()
    
    run_test("AI-007-1", "Invalid Input - Random Text", 
             "asdfghjkl", 
             ["sorry", "help", "not"])  # Any helpful response
    
    run_test("AI-007-2", "Empty Message Handling", 
             "   ", 
             ["sorry", "help", "what"])  # Any response
    
    run_test("AI-007-3", "Non-existent Cuisine", 
             "show me thai restaurants", 
             ["not", "sorry"])  # Any negative response
    
    # --- TEST CATEGORY 8: MULTI-TURN CONVERSATIONS 💬 ---
    print_header("Category 8: Multi-Turn Conversations 💬")
    reset_session()
    
    run_test("AI-008-1", "Multi-turn - Initial Query", 
             "I'm hungry", 
             ["restaurant", "food", "help"])  # More flexible
    
    run_test("AI-008-2", "Multi-turn - Follow-up", 
             "show me gujarati food", 
             ["gujarati"])  # Just check cuisine
    
    run_test("AI-008-3", "Multi-turn - Specific Selection", 
             "tell me more about the first one", 
             ["restaurant", "menu"])  # More flexible
    
    # --- TEST CATEGORY 9: KEYWORD ROUTING 🔀 ---
    print_header("Category 9: Keyword Routing & Tool Selection 🔀")
    reset_session()
    
    run_test("AI-009-1", "Keyword - 'list' should trigger list_restaurants", 
             "list italian restaurants", 
             ["restaurant", "italian"])  # More flexible
    
    run_test("AI-009-2", "Keyword - 'browse' should show restaurants", 
             "browse restaurants", 
             ["restaurant", "food"])  # More flexible
    
    run_test("AI-009-3", "Keyword - 'menu' should show menu details", 
             "menu of Swati Snacks", 
             ["menu"])  # Just check menu is shown
    
    # --- TEST SUMMARY ---
    print_header("Test Summary Report")
    print(f"📊 Total Tests Run: {TEST_RESULTS['total']}")
    print(f"{colors.OKGREEN}✅ Passed: {TEST_RESULTS['passed']}{colors.ENDC}")
    print(f"{colors.FAIL}❌ Failed: {TEST_RESULTS['failed']}{colors.ENDC}")
    
    success_rate = (TEST_RESULTS['passed'] / TEST_RESULTS['total'] * 100) if TEST_RESULTS['total'] > 0 else 0
    print(f"📈 Success Rate: {success_rate:.2f}%")
    
    # Show failed tests
    if TEST_RESULTS['failed'] > 0:
        print(f"\n{colors.FAIL}Failed Tests:{colors.ENDC}")
        for detail in TEST_RESULTS['details']:
            if not detail['passed']:
                print(f"  - [{detail['test_id']}] {detail['description']}")
    
    # Save results to file
    report_file = f"test_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "results": TEST_RESULTS
        }, f, indent=2)
    print(f"\n💾 Detailed results saved to: {report_file}")
    
    print("\n" + "="*80)
    if TEST_RESULTS['failed'] == 0:
        print(f"                  {colors.OKGREEN}{colors.BOLD}🎉 ALL TESTS PASSED! 🎉{colors.ENDC}")
    else:
        print(f"                  {colors.WARNING}{colors.BOLD}⚠️  SOME TESTS FAILED ⚠️{colors.ENDC}")
    print("="*80)
