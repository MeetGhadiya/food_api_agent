# 🤖 AI Food Delivery Chatbot - Complete Implementation

A production-ready AI-powered chatbot for food delivery platforms (like Swiggy) built with:
- **React + Tailwind CSS** - Modern, responsive frontend
- **Google Gemini AI** - Natural language processing
- **Flask** - AI agent backend
- **FastAPI** - REST API backend
- **MongoDB** - Database

---

## 🎯 Features

✅ **Natural Language Ordering** - "Order a pizza from Domino's"
✅ **Restaurant Browsing** - "Show me Italian restaurants"
✅ **Order Tracking** - "Show my orders"
✅ **Smart Authentication** - Auto-handles login when needed
✅ **Beautiful UI** - Popup chat window with animations
✅ **Secure** - JWT token storage in localStorage
✅ **Error Handling** - Graceful fallbacks
✅ **Real-time** - Instant AI responses

---

## 📁 Project Structure

```
food_api_agent-1/
├── food_api/                      # FastAPI Backend (Port 8000)
│   └── app/
│       ├── main.py                # REST API endpoints
│       ├── database.py            # MongoDB connection
│       ├── models.py              # Database models
│       └── security.py            # JWT authentication
│
├── food_chatbot_agent/            # AI Agent Backend (Port 5000)
│   ├── agent.py                   # Flask + Gemini AI
│   ├── requirements.txt
│   └── .env                       # API keys
│
└── chatbot_frontend/              # React Frontend (Port 5173)
    ├── src/
    │   ├── components/
    │   │   ├── ChatBot.jsx        # Main chatbot wrapper
    │   │   ├── ChatButton.jsx     # Floating button
    │   │   ├── ChatWindow.jsx     # Chat interface
    │   │   └── Message.jsx        # Message bubble
    │   ├── services/
    │   │   ├── api.js             # API client
    │   │   └── auth.js            # Auth manager
    │   ├── App.jsx                # Main app
    │   └── main.jsx               # Entry point
    └── package.json
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB running
- Google Gemini API Key

### Step 1: Setup AI Agent Backend

```bash
# Navigate to agent directory
cd food_chatbot_agent

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_gemini_api_key_here
FASTAPI_BASE_URL=http://localhost:8000
EOF

# Get Gemini API key from: https://makersuite.google.com/app/apikey
# Replace 'your_gemini_api_key_here' with your actual key
```

### Step 2: Setup React Frontend

```bash
# Navigate to frontend directory
cd ../chatbot_frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

### Step 3: Start All Services

**Terminal 1 - FastAPI Backend:**
```bash
cd food_api
uvicorn app.main:app --reload
```

**Terminal 2 - AI Agent:**
```bash
cd food_chatbot_agent
python agent.py
```

**Terminal 3 - React Frontend:**
```bash
cd chatbot_frontend
npm run dev
```

### Step 4: Open in Browser

```
http://localhost:5173
```

You should see:
- Main website with restaurant cards
- Floating chat button in bottom-right corner
- Click to open AI chatbot

---

## 💬 Usage Examples

### Browse Restaurants
```
You: "Show me all restaurants"
Bot: [Lists all restaurants with details]

You: "What Italian restaurants do you have?"
Bot: [Filters by Italian cuisine]
```

### Order Food
```
You: "I want to order a Margherita pizza from Pizza Palace"
Bot: "I'll need you to login first..."
[If not logged in, prompts for authentication]

You: [Provides login credentials]
Bot: "✅ Login successful! Placing your order..."
Bot: "✅ Order placed successfully! Order ID: #12345"
```

### Create Account
```
You: "Create an account for me"
Bot: "I'll help you register. What username would you like?"
[Guides through registration process]
```

### Check Orders
```
You: "Show my orders"
Bot: [Lists all your previous orders with details]
```

---

## 🔧 Configuration

### Environment Variables

**`food_chatbot_agent/.env`**
```env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
FASTAPI_BASE_URL=http://localhost:8000
AGENT_PORT=5000
```

### API Endpoints

