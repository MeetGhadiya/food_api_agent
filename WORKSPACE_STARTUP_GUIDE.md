# 🚀 FoodieExpress Workspace - Complete Startup Guide

**Last Updated:** October 17, 2025  
**Version:** 4.0.0  
**Status:** Production Ready

---

## 📋 Quick Start Options

### ⭐ **Option 1: Docker (Recommended - All Services)**

**Prerequisites:**
- ✅ Docker Desktop installed and running
- ✅ 8GB RAM minimum (16GB recommended)
- ✅ `.env` file configured

**Steps:**

1. **Start Docker Desktop**
   ```powershell
   # Docker Desktop should be running (look for whale icon in system tray)
   # Or start it with:
   Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

2. **Wait for Docker to be ready** (~30 seconds)
   ```powershell
   # Test Docker is ready
   docker ps
   ```

3. **Start all services**
   ```powershell
   cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1"
   docker-compose up -d
   ```

4. **Verify services are running**
   ```powershell
   docker-compose ps
   ```

5. **Access the application**
   - 🌐 **Frontend (React UI):** http://localhost:5173
   - 🔧 **API Documentation:** http://localhost:8000/docs
   - 🤖 **AI Chatbot Agent:** http://localhost:5000
   - 🗄️ **MongoDB Express:** http://localhost:8082 (if using override)
   - 📊 **Redis Commander:** http://localhost:8081 (if using override)

**Stop services:**
```powershell
docker-compose down
```

---

### 🔧 **Option 2: Manual Startup (Development)**

Run each service individually for development and debugging.

#### **Step 1: Start API Backend**

```powershell
# Terminal 1 - API Backend
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\food_api"

# Create/activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Start API server
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
✅ MongoDB client initialized successfully
✅ Database connection established.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Access:** http://localhost:8000/docs

---

#### **Step 2: Start AI Chatbot Agent**

```powershell
# Terminal 2 - AI Agent
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\food_chatbot_agent"

# Create/activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Start agent server
python app.py
```

**Expected output:**
```
✅ Redis connection successful
 * Running on http://0.0.0.0:5000
```

**Access:** http://localhost:5000

---

#### **Step 3: Start Frontend**

```powershell
# Terminal 3 - Frontend
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\chatbot_frontend"

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Access:** http://localhost:5173

---

### 🧪 **Option 3: Run Tests Only**

Perfect for CI/CD or testing without starting full services.

#### **Quick Smoke Test** (7 critical tests, ~10 seconds)
```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1"
python quick_smoke_test.py
```

#### **Full Test Suite** (306 tests, ~2-5 minutes)
```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1"
python run_comprehensive_tests_v3.py
```

#### **Test with Coverage**
```powershell
python run_comprehensive_tests_v3.py --coverage
# Open htmlcov/index.html to view coverage report
```

#### **Validate Test Suite**
```powershell
python validate_test_suite.py
```

---

## 🔍 Service Health Check

Run this anytime to check service status:

```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1"
python check_api_status.py
```

**Expected output when all services running:**
```
================================================================================
  FOODIEEXPRESS - SERVICE STATUS CHECK
================================================================================

✅ FastAPI is running - FoodieExpress v4.0.0
✅ MongoDB is running and accessible
   → Production database 'food_db' exists

================================================================================
  ✅ ALL SERVICES RUNNING - Ready to run tests
================================================================================
```

---

## 📊 Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FoodieExpress v4.0                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Frontend   │ ───► │  AI Agent    │ ───► │  Backend  │ │
│  │  React+Vite  │      │   (Flask)    │      │ (FastAPI) │ │
│  │ Port: 5173   │      │  Port: 5000  │      │Port: 8000 │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                     │                     │        │
│         │                     ▼                     │        │
│         │              ┌──────────┐                 │        │
│         │              │  Redis   │                 │        │
│         │              │Port: 6379│                 │        │
│         │              └──────────┘                 │        │
│         │                                           │        │
│         └───────────────────────┬───────────────────┘        │
│                                 ▼                            │
│                          ┌──────────┐                        │
│                          │ MongoDB  │                        │
│                          │Port:27017│                        │
│                          └──────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐳 Docker Services Overview

| Service | Container Name | Port | Purpose | Health Check |
|---------|---------------|------|---------|--------------|
| **mongodb** | foodie-mongodb | 27017 | Database | `mongosh --eval db.ping()` |
| **redis** | foodie-redis | 6379 | Session Store | `redis-cli ping` |
| **backend** | foodie-backend | 8000 | FastAPI Server | `GET /health` |
| **agent** | foodie-agent | 5000 | AI Chatbot | `GET /health` |
| **frontend** | foodie-frontend | 5173 | React UI | `GET /` |

---

## 🔧 Common Commands

### Docker Management

```powershell
# View running containers
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f agent

# Restart a service
docker-compose restart backend

# Rebuild a service
docker-compose up -d --build backend

# Stop all services
docker-compose down

# Stop and remove volumes (clean reset)
docker-compose down -v

# Check resource usage
docker stats
```

### Database Management

```powershell
# Connect to MongoDB (Docker)
docker exec -it foodie-mongodb mongosh -u admin -p admin123

