# 🧪 Automated Testing Guide

## Overview

This project includes comprehensive automated tests for the FoodieExpress API. All tests are located in `food_api/tests/` and can be run automatically.

---

## 🚀 Quick Start

### Option 1: Interactive Test Runner (Recommended)
```powershell
python run_automated_tests.py
```

This will show you a menu with options:
1. Run all tests (quick)
2. Run all tests with coverage
3. Run specific test category
4. Check dependencies only
5. Exit

### Option 2: Batch File (Windows)
```powershell
.\RUN_TESTS.bat
```

Runs all tests quickly without prompts.

### Option 3: Direct pytest Command
```powershell
cd food_api
python -m pytest -v tests/
```

---

## 📋 Test Categories

### 1. **Authentication Tests** (`test_api_auth.py`)
Tests for user registration, login, and JWT token authentication.

**Coverage:**
- User registration (valid/invalid data)
- User login (correct/incorrect credentials)
- JWT token generation and validation
- Password hashing
- Email validation

**Run only auth tests:**
```powershell
cd food_api
python -m pytest tests/test_api_auth.py -v
```

### 2. **Public API Tests** (`test_api_public.py`)
Tests for publicly accessible endpoints (no authentication required).

**Coverage:**
- Restaurant listing
- Restaurant search by area
- Restaurant search by cuisine
- Menu item retrieval
- Public endpoint availability

**Run only public tests:**
```powershell
cd food_api
python -m pytest tests/test_api_public.py -v
```

### 3. **Review API Tests** (`test_api_reviews.py`)
Tests for restaurant review functionality.

**Coverage:**
- Create reviews (authenticated)
- Get reviews for restaurant
- Update reviews (owner only)
- Delete reviews (owner/admin)
- Review validation
- Rating constraints (1-5 stars)

**Run only review tests:**
```powershell
cd food_api
python -m pytest tests/test_api_reviews.py -v
```

### 4. **Main API Tests** (`test_main_api.py`)
Tests for core API functionality and endpoints.

**Coverage:**
- Health check endpoint
- API versioning
- Error handling
- CORS configuration
- Database connection

**Run only main tests:**
```powershell
cd food_api
python -m pytest tests/test_main_api.py -v
```

### 5. **Security Tests** (`test_security.py`)
Tests for security features and vulnerability prevention.

**Coverage:**
- Password strength validation
- SQL injection prevention
- XSS protection
- Authentication bypass attempts
- Role-based access control (RBAC)
- Admin-only endpoint protection

**Run only security tests:**
```powershell
cd food_api
python -m pytest tests/test_security.py -v
```

---

## 📊 Coverage Reports

### Generate Coverage Report
```powershell
cd food_api
python -m pytest --cov=app --cov-report=html --cov-report=term tests/
```

### View Coverage Report
After running coverage, open:
```
food_api/htmlcov/index.html
```

This shows:
- Lines covered by tests
- Lines not covered
- Coverage percentage per file
- Branch coverage

---

## 🔧 Test Configuration

### pytest.ini
Located in `food_api/pytest.ini`, this file configures pytest behavior:

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### conftest.py
Located in `food_api/tests/conftest.py`, this provides:
- Test fixtures (reusable test data)
- Database initialization
- Test user creation
- Authentication tokens
- Sample restaurants

---

## 📝 Test Fixtures Available

### User Fixtures
- `test_user` - Regular user for testing
- `test_admin` - Admin user for testing
- `auth_token` - JWT token for authenticated requests

### Data Fixtures
- `test_restaurant` - Sample restaurant
- `sample_restaurant` - Alias for test_restaurant

### Client Fixtures
- `client` - Synchronous HTTP client
- `async_client` - Asynchronous HTTP client

---

## 🎯 Writing New Tests

### Example Test Structure

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_example(async_client):
    """Test description"""
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = await async_client.post("/endpoint", json=data)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### Test Naming Convention
- File: `test_<feature>.py`
- Function: `test_<what_it_tests>`
- Use descriptive names: `test_user_can_login_with_valid_credentials`

---

## 🐛 Debugging Failed Tests

### Run with Verbose Output
```powershell
cd food_api
python -m pytest -vv tests/
```

### Run with Print Statements
```powershell
cd food_api
python -m pytest -s tests/
```

### Run Specific Test
```powershell
cd food_api
python -m pytest tests/test_api_auth.py::test_user_registration -v
```

### Stop on First Failure
```powershell
cd food_api
python -m pytest -x tests/
```

### Show Local Variables on Failure
```powershell
cd food_api
python -m pytest -l tests/
```

---

## 📦 Required Dependencies

Make sure these packages are installed:

```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

Check dependencies:
```powershell
python run_automated_tests.py
# Then select option 4
```

---

## 🔄 Continuous Integration

### GitHub Actions (Future)
You can set up GitHub Actions to run tests automatically on every push:

```yaml
# .github/workflows/tests.yml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd food_api
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx pytest-cov
      - name: Run tests
        run: |
          cd food_api
          pytest tests/ -v
```

---

## 📈 Test Metrics

Current test coverage (example):
- **Total Tests**: ~25-30 tests
- **Test Files**: 5
- **Code Coverage Target**: >80%
- **Execution Time**: ~10-30 seconds

---

## ⚡ Performance Testing

### Benchmark Tests (Future Enhancement)
```powershell
cd food_api
python -m pytest --benchmark-only tests/
```

---

## 🛡️ Security Testing Checklist

- ✅ Password hashing (bcrypt)
- ✅ JWT token validation
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CORS configuration
- ✅ Role-based access control
- ✅ Input validation
- ✅ Authentication bypass prevention

---

## 📞 Need Help?

If tests fail:

1. **Check database connection** - Make sure MongoDB is running
2. **Check .env file** - Verify credentials are correct
3. **Check dependencies** - Run `pip install -r requirements.txt`
4. **Read error messages** - They usually point to the problem
5. **Check test output** - Use `-v` flag for verbose output

---

## 🎉 Best Practices

1. **Run tests before committing** - Catch bugs early
2. **Write tests for new features** - Maintain coverage
3. **Keep tests independent** - No test should depend on another
4. **Use fixtures** - Don't repeat test data setup
5. **Test edge cases** - Not just happy paths
6. **Mock external services** - Tests should be isolated

---

## 📅 Test Execution Schedule

**Recommended:**
- Before every commit
- Before every pull request
- After every deployment
- Daily (in CI/CD pipeline)

---

## 🏆 Test Success Criteria

A successful test run should show:
- ✅ All tests passed (green)
- ✅ No warnings or errors
- ✅ Coverage above 80%
- ✅ Fast execution (<1 minute)

---

**Happy Testing! 🧪✨**