**AI Agent (Port 5000):**
- `POST /chat` - Send chat messages
- `GET /health` - Health check
- `POST /clear-session` - Clear chat history

**FastAPI Backend (Port 8000):**
- `GET /restaurants/` - List restaurants
- `POST /restaurants/` - Create restaurant
- `POST /orders/` - Place order
- `GET /orders/` - Get orders
- `POST /users/register` - Register user
- `POST /users/login` - Login user

---

## 🎨 Customization

### Change Colors

Edit `chatbot_frontend/tailwind.config.js`:
```javascript
colors: {
  primary: '#FF6B35',        // Orange
  'primary-dark': '#E85A2A',  // Dark orange
  secondary: '#4ECDC4',       // Teal
  accent: '#FFD23F',          // Yellow
}
```

### Change Bot Name

Edit `chatbot_frontend/src/components/ChatWindow.jsx`:
```jsx
<h3 className="font-semibold text-lg">FoodieBot</h3>
```

### Modify Welcome Message

Edit `chatbot_frontend/src/components/ChatWindow.jsx`:
```javascript
const [messages, setMessages] = useState([
  {
    text: "Your custom welcome message here...",
    isBot: true,
  },
]);
```

---

## 🧪 Testing

### Test AI Responses

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all restaurants", "user_id": "test"}'
```

### Test Scenarios

1. **Browse without login** ✅
   - "Show restaurants"
   - "What cuisines do you have?"

2. **Order with auto-login** ✅
   - "Order pizza" → prompts login
   - Provide credentials
   - Order completes

3. **Registration flow** ✅
   - "Create account"
   - Follow registration prompts
   - Auto-login after registration

---

## 🐛 Troubleshooting

### Issue: "CORS Error"

**Solution:**
```python
# In agent.py, ensure CORS is set:
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
```

### Issue: "Google API Key Invalid"

**Solution:**
1. Get new key from https://makersuite.google.com/app/apikey
2. Update `.env` file
3. Restart agent: `python agent.py`

### Issue: "Cannot connect to FastAPI"

**Solution:**
```bash
# Check if FastAPI is running:
curl http://localhost:8000/docs

# If not, start it:
cd food_api
uvicorn app.main:app --reload
```

### Issue: "MongoDB Connection Failed"

**Solution:**
```bash
# Check MongoDB status
mongosh

# Update connection string in food_api/app/database.py
```

---

## 📦 Deployment

### Build for Production

```bash
# Build React app
cd chatbot_frontend
npm run build

# Output in: dist/
```

### Docker Deployment

```dockerfile
# Dockerfile for AI Agent
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "agent.py"]
```

### Environment Variables for Production

```env
GOOGLE_API_KEY=prod_key_here
FASTAPI_BASE_URL=https://api.yourdomain.com
NODE_ENV=production
```

---

## 📊 API Documentation

### POST /chat

**Request:**
```json
{
  "message": "Show me all restaurants",
  "user_id": "user123",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "response": "I found 5 restaurants:\n\n🏪 Pizza Palace...",
  "function_called": "get_all_restaurants"
}
```

**Auth Response:**
```json
{
  "response": "✅ Login successful!",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "authenticated": true
}
```

---

## 🎉 What You Get

✅ **Complete working chatbot** with AI
✅ **Beautiful React UI** with Tailwind CSS
✅ **Secure authentication** with JWT
✅ **Natural language** understanding
✅ **Error handling** and loading states
✅ **Mobile responsive** design
✅ **Production ready** code
✅ **Full documentation**

---

## 📝 Next Steps

1. ✅ Install dependencies (all 3 projects)
2. ✅ Get Google Gemini API key
3. ✅ Start all 3 servers
4. ✅ Open http://localhost:5173
5. ✅ Click chat button
6. ✅ Try: "Show me all restaurants"
7. ✅ Try: "Order a pizza from Pizza Palace"

---

## 📞 Support

- **FastAPI Docs**: http://localhost:8000/docs
- **Agent Health**: http://localhost:5000/health
- **Frontend**: http://localhost:5173

---

**Enjoy your AI-powered food delivery chatbot! 🍕🤖✨**
