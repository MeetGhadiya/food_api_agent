================================================================================
                      FOODIEEXPRESS V2.0 - COMPLETE GUIDE
                    Full-Stack AI Food Delivery Platform
================================================================================

🎉 **CONGRATULATIONS!** The complete v2.0 upgrade is finished!

📋 TABLE OF CONTENTS
================================================================================
1. What's New in V2.0
2. Quick Start Guide
3. System Architecture
4. Feature Documentation
5. Testing Guide
6. API Reference
7. Troubleshooting
8. Development Notes

================================================================================
1. WHAT'S NEW IN V2.0 🌟
================================================================================

✅ **BACKEND ENHANCEMENTS (FastAPI)**
   • Restaurant Reviews & Ratings (1-5 stars)
   • Multi-Item Order Support (order multiple dishes at once)
   • Cuisine-Based Search (filter restaurants by cuisine type)
   • Role-Based Access Control (admin vs regular users)
   • Enhanced Order Tracking (detailed item breakdown)
   • Review Statistics (average rating, distribution)

✅ **AI AGENT IMPROVEMENTS (Flask + Gemini)**
   • New review functions (add, view, statistics)
   • Multi-item order handling
   • Cuisine search integration
   • Enhanced personality (emojis, friendly tone)
   • Better error handling and user guidance

✅ **DATABASE UPDATES (MongoDB)**
   • Review collection with user_id, rating, comment
   • Enhanced Order model (items array, total_price)
   • Restaurant cuisine field (Gujarati, Italian, etc.)
   • User role field (user, admin)

✅ **FRONTEND READY**
   • Existing React frontend compatible with v2.0
   • Authentication system integrated
   • Real-time chat interface
   • Responsive design

================================================================================
2. QUICK START GUIDE 🚀
================================================================================

OPTION A: One-Click Startup (Recommended)
------------------------------------------
1. Double-click: START_ALL_V2.bat
2. Wait 10-15 seconds for services to start
3. Open browser: http://localhost:5173
4. Done! 🎉

OPTION B: Manual Startup (For Development)
-------------------------------------------

Step 1: Start FastAPI Backend
```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\food_api"
python -m uvicorn app.main:app --reload
```
Wait for: "✅ Database connection established."
Check: http://localhost:8000/docs

Step 2: Start Flask AI Agent
```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\food_chatbot_agent"
python agent.py
```
Wait for: "🚀 Starting Flask server with Waitress..."
Check: http://localhost:5000/health

Step 3: Start React Frontend
```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\chatbot_frontend"
npm run dev
```
Wait for: "Local: http://localhost:5173"
Open: http://localhost:5173

================================================================================
3. SYSTEM ARCHITECTURE 🏗️
================================================================================

┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                            │
│                http://localhost:5173                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              REACT FRONTEND (Vite)                           │
│  • Components: ChatBot, ChatWindow, Message                  │
│  • Services: api.js, auth.js                                 │
│  • Styling: TailwindCSS                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ POST /chat
                     │ GET /health
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           FLASK AI AGENT (Port 5000)                         │
│  • Google Gemini AI 2.0                                      │
│  • Function Calling (11 functions)                           │
│  • Session Management                                        │
│  • Token-based Authentication                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API Calls
                     │ (restaurants, orders, reviews, auth)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           FASTAPI BACKEND (Port 8000)                        │
│  • 16 REST Endpoints                                         │
│  • JWT Authentication                                        │
│  • RBAC (Role-Based Access)                                  │
│  • Beanie ODM                                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Motor (Async Driver)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   MONGODB ATLAS                              │
│  Collections:                                                │
│  • restaurants (7 documents with cuisine field)              │
│  • users (with role: user/admin)                             │
│  • orders (multi-item support)                               │
│  • reviews (rating, comment, user_id)                        │
└─────────────────────────────────────────────────────────────┘

================================================================================
4. FEATURE DOCUMENTATION 📚
================================================================================

FEATURE 1: Multi-Item Orders
-----------------------------
**What It Does:**
- Order multiple dishes in a single order
- Each item has: name, quantity, price
- Automatic total calculation
- Detailed order history

**How To Use:**
User: "Order 2 bhel puri and 1 pav bhaji from Swati Snacks"
AI: Processes and places order with multiple items

**Technical:**
- Endpoint: POST /orders/
- Schema: OrderCreate with items array
- Response: OrderOut with total_price

**Example API Call:**
```json
POST /orders/
{
  "restaurant_name": "Swati Snacks",
  "items": [
    {"item_name": "Bhel Puri", "quantity": 2, "price": 60.0},
    {"item_name": "Pav Bhaji", "quantity": 1, "price": 120.0}
  ]
}
```

