# FoodieExpress v2.0 - AI-Powered Food Delivery Platform 🍕

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/MeetGhadiya/food_api_agent)
[![Status](https://img.shields.io/badge/status-production%20ready-green.svg)](https://github.com/MeetGhadiya/food_api_agent)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A modern, full-stack AI-powered food delivery chatbot with **Restaurant Reviews**, **Multi-Item Orders**, and **Cuisine Search** built with React, FastAPI, Flask, and Google Gemini AI 2.0.

![FoodieExpress Banner](docs/banner.png)

## 🌟 What's New in V2.0

- ⭐ **Restaurant Reviews & Ratings** - Rate restaurants 1-5 stars with comments
- 🛒 **Multi-Item Orders** - Order multiple dishes in one order with quantities
- 🔍 **Cuisine-Based Search** - Filter restaurants by cuisine (Gujarati, Italian, etc.)
- 🔒 **Role-Based Access Control** - Admin and user roles with protected endpoints
- 📊 **Review Statistics** - View average ratings and rating distributions
- 🤖 **Enhanced AI Personality** - Friendly, helpful responses with emojis
- 💰 **Automatic Total Calculation** - Order totals calculated automatically
- 📝 **Detailed Order History** - See complete item breakdowns

## 🚀 Quick Start

### One-Click Launch (Windows)

```powershell
# Double-click this file:
START_ALL_V2.bat
```

Wait 10-15 seconds, then open: **http://localhost:5173**

### Manual Launch

```powershell
# Terminal 1: FastAPI Backend
cd food_api
python -m uvicorn app.main:app --reload

# Terminal 2: Flask AI Agent
cd food_chatbot_agent
python agent.py

# Terminal 3: React Frontend
cd chatbot_frontend
npm run dev
```

## 🏗️ System Architecture

```
┌─────────────────┐
│  React Frontend │  Port 5173 (Vite + TailwindCSS)
│  ChatBot UI     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Flask AI Agent  │  Port 5000 (Gemini AI 2.0)
│ 11 Functions    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FastAPI Backend │  Port 8000 (16 Endpoints)
│ JWT + RBAC      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MongoDB Atlas  │  4 Collections
│  Beanie ODM     │
└─────────────────┘
```

## 📋 Features

### 🍽️ Restaurant Management
- Browse all restaurants
- Search by cuisine type
- View detailed restaurant info
- Admin: Create/Update/Delete restaurants

### 🛒 Order System
- Place multi-item orders
- Order multiple dishes at once
- View order history
- Track orders by ID
- Automatic total calculation

### ⭐ Review System
- Rate restaurants (1-5 stars)
- Add text comments
- View all reviews
- See review statistics
- One review per user per restaurant
- Duplicate prevention

### 🤖 AI Chatbot
- Natural language ordering
- Restaurant recommendations
- Order tracking
- Review submission
- Friendly personality with emojis
- Context-aware responses

### 🔒 Security
- JWT authentication
- Role-based access (user/admin)
- Protected endpoints
- Secure password hashing
- Token expiration

## 📦 Tech Stack

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Axios
- Lucide Icons

**Backend:**
- FastAPI 0.119.0
- Beanie ODM
- MongoDB Atlas
- JWT Authentication
- Python 3.13+

**AI Agent:**
- Flask
- Google Gemini AI 2.0
- Waitress (WSGI Server)
- Function Calling

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- Node.js 18+
- MongoDB Atlas account
- Google Gemini API key

### Step 1: Clone Repository
```bash
git clone https://github.com/MeetGhadiya/food_api_agent.git
cd food_api_agent-1
```

### Step 2: Setup Backend
```powershell
cd food_api
pip install -r requirements.txt

# Configure MongoDB connection in app/database.py
```

### Step 3: Setup AI Agent
```powershell
cd food_chatbot_agent
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_key_here" > .env
echo "FASTAPI_BASE_URL=http://localhost:8000" >> .env
```

### Step 4: Setup Frontend
```powershell
cd chatbot_frontend
npm install
```

### Step 5: Run Migration
```powershell
cd food_api
python migrate_add_cuisine.py
```

## 📖 API Documentation

### Public Endpoints

```
GET  /                              Welcome message
GET  /restaurants/                  List all restaurants
GET  /restaurants/?cuisine=Italian  Filter by cuisine
GET  /restaurants/{name}            Get restaurant details
GET  /restaurants/{name}/reviews    Get reviews
GET  /restaurants/{name}/reviews/stats  Get statistics
POST /users/register                Register user
POST /users/login                   Login user
GET  /health                        Health check
```

### Protected Endpoints (JWT Required)

```
GET  /users/me                      Current user info
POST /orders/                       Place order
GET  /orders/                       User's orders
GET  /orders/{id}                   Order details
POST /restaurants/{name}/reviews    Submit review
```

### Admin Endpoints (Admin Role Required)

```
POST   /restaurants/                Create restaurant
PUT    /restaurants/{name}          Update restaurant
DELETE /restaurants/{name}          Delete restaurant
```

Full API docs: http://localhost:8000/docs

## 🧪 Testing

See **TESTING_GUIDE_V2.md** for comprehensive test scenarios and PowerShell commands.

Quick test:
```powershell
# Check services
Invoke-WebRequest -Uri http://localhost:8000/health
Invoke-WebRequest -Uri http://localhost:5000/health

# Browse restaurants
Invoke-WebRequest -Uri http://localhost:8000/restaurants/

# Search by cuisine
Invoke-WebRequest -Uri "http://localhost:8000/restaurants/?cuisine=Italian"
```

## 💡 Usage Examples

### Chat with AI Assistant
```
User: "Show me Italian restaurants"
AI: 🍽️ Found 1 Italian restaurant!
    🏪 Manek Chowk Pizza
    📍 Manek Chowk, Ahmedabad

User: "Order 2 margherita pizzas from Manek Chowk Pizza"
AI: ✅ Order placed successfully!
    Total: ₹300
    Estimated delivery: 30-45 minutes

User: "Review Manek Chowk Pizza - 5 stars, amazing pizza!"
AI: ✅ Review submitted! Thank you for your feedback!
```

### API Request Examples

**Place Multi-Item Order:**
```json
POST /orders/
Authorization: Bearer <token>
{
  "restaurant_name": "Swati Snacks",
  "items": [
    {"item_name": "Bhel Puri", "quantity": 2, "price": 60.0},
    {"item_name": "Pav Bhaji", "quantity": 1, "price": 120.0}
  ]
}
```

**Submit Review:**
```json
POST /restaurants/Swati Snacks/reviews
Authorization: Bearer <token>
{
  "rating": 5,
  "comment": "Amazing food! Best bhel puri in Ahmedabad!"
}
```

## 📁 Project Structure

```
food_api_agent-1/
├── food_api/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # 16 API endpoints
│   │   ├── models.py           # 4 database models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── database.py         # MongoDB connection
│   │   ├── security.py         # JWT & password hashing
│   │   └── dependencies.py     # Auth dependencies
│   ├── requirements.txt
│   └── migrate_add_cuisine.py  # Migration script
│
├── food_chatbot_agent/          # Flask AI Agent
│   ├── agent.py                # 11 AI functions
│   ├── requirements.txt
│   └── .env                    # API keys
│
├── chatbot_frontend/            # React Frontend
│   ├── src/
│   │   ├── components/         # ChatBot, ChatWindow, Message
│   │   └── services/           # api.js, auth.js
│   ├── package.json
│   └── vite.config.js
│
├── START_ALL_V2.bat            # Launch script
├── COMPLETE_V2_GUIDE.md        # Full documentation
├── TESTING_GUIDE_V2.md         # Testing commands
└── README.md                   # This file
```

## 🔧 Configuration

### MongoDB Connection
Edit `food_api/app/database.py`:
```python
MONGO_URL = "mongodb+srv://username:password@cluster.mongodb.net/food_db"
```

### Gemini API Key
Edit `food_chatbot_agent/.env`:
```
GOOGLE_API_KEY=your_gemini_api_key_here
FASTAPI_BASE_URL=http://localhost:8000
```

### CORS Settings
Edit `food_api/app/main.py`:
```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000"
]
```

## 🐛 Troubleshooting

**Services won't start:**
- Check ports 8000, 5000, 5173 are not in use
- Verify Python 3.13+ and Node.js 18+ installed

**Can't login:**
- Check MongoDB connection
- Verify user exists in database

**Orders fail:**
- Ensure user is logged in (JWT token present)
- Check restaurant name spelling

**Reviews not showing:**
- Verify restaurant name (case-sensitive)
- Check Review model in init_beanie()

See **COMPLETE_V2_GUIDE.md** section 7 for detailed troubleshooting.

## 📚 Documentation

- **COMPLETE_V2_GUIDE.md** - Full system documentation
- **TESTING_GUIDE_V2.md** - Comprehensive test scenarios
- **UPGRADE_V2_DOCUMENTATION.md** - Upgrade process details
- **V2_UPGRADE_COMPLETE.md** - Upgrade completion summary
- **desc.txt** - Original v1.x documentation

## 🎯 Roadmap

### Current Version (v2.0)
- ✅ Multi-item orders
- ✅ Restaurant reviews
- ✅ Cuisine search
- ✅ RBAC security

### Future Enhancements
- 🔲 Order status tracking
- 🔲 Restaurant images
- 🔲 Payment integration
- 🔲 Delivery address management
- 🔲 Email notifications
- 🔲 Mobile app
- 🔲 Real-time tracking
- 🔲 Loyalty program

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Meet Ghadiya**
- GitHub: [@MeetGhadiya](https://github.com/MeetGhadiya)
- Repository: [food_api_agent](https://github.com/MeetGhadiya/food_api_agent)

## 🙏 Acknowledgments

- Google Gemini AI for powering the chatbot
- FastAPI for the amazing web framework
- MongoDB Atlas for database hosting
- React community for frontend tools
- All contributors and testers

## 📊 Project Stats

- **Version:** 2.0.0
- **Lines of Code:** ~3,000+
- **API Endpoints:** 16
- **AI Functions:** 11
- **Database Collections:** 4
- **Restaurants:** 7 (default)
- **Features:** 8 major

## 🔗 Links

- **Live Demo:** (Coming soon)
- **API Documentation:** http://localhost:8000/docs
- **AI Agent Health:** http://localhost:5000/health
- **Frontend:** http://localhost:5173

---

**Made with ❤️ by Meet Ghadiya**

*FoodieExpress - Your AI-Powered Food Companion* 🍕🤖
