"""
Automated Test Runner for FoodieExpress API
Runs all test cases with detailed reporting and coverage analysis
"""

import subprocess
import sys
import os
from datetime import datetime
import json

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def run_tests():
    """Run all test cases with pytest"""
    print_header("FoodieExpress API - Automated Test Suite")
    
    # Change to food_api directory
    os.chdir('food_api')
    
    # Test categories
    test_files = {
        "Authentication Tests": "tests/test_api_auth.py",
        "Public API Tests": "tests/test_api_public.py",
        "Review API Tests": "tests/test_api_reviews.py",
        "Main API Tests": "tests/test_main_api.py",
        "Security Tests": "tests/test_security.py"
    }
    
    print_info(f"Starting test execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Test files found: {len(test_files)}")
    print()
    
    # Run all tests with pytest
    print_header("Running All Tests")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",  # Verbose output
        "--tb=short",  # Shorter traceback format
        "--color=yes",  # Colored output
        "-s",  # Show print statements
        "tests/"  # Run all tests in tests directory
    ]
    
    print_info(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Check result
        if result.returncode == 0:
            print_header("Test Results: ALL TESTS PASSED ✅")
            print_success("All test cases executed successfully!")
            return True
        else:
            print_header("Test Results: SOME TESTS FAILED ❌")
            print_error("Some test cases failed. Please review the output above.")
            return False
            
    except Exception as e:
        print_error(f"Error running tests: {e}")
        return False


def run_tests_with_coverage():
    """Run tests with code coverage analysis"""
    print_header("Running Tests with Coverage Analysis")
    
    os.chdir('food_api')
    
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=app",  # Measure coverage for app directory
        "--cov-report=term-missing",  # Show lines not covered
        "--cov-report=html",  # Generate HTML report
        "-v",
        "tests/"
    ]
    
    print_info(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print_success("Tests with coverage completed successfully!")
            print_info("HTML coverage report generated in: htmlcov/index.html")
        else:
            print_warning("Tests completed with some failures")
        
        return result.returncode == 0
        
    except Exception as e:
        print_error(f"Error running tests with coverage: {e}")
        return False


def run_specific_test_category(category):
    """Run a specific category of tests"""
    test_files = {
        "auth": "tests/test_api_auth.py",
        "public": "tests/test_api_public.py",
        "reviews": "tests/test_api_reviews.py",
        "main": "tests/test_main_api.py",
        "security": "tests/test_security.py"
    }
    
    if category not in test_files:
        print_error(f"Unknown test category: {category}")
        print_info(f"Available categories: {', '.join(test_files.keys())}")
        return False
    
    print_header(f"Running {category.upper()} Tests")
    
    os.chdir('food_api')
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        test_files[category]
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print_error(f"Error running {category} tests: {e}")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = ['pytest', 'httpx', 'pytest-cov', 'pytest-asyncio']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            missing.append(package)
    
    if missing:
        print()
        print_warning("Missing packages detected!")
        print_info("Install them with:")
        print(f"    pip install {' '.join(missing)}")
        return False
    
    print()
    print_success("All dependencies are installed!")
    return True


def generate_test_report():
    """Generate a comprehensive test report"""
    print_header("Generating Test Report")
    
    os.chdir('food_api')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"test_report_{timestamp}.json"
    
    cmd = [
        sys.executable, "-m", "pytest",
        "--json-report",
        f"--json-report-file={report_file}",
        "-v",
        "tests/"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if os.path.exists(report_file):
            print_success(f"Test report generated: {report_file}")
            return True
        else:
            print_warning("Report file not generated (pytest-json-report may not be installed)")
            return False
            
    except Exception as e:
        print_error(f"Error generating report: {e}")
        return False


def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}FoodieExpress API - Automated Test Runner{Colors.END}")
    print(f"{Colors.CYAN}Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
    
    # Check if we're in the right directory
    if not os.path.exists('food_api'):
        print_error("food_api directory not found!")
        print_info("Please run this script from the project root directory")
        sys.exit(1)
    
    # Menu
    print("Select test mode:")
    print("  1. Run all tests (quick)")
    print("  2. Run all tests with coverage")
    print("  3. Run specific test category")
    print("  4. Check dependencies only")
    print("  5. Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n\nTest execution cancelled by user.")
        sys.exit(0)
    
    print()
    
    if choice == "1":
        # Check dependencies first
        if not check_dependencies():
            print_error("Please install missing dependencies before running tests")
            sys.exit(1)
        
        # Run all tests
        success = run_tests()
        sys.exit(0 if success else 1)
        
    elif choice == "2":
        # Check dependencies
        if not check_dependencies():
            print_error("Please install missing dependencies before running tests")
            sys.exit(1)
        
        # Run tests with coverage
        success = run_tests_with_coverage()
        sys.exit(0 if success else 1)
        
    elif choice == "3":
        print("Available categories:")
        print("  - auth (Authentication tests)")
        print("  - public (Public API tests)")
        print("  - reviews (Review API tests)")
        print("  - main (Main API tests)")
        print("  - security (Security tests)")
        print()
        
        category = input("Enter category name: ").strip().lower()
        success = run_specific_test_category(category)
        sys.exit(0 if success else 1)
        
    elif choice == "4":
        check_dependencies()
        sys.exit(0)
        
    elif choice == "5":
        print("Exiting...")
        sys.exit(0)
        
    else:
        print_error("Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest execution cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
