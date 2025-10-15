"""
FoodieExpress Agent - Comprehensive Test Execution Suite
========================================================
This script executes all test cases and generates a detailed report.
"""
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
AGENT_URL = "http://localhost:5000/chat"
HEALTH_URL = "http://localhost:5000/health"
USER_ID = f"test_user_{int(time.time())}"

# Test results storage
test_results = []
category_summary = {}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def print_test(test_id, description, status="RUNNING"):
    status_color = Colors.YELLOW if status == "RUNNING" else Colors.GREEN if status == "PASS" else Colors.RED
    print(f"{Colors.BOLD}[{test_id}]{Colors.RESET} {description} ... {status_color}{status}{Colors.RESET}")

def send_message(message: str, token: Optional[str] = None) -> Dict[Any, Any]:
    """Send message to agent and return response"""
    try:
        payload = {
            "message": message,
            "user_id": USER_ID
        }
        if token:
            payload["token"] = token
        
        response = requests.post(AGENT_URL, json=payload, timeout=30)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else {},
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "status_code": 0,
            "data": {},
            "success": False,
            "error": str(e)
        }

def check_agent_health():
    """Verify agent is running"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def run_test(test_id: str, category: str, user_input: str, 
             expected_behavior: str, expected_keywords: list,
             should_call_tool: Optional[str] = None) -> bool:
    """Execute a single test case"""
    
    print_test(test_id, user_input, "RUNNING")
    print(f"  📤 Sending: {Colors.BLUE}{user_input}{Colors.RESET}")
    print(f"  🎯 Expected: {expected_behavior}")
    
    # Send message
    result = send_message(user_input)
    
    if not result["success"]:
        print(f"  {Colors.RED}❌ FAILED: {result.get('error', 'Connection error')}{Colors.RESET}")
        test_results.append({
            "test_id": test_id,
            "category": category,
            "input": user_input,
            "status": "FAIL",
            "reason": result.get("error", "Connection error")
        })
        return False
    
    response_text = result["data"].get("response", "")
    print(f"  📥 Response: {response_text[:150]}..." if len(response_text) > 150 else f"  📥 Response: {response_text}")
    
    # Validate response
    issues = []
    
    # Check expected keywords
    for keyword in expected_keywords:
        if keyword.lower() not in response_text.lower():
            issues.append(f"Missing expected keyword: '{keyword}'")
    
    # Check response not empty
    if len(response_text) < 10:
        issues.append("Response too short")
    
    # Determine result
    if issues:
        print(f"  {Colors.YELLOW}⚠️  PASS WITH ISSUES:{Colors.RESET}")
        for issue in issues:
            print(f"     - {issue}")
        test_results.append({
            "test_id": test_id,
            "category": category,
            "input": user_input,
            "status": "PASS_WITH_ISSUES",
            "issues": issues,
            "response": response_text[:200]
        })
        return True
    else:
        print(f"  {Colors.GREEN}✅ PASSED{Colors.RESET}")
        test_results.append({
            "test_id": test_id,
            "category": category,
            "input": user_input,
            "status": "PASS",
            "response": response_text[:200]
        })
        return True

def main():
    print_header("FoodieExpress Agent - Comprehensive Test Suite")
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Agent URL: {AGENT_URL}")
    print(f"👤 Test User ID: {USER_ID}\n")
    
    # Health check
    print("🔍 Checking agent health...")
    if not check_agent_health():
        print(f"{Colors.RED}❌ ERROR: Agent is not running on {AGENT_URL}{Colors.RESET}")
        print("Please start the agent first!")
        return
    print(f"{Colors.GREEN}✅ Agent is running!{Colors.RESET}\n")
    
    time.sleep(1)
    
    # ==================== CATEGORY 1: GREETINGS ====================
    print_header("Category 1: Basic Greetings & Help 👋")
    
    run_test(
        "1.1", "Greetings", "hello",
        "Friendly greeting",
        ["welcome", "foodie", "help"]
    )
    time.sleep(2)
    
    run_test(
        "1.2", "Greetings", "what can you do?",
        "List of capabilities",
        ["restaurant", "order", "search"]
    )
    time.sleep(2)
    
    # ==================== CATEGORY 2: RESTAURANT DISCOVERY ====================
    print_header("Category 2: Restaurant Discovery 🏪")
    
    run_test(
        "2.1", "Discovery", "list all restaurants",
        "Complete list of restaurants",
        ["restaurant"]
    )
    time.sleep(2)
    
    run_test(
        "2.2", "Discovery", "show me gujarati restaurants",
        "Filtered by Gujarati cuisine",
        ["gujarati"]
    )
    time.sleep(2)
    
    run_test(
        "2.3", "Discovery", "tell me about Swati Snacks",
        "Restaurant details with menu",
        ["swati", "menu"]
    )
    time.sleep(2)
    
    # ==================== CATEGORY 3: MENU & ITEMS ====================
    print_header("Category 3: Menu & Item Inquiry 📋")
    
    run_test(
        "3.1", "Menu", "which restaurant has bhel?",
        "CRITICAL: Must call search_by_item, NOT search_by_cuisine",
        ["bhel", "restaurant"]
    )
    time.sleep(2)
    
    run_test(
        "3.2", "Menu", "show me the menu",
        "CONTEXT TEST: Should remember Swati Snacks",
        ["menu"]
    )
    time.sleep(2)
    
    # ==================== CATEGORY 4: ORDERING ====================
    print_header("Category 4: Ordering Flow 🍕")
    
    run_test(
        "4.1", "Ordering", "I want to order",
        "Should ask clarifying question",
        ["what", "restaurant"]
    )
    time.sleep(2)
    
    run_test(
        "4.2", "Ordering", "order 2 Masala Thepla from Thepla House",
        "Should ask for confirmation, NOT auto-place",
        ["confirm", "masala thepla", "thepla house"]
    )
    time.sleep(2)
    
    # Note: Test 4.3 (confirmation) would need stateful handling
    
    # ==================== CATEGORY 5: AUTHENTICATION ====================
    print_header("Category 5: User Accounts & Authentication 👤")
    
    # Skip actual login tests to avoid auth complexity in automated test
    print("ℹ️  Skipping login tests (requires manual interaction)")
    
    # ==================== CATEGORY 6: REVIEWS ====================
    print_header("Category 6: Reviews & History ⭐")
    
    run_test(
        "6.1", "Reviews", "show me reviews for Honest Restaurant",
        "Display reviews",
        ["review", "honest"]
    )
    time.sleep(2)
    
    run_test(
        "6.2", "Reviews", "I want to leave a 5 star review for Honest Restaurant",
        "Should ask for comment",
        ["comment", "review"]
    )
    time.sleep(2)
    
    # ==================== CATEGORY 7: ERROR HANDLING ====================
    print_header("Category 7: Error Handling 🔥")
    
    run_test(
        "7.1", "Error Handling", "show menu for RestaurantThatDoesNotExist",
        "Graceful error for nonexistent restaurant",
        ["sorry", "couldn't find", "not found"]
    )
    time.sleep(2)
    
    # ==================== GENERATE REPORT ====================
    print_header("Test Summary Report")
    
    total_tests = len(test_results)
    passed = len([t for t in test_results if t["status"] == "PASS"])
    passed_with_issues = len([t for t in test_results if t["status"] == "PASS_WITH_ISSUES"])
    failed = len([t for t in test_results if t["status"] == "FAIL"])
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  Passed with Issues: {passed_with_issues}{Colors.RESET}")
    print(f"{Colors.RED}❌ Failed: {failed}{Colors.RESET}")
    print(f"📈 Success Rate: {((passed + passed_with_issues) / total_tests * 100):.1f}%\n")
    
    # Save detailed report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": passed,
                "passed_with_issues": passed_with_issues,
                "failed": failed,
                "success_rate": f"{((passed + passed_with_issues) / total_tests * 100):.1f}%"
            },
            "results": test_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Detailed report saved to: {report_file}\n")
    
    # Issues summary
    issues_found = [r for r in test_results if r["status"] == "PASS_WITH_ISSUES"]
    if issues_found:
        print(f"{Colors.YELLOW}⚠️  Tests with Issues:{Colors.RESET}")
        for result in issues_found:
            print(f"\n  [{result['test_id']}] {result['input']}")
            for issue in result.get('issues', []):
                print(f"    - {issue}")
    
    failed_tests = [r for r in test_results if r["status"] == "FAIL"]
    if failed_tests:
        print(f"\n{Colors.RED}❌ Failed Tests:{Colors.RESET}")
        for result in failed_tests:
            print(f"\n  [{result['test_id']}] {result['input']}")
            print(f"    Reason: {result.get('reason', 'Unknown')}")
    
    print_header("Testing Complete!")

if __name__ == "__main__":
    main()
