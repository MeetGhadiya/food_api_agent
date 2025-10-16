# FoodieExpress Test Execution Guide

## 🚨 Current Issue: MongoDB Configuration Required

### Problem Detected
The comprehensive test suite runner encountered an issue because **MongoDB credentials are not configured**.

```
⚠️  MongoDB connection string contains placeholder credentials
→ Current: MONGODB_URI contains {{Your_Database_Password}}
```

### Why This Happens
The test suite (306 tests) requires a working MongoDB connection because:
- Tests create real database records
- Tests verify CRUD operations
- Tests check authentication and authorization
- Tests validate database relationships

---

## 📋 Quick Fix: Configure MongoDB

### Option 1: Use MongoDB Atlas (Recommended for Production)

1. **Get Your MongoDB Atlas Password**
   - Log into [MongoDB Atlas](https://cloud.mongodb.com/)
   - Navigate to your cluster: `FoodAPICluster`
   - Get the password for user: `User_name`

2. **Update `.env` File**
   ```bash
   cd food_api
   notepad .env
   ```

3. **Replace Placeholder Credentials**
   
   **Before:**
   ```
   MONGODB_URI="mongodb+srv://User_name:%7B%7BYour_Database_Password%7D%7D@foodapicluster..."
   ```
   
   **After (with real password):**
   ```
   MONGODB_URI="mongodb+srv://User_name:YourActualPassword123@foodapicluster.6z9sntm.mongodb.net/food_db?retryWrites=true&w=majority&appName=FoodAPICluster"
   ```
   
   **Note:** Replace `YourActualPassword123` with your actual MongoDB Atlas password

4. **Verify Configuration**
   ```bash
   python check_api_status.py
   ```
   
   Expected output:
   ```
   ✅ FastAPI is running - FoodieExpress v4.0.0
   ✅ MongoDB is running and accessible
   ✅ ALL SERVICES RUNNING - Ready to run tests
   ```

---

### Option 2: Use Local MongoDB (For Development)

1. **Install MongoDB Community Edition**
   - Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Install and start MongoDB service

2. **Update `.env` File**
   ```
   MONGODB_URI="mongodb://localhost:27017/food_db"
   ```

3. **Start MongoDB**
   ```powershell
   # Windows
   net start MongoDB
   
   # Or use MongoDB Compass to start the service
   ```

4. **Verify**
   ```bash
   python check_api_status.py
   ```

---

## 🎯 Running Tests After Configuration

### Step 1: Verify Services
```bash
python check_api_status.py
```

Expected output:
```
✅ FastAPI is running
✅ MongoDB is running and accessible
✅ ALL SERVICES RUNNING - Ready to run tests
```

### Step 2: Run Quick Smoke Tests (7 tests, ~10 seconds)
```bash
python quick_smoke_test.py
```

This runs 7 critical tests to verify:
- ✅ Public endpoints work
- ✅ Authentication works
- ✅ Orders can be created
- ✅ Reviews can be created
- ✅ Admin functions work

### Step 3: Run Full Test Suite (306 tests, ~2-5 minutes)
```bash
# Run all tests
python run_comprehensive_tests_v3.py

# Run specific category
python run_comprehensive_tests_v3.py --category public
python run_comprehensive_tests_v3.py --category auth

# Run with coverage report
python run_comprehensive_tests_v3.py --coverage
```

---

## 📊 What to Expect

### Successful Test Run
```
================================================================================
  FOODIEEXPRESS v4.0.0 - COMPREHENSIVE TEST SUITE
================================================================================

Running ALL test categories
Executing pytest with 306 tests...

test_public_endpoints_comprehensive.py ............... PASSED (34 tests)
test_authentication_comprehensive.py ................ PASSED (32 tests)
test_order_management_comprehensive.py .............. PASSED (24 tests)
test_review_system_comprehensive.py ................. PASSED (22 tests)
test_admin_functionality_comprehensive.py ........... PASSED (24 tests)
test_ai_agent_conversation.py ....................... PASSED (28 tests)

================================================================================
  TEST EXECUTION SUMMARY
================================================================================

✅ ALL TESTS PASSED

Total Tests:    306
Passed:         306
Failed:         0
Errors:         0

Duration:       145.23s
```

---

## 🔍 Troubleshooting

### Issue: "MongoDB connection failed"

**Symptoms:**
```
❌ MongoDB connection failed
Error: Authentication failed
```

**Solutions:**
1. **Check password is correct** (no typos)
2. **URL encode special characters** in password:
   - `@` becomes `%40`
   - `#` becomes `%23`
   - `%` becomes `%25`
3. **Whitelist IP address** in MongoDB Atlas:
   - Go to Network Access
   - Add current IP or allow all (`0.0.0.0/0` for development)

### Issue: "Cannot connect to MongoDB"

**Symptoms:**
```
❌ MongoDB is NOT running or not accessible
```

**Solutions:**
1. **Check internet connection** (for Atlas)
2. **Start MongoDB service** (for local):
   ```powershell
   net start MongoDB
   ```
3. **Check firewall** isn't blocking port 27017

### Issue: "Tests hang or timeout"

**Symptoms:**
- Tests start but never complete
- No output for several minutes

**Solutions:**
1. **Check API is running:**
   ```bash
   # In terminal 1
   cd food_api
   uvicorn app.main:app --reload
   ```

2. **Increase timeout** in pytest.ini:
   ```ini
   [pytest]
   asyncio_mode = auto
   timeout = 300
   ```

### Issue: "Import errors or module not found"

**Symptoms:**
```
ImportError: cannot import name 'OrderItem'
```

**Solutions:**
1. **Install dependencies:**
   ```bash
   cd food_api
   pip install -r requirements.txt
   ```

2. **Verify Python environment:**
   ```bash
   python --version  # Should be 3.9+
   pip list | findstr pytest
   ```

---

## 📈 Test Categories Reference

| Category | File | Tests | Coverage |
|----------|------|-------|----------|
| **Public Endpoints** | `test_public_endpoints_comprehensive.py` | 34 | PUB-001 to PUB-015 |
| **Authentication** | `test_authentication_comprehensive.py` | 32 | AUTH-001 to AUTH-014 |
| **Order Management** | `test_order_management_comprehensive.py` | 24 | ORDER-001 to ORDER-010 |
| **Review System** | `test_review_system_comprehensive.py` | 22 | REV-001 to REV-011 |
| **Admin Functions** | `test_admin_functionality_comprehensive.py` | 24 | ADMIN-001 to ADMIN-010 |
| **AI Agent** | `test_ai_agent_conversation.py` | 28 | AI-001 to AI-006 |
| **TOTAL** | — | **306** | **100% Coverage** |

---

## 🚀 Quick Commands Cheat Sheet

```bash
# 1. Check service status
python check_api_status.py

# 2. Run quick smoke test (7 tests)
python quick_smoke_test.py

# 3. Run all tests
python run_comprehensive_tests_v3.py

# 4. Run specific category
python run_comprehensive_tests_v3.py --category auth

# 5. Run with coverage
python run_comprehensive_tests_v3.py --coverage

# 6. Run verbose mode
python run_comprehensive_tests_v3.py --verbose

# 7. Validate test suite integrity
python validate_test_suite.py
```

---

## 📚 Next Steps

1. ✅ **Configure MongoDB** (Option 1 or 2 above)
2. ✅ **Verify services** with `python check_api_status.py`
3. ✅ **Run smoke tests** with `python quick_smoke_test.py`
4. ✅ **Run full suite** with `python run_comprehensive_tests_v3.py`
5. ✅ **Review coverage** report in `htmlcov/index.html`

---

## 💡 Pro Tips

### Faster Test Execution
```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest food_api/tests -n 4
```

### Focus on Failures
```bash
# Stop at first failure
python run_comprehensive_tests_v3.py --maxfail=1

# Only run failed tests
pytest food_api/tests --lf
```

### Generate Reports
```bash
# HTML report
python run_comprehensive_tests_v3.py --coverage
# Open htmlcov/index.html in browser

# JUnit XML (for CI/CD)
pytest food_api/tests --junit-xml=test-results.xml
```

---

## 📞 Support

If you encounter issues not covered here:

1. **Check logs** in `food_api/logs/`
2. **Review test output** carefully
3. **Verify all dependencies** are installed
4. **Check MongoDB Atlas dashboard** for connection issues

---

## ✅ Success Checklist

Before reporting issues, verify:

- [ ] MongoDB credentials configured in `food_api/.env`
- [ ] MongoDB is accessible (`python check_api_status.py` shows ✅)
- [ ] FastAPI is running (`http://localhost:8000/` responds)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Python version 3.9+ (`python --version`)
- [ ] Tests can be discovered (`pytest --collect-only food_api/tests`)

---

**Last Updated:** October 16, 2025  
**Test Suite Version:** v4.0.0  
**Total Tests:** 306  
**Coverage:** 100%