# Connect to Redis (Docker)
docker exec -it foodie-redis redis-cli

# Backup MongoDB
docker exec foodie-mongodb mongodump --out /data/backup

# View database logs
docker-compose logs mongodb
```

### Development Workflow

```powershell
# Make code changes, then rebuild
docker-compose up -d --build backend

# View real-time logs while developing
docker-compose logs -f backend agent

# Quick restart after config changes
docker-compose restart

# Check container health
docker inspect foodie-backend --format='{{.State.Health.Status}}'
```

---

## 🐛 Troubleshooting

### Issue: "Docker is not running"

**Symptoms:**
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Solutions:**
1. **Start Docker Desktop**
   - Look for whale icon in system tray
   - Or run: `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"`
2. **Wait 30 seconds** for Docker to initialize
3. **Test:** `docker ps`

---

### Issue: "Port already in use"

**Symptoms:**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solutions:**
```powershell
# Find process using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use different port in docker-compose.yml
```

---

### Issue: "MongoDB connection failed"

**Symptoms:**
```
❌ MongoDB connection failed
```

**Solutions:**

**If using Docker MongoDB:**
```powershell
# Check MongoDB container is running
docker ps | findstr mongodb

# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

**If using MongoDB Atlas:**
```powershell
# Update .env file with correct credentials
notepad .env

# Verify MONGODB_URI format:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
```

---

### Issue: "Services won't start"

**Symptoms:**
```
ERROR: Service 'backend' failed to build
```

**Solutions:**
```powershell
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check disk space
docker system df

# Prune unused resources
docker system prune -a
```

---

### Issue: "Frontend not loading"

**Symptoms:**
- Page shows blank or error
- Console shows CORS errors

**Solutions:**
1. **Check backend is running:** http://localhost:8000
2. **Check CORS settings** in `.env`:
   ```
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5000
   ```
3. **Clear browser cache** and reload
4. **Check frontend logs:**
   ```powershell
   docker-compose logs frontend
   ```

---

## 📈 Performance Optimization

### For Development (Fast Iteration)
```powershell
# Use manual startup (Option 2) for faster restarts
# Only run services you're actively developing
```

### For Production Testing
```powershell
# Use Docker with production settings
docker-compose -f docker-compose.yml up -d

# Monitor resource usage
docker stats
```

### Database Performance
```powershell
# Create indexes (in MongoDB shell)
db.restaurants.createIndex({ "cuisine": 1 })
db.orders.createIndex({ "user_id": 1, "created_at": -1 })
```

---

## 🎯 What to Do Next

### ✅ **First Time Setup**
1. ✅ Start Docker Desktop
2. ✅ Run `docker-compose up -d`
3. ✅ Wait for all health checks to pass
4. ✅ Open http://localhost:5173
5. ✅ Create admin user (see below)
6. ✅ Test the application

### 🔐 **Create Admin User**
```powershell
# After services are running
cd food_api
python scripts/make_admin.py
```

### 🧪 **Run Tests**
```powershell
# Quick smoke test
python quick_smoke_test.py

# Full test suite
python run_comprehensive_tests_v3.py
```

### 📊 **Populate Test Data**
```powershell
cd food_api
python populate_new_data.py
```

### 🎨 **Access Admin Features**
- Create admin user (see above)
- Login at http://localhost:5173
- Access admin dashboard

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview and setup |
| `TEST_EXECUTION_GUIDE.md` | Comprehensive testing guide |
| `TESTING_GUIDE.md` | Testing strategies and best practices |
| `TEST_SUITE_INDEX.md` | Test suite navigation |
| `COMPREHENSIVE_TEST_SUITE_README.md` | Detailed test documentation |
| `QUICK_START_TESTING.md` | Quick testing reference |

---

## 💡 Pro Tips

### Fast Development Cycle
```powershell
# Terminal 1: Backend with auto-reload
cd food_api
uvicorn app.main:app --reload

# Terminal 2: Frontend with HMR
cd chatbot_frontend  
npm run dev

# Terminal 3: Monitor logs
docker-compose logs -f redis mongodb
```

### Debug Mode
```powershell
# Run with verbose logging
docker-compose --verbose up

# Attach to container for debugging
docker exec -it foodie-backend /bin/sh

# View environment variables
docker exec foodie-backend env
```

### Quick Reset
```powershell
# Nuclear option - fresh start
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

---

## ✅ Success Checklist

Before considering the workspace "running":

- [ ] Docker Desktop is running
- [ ] All 5 containers are healthy (`docker-compose ps`)
- [ ] Frontend loads at http://localhost:5173
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Can create user and login
- [ ] Chatbot responds to messages
- [ ] Health check passes: `python check_api_status.py`

---

## 📞 Quick Reference URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Register new user |
| **API Docs** | http://localhost:8000/docs | - |
| **AI Agent** | http://localhost:5000 | - |
| **MongoDB Express** | http://localhost:8082 | admin / admin |
| **Redis Commander** | http://localhost:8081 | - |

---

**Need Help?** Check the logs:
```powershell
docker-compose logs -f
```

**Everything Working?** 🎉 Start exploring the app at http://localhost:5173