FEATURE 2: Restaurant Reviews
------------------------------
**What It Does:**
- Users can rate restaurants (1-5 stars)
- Add optional text comment
- One review per user per restaurant
- View all reviews and statistics

**How To Use:**
User: "I want to review Swati Snacks"
AI: "Sure! How would you rate it (1-5 stars)?"
User: "5 stars, amazing food!"
AI: Submits review

**Technical:**
- Endpoint: POST /restaurants/{name}/reviews
- Schema: ReviewCreate (rating, comment)
- Validation: Rating must be 1-5
- Duplicate Prevention: One review per user

**Example API Call:**
```json
POST /restaurants/Swati Snacks/reviews
Authorization: Bearer <token>
{
  "rating": 5,
  "comment": "Amazing food! Best bhel puri in Ahmedabad!"
}
```

FEATURE 3: Review Statistics
-----------------------------
**What It Does:**
- Calculate average rating
- Show rating distribution (5★: 10, 4★: 5, etc.)
- Display total review count

**How To Use:**
User: "What's the rating for Swati Snacks?"
AI: Shows average rating and distribution

**Technical:**
- Endpoint: GET /restaurants/{name}/reviews/stats
- Aggregation: Count by rating, calculate average
- Response: average_rating, total_reviews, rating_distribution

FEATURE 4: Cuisine-Based Search
--------------------------------
**What It Does:**
- Filter restaurants by cuisine type
- Available cuisines: Gujarati, Italian, North Indian, South Indian, Desserts

**How To Use:**
User: "Show me Italian restaurants"
AI: Returns filtered list of Italian restaurants

**Technical:**
- Endpoint: GET /restaurants/?cuisine=Italian
- Filter: Case-insensitive cuisine matching
- Returns: List of matching restaurants

**Current Restaurants:**
• Swati Snacks → Gujarati
• Agashiye The House of MG → Gujarati
• PATEL & SONS → Gujarati
• Manek Chowk Pizza → Italian
• Honest Restaurant → North Indian
• Sankalp Restaurant → South Indian
• The Chocolate Room → Desserts & Beverages

FEATURE 5: Role-Based Access Control (RBAC)
--------------------------------------------
**What It Does:**
- Users have roles: "user" (default) or "admin"
- Admin-only endpoints protected
- 403 Forbidden for unauthorized access

**Protected Endpoints (Admin Only):**
- POST /restaurants/ (create restaurant)
- PUT /restaurants/{name} (update restaurant)
- DELETE /restaurants/{name} (delete restaurant)

**Technical:**
- Dependency: get_current_admin_user()
- Check: user.role == "admin"
- Default: New users get "user" role

**Create Admin User:**
```json
POST /users/register
{
  "username": "admin",
  "email": "admin@foodie.com",
  "password": "adminpass",
  "role": "admin"
}
```

================================================================================
5. TESTING GUIDE 🧪
================================================================================

See TESTING_GUIDE_V2.md for comprehensive test scenarios!

