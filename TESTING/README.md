# FoodieExpress - Comprehensive Test Suite

## Overview

This directory contains automated tests for the FoodieExpress AI-powered food delivery platform. The test suite validates both API functionality and AI agent conversational flows.

## Test Coverage

### Categories Tested:

1. **Basic Greetings & Help** - Agent responsiveness and capability description
2. **Restaurant Discovery** - Listing, filtering, and searching restaurants
3. **Menu & Item Inquiry** - Item search and menu retrieval
4. **Context Retention** - Multi-turn conversation memory
5. **Ordering Flow** - Order placement and confirmation
6. **Reviews & Ratings** - Review retrieval and submission
7. **Error Handling** - Graceful failure and edge cases
8. **Multi-Turn Conversations** - Complex conversation flows
9. **Keyword Routing** - Proper tool selection based on user input

## Prerequisites

Before running the tests, ensure all services are running:

1. **MongoDB** - Database must be accessible
2. **FastAPI Backend** - Running on `http://localhost:8000`
3. **Flask Agent** - Running on `http://localhost:5000`
4. **Ollama** - LLM service running locally

## Quick Start

### 1. Start All Services

#### Terminal 1 - Start FastAPI Backend:
```powershell
cd food_api
..\..venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

#### Terminal 2 - Start Flask Agent:
```powershell
cd food_chatbot_agent
..\..venv\Scripts\python.exe agent.py
```

#### Terminal 3 - Ensure Ollama is Running:
```powershell
ollama serve
```

### 2. Run the Tests

#### Terminal 4 - Run Test Suite:
```powershell
cd TESTING
python run_comprehensive_tests.py
```

## Understanding Test Output

### Test Format:
```
[TEST-ID] Description ... RUNNING
  📤 Sending: User message
  🎯 Expected: Contains [keywords], does not contain [forbidden]
  📥 Response: Agent response (truncated)
  ✅ PASSED / ❌ FAILED
```

### Result Summary:
- **Total Tests** - Number of tests executed
- **Passed** - Tests that met all criteria
- **Failed** - Tests that failed expectations
- **Success Rate** - Percentage of passing tests

### Test Results File:
After each run, a JSON report is saved:
- `test_results_YYYYMMDD_HHMMSS.json`

## Test Configuration

You can modify these variables in `run_comprehensive_tests.py`:

```python
AGENT_URL = "http://localhost:5000/chat"  # Flask agent endpoint
API_BASE_URL = "http://localhost:8000"     # FastAPI backend
```

## Adding New Tests

To add a new test case, use the `run_test()` function:

```python
run_test(
    "TEST-ID",                    # Unique test identifier
    "Test Description",           # What this test validates
    "user message",               # Message to send to agent
    ["expected", "keywords"],     # Must be in response
    forbidden_keywords=["bad"]    # Must NOT be in response
)
```

## Test Debugging

### If Tests Fail:

1. **Check Services** - Ensure all services are running and healthy
2. **Check Logs** - Review agent and API logs for errors
3. **Check Database** - Verify data exists (restaurants, etc.)
4. **Network** - Ensure no firewall blocking localhost connections

### Common Issues:

| Issue | Solution |
|-------|----------|
| Connection Error | Start the Flask agent service |
| 404 Not Found | Start the FastAPI backend |
| Timeout | Increase timeout in `send_message()` |
| Empty Response | Check Ollama is running |
| Context Loss | Review agent's history handling |

## Test Categories Detail

### AI-001: Basic Greetings
- Tests agent responsiveness
- Validates help text
- Checks capability listing

### AI-002: Restaurant Discovery
- List all restaurants
- Filter by cuisine
- Get specific restaurant
- Handle non-existent restaurant

### AI-003: Item Search (Critical)
- **Primary tool test**: "where can I find bhel?" must use `search_by_item`
- Must NOT ask for cuisine
- Should return relevant restaurants

### AI-004: Context Retention
- Establishes context with first query
- Validates memory in follow-up queries
- Should not re-ask for known information

### AI-005: Ordering Flow
- Tests order initiation
- Validates confirmation flow
- Checks for unimplemented features

### AI-006: Reviews
- Retrieves restaurant reviews
- Initiates review submission flow

### AI-007: Error Handling
- Invalid input handling
- Non-existent data queries
- Graceful degradation

### AI-008: Multi-Turn
- Complex conversation flows
- Context across multiple exchanges
- Reference resolution ("the first one")

### AI-009: Keyword Routing
- "list" → list_restaurants tool
- "menu" → get_menu tool
- "where has X" → search_by_item tool

## CI/CD Integration

To integrate with CI/CD, run:

```bash
python run_comprehensive_tests.py
exit_code=$?  # 0 if all passed, 1 if any failed
```

## Reporting Issues

When reporting test failures, include:
1. Test ID that failed
2. Expected vs actual response
3. Relevant logs from agent/API
4. Test results JSON file

## Next Steps

After running tests:
1. Review failed tests in terminal output
2. Check `test_results_*.json` for details
3. Fix issues in agent or API
4. Re-run tests to verify fixes

## Additional Resources

- [Full Test Plan](../TEST_PLAN_V2.txt)
- [API Documentation](../food_api/README.md)
- [Agent Documentation](../food_chatbot_agent/WEB_README.md)
