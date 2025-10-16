# MongoDB Setup Guide - TEMPLATE

**⚠️ IMPORTANT: This is a TEMPLATE file. Never put real credentials here!**

---

## 📋 MongoDB Atlas Setup

### Step 1: Create MongoDB Atlas Account
1. Go to: https://cloud.mongodb.com/
2. Sign up or login
3. Create a new project (e.g., "FoodieExpress")

### Step 2: Create a Cluster
1. Click "Build a Cluster"
2. Choose FREE tier (M0)
3. Select region closest to you
4. Name your cluster (e.g., "FoodAPICluster")
5. Click "Create Cluster" (takes 1-3 minutes)

### Step 3: Create Database User
1. Go to "Database Access" (left sidebar)
2. Click "Add New Database User"
3. Authentication Method: Password
4. Username: `[CHOOSE_A_USERNAME]` (e.g., foodapi_user)
5. Password: `[GENERATE_STRONG_PASSWORD]` (click "Autogenerate")
6. **IMPORTANT**: Save this password securely!
7. Database User Privileges: "Atlas admin" or "Read and write to any database"
8. Click "Add User"

### Step 4: Configure Network Access
1. Go to "Network Access" (left sidebar)
2. Click "Add IP Address"
3. For development: Click "Allow Access from Anywhere" (0.0.0.0/0)
4. For production: Add your specific IP address
5. Click "Confirm"

### Step 5: Get Connection String
1. Go to "Database" (left sidebar)
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Driver: Python
5. Version: 3.12 or later
6. Copy the connection string:
   ```
   mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 6: Create .env File

**DO THIS**:
```bash
# Navigate to food_api directory
cd food_api

# Create .env file (NEVER commit this!)
# On Windows:
notepad .env

# On Mac/Linux:
nano .env
```

**Add this content** (replace with YOUR values):
```bash
# MongoDB Atlas Connection
MONGODB_URI=mongodb+srv://[USERNAME]:[PASSWORD]@[CLUSTER].mongodb.net/[DATABASE_NAME]?retryWrites=true&w=majority&appName=[APP_NAME]

# Example structure (DO NOT use this exact string):
# MONGODB_URI=mongodb+srv://myuser:MySecureP@ssw0rd@mycluster.abc123.mongodb.net/mydb?retryWrites=true&w=majority
```

**Replace**:
- `[USERNAME]` - Your database username (from Step 3)
- `[PASSWORD]` - Your database password (from Step 3)
- `[CLUSTER]` - Your cluster address (from Step 5)
- `[DATABASE_NAME]` - Your database name (e.g., `foodie_db`)
- `[APP_NAME]` - Your app name (e.g., `FoodAPICluster`)

### Step 7: Verify .env is in .gitignore

**CHECK**:
```bash
cat .gitignore | grep ".env"
```

**Should see**:
```
.env
*.env
.env.*
!.env.example
```

**CRITICAL**: Never commit the `.env` file to git!

### Step 8: Test Connection

**Run API**:
```bash
cd food_api
python -m uvicorn app.main:app --reload
```

**Test endpoint**:
```bash
curl http://localhost:8000/restaurants/
```

**Expected**: Returns list of restaurants from MongoDB

---

## ✅ Verification Checklist

- [ ] MongoDB Atlas account created
- [ ] Cluster created and running
- [ ] Database user created with strong password
- [ ] Network access configured (IP whitelisted)
- [ ] Connection string obtained
- [ ] `.env` file created in `food_api/` directory
- [ ] `.env` contains correct MONGODB_URI
- [ ] `.env` is listed in `.gitignore`
- [ ] `.env` is NOT committed to git (verify with `git status`)
- [ ] API starts without errors
- [ ] `/restaurants/` endpoint returns data

---

## 🔒 Security Best Practices

### ✅ DO:
- Use strong passwords (20+ characters, mixed case, numbers, symbols)
- Keep `.env` in `.gitignore`
- Rotate passwords periodically (every 3-6 months)
- Use different passwords for dev/staging/production
- Limit network access to specific IPs in production
- Use environment-specific .env files (`.env.dev`, `.env.prod`)

### ❌ DON'T:
- Put credentials in markdown documentation files
- Commit `.env` files to git
- Share passwords in chat/email
- Use weak passwords
- Allow access from anywhere (0.0.0.0/0) in production
- Hardcode credentials in code

---

## 🆘 Troubleshooting

### Error: "Authentication failed"
- ✅ Check username and password in .env
- ✅ Make sure password doesn't contain special characters that need URL encoding
- ✅ Verify database user exists in MongoDB Atlas

### Error: "Network timeout"
- ✅ Check network access settings in MongoDB Atlas
- ✅ Verify your IP is whitelisted
- ✅ Check firewall/VPN settings

### Error: "Database not found"
- ✅ MongoDB Atlas creates databases automatically
- ✅ Make sure database name in connection string is correct
- ✅ Try creating database manually in MongoDB Atlas UI

---

## 📖 Example (with placeholders)

**Connection String Structure**:
```
mongodb+srv://[USER]:[PASS]@[CLUSTER].[ID].mongodb.net/[DB]?retryWrites=true&w=majority&appName=[APP]
```

**Real Example** (with fake credentials for illustration only):
```
mongodb+srv://demo_user:MyS3cr3tP@ss!@mycluster.abc123.mongodb.net/demo_db?retryWrites=true&w=majority&appName=DemoApp
```

**Your .env should look like**:
```bash
MONGODB_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/YOUR_DATABASE?retryWrites=true&w=majority&appName=YOUR_APP
```

---

## 🔗 Resources

- MongoDB Atlas Docs: https://www.mongodb.com/docs/atlas/
- Connection String Format: https://www.mongodb.com/docs/manual/reference/connection-string/
- Python Motor Driver: https://motor.readthedocs.io/

---

**Created**: October 16, 2025  
**Purpose**: Safe documentation template without real credentials  
**Status**: ✅ Safe to commit to git
