# 🔐 Authentication Guide - FoodieBot

## ✅ Problem Fixed!

The chatbot was getting stuck in a loop when users tried to order food without being logged in. It would ask for authentication but not provide clear instructions on HOW to login.

## 🎯 What Was Changed

### 1. **Improved Authentication Message**
Changed from vague "you need to login" to specific instructions:

```
🔒 Authentication Required

To place orders, you need to be logged in first.

**Option 1: Login**
Just say: "Login with username [your_username] and password [your_password]"

**Option 2: Create Account**
Just say: "Register with username [username], email [email] and password [password]"

**Example:**
- "Login with username john and password pass123"
- "Register with username john, email john@email.com and password pass123"
```

### 2. **Added System Instructions**
Added AI guidance to help it understand authentication flow better.

### 3. **Updated Model**
Changed from outdated `gemini-1.5-flash` to `gemini-2.0-flash`

## 📝 How To Use The Chatbot

### Step 1: Browse Restaurants (No Login Required)
```
"Show me all restaurants"
"What Italian restaurants do you have?"
"Tell me about Pizza Palace"
```

### Step 2: Create Account
```
"Register with username john, email john@example.com and password mypass123"
```

### Step 3: Login (if already have account)
```
"Login with username john and password mypass123"
```

### Step 4: Place Orders (Requires Login)
```
"Order a Margherita pizza from Pizza Palace"
"Order a DALPAKVAN from Agashiye The House of MG"
```

### Step 5: Check Orders (Requires Login)
```
"Show my orders"
"What orders have I placed?"
```

## 🔄 How Authentication Works

1. **User tries to order without login** → Bot shows clear login instructions
2. **User says "Login with username X and password Y"** → Bot calls `login_user` function
3. **Backend validates credentials** → Returns JWT token
4. **Frontend stores token** → Automatically includes in future requests
5. **User can now place orders** → Token is verified by backend

## 🧪 Test Commands

### Test Registration:
```powershell
$result = Invoke-RestMethod -Uri http://localhost:5000/chat -Method Post -Body (@{ 
    message = "Register with username testuser123, email test@example.com and password test123"; 
    user_id = "test" 
} | ConvertTo-Json) -ContentType "application/json"
$result.response
```

### Test Login:
```powershell
$result = Invoke-RestMethod -Uri http://localhost:5000/chat -Method Post -Body (@{ 
    message = "Login with username demouser and password demo123"; 
    user_id = "demo" 
} | ConvertTo-Json) -ContentType "application/json"
$token = $result.token
$result.response
```

### Test Order (with token):
```powershell
$result = Invoke-RestMethod -Uri http://localhost:5000/chat -Method Post -Body (@{ 
    message = "Order a pizza from Pizza Palace"; 
    user_id = "demo";
    token = $token
} | ConvertTo-Json) -ContentType "application/json"
$result.response
```

## 🎉 Result

Now users get **clear, actionable instructions** instead of being stuck in a loop!

Before: ❌ "You need to login" → User confused → Tries again → Same message → Loop

After: ✅ "You need to login. Say: 'Login with username john and password pass123'" → User knows exactly what to do → Success!
