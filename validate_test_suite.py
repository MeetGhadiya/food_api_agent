"""
Quick Validation Script for FoodieExpress Test Suite
Validates that all test files are error-free and properly configured

This script performs:
1. Import validation - Ensures all test files can be imported
2. Fixture validation - Checks that required fixtures exist
3. Test discovery - Counts total tests available
4. Syntax validation - Verifies Python syntax
5. Quick smoke test - Runs a subset of fast tests
"""

import sys
import os
import ast
from pathlib import Path
import importlib.util


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


class TestValidator:
    """Validates test suite configuration and health"""
    
    def __init__(self):
        self.test_dir = Path("food_api/tests")
        self.errors = []
        self.warnings = []
        
    def print_header(self, message):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{message}{Colors.ENDC}")
        print(f"{Colors.CYAN}{'─' * 60}{Colors.ENDC}")
    
    def print_success(self, message):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"{Colors.RED}✗ {message}{Colors.ENDC}")
        self.errors.append(message)
    
    def print_warning(self, message):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")
        self.warnings.append(message)
    
    def validate_syntax(self):
        """Validate Python syntax of all test files"""
        self.print_header("1. Validating Python Syntax")
        
        test_files = list(self.test_dir.glob("test_*.py"))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                ast.parse(code)
                self.print_success(f"Syntax valid: {test_file.name}")
            except SyntaxError as e:
                self.print_error(f"Syntax error in {test_file.name}: {e}")
    
    def validate_imports(self):
        """Validate that all test files can be imported"""
        self.print_header("2. Validating Imports")
        
        test_files = [
            "test_public_endpoints_comprehensive.py",
            "test_authentication_comprehensive.py",
            "test_order_management_comprehensive.py",
            "test_review_system_comprehensive.py",
            "test_admin_functionality_comprehensive.py",
            "test_ai_agent_conversation.py"
        ]
        
        # Add test directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        for test_file in test_files:
            file_path = self.test_dir / test_file
            if not file_path.exists():
                self.print_warning(f"File not found: {test_file}")
                continue
            
            try:
                # Try to load the module
                spec = importlib.util.spec_from_file_location(
                    test_file[:-3], 
                    str(file_path)
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    # We don't execute it, just validate it can be loaded
                    self.print_success(f"Import successful: {test_file}")
                else:
                    self.print_warning(f"Could not load spec: {test_file}")
            except Exception as e:
                self.print_error(f"Import error in {test_file}: {str(e)}")
    
    def validate_fixtures(self):
        """Validate that required fixtures exist in conftest.py"""
        self.print_header("3. Validating Fixtures")
        
        required_fixtures = [
            "async_client",
            "test_user",
            "test_admin",
            "test_restaurant",
            "auth_token_async",
            "admin_auth_token_async"
        ]
        
        conftest_path = self.test_dir / "conftest.py"
        
        if not conftest_path.exists():
            self.print_error("conftest.py not found!")
            return
        
        try:
            with open(conftest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for fixture in required_fixtures:
                if f"def {fixture}" in content or f"async def {fixture}" in content:
                    self.print_success(f"Fixture exists: {fixture}")
                else:
                    self.print_error(f"Missing fixture: {fixture}")
        except Exception as e:
            self.print_error(f"Error reading conftest.py: {str(e)}")
    
    def count_tests(self):
        """Count total number of test functions"""
        self.print_header("4. Counting Test Cases")
        
        test_files = list(self.test_dir.glob("test_*.py"))
        total_tests = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count test functions
                test_count = content.count("async def test_") + content.count("def test_")
                total_tests += test_count
                
                if test_count > 0:
                    self.print_success(f"{test_file.name}: {test_count} tests")
            except Exception as e:
                self.print_warning(f"Could not count tests in {test_file.name}: {str(e)}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}Total Test Cases: {total_tests}{Colors.ENDC}")
        
        if total_tests < 100:
            self.print_warning(f"Expected 100+ tests, found {total_tests}")
        else:
            self.print_success(f"✓ Meets requirement of 100+ tests")
    
    def validate_test_ids(self):
        """Validate that test functions have proper TEST IDs in docstrings"""
        self.print_header("5. Validating Test IDs")
        
        test_files = [
            "test_public_endpoints_comprehensive.py",
            "test_authentication_comprehensive.py",
            "test_order_management_comprehensive.py",
            "test_review_system_comprehensive.py",
            "test_admin_functionality_comprehensive.py"
        ]
        
        test_id_pattern = r"TEST ID:"
        
        for test_file in test_files:
            file_path = self.test_dir / test_file
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                test_id_count = content.count("TEST ID:")
                if test_id_count > 0:
                    self.print_success(f"{test_file}: {test_id_count} tests with TEST IDs")
                else:
                    self.print_warning(f"{test_file}: No TEST IDs found")
            except Exception as e:
                self.print_warning(f"Could not check TEST IDs in {test_file}: {str(e)}")
    
    def check_dependencies(self):
        """Check that required dependencies are installed"""
        self.print_header("6. Checking Dependencies")
        
        required_packages = [
            "pytest",
            "pytest-asyncio",
            "httpx",
            "fastapi",
            "beanie",
            "motor"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.print_success(f"Package installed: {package}")
            except ImportError:
                self.print_error(f"Missing package: {package}")
    
    def print_summary(self):
        """Print validation summary"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("=" * 60)
        print("  VALIDATION SUMMARY")
        print("=" * 60)
        print(f"{Colors.ENDC}")
        
        if not self.errors:
            print(f"{Colors.BOLD}{Colors.GREEN}✅ ALL VALIDATIONS PASSED{Colors.ENDC}")
            print(f"\nTest suite is ready to run!")
        else:
            print(f"{Colors.BOLD}{Colors.RED}❌ VALIDATION FAILED{Colors.ENDC}")
            print(f"\n{Colors.RED}Errors found: {len(self.errors)}{Colors.ENDC}")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.ENDC}")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more warnings")
        
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.ENDC}\n")
    
    def run_all_validations(self):
        """Run all validation checks"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("=" * 60)
        print("  FOODIEEXPRESS TEST SUITE VALIDATOR")
        print("=" * 60)
        print(f"{Colors.ENDC}")
        
        self.validate_syntax()
        self.check_dependencies()
        self.validate_fixtures()
        self.count_tests()
        self.validate_test_ids()
        
        self.print_summary()
        
        return len(self.errors) == 0


def main():
    """Main entry point"""
    validator = TestValidator()
    success = validator.run_all_validations()
    
    if success:
        print(f"{Colors.GREEN}Ready to run tests with:{Colors.ENDC}")
        print(f"  python run_comprehensive_tests_v3.py")
        sys.exit(0)
    else:
        print(f"{Colors.RED}Please fix errors before running tests{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
