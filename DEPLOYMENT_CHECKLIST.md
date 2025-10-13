================================================================================
                   FOODIEEXPRESS V2.0 - DEPLOYMENT CHECKLIST
================================================================================

Use this checklist to ensure everything is properly deployed and working.

⬜ = Not Started  ⏳ = In Progress  ✅ = Complete  ❌ = Failed

================================================================================
                         PRE-DEPLOYMENT CHECKS
================================================================================

ENVIRONMENT SETUP
⬜ Python 3.13+ installed
⬜ Node.js 18+ installed
⬜ MongoDB Atlas account created
⬜ Google Gemini API key obtained
⬜ Git repository cloned/updated

CONFIGURATION FILES
⬜ food_api/app/database.py - MongoDB URL configured
⬜ food_chatbot_agent/.env - GOOGLE_API_KEY set
⬜ food_chatbot_agent/.env - FASTAPI_BASE_URL set

DEPENDENCIES
⬜ food_api/requirements.txt - All packages installed
⬜ food_chatbot_agent/requirements.txt - All packages installed
⬜ chatbot_frontend/package.json - npm install completed

DATABASE SETUP
⬜ MongoDB Atlas cluster created
⬜ Database "food_db" exists
⬜ Network access configured (allow all or specific IP)
⬜ Database user created with read/write permissions

MIGRATION
⬜ migrate_add_cuisine.py executed successfully
⬜ 7 restaurants have cuisine field
⬜ All restaurants verified in database

================================================================================
                          SERVICE STARTUP TESTS
================================================================================

