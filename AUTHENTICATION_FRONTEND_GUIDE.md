# 🔐 Authentication Endpoints - Frontend Integration Guide

## 🚨 CORS Errors Fixed for Both Login & Registration

Your frontend was getting CORS errors because:
1. ❌ **500 Internal Server Error** was happening FIRST
2. ❌ **Missing endpoints** - Frontend called `/users/login` and `/users/register` but they didn't exist
3. ❌ **CORS headers missing** on error responses

### ✅ What I Fixed:

1. **Added `/users/register` endpoint** - Now matches what your frontend expects
2. **Added `/users/login` endpoint** - Already added earlier
3. **Enhanced error handling** - Better error logging
4. **CORS working** - All endpoints now properly support CORS

---

## 🎯 CORRECT FRONTEND CODE

### 1. **Registration Function**

```javascript
// registerUser.js
async function registerUser(userData) {
    try {
        const response = await fetch('http://localhost:8000/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: userData.username,
                email: userData.email,
                password: userData.password,
                first_name: userData.firstName,
                last_name: userData.lastName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const data = await response.json();
        console.log('✅ Registration successful!');
        return data;
        
    } catch (error) {
        console.error('❌ Registration error:', error.message);
        throw error;
    }
}

// Usage
registerUser({
    username: 'JohnDoe123',
    email: 'john@example.com',
    password: 'MyPassword123',
    firstName: 'John',
    lastName: 'Doe'
})
.then(data => {
    alert('Registration successful! Please login.');
    console.log('User ID:', data.user_id);
})
.catch(err => {
    alert('Registration failed: ' + err.message);
});
```

**Request Format:**
```json
{
  "username": "JohnDoe123",
  "email": "john@example.com",
  "password": "MyPassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Success Response (201 Created):**
```json
{
  "message": "Registration successful! You can now login.",
  "user_id": "6710b8c6733ee9763f0ca04a",
  "username": "JohnDoe123",
  "email": "john@example.com"
}
```

**Error Responses:**
```json
// 400 - Weak password
{
  "detail": "Password must be at least 8 characters long and contain uppercase, lowercase, and numbers"
}

// 400 - Email exists
{
  "detail": "An account with this email already exists"
}

