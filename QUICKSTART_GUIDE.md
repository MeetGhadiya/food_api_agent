# Quick Start Guide - Food Delivery Chatbot

## 🚀 Starting All Services

### Option 1: One-Click Start (Recommended)
Double-click `start_all_services.bat` in the root directory. This will:
1. Start FastAPI Backend (port 8000)
2. Start Flask AI Agent (port 5000)  
3. Start React Frontend (port 5173)
4. Automatically open http://localhost:5173 in your browser

### Option 2: Manual Start
If you prefer to start services individually:

1. **FastAPI Backend:**
   ```
   cd food_api
   start_api.bat
   ```

2. **Flask AI Agent:**
   ```
   cd food_chatbot_agent
   start_agent.bat
   ```

3. **React Frontend:**
   ```
   cd chatbot_frontend
   start_frontend.bat
   ```

## 📊 Service Status Check

After starting services, verify they're running:

```powershell
netstat -ano | findstr "LISTENING" | findstr ":8000 :5000 :5173"
```

You should see all three ports in LISTENING state.

## 🔧 Troubleshooting

### Issue: "I am having trouble connecting to the restaurant service"

**Cause:** One or more backend services are not running.

**Solution:**
1. Close all terminal windows
2. Run `start_all_services.bat` again
3. Wait 10 seconds for all services to fully start
4. Refresh your browser at http://localhost:5173
5. Try sending a message like "list all restaurants"

### Issue: Port already in use

**Cause:** Previous instance still running.

**Solution:**
```powershell
# Find the process using the port (replace 8000 with 5000 or 5173)
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID from above)
taskkill /F /PID <PID>
```

### Issue: Frontend shows blank page

**Cause:** Node modules not installed or Vite server crashed.

**Solution:**
```powershell
cd chatbot_frontend
npm install
npm run dev
```

### Issue: "GOOGLE_API_KEY not found"

**Cause:** Missing environment variable.

**Solution:**
1. Open `food_chatbot_agent\.env`
2. Ensure `GOOGLE_API_KEY` is set
3. Get key from: https://makersuite.google.com/app/apikey
4. Restart the Flask agent

## 🧪 Testing the System

### Test 1: Backend API
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/restaurants/" | ConvertFrom-Json
```

### Test 2: AI Agent
```powershell
$body = @{message='list restaurants'; user_id='test'} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/chat" -Method POST -Body $body -ContentType "application/json" | ConvertFrom-Json
```

### Test 3: Frontend
Open http://localhost:5173 and type: "show me all restaurants"

## 📝 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| FastAPI Backend | http://localhost:8000 | Restaurant data & orders |
| FastAPI Docs | http://localhost:8000/docs | Interactive API documentation |
| Flask AI Agent | http://localhost:5000 | AI chatbot backend |
| React Frontend | http://localhost:5173 | User interface |

## ⚙️ Environment Requirements

- Python 3.13+ with virtual environment at `.venv/`
- Node.js 18+ with npm
- Google Gemini API key (in `food_chatbot_agent/.env`)

## 🔄 Restarting Services

If you need to restart:
1. Close all CMD windows running the services
2. Run `start_all_services.bat` again

## 💡 Tips

- Keep the three terminal windows open while using the app
- If chat seems stuck, click the refresh icon in the chat header
- Login using the button in top-right corner to place orders
- All services support hot-reload (auto-restart on code changes)

---

For detailed setup instructions, see `README.md` in the root directory.
