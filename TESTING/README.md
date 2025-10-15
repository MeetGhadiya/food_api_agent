# FoodieExpress Comprehensive Test Suite

## Overview
This folder contains automated test scripts for the FoodieExpress AI Agent. Tests validate conversational flow, tool routing, context handling, and error handling.

## Test Output Format
```
[3.2] show me the menu ... RUNNING
  📤 Sending: show me the menu
  🎯 Expected: CONTEXT TEST: Should remember Swati Snacks
  📥 Response: I couldn't find a restaurant named 'The Menu'. Would you like me to list all available restaurants?
  ✅ PASSED
```

## Files
- **run_comprehensive_tests.py** - Main test suite with 40+ test cases

## Prerequisites
Before running tests, ensure these services are running:

1. **Ollama** - AI model (llama3.2:3b)
2. **FastAPI Backend** - Port 8000
   ```bash
   cd food_api
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. **Flask Agent** - Port 5000
   ```bash
   cd food_api_agent-1
   python agent_simple.py
   ```

## How to Run Tests

### Quick Start
```bash
# Navigate to project root
cd food_api_agent-1

# Run all tests
python TESTING/run_comprehensive_tests.py
```

### Expected Output
```
================================================================================
                       FoodieExpress Agent - Comprehensive Test Suite
================================================================================
⏰ Test Started: 2025-10-15 17:00:00
🌐 Agent URL: http://localhost:5000/chat
👤 Test User ID: test_user_xxxxx

🔍 Checking agent health...
✅ Agent is running!

================================================================================
                       Category 1: Basic Greetings & Help 👋
================================================================================

[1.1] Basic Greeting ... RUNNING
  📤 Sending: hello
  🎯 Expected: Contains ['foodie', 'welcome', 'help']
  📥 Response: 👋 Hello! Welcome to FoodieExpress...
  ✅ PASSED

... (more tests)

================================================================================
                       Test Summary Report
================================================================================
📊 Total Tests Run: 40
✅ Passed: 38
❌ Failed: 2
📈 Success Rate: 95.00% - EXCELLENT

================================================================================
                       Testing Complete!
