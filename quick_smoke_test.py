"""
Quick Smoke Test for FoodieExpress API
Runs a minimal set of critical tests to verify the API is working

Usage:
    python quick_smoke_test.py
"""

import subprocess
import sys
from pathlib import Path


def run_smoke_tests():
    """Run quick smoke tests"""
    
    print("\n" + "="*80)
    print("  FOODIEEXPRESS - QUICK SMOKE TEST")
    print("  Running critical tests to verify API functionality")
    print("="*80 + "\n")
    
    # Define critical smoke tests
    smoke_tests = [
        # Public endpoints
        "food_api/tests/test_public_endpoints_comprehensive.py::test_pub_001_root_endpoint",
        "food_api/tests/test_public_endpoints_comprehensive.py::test_pub_002_list_all_restaurants",
        
        # Authentication
        "food_api/tests/test_authentication_comprehensive.py::test_auth_001_register_new_user_success",
        "food_api/tests/test_authentication_comprehensive.py::test_auth_003_login_valid_credentials",
        
        # Orders
        "food_api/tests/test_order_management_comprehensive.py::test_order_001_create_valid_multiitem_order",
        
        # Reviews
        "food_api/tests/test_review_system_comprehensive.py::test_rev_001_create_valid_review",
        
        # Admin
        "food_api/tests/test_admin_functionality_comprehensive.py::test_admin_001_create_restaurant"
    ]
    
    # Build pytest command
    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        "--color=yes",
        "--asyncio-mode=auto",
        "--maxfail=3"  # Stop after 3 failures
    ] + smoke_tests
    
    print(f"Running {len(smoke_tests)} critical smoke tests...\n")
    
    # Run tests
    result = subprocess.run(cmd)
    
    print("\n" + "="*80)
    if result.returncode == 0:
        print("  ✅ SMOKE TESTS PASSED - API is working correctly")
    else:
        print("  ❌ SMOKE TESTS FAILED - Check the output above for errors")
    print("="*80 + "\n")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_smoke_tests())