FASTAPI BACKEND (Port 8000)
⬜ Service starts without errors
⬜ Database connection established
⬜ Swagger docs accessible (http://localhost:8000/docs)
⬜ GET / returns welcome message
⬜ GET /health returns status: ok
⬜ GET /restaurants/ returns 7 restaurants
⬜ All restaurants have cuisine field

Test Commands:
```powershell
cd food_api
python -m uvicorn app.main:app --reload
```

Expected Output:
- "✅ Database connection established."
- "INFO: Application startup complete."

Verify:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:8000/restaurants/ -UseBasicParsing
```

FLASK AI AGENT (Port 5000)
⬜ Service starts without errors
⬜ Gemini AI configured successfully
⬜ Health check passes
⬜ GET / returns service info with v2.0 features
⬜ POST /chat accepts messages

Test Commands:
```powershell
cd food_chatbot_agent
python agent.py
```

Expected Output:
- "✅ Google Gemini AI: Configured"
- "✅ FastAPI Backend: http://localhost:8000"
- "✅ Waitress imported successfully"

Verify:
```powershell
Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing
```

REACT FRONTEND (Port 5173)
⬜ npm run dev starts successfully
⬜ Vite dev server running
⬜ No compilation errors
⬜ Page loads in browser
⬜ ChatBot button visible
⬜ Login button visible

Test Commands:
```powershell
cd chatbot_frontend
npm run dev
```

Expected Output:
- "VITE v... ready in ... ms"
- "Local: http://localhost:5173/"

Verify:
- Open http://localhost:5173 in browser
- Page should load without errors

================================================================================
                      FUNCTIONALITY TESTS (CRITICAL)
================================================================================

USER MANAGEMENT
⬜ User registration works
⬜ User login works
⬜ JWT token returned and stored
⬜ Token persists in localStorage
⬜ Logout clears token

Test Steps:
1. Click "Login" button
2. Fill registration form
3. Submit
4. Check browser console for token
5. Verify token in localStorage

RESTAURANT BROWSING
⬜ Browse all restaurants works
⬜ Restaurant details displayed (name, area, cuisine)
⬜ AI returns formatted list with emojis
⬜ All 7 restaurants appear

Test Chat:
- "Show me all restaurants"
- "Tell me about Swati Snacks"

CUISINE SEARCH
⬜ Search by cuisine works
⬜ "Italian" returns Manek Chowk Pizza
⬜ "Gujarati" returns 3 restaurants
⬜ "North Indian" returns Honest Restaurant
⬜ "South Indian" returns Sankalp Restaurant
⬜ Invalid cuisine returns appropriate message

Test Chat:
- "Show me Italian restaurants"
- "I want Gujarati food"
- "Find South Indian restaurants"

MULTI-ITEM ORDERS
⬜ Single item order works
⬜ Multiple items order works
⬜ Quantities handled correctly
⬜ Total price calculated correctly
⬜ Order appears in history
⬜ Item breakdown displayed

Test Chat (Must be logged in):
- "Order 2 bhel puri from Swati Snacks"
- "Order bhel puri and pav bhaji from Swati Snacks"

Expected:
- Order placed successfully
- Total = sum of (quantity × price) for all items
- Order ID returned

REVIEW SYSTEM
⬜ Submit review works (1-5 stars)
⬜ View reviews works
⬜ Review statistics works
⬜ Duplicate review prevented
⬜ Rating validation (must be 1-5)
⬜ Reviews appear with username

Test Chat (Must be logged in):
- "I want to review Swati Snacks - 5 stars, amazing food!"
- "Show reviews for Swati Snacks"
- "What's the rating for Swati Snacks?"

Try duplicate:
- Submit same review again (should fail)

ORDER HISTORY
⬜ View orders works
⬜ All orders displayed
⬜ Item details shown
⬜ Total prices correct
⬜ Order dates shown

Test Chat (Must be logged in):
- "Show my orders"
- "What did I order?"

AUTHENTICATION FLOWS
⬜ Unauthenticated order attempt shows login prompt
⬜ Unauthenticated review attempt shows login prompt
⬜ Login required message appears for protected actions
⬜ After login, protected actions work

ADMIN FEATURES (Optional - requires admin user)
⬜ Create admin user with role="admin"
⬜ Admin can create restaurant
⬜ Admin can update restaurant
⬜ Admin can delete restaurant
⬜ Regular user gets 403 for admin endpoints

================================================================================
                        ERROR HANDLING TESTS
================================================================================

BACKEND ERROR HANDLING
⬜ Invalid restaurant name returns 404
⬜ Invalid credentials return 401
⬜ Missing auth token returns 401
⬜ Non-admin admin endpoint returns 403
⬜ Invalid rating (0 or 6) returns 400
⬜ Duplicate review returns 400
⬜ Database errors handled gracefully

FRONTEND ERROR HANDLING
⬜ Backend down shows appropriate error
⬜ Network errors caught and displayed
⬜ Invalid API responses handled
⬜ Loading states shown during requests
⬜ Error messages user-friendly

AI AGENT ERROR HANDLING
⬜ Invalid function args handled
⬜ API errors caught and reported
⬜ Timeout errors handled
⬜ Empty responses handled
⬜ Token missing shows auth message

================================================================================
                         INTEGRATION TESTS
================================================================================

COMPLETE USER FLOW
⬜ User opens frontend
⬜ User registers account
⬜ User logs in
⬜ User browses restaurants
⬜ User searches by cuisine
⬜ User places multi-item order
⬜ User views order history
⬜ User submits review
⬜ User views reviews
⬜ User views review statistics

Test Script (PowerShell):
See TESTING_GUIDE_V2.md - "TEST 15: Complete User Flow Test"

API CHAIN TEST
⬜ Frontend → AI Agent → FastAPI → MongoDB (full chain)
⬜ Response propagates back correctly
⬜ Data persistence verified
⬜ All layers communicate properly

CONCURRENT OPERATIONS
⬜ Multiple users can order simultaneously
⬜ Reviews don't interfere with each other
⬜ Session management works per user
⬜ No race conditions

================================================================================
                         PERFORMANCE CHECKS
================================================================================

RESPONSE TIMES
⬜ GET /restaurants/ < 500ms
⬜ POST /orders/ < 1000ms
⬜ POST /chat < 3000ms (AI call)
⬜ Frontend loads < 2000ms

LOAD HANDLING
⬜ Backend handles 10 concurrent requests
⬜ AI agent handles 5 concurrent chats
⬜ Frontend responsive during API calls

RESOURCE USAGE
⬜ FastAPI memory < 200MB
⬜ Flask memory < 150MB
⬜ Frontend bundle size reasonable
⬜ MongoDB queries optimized

================================================================================
                         SECURITY CHECKS
================================================================================

AUTHENTICATION
⬜ JWT tokens expire after 30 minutes
⬜ Invalid tokens rejected
⬜ Passwords hashed (not stored plain)
⬜ SQL injection prevention (N/A - NoSQL)
⬜ XSS prevention in inputs

AUTHORIZATION
⬜ Protected endpoints require auth
⬜ Admin endpoints require admin role
⬜ Users can only see own orders
⬜ Users can only review once per restaurant

DATA VALIDATION
⬜ Rating must be 1-5
⬜ Email format validated
⬜ Password strength enforced (if applicable)
⬜ Input sanitization working

================================================================================
                       DOCUMENTATION CHECKS
================================================================================

README FILES
⬜ README_V2.md complete and accurate
⬜ COMPLETE_V2_GUIDE.md comprehensive
⬜ TESTING_GUIDE_V2.md has all test cases
⬜ V2_UPGRADE_COMPLETE.md summarizes changes

API DOCUMENTATION
⬜ Swagger UI accessible and complete
⬜ All endpoints documented
⬜ Request/response schemas shown
⬜ Authentication requirements clear

CODE DOCUMENTATION
⬜ Functions have docstrings
⬜ Complex logic has comments
⬜ TODO items addressed or noted
⬜ Backup files preserved

================================================================================
                         DEPLOYMENT STEPS
================================================================================

PREPARE FOR DEPLOYMENT
⬜ All tests passing
⬜ No console errors
⬜ All files committed to Git
⬜ Version number updated (2.0.0)
⬜ Changelog created

BACKUP
⬜ Database backup created
⬜ Code repository tagged (v2.0.0)
⬜ Environment variables documented
⬜ Configuration files backed up

DEPLOY
⬜ Push to repository
⬜ Update production environment variables
⬜ Run migrations on production database
⬜ Start services in correct order
⬜ Verify all services running

POST-DEPLOYMENT
⬜ Smoke tests passed
⬜ Monitor logs for errors
⬜ Check resource usage
⬜ Verify user flows work
⬜ Update documentation with production URLs

================================================================================
                         MONITORING SETUP
================================================================================

LOGGING
⬜ FastAPI logs configured
⬜ Flask logs configured
⬜ Frontend error tracking
⬜ Log rotation setup

ALERTS
⬜ Service downtime alerts
⬜ Error rate monitoring
⬜ Performance degradation alerts
⬜ Database connection monitoring

METRICS
⬜ Request count tracking
⬜ Response time monitoring
⬜ Error rate tracking
⬜ User activity monitoring

================================================================================
                         ROLLBACK PLAN
================================================================================

IF DEPLOYMENT FAILS:
1. ⬜ Stop all services
2. ⬜ Restore database from backup
3. ⬜ Revert code to previous version (git checkout v1.x)
4. ⬜ Start services with old code
5. ⬜ Verify functionality
6. ⬜ Investigate issues before retrying

BACKUP LOCATIONS:
- Code: Git tag v1.x or main_backup.py, agent_v1_backup.py
- Database: MongoDB Atlas snapshot
- Config: Documented in COMPLETE_V2_GUIDE.md

================================================================================
                         FINAL SIGN-OFF
================================================================================

⬜ All critical tests passed
⬜ All blockers resolved
⬜ Documentation complete
⬜ Team notified of deployment
⬜ Monitoring active
⬜ Rollback plan ready

DEPLOYMENT APPROVED BY:
Name: ___________________
Date: ___________________
Signature: ______________

DEPLOYMENT NOTES:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

================================================================================
                         POST-DEPLOYMENT REVIEW
================================================================================

24 HOURS AFTER DEPLOYMENT:
⬜ No critical errors reported
⬜ Performance within acceptable range
⬜ User feedback collected
⬜ Analytics reviewed
⬜ Any issues documented and tracked

1 WEEK AFTER DEPLOYMENT:
⬜ All features being used
⬜ No regression issues
⬜ Performance stable
⬜ User satisfaction high
⬜ Lessons learned documented

================================================================================

Version: 2.0.0
Status: Ready for Deployment
Date: October 13, 2025

================================================================================
