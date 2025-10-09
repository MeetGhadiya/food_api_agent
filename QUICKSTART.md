# 🚀 Quick Start Guide - AI Food Delivery Chatbot

## ⚡ 3-Minute Setup

### Step 1: Install AI Agent Dependencies (30 seconds)

```bash
cd food_chatbot_agent
pip install flask flask-cors google-generativeai requests python-dotenv
```

### Step 2: Configure Google Gemini API (60 seconds)

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Create `.env` file:

```bash
cd food_chatbot_agent
echo "GOOGLE_API_KEY=your_key_here" > .env
echo "FASTAPI_BASE_URL=http://localhost:8000" >> .env
```

### Step 3: Install React Dependencies (60 seconds)

```bash
cd chatbot_frontend
npm install
```

### Step 4: Start Everything (30 seconds)

**Open 3 terminals:**

```bash
# Terminal 1: FastAPI Backend
cd food_api
uvicorn app.main:app --reload

# Terminal 2: AI Agent
cd food_chatbot_agent
python agent.py

# Terminal 3: React Frontend
cd chatbot_frontend
npm run dev
```

### Step 5: Open Browser

```
http://localhost:5173
```

**Click the orange chat button in bottom-right corner!** 💬

---

## 🎯 Try These Commands

### No Login Required:
- "Show me all restaurants"
- "What Italian restaurants do you have?"
- "Tell me about Pizza Palace"

### Requires Login (will prompt):
- "Order a Margherita pizza from Pizza Palace"
- "Show my orders"
- "Create an account"

---

## ✅ Verify Setup

### Check FastAPI:
```bash
curl http://localhost:8000/docs
# Should open API documentation
```

### Check AI Agent:
```bash
curl http://localhost:5000/health
# Should return: {"status": "ok"}
```

### Check React:
- Open http://localhost:5173
- See main website with restaurant cards
- Orange chat button visible in bottom-right

---

## 🐛 Common Issues

### "Module not found"
```bash
pip install -r food_chatbot_agent/requirements.txt
npm install --prefix chatbot_frontend
```

### "Port already in use"
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

### "CORS Error"
- Restart AI agent: `python agent.py`
- Make sure React is on port 5173

---

## 📱 Demo Flow

1. User opens website → sees restaurants
2. Clicks chat button → chatbot opens
3. Types "Show me all restaurants" → gets list
4. Types "Order pizza from Pizza Palace" → bot asks to login
5. Provides credentials → order placed! ✅

---

**That's it! You now have a fully functional AI chatbot! 🎉**
