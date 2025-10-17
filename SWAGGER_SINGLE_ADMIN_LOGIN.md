# ✅ Swagger UI - Single Admin Login

## 🎯 What Was Changed

Swagger UI now uses **HTTP Basic Authentication** with a single admin account instead of JWT Bearer tokens.

---

## 🔐 Admin Credentials

**Username:** `Meet`  
**Password:** `Meet7805`

---

## 📖 How to Use Swagger UI

### Step 1: Open Swagger
Go to: http://localhost:8000/docs

### Step 2: Click "Authorize" Button
You'll see a lock icon at the top right of the Swagger UI.

### Step 3: Enter Admin Credentials
```
Username: Meet
Password: Meet7805
```

### Step 4: Click "Authorize"
You're now authenticated and can test all API endpoints!

### Step 5: Test Any Endpoint
All protected endpoints will now work in Swagger UI.

---

## 🔧 Technical Details

### Authentication Type Changed
**Before:** JWT Bearer Token (complex, required login endpoint)  
**After:** HTTP Basic Auth (simple username/password)

### Security Scheme
```json
{
  "BasicAuth": {
    "type": "http",
    "scheme": "basic",
    "description": "Admin access: Username=Meet, Password=Meet7805"
  }
}
```

### Implementation
```python
# Single admin account
SWAGGER_USERNAME = "Meet"
SWAGGER_PASSWORD = "Meet7805"

def verify_swagger_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify Swagger UI credentials (single admin account)"""
    correct_username = secrets.compare_digest(credentials.username, SWAGGER_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, SWAGGER_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
```

---

## 🎨 What You'll See

### Before Authorization:
```
Available authorizations

BasicAuth (http, Basic)

Value: [empty text box]

[Authorize] [Close]
```

### After Authorization:
```
✅ Authorized

Username: Meet

[Logout]
```

---

## ✅ Benefits

1. **Simple:** Just username and password (no tokens to copy)
2. **Single Admin:** Only one account (Meet/Meet7805)
3. **Secure:** Uses `secrets.compare_digest()` for timing-attack resistance
4. **Clean UI:** No more confusing OAuth2 dialog

---

## 🔄 How It Works

1. Click "Authorize" in Swagger UI
2. Enter `Meet` / `Meet7805`
3. Browser stores credentials in session
4. All API requests automatically include authorization
5. No need to manually copy/paste tokens!

---

## 🚀 Try It Now!

1. **Open Swagger:** http://localhost:8000/docs
2. **Click green "Authorize" button** (top right)
3. **Enter:**
   - Username: `Meet`
   - Password: `Meet7805`
4. **Click "Authorize"**
5. **Test any endpoint!** 🎉

---

## 📋 Changes Made

### File: `food_api/app/main.py`

1. **Added imports:**
```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
```

2. **Changed security scheme:**
```python
# Old: HTTPBearer (JWT)
"HTTPBearer": {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}

# New: BasicAuth (username/password)
"BasicAuth": {
    "type": "http",
    "scheme": "basic",
    "description": "Admin access: Username=Meet, Password=Meet7805"
}
```

3. **Added admin credentials:**
```python
security = HTTPBasic()
SWAGGER_USERNAME = "Meet"
SWAGGER_PASSWORD = "Meet7805"
```

4. **Updated security references:**
All endpoints now use `BasicAuth` instead of `HTTPBearer` in Swagger UI.

---

## 🔒 Security Notes

- **Credentials are hardcoded** for simplicity (suitable for development/demo)
- Uses `secrets.compare_digest()` to prevent timing attacks
- For production: Consider environment variables or database storage
- Browser caches credentials during session

---

## ⚠️ Important

### This Only Affects Swagger UI!
- **Your app's JWT authentication** still works normally for frontend
- **Registration/login endpoints** still work as before
- **This is ONLY for Swagger documentation access**

### Your Frontend
Your frontend should **still use JWT tokens** from `/users/login`:
```javascript
// Frontend still uses JWT (not affected)
const response = await fetch('/users/login', { ... });
const { access_token } = await response.json();
```

---

## ✅ Summary

- ✅ **Swagger UI:** Single admin login (Meet/Meet7805)
- ✅ **Simple:** No more token copying
- ✅ **Secure:** Constant-time comparison
- ✅ **Clean:** One authorization button
- ✅ **Frontend:** JWT authentication unchanged

**Your Swagger UI now has a simple, single-admin login!** 🎉

---

**Last Updated:** October 17, 2025  
**Status:** ✅ Single admin authentication implemented
