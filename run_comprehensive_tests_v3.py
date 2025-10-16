"""
Comprehensive Test Runner for FoodieExpress v4.0.0
Automated Test Suite Execution with Coverage Reporting

This script runs all 100+ test cases from TEST_PLAN_V2.txt with:
- Detailed test execution reporting
- Coverage analysis
- Error detection and reporting
- Test categorization and filtering
- Zero-error validation

Usage:
    python run_comprehensive_tests_v3.py
    python run_comprehensive_tests_v3.py --category public
    python run_comprehensive_tests_v3.py --coverage
    python run_comprehensive_tests_v3.py --verbose
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
import json


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestRunner:
    """Comprehensive test runner for FoodieExpress test suite"""
    
    def __init__(self):
        self.test_categories = {
            "public": "test_public_endpoints_comprehensive.py",
            "auth": "test_authentication_comprehensive.py",
            "orders": "test_order_management_comprehensive.py",
            "reviews": "test_review_system_comprehensive.py",
            "admin": "test_admin_functionality_comprehensive.py",
            "ai_agent": "test_ai_agent_conversation.py",
            "legacy_public": "test_api_public.py",
            "legacy_auth": "test_api_auth.py",
            "legacy_reviews": "test_api_reviews.py"
        }
        
        self.test_dir = Path("food_api/tests")
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0
        }
    
    def print_header(self):
        """Print test suite header"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("=" * 80)
        print("  FOODIEEXPRESS v4.0.0 - COMPREHENSIVE TEST SUITE")
        print("  Automated Testing Aligned with TEST_PLAN_V2.txt")
        print("=" * 80)
        print(f"{Colors.ENDC}")
        print(f"{Colors.BLUE}Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.BLUE}Test Coverage: 100+ test cases across all categories{Colors.ENDC}\n")
    
    def print_category_header(self, category_name):
        """Print category header"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}")
        print(f"{'─' * 80}")
        print(f"  CATEGORY: {category_name.upper()}")
        print(f"{'─' * 80}")
        print(f"{Colors.ENDC}")
    
    def run_tests(self, category=None, coverage=False, verbose=False, markers=None):
        """
        Run test suite with specified options
        
        Args:
            category: Specific category to test (or None for all)
            coverage: Enable coverage reporting
            verbose: Enable verbose output
            markers: Pytest markers to filter tests (e.g., "integration", "unit")
        """
        self.print_header()
        
        # Build pytest command
        cmd = ["pytest"]
        
        # Add test files based on category
        if category:
            if category in self.test_categories:
                test_file = self.test_dir / self.test_categories[category]
                cmd.append(str(test_file))
                print(f"{Colors.CYAN}Running tests for category: {category}{Colors.ENDC}\n")
            else:
                print(f"{Colors.RED}Error: Unknown category '{category}'{Colors.ENDC}")
                print(f"Available categories: {', '.join(self.test_categories.keys())}")
                return False
        else:
            # Run all tests
            cmd.append(str(self.test_dir))
            print(f"{Colors.CYAN}Running ALL test categories{Colors.ENDC}\n")
        
        # Add markers if specified
        if markers:
            cmd.extend(["-m", markers])
        
        # Add coverage options
        if coverage:
            cmd.extend([
                "--cov=food_api/app",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-branch"
            ])
        
        # Add output options
        cmd.extend([
            "-v" if verbose else "-q",
            "--tb=short",
            "--color=yes",
            "--strict-markers",
            "--asyncio-mode=auto"
        ])
        
        # Add JUnit XML report for parsing (built into pytest)
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        cmd.extend(["--junit-xml", report_file])
        
        # Run tests
        print(f"{Colors.BLUE}Executing: {' '.join(cmd)}{Colors.ENDC}\n")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Display output
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            # Parse results from pytest output
            self.parse_pytest_output(result.stdout)
            
            # Parse XML report if it exists
            if os.path.exists(report_file):
                self.parse_xml_results(report_file)
            
            # Print summary
            self.print_summary()
            
            # Return success/failure
            return result.returncode == 0
            
        except Exception as e:
            print(f"{Colors.RED}Error running tests: {str(e)}{Colors.ENDC}")
            return False
    
    def parse_pytest_output(self, output):
        """Parse pytest output to extract test statistics"""
        import re
        
        # Look for the summary line like "5 passed, 2 failed in 10.5s"
        summary_pattern = r'(\d+)\s+passed'
        failed_pattern = r'(\d+)\s+failed'
        error_pattern = r'(\d+)\s+error'
        skipped_pattern = r'(\d+)\s+skipped'
        duration_pattern = r'in\s+([\d.]+)s'
        
        passed_match = re.search(summary_pattern, output)
        if passed_match:
            self.results["passed"] = int(passed_match.group(1))
        
        failed_match = re.search(failed_pattern, output)
        if failed_match:
            self.results["failed"] = int(failed_match.group(1))
        
        error_match = re.search(error_pattern, output)
        if error_match:
            self.results["errors"] = int(error_match.group(1))
        
        skipped_match = re.search(skipped_pattern, output)
        if skipped_match:
            self.results["skipped"] = int(skipped_match.group(1))
        
        duration_match = re.search(duration_pattern, output)
        if duration_match:
            self.results["duration"] = float(duration_match.group(1))
        
        # Calculate total
        self.results["total"] = (
            self.results["passed"] + 
            self.results["failed"] + 
            self.results["errors"] + 
            self.results["skipped"]
        )
    
    def parse_xml_results(self, report_file):
        """Parse JUnit XML test report"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(report_file)
            root = tree.getroot()
            
            # Extract from testsuite element
            for testsuite in root.findall('.//testsuite'):
                self.results["total"] = int(testsuite.get("tests", 0))
                self.results["failed"] = int(testsuite.get("failures", 0))
                self.results["errors"] = int(testsuite.get("errors", 0))
                self.results["skipped"] = int(testsuite.get("skipped", 0))
                self.results["duration"] = float(testsuite.get("time", 0))
                self.results["passed"] = (
                    self.results["total"] - 
                    self.results["failed"] - 
                    self.results["errors"] - 
                    self.results["skipped"]
                )
            
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not parse XML report: {str(e)}{Colors.ENDC}")
    
    def parse_results(self, report_file):
        """Parse JSON test report (legacy - kept for compatibility)"""
        try:
            with open(report_file, 'r') as f:
                data = json.load(f)
            
            summary = data.get("summary", {})
            self.results["total"] = summary.get("total", 0)
            self.results["passed"] = summary.get("passed", 0)
            self.results["failed"] = summary.get("failed", 0)
            self.results["errors"] = summary.get("error", 0)
            self.results["skipped"] = summary.get("skipped", 0)
            self.results["duration"] = data.get("duration", 0)
            
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not parse test report: {str(e)}{Colors.ENDC}")
    
    def print_summary(self):
        """Print test execution summary"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("=" * 80)
        print("  TEST EXECUTION SUMMARY")
        print("=" * 80)
        print(f"{Colors.ENDC}")
        
        # Determine overall status
        if self.results["failed"] == 0 and self.results["errors"] == 0:
            status_color = Colors.GREEN
            status_text = "✅ ALL TESTS PASSED"
        else:
            status_color = Colors.RED
            status_text = "❌ SOME TESTS FAILED"
        
        print(f"{Colors.BOLD}{status_color}{status_text}{Colors.ENDC}\n")
        
        # Print statistics
        print(f"Total Tests:    {self.results['total']}")
        print(f"{Colors.GREEN}Passed:         {self.results['passed']}{Colors.ENDC}")
        
        if self.results['failed'] > 0:
            print(f"{Colors.RED}Failed:         {self.results['failed']}{Colors.ENDC}")
        else:
            print(f"Failed:         {self.results['failed']}")
        
        if self.results['errors'] > 0:
            print(f"{Colors.RED}Errors:         {self.results['errors']}{Colors.ENDC}")
        else:
            print(f"Errors:         {self.results['errors']}")
        
        if self.results['skipped'] > 0:
            print(f"{Colors.YELLOW}Skipped:        {self.results['skipped']}{Colors.ENDC}")
        
        print(f"\nDuration:       {self.results['duration']:.2f}s")
        
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")
    
    def validate_zero_errors(self):
        """Validate that there are no errors in test execution"""
        if self.results["failed"] == 0 and self.results["errors"] == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ Zero-error validation: PASSED{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.RED}{Colors.BOLD}✗ Zero-error validation: FAILED{Colors.ENDC}")
            print(f"{Colors.RED}  - {self.results['failed']} test(s) failed{Colors.ENDC}")
            print(f"{Colors.RED}  - {self.results['errors']} error(s) occurred{Colors.ENDC}")
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FoodieExpress Comprehensive Test Suite Runner"
    )
    parser.add_argument(
        "--category",
        choices=["public", "auth", "orders", "reviews", "admin", "ai_agent", "all"],
        help="Run tests for specific category"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--markers",
        help="Run tests matching specific markers (e.g., 'integration', 'unit', 'smoke')"
    )
    parser.add_argument(
        "--validate-zero-errors",
        action="store_true",
        help="Fail if any tests fail or error"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner()
    
    # Run tests
    category = args.category if args.category != "all" else None
    success = runner.run_tests(
        category=category,
        coverage=args.coverage,
        verbose=args.verbose,
        markers=args.markers
    )
    
    # Validate zero errors if requested
    if args.validate_zero_errors:
        if not runner.validate_zero_errors():
            sys.exit(1)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