Quick Test Checklist:
----------------------
✅ Backend running (http://localhost:8000/docs)
✅ AI Agent running (http://localhost:5000/health)
✅ Frontend running (http://localhost:5173)
✅ User registration works
✅ User login works
✅ Browse restaurants works
✅ Cuisine search works (try "Italian")
✅ Place order works (multi-item)
✅ View orders works
✅ Submit review works
✅ View reviews works
✅ Review stats works
✅ Duplicate review prevention works
✅ Admin endpoints protected (403 for regular users)

================================================================================
6. API REFERENCE 📖
================================================================================

PUBLIC ENDPOINTS (No Authentication)
-------------------------------------
1. GET /
   Response: Welcome message, version

2. GET /restaurants/
   Query: ?cuisine=<type> (optional)
   Response: List of restaurants

3. GET /restaurants/{name}
   Response: Restaurant details

4. GET /restaurants/{name}/reviews
   Response: List of reviews for restaurant

5. GET /restaurants/{name}/reviews/stats
   Response: Review statistics (avg, count, distribution)

6. POST /users/register
   Body: {username, email, password, role?}
   Response: User object

7. POST /users/login
   Body: username, password (form data)
   Response: {access_token, token_type}

8. GET /health
   Response: Health status

PROTECTED ENDPOINTS (JWT Required)
-----------------------------------
9. GET /users/me
   Header: Authorization: Bearer <token>
   Response: Current user info

10. POST /orders/
    Header: Authorization: Bearer <token>
    Body: {restaurant_name, items: [{item_name, quantity, price}]}
    Response: Order object with total_price

11. GET /orders/
    Header: Authorization: Bearer <token>
    Response: List of user's orders

12. GET /orders/{id}
    Header: Authorization: Bearer <token>
    Response: Specific order details

13. POST /restaurants/{name}/reviews
    Header: Authorization: Bearer <token>
    Body: {rating (1-5), comment}
    Response: Review object

ADMIN ENDPOINTS (Admin Role Required)
--------------------------------------
14. POST /restaurants/
    Header: Authorization: Bearer <token>
    Body: {name, area, cuisine, items?}
    Response: Restaurant object
    Note: Returns 403 if not admin

15. PUT /restaurants/{name}
    Header: Authorization: Bearer <token>
    Body: Restaurant fields to update
    Response: Updated restaurant

16. DELETE /restaurants/{name}
    Header: Authorization: Bearer <token>
    Response: Success message

================================================================================
7. TROUBLESHOOTING 🔧
================================================================================

ISSUE: "Can't connect to MongoDB"
FIX: Check MongoDB Atlas URL in food_api/app/database.py
     Ensure network access is allowed in MongoDB Atlas

ISSUE: "API returns 404 for restaurants"
FIX: Run migration script: python migrate_add_cuisine.py
     Check database has 7 restaurants

ISSUE: "AI Agent says 'login required' but I'm logged in"
FIX: Check browser console for token
     Clear localStorage and re-login
     Restart AI Agent service

ISSUE: "Reviews not showing"
FIX: Ensure Review model in database.py init_beanie()
     Check restaurant name spelling (case-sensitive)

ISSUE: "Can't place order"
FIX: Make sure you're logged in (JWT token present)
     Check FastAPI logs for errors
     Verify restaurant name exists

ISSUE: "Frontend not connecting to backend"
FIX: Check CORS settings in main.py
     Verify ports: 8000 (API), 5000 (Agent), 5173 (Frontend)
     Restart all services

ISSUE: "Admin endpoints return 403"
FIX: Create admin user with role="admin"
     Get JWT token for admin user
     Use admin token in requests

================================================================================
8. DEVELOPMENT NOTES 💡
================================================================================

FILES MODIFIED IN V2.0 UPGRADE
-------------------------------
✅ food_api/app/models.py
   - Added: Review model
   - Modified: Restaurant (cuisine), User (role), Order (restructured)

✅ food_api/app/schemas.py
   - Added: OrderItemCreate, OrderOut, ReviewCreate, ReviewOut
   - Modified: RestaurantCreate, UserCreate, OrderCreate

✅ food_api/app/main.py
   - Complete rewrite (~450 lines)
   - Added: 6 new endpoints
   - Modified: 10 existing endpoints

✅ food_api/app/dependencies.py
   - Added: get_current_admin_user()

✅ food_api/app/database.py
   - Added: Review to init_beanie()

✅ food_chatbot_agent/agent.py
   - Added: add_review(), get_reviews(), get_review_stats()
   - Modified: place_order() for multi-items
   - Modified: search_restaurants_by_cuisine() uses query param
   - Enhanced: System instructions with v2.0 features

✅ migrate_add_cuisine.py
   - NEW: Migration script for adding cuisine field
   - Status: Successfully executed (7 restaurants updated)

BACKUP FILES CREATED
--------------------
• food_api/app/main_backup.py (original main.py)
• food_api/app/main_v2.py (v2.0 before deployment)
• food_chatbot_agent/agent_v1_backup.py (original agent)
• food_chatbot_agent/agent_v2.py (v2.0 before deployment)

DATABASE STATE
--------------
✅ 7 restaurants with cuisine field
✅ All users have role field (default: "user")
✅ Orders support multi-item structure
✅ Reviews collection initialized

AI AGENT FUNCTIONS (11 Total)
------------------------------
1. get_all_restaurants()
2. get_restaurant_by_name(name)
3. search_restaurants_by_cuisine(cuisine)
4. place_order(restaurant_name, items[], token)
5. get_user_orders(token)
6. add_review(restaurant_name, rating, comment, token)
7. get_reviews(restaurant_name)
8. get_review_stats(restaurant_name)
9. register_user(username, email, password)
10. login_user(username, password)
11. create_restaurant(name, area, cuisine, token) [ADMIN]

FUTURE ENHANCEMENTS (Ideas)
----------------------------
• Order status tracking (pending, preparing, delivered)
• Restaurant images and photos
• Delivery address management
• Payment integration
• Order cancellation
• Edit/delete reviews
• Restaurant search by location
• Favorites/Bookmarks
• Promotional offers
• Order scheduling
• Multiple delivery addresses
• Loyalty points system

================================================================================
                               END OF GUIDE
================================================================================

Version: 2.0.0
Status: Complete ✅
Date: October 13, 2025
Developer: MeetGhadiya

For questions or issues, refer to:
• TESTING_GUIDE_V2.md - Comprehensive testing commands
• UPGRADE_V2_DOCUMENTATION.md - Upgrade process details
• desc.txt - Original project documentation (v1.x)

Happy Coding! 🚀🍕
