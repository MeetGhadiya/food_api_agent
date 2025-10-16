# 🚀 FoodieExpress Test Suite - Quick Start Guide

## ✅ What's Been Created

Your comprehensive test automation suite is now ready! Here's what you have:

### 📁 Files Created:

```
TESTING/
├── run_comprehensive_tests.py  ✅ Main test suite (30+ tests)
├── check_services.py           ✅ Service health checker
├── RUN_TESTS.bat              ✅ Windows quick-run script
└── README.md                   ✅ Complete documentation
```

## 🎯 Test Coverage

### 9 Test Categories:
1. **Basic Greetings & Help** (3 tests) - 👋 Agent responsiveness
2. **Restaurant Discovery** (4 tests) - 🏪 Search & filter
3. **Menu & Item Inquiry** (4 tests) - 📋 Item search (critical!)
4. **Context Retention** (2 tests) - 🧠 Memory across turns
5. **Ordering Flow** (3 tests) - 🍕 Order placement
6. **Reviews & Ratings** (2 tests) - ⭐ Review system
7. **Error Handling** (3 tests) - 🔥 Edge cases
8. **Multi-Turn Conversations** (3 tests) - 💬 Complex flows
9. **Keyword Routing** (3 tests) - 🔀 Tool selection

**Total: 27 automated tests** covering all critical AI agent functionality!

## 🚦 How to Run Tests

### Method 1: Quick Run (Windows)
```powershell
cd TESTING
.\RUN_TESTS.bat
```

### Method 2: Python Direct
```powershell
cd TESTING
python run_comprehensive_tests.py
```

### Method 3: Check Services First
```powershell
cd TESTING
python check_services.py  # Check if all services are running
python run_comprehensive_tests.py  # Then run tests
```

## 📋 Prerequisites Checklist

Before running tests, ensure these services are running:

- [ ] **MongoDB** - Database accessible
- [ ] **Ollama** - `ollama serve` running
- [ ] **FastAPI Backend** - Port 8000
  ```powershell
  cd food_api
  uvicorn app.main:app --reload
  ```
- [ ] **Flask Agent** - Port 5000
  ```powershell
  cd food_chatbot_agent
  python agent.py
  ```

## 📊 Understanding Results

### Test Output Format:
```
[AI-003-1] Search by Item - Bhel (PRIMARY TOOL TEST) ... RUNNING
  📤 Sending: where can I find bhel?
  🎯 Expected: Contains ['swati'], does not contain ['cuisine']
  📥 Response: Based on my search, Swati Snacks serves bhel...
  ✅ PASSED
```

### Summary Report:
```
📊 Total Tests Run: 27
✅ Passed: 25
❌ Failed: 2
📈 Success Rate: 92.59%
```

### Results File:
- `test_results_YYYYMMDD_HHMMSS.json` - Detailed JSON report

## 🔍 Critical Tests to Watch

### 🎯 AI-003-1: Primary Tool Test
**Most Important Test!**
- User: "where can I find bhel?"
- Must call `search_by_item` tool
- Must NOT ask for cuisine
- This validates the agent's tool selection logic

### 🧠 AI-004-2: Context Retention
- Establishes context, then tests memory
- Agent should remember previous conversation
- Should NOT re-ask "which restaurant?"

### 🔀 AI-009 Series: Keyword Routing
- Tests that keywords trigger correct tools
- "list" → list_restaurants
- "menu" → get_menu
- "where has" → search_by_item

## 🐛 Troubleshooting

### Common Issues:

| Error | Solution |
|-------|----------|
| `CONNECTION ERROR` | Start Flask agent: `python agent.py` |
| `404 Not Found` | Start FastAPI: `uvicorn app.main:app --reload` |
| `Timeout` | Check Ollama is running: `ollama serve` |
| `Empty Response` | Restart agent, check Ollama model loaded |

### Debug Steps:
1. Run `check_services.py` first
2. Check terminal logs for each service
3. Test individual endpoints manually
4. Review `test_results_*.json` for details

## 📈 Next Steps

After running tests:

1. **Review Results** - Check which tests passed/failed
2. **Fix Issues** - Update agent logic or API as needed
3. **Re-run Tests** - Verify fixes work
4. **Add Tests** - Extend with more test cases
5. **Document** - Update test results in project docs

## 🎨 Test Output Colors

- 🟢 **Green (PASSED)** - Test met all criteria
- 🔴 **Red (FAILED)** - Test didn't meet expectations
- 🔵 **Blue (RUNNING)** - Test in progress
- 🟡 **Yellow (WARNING)** - Service issues

## 📝 Adding New Tests

To add a test, edit `run_comprehensive_tests.py`:

```python
run_test(
    "NEW-001",                     # Unique ID
    "Test Description",            # What it tests
    "user message to send",        # Input
    ["must", "contain", "these"],  # Expected keywords
    forbidden_keywords=["not this"] # Should NOT contain
)
```

## 🎯 Success Criteria

### Target Metrics:
- ✅ **90%+ Pass Rate** - Excellent
- ⚠️ **70-89% Pass Rate** - Needs work
- ❌ **<70% Pass Rate** - Critical issues

### Must-Pass Tests:
- All AI-003 tests (Item Search)
- All AI-004 tests (Context Retention)
- All AI-007 tests (Error Handling)

## 🚀 Ready to Test!

You're all set! The test suite will:
- ✅ Automatically test 27 scenarios
- ✅ Validate agent responses
- ✅ Check tool selection logic
- ✅ Test error handling
- ✅ Generate detailed reports

**Run it now:**
```powershell
cd TESTING
python run_comprehensive_tests.py
```

## 📚 Additional Resources

- `README.md` - Full documentation
- `TEST_PLAN_V2.txt` - Complete test plan (100+ tests)
- Test results JSON - Detailed execution data

---

**Happy Testing! 🎉**

Questions? Check the README.md or review the test output for details.
