# 📋 FoodieExpress Agent - Complete Test Cases Documentation

**Version:** 2.0  
**Date:** October 15, 2025  
**Total Test Cases:** 40+  
**Test Categories:** 12  

---

## 📑 Table of Contents

1. [Test Overview](#test-overview)
2. [Test Categories](#test-categories)
3. [Detailed Test Cases](#detailed-test-cases)
4. [Expected Results](#expected-results)
5. [Known Issues](#known-issues)
6. [Test Execution Guide](#test-execution-guide)

---

## 🎯 Test Overview

### Purpose
This test suite validates the FoodieExpress chatbot agent's conversational capabilities, tool routing, context handling, and business logic implementation.

### Scope
- **Conversational Testing:** Natural language understanding and responses
- **Tool Routing:** Correct API calls based on user intent
- **Context Handling:** Multi-turn conversation memory
- **Business Logic:** Prices, locations, ordering flow
- **Error Handling:** Graceful failure scenarios

### Success Criteria
- **90-100%:** EXCELLENT ✅ - Production ready
- **75-89%:** GOOD ⚠️ - Minor improvements needed
- **50-74%:** NEEDS IMPROVEMENT ⚠️ - Significant issues
- **<50%:** CRITICAL ❌ - Major fixes required

---

## 📊 Test Categories

| # | Category | Tests | Priority | Description |
|---|----------|-------|----------|-------------|
| 1 | Basic Greetings & Help 👋 | 3 | HIGH | Conversational basics |
| 2 | Restaurant Discovery 🏪 | 5 | HIGH | Listing & filtering |
| 3 | Menu & Item Inquiry 📋 | 5 | HIGH | Search & context |
| 4 | Ordering Flow 🍕 | 3 | MEDIUM | Order requests |
| 5 | Cuisine & Location 🌍 | 2 | MEDIUM | Filters |
| 6 | Reviews & Ratings ⭐ | 2 | LOW | Review handling |
| 7 | Error Handling 🔥 | 3 | HIGH | Graceful failures |
| 8 | Multi-turn Conversations 💬 | 4 | HIGH | Context retention |
| 9 | Tool Routing 🔧 | 4 | HIGH | API call validation |
| 10 | Response Quality 📝 | 2 | MEDIUM | Tone & formatting |
| 11 | API Error Handling 🚨 | 1 | HIGH | Service failures |
| 12 | Business Logic ✅ | 2 | MEDIUM | Data validation |

---

## 📝 Detailed Test Cases

### Category 1: Basic Greetings & Help 👋

#### Test 1.1: Basic Greeting
**Input:** `hello`

**Expected Keywords:** `foodie`, `welcome`, `help`

**Forbidden Keywords:** None

**Purpose:** Verify agent responds warmly to greetings

**Expected Behavior:**
- Agent introduces itself as FoodieExpress assistant
- Welcomes the user
- Offers help or guidance
- Uses friendly tone and emojis

**Sample Expected Response:**
```
👋 Hello! Welcome to FoodieExpress! I'm your friendly chatbot assistant 🍴. 
How can I help you today?
```

---

#### Test 1.2: Capabilities Check
**Input:** `what can you do?`

**Expected Keywords:** `restaurant`, `search`

**Forbidden Keywords:** None

**Purpose:** Verify agent explains its capabilities clearly

**Expected Behavior:**
- Lists main functions (browse, search, menu, order)
- Mentions restaurant discovery features
- Provides examples of what it can do
- Invites follow-up questions

**Sample Expected Response:**
```
🤔 I can help you with:
1. Find restaurants and browse options
2. Search by cuisine or food item
3. Show restaurant menus
4. Assist with orders
```

---

#### Test 1.3: Help Request
**Input:** `help me`

**Expected Keywords:** `restaurant`, `food`, `order`

**Forbidden Keywords:** None

**Purpose:** Verify agent provides helpful guidance

**Expected Behavior:**
- Asks clarifying questions
- Offers multiple assistance options
- Shows willingness to help
- Provides concrete examples

---

### Category 2: Restaurant Discovery 🏪

#### Test 2.1: List All Restaurants
**Input:** `list all restaurants`

**Expected Keywords:** `swati snacks`, `agashiye`

**Forbidden Keywords:** `error`, `sorry`

**Tool Used:** `get_all_restaurants()`

**Purpose:** Verify agent can retrieve and display all restaurants

**Expected Behavior:**
- Calls `get_all_restaurants()` API
- Displays all 7 restaurants from database
- Shows name, location, cuisine for each
- Formats output clearly with emojis

**Sample Expected Response:**
```
Here are the restaurants I found! 🏪

• **Swati Snacks** in Ashram Road, Ahmedabad (Cuisine: Gujarati)
• **Agashiye The House of MG** in Lal Darwaja, Ahmedabad (Cuisine: Gujarati)
• **PATEL & SONS** in Maninagar, Ahmedabad (Cuisine: Gujarati)
...
```

---

#### Test 2.2: Filter by Cuisine - Gujarati
**Input:** `show me gujarati restaurants`

**Expected Keywords:** `swati snacks`, `gujarati`

**Forbidden Keywords:** `italian`, `south indian`

**Tool Used:** `search_by_cuisine("Gujarati")`

**Purpose:** Verify cuisine filtering works correctly

**Expected Behavior:**
- Calls `search_by_cuisine()` with "Gujarati"
- Returns only Gujarati restaurants
- Excludes other cuisines
- Shows relevant details

**Expected Restaurants:**
1. Swati Snacks
2. Agashiye The House of MG
3. PATEL & SONS

---

#### Test 2.3: Filter by Cuisine - Italian
**Input:** `I want italian food`

**Expected Keywords:** `italian`, `manek chowk pizza`

**Forbidden Keywords:** `gujarati`

**Tool Used:** `search_by_cuisine("Italian")`

**Purpose:** Verify natural language cuisine extraction

**Expected Behavior:**
- Extracts "Italian" from casual request
- Calls appropriate API
- Returns only Italian restaurants
- Handles natural language variations

**Expected Restaurants:**
1. Manek Chowk Pizza

---

#### Test 2.4: Get Restaurant by Name
**Input:** `tell me about Swati Snacks`

**Expected Keywords:** `swati snacks`, `menu`

**Forbidden Keywords:** `not found`

**Tool Used:** `get_restaurant_by_name("Swati Snacks")`

**Purpose:** Verify restaurant name lookup

**Expected Behavior:**
- Extracts restaurant name correctly
- Calls `get_restaurant_by_name()` API
- Shows restaurant details
- Displays menu items with prices
- Shows location and cuisine

**Sample Expected Response:**
```
🏪 **Swati Snacks**
📍 Location: Ashram Road, Ahmedabad
🍴 Cuisine: Gujarati

📋 **Menu:**
- Masala Thepla - ₹50
- Bhel Puri - ₹40
- Sev Puri - ₹45
...
```

---

#### Test 2.5: Restaurant Details
**Input:** `what's at Honest Restaurant?`

**Expected Keywords:** `honest restaurant`, `menu`

**Forbidden Keywords:** None

**Tool Used:** `get_restaurant_by_name("Honest Restaurant")`

**Purpose:** Verify alternative phrasing for restaurant lookup

**Expected Behavior:**
- Understands "what's at" means "show details for"
- Correctly identifies restaurant name
- Shows menu and details

---

### Category 3: Menu & Item Inquiry 📋

#### Test 3.1: Search by Item - Bhel
**Input:** `which restaurant has bhel?`

**Expected Keywords:** `swati snacks`

**Forbidden Keywords:** `cuisine`, `what cuisine`

**Tool Used:** `search_by_item("bhel")`

**Purpose:** Verify item-based search functionality

**Expected Behavior:**
- Extracts item name "bhel" from question
- Calls `search_by_item()` API
- Returns restaurants serving that item
- Shows relevant menu details

**Expected Restaurants:**
1. Swati Snacks (has "Bhel Puri")

---

#### Test 3.2a: Establish Context - Tell About Restaurant
**Input:** `tell me about Swati Snacks`

**Expected Keywords:** `swati snacks`, `menu`

**Purpose:** Set up context for next test

**Expected Behavior:**
- Shows Swati Snacks details
- Displays menu
- Stores in conversation history

---

#### Test 3.2b: Context Test - Menu Request
**Input:** `show me the menu`

**Expected Context:** Should remember Swati Snacks from previous message

**Tool Used:** Should use context, NOT search for restaurant named "The Menu"

**Purpose:** **CRITICAL** - Verify context retention in multi-turn conversation

**Expected Behavior:**
- Agent remembers user asked about Swati Snacks
- Shows Swati Snacks menu again
- Does NOT search for restaurant named "The Menu"
- Uses conversation history

**Known Issue:** ⚠️ Agent may fail this test due to simple keyword matching without full context awareness

---

#### Test 3.3: Menu with Specific Item
**Input:** `does Agashiye have dal?`

**Expected Keywords:** `agashiye`, `dal`

**Purpose:** Verify item availability query

**Expected Behavior:**
- Looks up Agashiye menu
- Checks for dal-related items
- Provides yes/no answer with details

---

#### Test 3.4: Price Inquiry
**Input:** `how much is thepla at Swati Snacks?`

**Expected Keywords:** `thepla`, `50`, `₹`

**Purpose:** Verify price information retrieval

**Expected Behavior:**
- Identifies restaurant (Swati Snacks)
- Finds item (Masala Thepla)
- Shows price (₹50)

---

#### Test 3.5: Menu Item Details
**Input:** `what food does PATEL & SONS serve?`

**Expected Keywords:** `patel`, `menu`

**Purpose:** Verify menu display for specific restaurant

---

### Category 4: Ordering Flow 🍕

#### Test 4.1: Simple Order Request
**Input:** `I want to order masala thepla`

**Expected Keywords:** `swati snacks`, `masala thepla`, `order`

**Purpose:** Verify order processing

**Expected Behavior:**
- Identifies item (Masala Thepla)
- Finds restaurant serving it (Swati Snacks)
- Either processes order OR explains limitation
- Provides clear next steps

**Note:** Agent may not have `place_order()` tool implemented yet

---

#### Test 4.2: Order Confirmation
**Input:** `order 2 Masala Thepla from Swati Snacks`

**Expected Keywords:** `confirm`, `2`, `masala thepla`, `correct`

**Purpose:** **IMPORTANT** - Verify confirmation gate before placing order

**Expected Behavior:**
- Agent should ask: "Confirm: 2x Masala Thepla from Swati Snacks. Is this correct? (yes/no)"
- Should NOT place order immediately
- Should wait for user confirmation

**Known Issue:** ⚠️ Confirmation gate not implemented - TASK 2

---

#### Test 4.3: Order Clarification
**Input:** `I want bhel`

**Expected Keywords:** `swati snacks`, `bhel`

**Purpose:** Verify agent clarifies ambiguous orders

**Expected Behavior:**
- Identifies multiple restaurants with bhel (if any)
- Asks user to clarify which restaurant
- Provides options

---

### Category 5: Cuisine & Location 🌍

#### Test 5.1: Location-based Search
**Input:** `restaurants in Maninagar`

**Expected Keywords:** `maninagar`, `patel`

**Purpose:** Verify location filtering

**Expected Behavior:**
- Filters restaurants by area
- Shows only Maninagar restaurants
- Lists PATEL & SONS

---

#### Test 5.2: Combined Cuisine + Location
**Input:** `gujarati food in Ashram Road`

**Expected Keywords:** `swati snacks`, `gujarati`, `ashram road`

**Purpose:** Verify multiple filter criteria

---

### Category 6: Reviews & Ratings ⭐

#### Test 6.1: Show Reviews
**Input:** `show me reviews for Swati Snacks`

**Expected Keywords:** `swati snacks`, `review`, `rating`

**Purpose:** Verify review retrieval

**Expected Behavior:**
- Calls `get_reviews()` API
- Shows review text, rating, username
- Formats clearly

---

#### Test 6.2: Submit Review
**Input:** `I want to leave a review for Honest Restaurant`

**Expected Keywords:** `review`, `honest restaurant`

**Purpose:** Verify review submission handling

**Expected Behavior:**
- Acknowledges review request
- Explains authentication requirement OR
- Explains feature limitation
- Does NOT submit anonymous reviews

**Note:** Agent may not have `submit_review()` tool implemented

---

### Category 7: Error Handling 🔥

#### Test 7.1: Invalid Restaurant
**Input:** `tell me about XYZ Restaurant`

**Expected Keywords:** `not found`, `couldn't find`, `don't have`

**Forbidden Keywords:** `error`, `crash`

**Purpose:** Verify graceful handling of non-existent restaurants

**Expected Behavior:**
- Returns friendly "not found" message
- Suggests alternatives
- Offers to show available restaurants
- Does NOT crash or show error messages

---

#### Test 7.2: Ambiguous Request
**Input:** `I want food`

**Expected Keywords:** `cuisine`, `looking for`, `help`

**Purpose:** Verify agent asks clarifying questions

**Expected Behavior:**
- Recognizes ambiguous request
- Asks clarifying questions
- Offers options
- Guides user

---

#### Test 7.3: Invalid Item
**Input:** `which restaurant has unicorn meat?`

**Expected Keywords:** `not found`, `don't have`, `couldn't find`

**Forbidden Keywords:** `error`

**Purpose:** Verify graceful handling of non-existent items

---

### Category 8: Multi-turn Conversations 💬

#### Test 8.1a: List Restaurants (Setup)
**Input:** `list gujarati restaurants`

**Expected Keywords:** `swati snacks`, `agashiye`, `patel`

**Purpose:** Set up context for follow-up question

---

#### Test 8.1b: Follow-up Question
**Input:** `tell me more about the first one`

**Expected Context:** Should remember the list and identify "first one" as Swati Snacks

**Expected Keywords:** `swati snacks`, `menu`

**Purpose:** **CRITICAL** - Verify agent tracks conversation context

**Known Issue:** ⚠️ Agent may ask "which restaurant?" instead of using context

---

#### Test 8.2a: Get Restaurant Details (Setup)
**Input:** `tell me about Agashiye`

**Expected Keywords:** `agashiye`, `menu`

**Purpose:** Set up context for follow-up

---

#### Test 8.2b: Follow-up About Same Restaurant
**Input:** `what else do they have?`

**Expected Context:** Should remember Agashiye from previous message

**Expected Keywords:** `agashiye`, `menu`

**Purpose:** **CRITICAL** - Verify pronoun resolution and context retention

**Known Issue:** ⚠️ Agent may ask "which restaurant?" instead of using context

---

### Category 9: Tool Routing 🔧

#### Test 9.1: Verify get_all_restaurants() Tool
**Input:** `show all restaurants`

**Expected:** Tool call to `get_all_restaurants()`

**Verification:** Response includes all restaurants

---

#### Test 9.2: Verify search_by_cuisine() Tool
**Input:** `italian places`

**Expected:** Tool call to `search_by_cuisine("Italian")`

**Verification:** Response includes only Italian restaurants

---

#### Test 9.3: Verify get_restaurant_by_name() Tool
**Input:** `info on Honest Restaurant`

**Expected:** Tool call to `get_restaurant_by_name("Honest Restaurant")`

**Verification:** Response includes Honest Restaurant details

---

#### Test 9.4: Verify search_by_item() Tool
**Input:** `who serves samosa?`

**Expected:** Tool call to `search_by_item("samosa")`

**Verification:** Response includes restaurants with samosa

---

### Category 10: Response Quality 📝

#### Test 10.1: Emoji Usage
**Input:** `hello`

**Expected:** Response includes appropriate emojis (🍕, 👋, 🍴, etc.)

**Purpose:** Verify friendly, engaging tone

---

#### Test 10.2: Clear Formatting
**Input:** `list all restaurants`

**Expected:** Response uses bullet points, bold text, clear structure

**Purpose:** Verify readability and formatting

---

### Category 11: API Error Handling 🚨

#### Test 11.1: Backend Service Down
**Simulation:** Stop FastAPI service, send request

**Expected Keywords:** `trouble`, `try again`, `service`

**Forbidden Keywords:** `error`, `crash`, `500`

**Purpose:** Verify graceful handling of API failures

**Expected Behavior:**
- Friendly error message
- Suggests user try again later
- Does NOT expose technical errors

**Note:** This is a manual test - stop FastAPI before running

---

### Category 12: Business Logic ✅

#### Test 12.1: Price Validation
**Input:** `how much is masala thepla?`

**Expected Keywords:** `50`, `₹`

**Purpose:** Verify correct price information

**Expected:** Shows ₹50 (correct price from database)

---

#### Test 12.2: Location Accuracy
**Input:** `where is Swati Snacks?`

**Expected Keywords:** `ashram road`, `ahmedabad`

**Purpose:** Verify correct location information

**Expected:** Shows "Ashram Road, Ahmedabad"

---

## ✅ Expected Results Summary

### High Priority Tests (Must Pass)
- ✅ Test 1.1: Basic Greeting
- ✅ Test 2.1: List All Restaurants
- ✅ Test 2.2: Filter by Cuisine
- ⚠️ Test 3.2b: Context Handling (Known Issue)
- ⚠️ Test 4.2: Order Confirmation (Known Issue)
- ✅ Test 7.1: Invalid Restaurant Handling
- ⚠️ Test 8.1b, 8.2b: Multi-turn Context (Known Issues)

### Medium Priority Tests (Should Pass)
- ✅ Test 1.2: Capabilities
- ✅ Test 2.4: Restaurant by Name
- ✅ Test 3.1: Search by Item
- ✅ Test 5.1: Location Search
- ✅ Test 9.1-9.4: Tool Routing

### Low Priority Tests (Nice to Have)
- Test 6.1: Reviews
- Test 10.1: Emoji Usage
- Test 12.1-12.2: Business Logic

---

## ⚠️ Known Issues

### Issue 1: Context Handling (Tests 3.2b, 8.1b, 8.2b)
**Severity:** HIGH

**Description:** Agent uses simple keyword matching without full conversation context awareness

**Example:**
```
User: "tell me about Swati Snacks"
Agent: [shows details]
User: "show me the menu"
Agent: Searches for restaurant named "The Menu" ❌
Expected: Shows Swati Snacks menu ✅
```

**Root Cause:** Tool routing based on keywords, not context

**Solution:** Implement conversation history tracking and entity resolution

**Impact:** Affects 3 tests, reduces conversational quality

---

### Issue 2: Order Confirmation Gate (Test 4.2)
**Severity:** MEDIUM

**Description:** No confirmation step before placing orders

**Example:**
```
User: "order 2 masala thepla from Swati Snacks"
Agent: May place immediately or explain limitation
Expected: "Confirm: 2x Masala Thepla. Is this correct?"
```

**Root Cause:** `place_order()` tool not implemented, no confirmation logic

**Solution:** Add confirmation state management

**Impact:** Affects 1 test, reduces order safety

---

### Issue 3: Tool Availability
**Severity:** LOW

**Description:** Some tools may not be implemented:
- `place_order()`
- `submit_review()`
- `get_reviews()`

**Impact:** Tests 4.x, 6.x may fail or agent explains limitations

**Solution:** Implement remaining tools OR gracefully explain limitations

---

## 🚀 Test Execution Guide

### Prerequisites
1. **Ollama:** Running with llama3.2:3b model
2. **FastAPI:** Running on port 8000
3. **Flask Agent:** Running on port 5000
4. **MongoDB:** Connected with 7 restaurants

### Run Tests
```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1"
python TESTING\run_comprehensive_tests.py
```

### Expected Output Format
```
[1.1] Basic Greeting ... RUNNING
  📤 Sending: hello
  🎯 Expected: Contains ['foodie', 'welcome', 'help']
  📥 Response: 👋 Hello! Welcome to FoodieExpress!...
  ✅ PASSED

[1.2] Capabilities Check ... RUNNING
  📤 Sending: what can you do?
  🎯 Expected: Contains ['restaurant', 'search']
  📥 Response: 🤔 I can help you with...
  ✅ PASSED
```

### Final Summary
```
================================================================================
                       Test Summary Report
================================================================================
📊 Total Tests Run: 40
✅ Passed: 36
❌ Failed: 4
📈 Success Rate: 90.00% - EXCELLENT

Failed Tests:
- [3.2b] Context Test - Menu Request
- [4.2] Order Confirmation
- [8.1b] Multi-turn Context - First One
- [8.2b] Multi-turn Menu - What Else

================================================================================
                       Testing Complete!
================================================================================
```

---

## 📊 Test Metrics

### Coverage
- **API Endpoints:** 5/5 tools tested
- **Conversation Flows:** 10+ scenarios
- **Edge Cases:** 5 error scenarios
- **Business Logic:** 2 validation tests

### Performance
- **Test Duration:** ~5-8 minutes for full suite
- **Timeout per Test:** 45 seconds
- **Parallel Execution:** No (sequential for context tests)

### Reliability
- **Flakiness:** Low - deterministic responses expected
- **Re-run Rate:** Tests can be re-run immediately
- **Session Isolation:** Each test run uses unique user_id

---

## 🔄 Continuous Improvement

### After Each Test Run
1. Review failed tests
2. Prioritize by severity
3. Fix critical issues first
4. Re-run to validate fixes
5. Update this documentation

### Target Metrics
- **Sprint 1:** 70% pass rate (baseline)
- **Sprint 2:** 85% pass rate (context improvements)
- **Sprint 3:** 95% pass rate (production ready)

---

## 📞 Support

**Test Issues:** Check `TEST_RESULTS_PARTIAL.md` for detailed failure analysis

**Agent Issues:** Check `agent_simple.py` for tool implementations

**API Issues:** Check `food_api/app/main.py` for endpoint status

---

**Document Version:** 2.0  
**Last Updated:** October 15, 2025  
**Maintained By:** Test Automation Team
