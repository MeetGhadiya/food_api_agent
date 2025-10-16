"""
Batched Test Runner - Runs tests in small batches with health checks
This prevents agent crashes by running tests in manageable chunks
"""

import requests
import json
import time
import uuid
import subprocess
import sys
from typing import List, Dict

# --- CONFIGURATION ---
AGENT_URL = "http://localhost:5000/chat"
API_BASE_URL = "http://localhost:8000"
BATCH_SIZE = 10  # Run 10 tests per batch
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
REQUEST_TIMEOUT = 30  # Reduced to 30 seconds

# Test results storage
ALL_RESULTS = {"passed": 0, "failed": 0, "total": 0, "skipped": 0, "details": []}

class colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_agent_health(max_attempts=3):
    """Check if agent is responsive"""
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print(f"{colors.OKGREEN}✅ Agent is healthy{colors.ENDC}")
                return True
        except Exception as e:
            print(f"{colors.WARNING}⚠️  Attempt {attempt + 1}/{max_attempts}: Agent not responding{colors.ENDC}")
            time.sleep(2)
    return False

def send_message_with_retry(user_id, message, token=None, max_retries=MAX_RETRIES):
    """Send message with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            response = requests.post(
                AGENT_URL,
                json={"user_id": user_id, "message": message, "history": []},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json().get("response", "Error: no response")
        
        except requests.exceptions.Timeout:
            print(f"{colors.WARNING}  ⏱️  Timeout on attempt {attempt + 1}/{max_retries}{colors.ENDC}")
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY)
        except requests.exceptions.ConnectionError:
            print(f"{colors.FAIL}  🔌 Connection error on attempt {attempt + 1}/{max_retries}{colors.ENDC}")
            if attempt < max_retries - 1:
                print(f"  Waiting {RETRY_DELAY} seconds before retry...")
                time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"{colors.FAIL}  ❌ Error: {str(e)}{colors.ENDC}")
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY)
    
    return f"ERROR: Failed after {max_retries} attempts"

def run_test(test_id, description, message, expected_keywords=None, forbidden_keywords=None, user_id=None):
    """Run a single test with retry logic"""
    global ALL_RESULTS
    
    if expected_keywords is None:
        expected_keywords = []
    if forbidden_keywords is None:
        forbidden_keywords = []
    if user_id is None:
        user_id = f"test_user_{uuid.uuid4()}"
    
    ALL_RESULTS["total"] += 1
    
    print(f"\n[{test_id}] {description}")
    print(f"  📤 Input: {message[:50]}...")
    
    # Send message with retry
    response = send_message_with_retry(user_id, message)
    
    # Check for error
    if response.startswith("ERROR:"):
        print(f"  {colors.FAIL}❌ FAILED - {response}{colors.ENDC}")
        ALL_RESULTS["failed"] += 1
        ALL_RESULTS["details"].append({"id": test_id, "status": "FAILED", "error": response})
        return False
    
    # Check keywords
    response_lower = response.lower()
    all_expected_found = all(keyword.lower() in response_lower for keyword in expected_keywords)
    any_forbidden_found = any(keyword.lower() in response_lower for keyword in forbidden_keywords)
    
    if all_expected_found and not any_forbidden_found:
        print(f"  {colors.OKGREEN}✅ PASSED{colors.ENDC}")
        ALL_RESULTS["passed"] += 1
        ALL_RESULTS["details"].append({"id": test_id, "status": "PASSED"})
        return True
    else:
        print(f"  {colors.FAIL}❌ FAILED{colors.ENDC}")
        if not all_expected_found:
            missing = [k for k in expected_keywords if k.lower() not in response_lower]
            print(f"     Missing: {missing}")
        if any_forbidden_found:
            found = [k for k in forbidden_keywords if k.lower() in response_lower]
            print(f"     Forbidden found: {found}")
        ALL_RESULTS["failed"] += 1
        ALL_RESULTS["details"].append({"id": test_id, "status": "FAILED"})
        return False

def run_test_batch(batch_name, tests):
    """Run a batch of tests"""
    print("\n" + "="*80)
    print(f"{colors.BOLD}BATCH: {batch_name}{colors.ENDC}")
    print("="*80)
    
    # Health check before batch
    if not check_agent_health():
        print(f"{colors.FAIL}❌ Agent not healthy - skipping batch{colors.ENDC}")
        return False
    
    user_id = f"test_user_{uuid.uuid4()}"  # Same user for entire batch
    
    for test in tests:
        run_test(
            test["id"],
            test["desc"],
            test["msg"],
            test.get("expected", []),
            test.get("forbidden", []),
            user_id
        )
        time.sleep(2)  # Short delay between tests
    
    print(f"\n{colors.OKCYAN}✓ Batch complete{colors.ENDC}")
    time.sleep(3)  # Longer delay between batches
    return True

# Define test batches
BATCH_1_BASIC = [
    {"id": "T001", "desc": "Basic Greeting", "msg": "hello", "expected": ["food", "assistant"]},
    {"id": "T002", "desc": "Capabilities", "msg": "what can you do?", "expected": ["restaurant"]},
    {"id": "T003", "desc": "List All", "msg": "list all restaurants", "expected": ["restaurant"]},
    {"id": "T004", "desc": "Count Check", "msg": "show me all restaurants", "expected": ["swati", "agashiye"]},
    {"id": "T005", "desc": "South Indian", "msg": "show me south indian restaurants", "expected": ["sankalp"], "forbidden": ["swati"]},
    {"id": "T006", "desc": "Gujarati", "msg": "show me gujarati restaurants", "expected": ["gujarati"]},
    {"id": "T007", "desc": "Italian", "msg": "show me italian restaurants", "expected": ["italian"]},
    {"id": "T008", "desc": "Case Test", "msg": "SHOW ME GUJARATI RESTAURANTS", "expected": ["gujarati"]},
    {"id": "T009", "desc": "Help", "msg": "help me", "expected": ["help", "restaurant"]},
    {"id": "T010", "desc": "Thanks", "msg": "thanks", "expected": ["welcome"]},
]

BATCH_2_CONTEXT = [
    {"id": "T011", "desc": "Establish Context", "msg": "tell me about Swati Snacks", "expected": ["swati", "menu"]},
    {"id": "T012", "desc": "Vague Menu (Context)", "msg": "show me the menu", "expected": ["thepla"], "forbidden": ["which restaurant"]},
    {"id": "T013", "desc": "Reviews (Context)", "msg": "what are the reviews?", "expected": ["review"], "forbidden": ["which restaurant"]},
    {"id": "T014", "desc": "New Context", "msg": "tell me about Thepla House", "expected": ["thepla house"]},
    {"id": "T015", "desc": "Menu Again", "msg": "show me the menu", "expected": ["thepla"], "forbidden": ["which restaurant"]},
    {"id": "T016", "desc": "Location (Context)", "msg": "where is it located?", "expected": ["prahlad", "ahmedabad"], "forbidden": ["which"]},
]

BATCH_3_ITEMS = [
    {"id": "T017", "desc": "Item Search - Bhel", "msg": "which restaurant has bhel?", "expected": ["swati"], "forbidden": ["cuisine"]},
    {"id": "T018", "desc": "Item Search - Pizza", "msg": "where can I get pizza?", "expected": ["pizza"]},
    {"id": "T019", "desc": "Item Search - Dhokla", "msg": "who serves dhokla?", "expected": ["restaurant"]},
    {"id": "T020", "desc": "Non-existent Item", "msg": "do you have sushi?", "expected": ["sorry"]},
]

BATCH_4_ERRORS = [
    {"id": "T021", "desc": "Non-existent Restaurant", "msg": "show menu for FakeRestaurant", "expected": ["sorry", "not found"]},
    {"id": "T022", "desc": "Invalid Cuisine", "msg": "show me mexican restaurants", "expected": ["sorry"]},
    {"id": "T023", "desc": "Gibberish", "msg": "asdfghjkl qwertyuiop", "expected": []},
]

if __name__ == "__main__":
    print("="*80)
    print(f"{colors.BOLD}FoodieExpress - Batched Test Runner{colors.ENDC}")
    print("="*80)
    print(f"⏰ Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📦 Batch Size: {BATCH_SIZE} tests per batch")
    print(f"🔄 Max Retries: {MAX_RETRIES}")
    
    # Initial health check
    print("\n🔍 Initial health check...")
    if not check_agent_health():
        print(f"{colors.FAIL}❌ Agent is not running. Please start the agent first.{colors.ENDC}")
        sys.exit(1)
    
    # Run batches
    run_test_batch("Batch 1: Basic Interaction", BATCH_1_BASIC)
    run_test_batch("Batch 2: Context Memory", BATCH_2_CONTEXT)
    run_test_batch("Batch 3: Item Search", BATCH_3_ITEMS)
    run_test_batch("Batch 4: Error Handling", BATCH_4_ERRORS)
    
    # Final summary
    print("\n" + "="*80)
    print(f"{colors.BOLD}FINAL SUMMARY{colors.ENDC}")
    print("="*80)
    print(f"📊 Total Tests: {ALL_RESULTS['total']}")
    print(f"{colors.OKGREEN}✅ Passed: {ALL_RESULTS['passed']}{colors.ENDC}")
    print(f"{colors.FAIL}❌ Failed: {ALL_RESULTS['failed']}{colors.ENDC}")
    
    if ALL_RESULTS['total'] > 0:
        success_rate = (ALL_RESULTS['passed'] / ALL_RESULTS['total']) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Save results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    result_file = f"batched_test_results_{timestamp}.json"
    with open(result_file, 'w') as f:
        json.dump(ALL_RESULTS, f, indent=2)
    print(f"\n💾 Results saved to: {result_file}")
    print(f"⏰ Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