// 400 - Username exists
{
  "detail": "An account with this username already exists"
}
```

---

### 2. **Login Function**

```javascript
// loginUser.js
async function loginUser(usernameOrEmail, password) {
    try {
        // Option 1: Use form data (current frontend approach)
        const formData = new URLSearchParams();
        formData.append('username', usernameOrEmail);
        formData.append('password', password);
        formData.append('grant_type', 'password');
        
        const response = await fetch('http://localhost:8000/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        
        // Save token
        localStorage.setItem('token', data.access_token);
        console.log('✅ Login successful!');
        
        return data;
        
    } catch (error) {
        console.error('❌ Login error:', error.message);
        throw error;
    }
}

// Usage
loginUser('MG9328', 'Meet7805')
    .then(data => {
        console.log('Token:', data.access_token);
        // Redirect to dashboard
    })
    .catch(err => {
        alert('Login failed: ' + err.message);
    });
```

**Request Format (Form Data):**
```
username=MG9328&password=Meet7805&grant_type=password
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 3. **Alternative: Use JSON Endpoints (RECOMMENDED)**

For better consistency, you can update your frontend to use the JSON-based endpoints:

```javascript
// RECOMMENDED: Use /api/auth/* endpoints

// Register with JSON
async function registerUserJSON(userData) {
    const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: userData.username,
            email: userData.email,
            password: userData.password,
            first_name: userData.firstName,
            last_name: userData.lastName
        })
    });
    return response.json();
}

// Login with JSON
async function loginUserJSON(usernameOrEmail, password) {
    const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username_or_email: usernameOrEmail,
            password: password
        })
    });
    
    const data = await response.json();
    localStorage.setItem('token', data.token); // Note: 'token' not 'access_token'
    localStorage.setItem('user', JSON.stringify(data.user)); // Includes user details!
    return data;
}
```

**Advantage of JSON endpoints:**
- ✅ More consistent API design
- ✅ Returns full user object (not just token)
- ✅ Better response structure
- ✅ Includes token expiry info

---

## 🧪 TESTING IN BROWSER CONSOLE

### Test Registration

Open your frontend (http://localhost:5173), press F12, go to Console, paste:

```javascript
// Test registration
fetch('http://localhost:8000/users/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'TestUser123',
        email: 'test@example.com',
        password: 'Password123',
        first_name: 'Test',
        last_name: 'User'
    })
})
.then(r => r.json())
.then(data => console.log('✅ Registration:', data))
.catch(err => console.error('❌ Error:', err));
```

### Test Login

```javascript
// Test login (form data)
const formData = new URLSearchParams();
formData.append('username', 'MG9328');
formData.append('password', 'Meet7805');
formData.append('grant_type', 'password');

fetch('http://localhost:8000/users/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: formData
})
.then(r => r.json())
.then(data => {
    console.log('✅ Login:', data);
    localStorage.setItem('token', data.access_token);
})
.catch(err => console.error('❌ Error:', err));
```

---

## 📊 ENDPOINT COMPARISON

| Feature | `/users/*` (Legacy) | `/api/auth/*` (Recommended) |
|---------|---------------------|----------------------------|
| **Registration** | `/users/register` ✅ | `/api/auth/register` ✅ |
| **Login** | `/users/login` ✅ | `/api/auth/login` ✅ |
| **Request Format** | Mixed (form/JSON) | JSON only |
| **Response** | Basic | Detailed (includes user object) |
| **CORS Support** | ✅ Yes | ✅ Yes |
| **Status** | Working now | Recommended |

---

## 🔍 Password Requirements

Your password must meet these requirements:
- ✅ At least 8 characters long
- ✅ Contains uppercase letter (A-Z)
- ✅ Contains lowercase letter (a-z)
- ✅ Contains number (0-9)

**Valid Examples:**
- ✅ `Password123`
- ✅ `MySecurePass1`
- ✅ `Test1234`

**Invalid Examples:**
- ❌ `password` (no uppercase, no number)
- ❌ `PASSWORD123` (no lowercase)
- ❌ `Pass1` (too short)

---

## 🛡️ Security Features

### Rate Limiting
- Login endpoint: **5 attempts per minute**
- If exceeded, wait 1 minute before trying again

### Password Security
- Hashed with **bcrypt** (industry standard)
- Never stored in plain text
- Validated for strength on registration

### JWT Tokens
- Expires in **1 hour** (3600 seconds)
- Include in requests: `Authorization: Bearer <token>`
- Signed with secret key (cannot be forged)

---

## 🎯 COMPLETE REACT EXAMPLE

```jsx
// LoginRegister.jsx
import { useState } from 'react';

function LoginRegister() {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        firstName: '',
        lastName: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('http://localhost:8000/users/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password,
                    first_name: formData.firstName,
                    last_name: formData.lastName
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail);
            }

            const data = await response.json();
            alert('Registration successful! Please login.');
            setIsLogin(true);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const formDataBody = new URLSearchParams();
            formDataBody.append('username', formData.username);
            formDataBody.append('password', formData.password);
            formDataBody.append('grant_type', 'password');

            const response = await fetch('http://localhost:8000/users/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: formDataBody
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail);
            }

            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            alert('Login successful!');
            // Redirect or update UI
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-tabs">
                <button 
                    onClick={() => setIsLogin(true)}
                    className={isLogin ? 'active' : ''}
                >
                    Login
                </button>
                <button 
                    onClick={() => setIsLogin(false)}
                    className={!isLogin ? 'active' : ''}
                >
                    Register
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {isLogin ? (
                <form onSubmit={handleLogin}>
                    <input
                        type="text"
                        placeholder="Username or Email"
                        value={formData.username}
                        onChange={(e) => setFormData({...formData, username: e.target.value})}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                        required
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>
            ) : (
                <form onSubmit={handleRegister}>
                    <input
                        type="text"
                        placeholder="Username"
                        value={formData.username}
                        onChange={(e) => setFormData({...formData, username: e.target.value})}
                        required
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                        required
                    />
                    <input
                        type="text"
                        placeholder="First Name"
                        value={formData.firstName}
                        onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                        required
                    />
                    <input
                        type="text"
                        placeholder="Last Name"
                        value={formData.lastName}
                        onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password (8+ chars, uppercase, lowercase, number)"
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                        required
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Registering...' : 'Register'}
                    </button>
                </form>
            )}
        </div>
    );
}

export default LoginRegister;
```

---

## 📋 SUMMARY

### ✅ Fixed Issues:
1. **Added `/users/register` endpoint** - Frontend can now register users
2. **Added `/users/login` endpoint** - Frontend can now login
3. **CORS configured** - All endpoints work with your frontend
4. **Error handling** - Better error messages and logging

### 🎯 What You Need to Do:
1. **Use the code examples above** in your frontend
2. **Test in browser console** first to verify it works
3. **Integrate into your React components**
4. **Handle errors gracefully** (show user-friendly messages)

### 🔗 Available Endpoints:

**For your current frontend (works now):**
- ✅ `POST /users/register` - Register new user
- ✅ `POST /users/login` - Login user

**Alternative (recommended for future):**
- ✅ `POST /api/auth/register` - Register with detailed response
- ✅ `POST /api/auth/login` - Login with user object included

Both work! CORS errors are fixed! 🎉

---

**Last Updated:** October 17, 2025  
**Status:** ✅ All endpoints working with CORS support