================================================================================
```

## Test Categories

### Category 1: Basic Greetings & Help 👋
- **1.1** - Basic greeting response
- **1.2** - Capabilities check
- **1.3** - Help request

### Category 2: Restaurant Discovery 🏪
- **2.1** - List all restaurants
- **2.2** - Filter by cuisine (Gujarati)
- **2.3** - Filter by cuisine (Italian)
- **2.4** - Get restaurant by name
- **2.5** - Restaurant details

### Category 3: Menu & Item Inquiry 📋
- **3.1** - Search by item (Bhel)
- **3.2a** - Establish context
- **3.2b** - Context test (should remember previous restaurant)
- **3.3** - Search by item (Pizza)
- **3.4** - Item not available

### Category 4: Ordering Flow 🍕
- **4.1** - Ambiguous order (no restaurant specified)
- **4.2** - Specific order request (should ask confirmation)
- **4.3** - Check order placement capability

### Category 5: Cuisine & Location Search 🌍
- **5.1** - South Indian cuisine
- **5.2** - Non-existent cuisine

### Category 6: Reviews & Ratings ⭐
- **6.1** - Get reviews for restaurant
- **6.2** - Check review submission capability

### Category 7: Error Handling & Edge Cases 🔥
- **7.1** - Non-existent restaurant
- **7.2** - Gibberish input
- **7.3** - Empty-like query

### Category 8: Multi-turn Conversations 💬
- **8.1a/b** - Multi-turn cuisine query
- **8.2a/b** - Multi-turn item query

### Category 9: Tool Routing Verification 🔧
- **9.1** - get_all_restaurants() tool
- **9.2** - search_by_cuisine() tool
- **9.3** - search_by_item() tool
- **9.4** - get_restaurant_by_name() tool

### Category 10: Response Quality Checks 📝
- **10.1** - Friendly tone check
- **10.2** - Emoji usage check

### Category 11: API Error Handling 🚨
- Requires manual service interruption

### Category 12: Business Logic Validation ✅
- **12.1** - Price information
- **12.2** - Restaurant location

## Understanding Test Results

### Pass Criteria
A test passes when:
- ✅ All expected keywords are found in the response
- ✅ No forbidden keywords are present
- ✅ Agent responds without errors

### Fail Indicators
- ❌ Missing expected keywords
- ❌ Forbidden keywords found
- ❌ Connection errors
- ❌ Timeout errors

## Known Issues to Test For

### Context Handling (Test 3.2b, 8.1b, 8.2b)
**Expected Behavior:**
```
User: "tell me about Swati Snacks"
Agent: [shows Swati Snacks details]
User: "show me the menu"
Agent: [shows Swati Snacks menu]  ← Should remember context
```

**Current Limitation:**
- Agent may search for "The Menu" restaurant instead of using context
- Simple keyword matching, no deep NLU

### Order Confirmation (Test 4.2)
**Expected Behavior:**
```
User: "order 2 Masala Thepla from Swati Snacks"
Agent: "Confirm: 2x Masala Thepla from Swati Snacks. Is this correct? (yes/no)"
```

**Current Limitation:**
- No confirmation gate implemented yet (TASK 2)
- place_order tool not implemented

### Review Submission (Test 6.2)
**Current Limitation:**
- Agent cannot submit reviews (no review tools implemented)
- Should explain this limitation gracefully

## Customizing Tests

### Adding New Tests
```python
run_test(
    "X.Y",                              # Test ID
    "Test Description",                 # Description
    "user message to send",            # Message
    ["keyword1", "keyword2"],          # Expected keywords
    forbidden_keywords=["bad"],        # Keywords that should NOT appear
    context_description="Optional"     # Custom expectation message
)
```

### Resetting Session
```python
reset_session()  # Clears conversation history
```

### Example: Multi-turn Test
```python
reset_session()
run_test("T1", "Setup", "tell me about Swati Snacks", ["swati"])
run_test("T2", "Context", "show menu", ["menu"], 
         context_description="Should remember Swati Snacks")
```

## Troubleshooting

### "Agent not responding"
```bash
# Check if agent is running
curl http://localhost:5000/health

# Restart agent if needed
python agent_simple.py
```

### "CONNECTION ERROR"
- Verify FastAPI is running on port 8000
- Verify MongoDB Atlas connection
- Check .env file has correct credentials

### Tests taking too long
- Each test has 45-second timeout
- Long responses from Ollama are normal
- Consider running subset of tests for faster iteration

## CI/CD Integration

### Exit Codes
- `0` - All tests passed
- `1` - One or more tests failed

### Example GitHub Actions
```yaml
- name: Run Agent Tests
  run: |
    python TESTING/run_comprehensive_tests.py
  continue-on-error: false
```

## Test Data
- **User ID**: Randomly generated UUID per test run
- **Session History**: Maintained across tests (use `reset_session()` to clear)
- **Conversation Memory**: Each test inherits previous conversation context unless reset

## Success Metrics
- **90-100%** - EXCELLENT ✅
- **75-89%** - GOOD ⚠️
- **50-74%** - NEEDS IMPROVEMENT ⚠️
- **< 50%** - CRITICAL ❌

## Next Steps After Testing
1. Review failed tests
2. Identify patterns in failures
3. Implement fixes (TASK 2: order confirmation, TASK 3: context handling)
4. Re-run tests
5. Document known issues

## Contributing
When adding new features:
1. Write test cases first
2. Run existing tests to ensure no regressions
3. Update this README with new test categories

---

**Last Updated:** October 15, 2025  
**Test Framework:** Python requests + custom test runner  
**Total Tests:** 40+ test cases
