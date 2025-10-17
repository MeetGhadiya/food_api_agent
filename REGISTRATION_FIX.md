# 🔧 FIX FOR REGISTRATION ERROR

## Problem Identified

**500 Internal Server Error** when registering = MongoDB connection is broken!

Your `.env` file had a placeholder password that was never replaced:
```
%7B%7BYour_Database_Password%7D%7D
```

## ✅ Solution Applied

I've updated your `.env` file to use **local MongoDB** instead of MongoDB Atlas.

**New connection string:**
```
MONGODB_URI="mongodb://localhost:27017/food_db"
```

## 🚀 Next Steps

### Step 1: Make Sure MongoDB is Running

Check if MongoDB is installed and running:

```powershell
# Check if MongoDB is running
Get-Process mongod -ErrorAction SilentlyContinue
```

**If NOT installed**, download and install MongoDB Community Edition:
- Download: https://www.mongodb.com/try/download/community
- Or use Docker: `docker run -d -p 27017:27017 mongo:latest`

**If installed but not running:**
```powershell
# Start MongoDB (if installed as Windows Service)
net start MongoDB

# Or run manually
mongod --dbpath="C:\data\db"
```

### Step 2: Restart Your FastAPI Backend

1. **Stop** the current backend (Ctrl+C in the terminal running it)
2. **Start** it again:
   ```powershell
   cd food_api
   python -m uvicorn app.main:app --reload
   ```

### Step 3: Try Registration Again

1. Go to http://localhost:5173
2. Click "Login" → "Register"
3. Fill in your details:
   - Username: `MG9328`
   - Email: `mitg7805@gmail.com`
   - Password: `Meet@123`
4. Click "Create Account"

**Should work now!** ✅

---

## Alternative: Use MongoDB Atlas (Cloud)

If you want to use MongoDB Atlas (cloud database):

1. Get your actual MongoDB Atlas password
2. Update `.env` file:
   ```
   MONGODB_URI="mongodb+srv://User_name:YOUR_ACTUAL_PASSWORD@foodapicluster.6z9sntm.mongodb.net/food_db?retryWrites=true&w=majority&appName=FoodAPICluster"
   ```
   Replace `YOUR_ACTUAL_PASSWORD` with your real password

3. Restart backend

---

## 🧪 Verify Fix

Run this after restarting backend:

```powershell
python diagnose_registration.py
```

You should see:
```
✅ Registration successful!
```

---

## Summary

**What was wrong:**
- MongoDB connection string had placeholder password
- Backend couldn't connect to database
- Registration failed with 500 error

**What we fixed:**
- Changed to local MongoDB connection
- Now backend will connect to local MongoDB

**What to do:**
1. Make sure MongoDB is running locally
2. Restart FastAPI backend
3. Try registration again

Should work now! 🎉
