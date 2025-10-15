# Quick MongoDB Setup Guide

## Choose Your Method:

### METHOD 1: MongoDB Atlas (Recommended - Takes 2 minutes)

1. **Go to**: https://cloud.mongodb.com
2. **Sign up/Login** (Free account)
3. **Create New Cluster**:
   - Click "Build a Database"
   - Choose "M0 Free" tier
   - Click "Create"
   - Wait 1-3 minutes

4. **Create Database User**:
   - Click "Database Access" (left sidebar)
   - Click "Add New Database User"
   - Username: `foodapi_user`
   - Password: (generate strong password)
   - Role: "Read and write to any database"
   - Click "Add User"

5. **Whitelist Your IP**:
   - Click "Network Access" (left sidebar)
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

6. **Get Connection String**:
   - Click "Database" (left sidebar)
   - Click "Connect" button on your cluster
   - Click "Connect your application"
   - Copy the connection string
   - It looks like: `mongodb+srv://foodapi_user:<password>@...`
   - Replace `<password>` with your actual password

7. **Create .env File**:
   - Open: `food_api\.env` (create new file)
   - Add:
   ```
   SECRET_KEY="your_secret_key_here_use_any_long_random_string"
   MONGODB_URI="mongodb+srv://foodapi_user:YOUR_PASSWORD@cluster.mongodb.net/foodie_db?retryWrites=true&w=majority"
   ALLOWED_ORIGINS="http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:5000"
   ```
   - Save file

8. **Restart FastAPI**:
   ```powershell
   cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1\food_api"
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

9. **Populate Data**:
   ```powershell
   python populate_new_data.py
   ```

10. **Test**:
    ```powershell
    curl http://localhost:8000/restaurants/
    ```
    Should see restaurant data! ✅

---

### METHOD 2: Local MongoDB Installation

1. **Download MongoDB**:
   - Go to: https://www.mongodb.com/try/download/community
   - Download Windows MSI installer
   - Run installer
   - Choose "Complete" installation
   - Install as Windows Service

2. **Verify Installation**:
   ```powershell
   net start MongoDB
   ```

3. **Create .env File**:
   - Open: `food_api\.env` (create new file)
   - Add:
   ```
   SECRET_KEY="your_secret_key_here_use_any_long_random_string"
   MONGODB_URI="mongodb://localhost:27017/foodie_db"
   ALLOWED_ORIGINS="http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:5000"
   ```

4. **Follow steps 8-10 from Method 1**

---

### METHOD 3: Docker (If you have Docker Desktop)

1. **Start Docker Desktop** (wait for it to fully start)

2. **Start MongoDB**:
   ```powershell
   cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1"
   docker-compose up -d mongodb
   ```

3. **Wait for initialization**:
   ```powershell
   Start-Sleep -Seconds 10
   ```

4. **Create .env File**:
   ```
   SECRET_KEY="your_secret_key_here"
   MONGODB_URI="mongodb://admin:secure_password_here@localhost:27017/foodie_db?authSource=admin"
   ALLOWED_ORIGINS="http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:5000"
   ```

5. **Follow steps 8-10 from Method 1**

---

## After MongoDB is Connected:

### You should see in FastAPI terminal:
```
✅ MongoDB client initialized successfully
✅ Database connection established.
```

### Test API works:
```powershell
curl http://localhost:8000/restaurants/
```

Should return JSON array (not error)!

### Re-run tests:
```powershell
cd "c:\Users\Skill\Desktop\m\API\agent workspace\food_api_agent-1"
.\.venv\Scripts\python.exe run_comprehensive_tests.py
```

### Watch agent terminal for DEBUG messages:
```
DEBUG: Calling API at URL: http://localhost:8000/restaurants/
DEBUG: API Response Status Code: 200
DEBUG: Received 15 restaurants
✅ Success!
```

---

## Need Help?

If you get errors, look at the agent terminal. The enhanced logging will show EXACTLY what's wrong:

- **ConnectionError** → FastAPI is not running
- **HTTPError 500** → MongoDB not connected
- **HTTPError 404** → Wrong endpoint/restaurant name
- **Timeout** → Request took too long

The error messages will guide you! 🎯
