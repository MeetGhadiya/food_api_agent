# 🚀 FoodieExpress V4.0 - Quick Start Guide

## ✅ Prerequisites Checklist

- [ ] **Docker Desktop** installed and running
- [ ] **8GB RAM** minimum available
- [ ] **MongoDB Atlas** account (free tier works)
- [ ] **Google Gemini API Key** from https://makersuite.google.com/app/apikey

---

## 🐳 Option 1: Docker Deployment (Recommended)

### Step 1: Start Docker Desktop
Open Docker Desktop from Start Menu and wait until it shows "Running"

### Step 2: Configure Environment
The `.env` file has been created with your credentials. Verify it contains:
- ✅ MONGODB_URI (your MongoDB Atlas connection string)
- ✅ GOOGLE_API_KEY (your Google Gemini API key)
- ✅ SECRET_KEY (JWT secret key)

### Step 3: Run the Application
Double-click `START_DOCKER.bat` or run in PowerShell:
```powershell
docker-compose up --build
```

### Step 4: Access the Services
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **AI Agent**: http://localhost:5000
- **Health Check**: http://localhost:8000/health

---

## 🔧 Option 2: Manual Development Setup

### Step 1: Create Virtual Environment
```powershell
cd food_api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Start Services Manually

**Terminal 1 - Backend:**
```powershell
cd food_api
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - AI Agent:**
```powershell
cd food_chatbot_agent
python agent.py
```

**Terminal 3 - Frontend:**
```powershell
cd chatbot_frontend
npm install
npm run dev
```

---

## 🧪 Testing

```powershell
cd food_api
pytest -v
pytest --cov=app
```

---

## 🐛 Troubleshooting

### PowerShell Script Execution Error
If you see "running scripts is disabled", use `START_DOCKER.bat` instead of PowerShell activation.

### Docker Container Keeps Restarting
1. Check `.env` file has correct MongoDB URI
2. Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0)
3. Check Docker logs: `docker-compose logs foodie-backend`

### MongoDB Connection Error
1. Verify MongoDB URI is correct in `.env`
2. Check MongoDB Atlas cluster is running
3. Add your IP or 0.0.0.0/0 to IP Access List in MongoDB Atlas

### Google API Key Error
1. Get key from https://makersuite.google.com/app/apikey
2. Update `GOOGLE_API_KEY` in `.env`
3. Restart containers: `docker-compose restart`

---

## 📊 Health Check

After services start, verify health:

```powershell
# Check backend health
curl http://localhost:8000/health

# Check all containers
docker ps

# View logs
docker-compose logs -f
```

---

## 🛑 Stopping the Application

Press `Ctrl+C` in the terminal, then:
```powershell
docker-compose down
```

---

## 🎯 Next Steps

1. **Create Admin User:**
   ```powershell
   docker exec -it foodie-backend python scripts/make_admin.py --email your@email.com
   ```

2. **Test API Endpoints:**
   - Visit http://localhost:8000/docs
   - Try the interactive API documentation

3. **Use the Chatbot:**
   - Open http://localhost:5173
   - Start chatting with the AI assistant

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify `.env` configuration
3. Ensure Docker Desktop is running
4. Check MongoDB Atlas connectivity

---

**Happy Coding! 🍕**
