# 🎯 FoodieBot Popup Widget - Swiggy-Style Integration Guide

## 🌟 Overview
The FoodieBot popup widget is a modern, non-intrusive chat assistant that works exactly like Swiggy's support chat - it appears as a floating button on your website and only asks for login when the user tries to perform protected actions like ordering food.

---

## 🚀 **Key Features**

### ✨ **Swiggy-Style Experience**
- **Floating Chat Button**: Always visible in bottom-right corner with pulse animation
- **Popup Modal**: Opens as a sleek chat window without disrupting the main page
- **Smart Authentication**: Only prompts for login when necessary (like when placing orders)
- **Persistent State**: Remembers login status across page refreshes
- **Auto-Detection**: Automatically detects if user is already logged in

### 🎨 **Modern Design**
- Clean, professional interface
- Gradient color scheme (Orange #FF6B35 + Teal #4ECDC4)
- Smooth animations and transitions
- Responsive for mobile and desktop
- Typing indicators and message animations

### 🔐 **Smart Authentication Flow**
```
User Action → Check Auth → Execute or Prompt Login
├─ Public Actions (Browse, Search) → Execute immediately
└─ Protected Actions (Order, Manage) → Prompt login only if needed
```

---

## 📋 **How It Works**

### 1. **Initial State**
- Floating chat button visible on every page
- User can click to open chat widget
- Welcome screen shows quick actions
- NO login required to start chatting

### 2. **Browsing & Searching** (No Login)
```javascript
User: "Show me all restaurants"
Bot: [Lists all restaurants immediately]

User: "Tell me about Pizza Palace"
Bot: [Shows restaurant details immediately]
```

### 3. **Ordering Flow** (Login Required)
```javascript
User: "I want to order pizza from Pizza Palace"
Bot: "🔒 Please login first to place an order!"
[Login modal automatically opens]

[User logs in]
Bot: "Welcome back! 🎉 You're now logged in."

User: "Order pizza from Pizza Palace"
Bot: "✅ Order placed successfully!"
```

---

## 🎯 **Integration Steps**

### **Step 1: Files Created**
```
food_api_agent/static/
├── popup_widget.html     # Main popup widget page
├── popup_styles.css      # Widget styling
└── popup_widget.js       # Widget functionality
```

### **Step 2: Access the Widget**
```
Full Interface:  http://localhost:5000
Popup Widget:    http://localhost:5000/widget
API Endpoint:    http://localhost:5000/chat
```

### **Step 3: Using the Widget**

#### Open in Browser:
```
http://localhost:5000/widget
```

You'll see:
- Demo website with restaurant cards (simulates your main site)
- Floating chat button in bottom-right corner
- Click the button to open chat widget

---

## 🎮 **User Interactions**

### **1. Quick Actions (Welcome Screen)**
When user opens widget, they see 3 quick action buttons:

| Button | Action | Auth Required |
|--------|--------|---------------|
| 🏪 Browse Restaurants | Shows all restaurants | ❌ No |
| 🛒 Place an Order | Asks what to order | ✅ Yes (prompts if not logged in) |
| 📝 View My Orders | Shows order history | ✅ Yes (prompts if not logged in) |

### **2. Suggestion Chips**
Pre-written suggestions for common queries:
- "🏪 All Restaurants"
- "🍕 Italian Food"
- "🛒 Order Pizza"

### **3. Natural Conversation**
Users can type anything:
```
"What restaurants do you have?"
"I'm craving Italian food"
"Order me a pizza"
"Show my past orders"
"Create a new restaurant called Burger King in Downtown serving American food"
```

---

## 🔐 **Authentication System**

### **How It Works**

#### **Login Detection:**
```javascript
// Check localStorage on page load
let authToken = localStorage.getItem('authToken');
let currentUser = localStorage.getItem('currentUser');

if (authToken && currentUser) {
    // User is logged in - update UI
    updateUIForLoggedIn();
}
```

#### **Protected Action Flow:**
```javascript
User attempts to order → Agent checks authToken

If authToken exists:
    ✅ Process order immediately
Else:
    🔒 Show login modal
    Wait for login
    Then process order
```

### **Login Persistence**
- Auth token stored in `localStorage`
- Persists across page refreshes
- Syncs with main website login (if integrated)
- Demo login button shows user status

---

## 💡 **Smart Features**

### **1. Contextual Login Prompt**
Different messages for different actions:

```javascript
Ordering Food:
"🔒 Please login first to place an order!"

Viewing Orders:
"🔒 Please login first to view your orders!"

Creating Restaurant:
"🔒 Please login first to create a restaurant!"
```

### **2. Auto-Focus on Login**
When login required:
1. Bot sends login required message
2. Wait 1 second (user reads message)
3. Auto-open login modal
4. User logs in
5. Resume original action

### **3. Welcome Back Message**
```javascript
User logs in → Bot says:
"Welcome back, [Username]! 🎉 You're now logged in. How can I help you?"
```

---

## 🎨 **Visual Design**

### **Chat Widget Button**
```css
Position: Fixed bottom-right (24px from edges)
Size: 64px × 64px circle
Color: Orange gradient with pulse animation
Icon: Chat bubbles (Font Awesome)
Shadow: Elevated with glow effect
```

### **Popup Window**
```css
Size: 400px × 600px (desktop)
Position: Bottom-right corner
Border Radius: 20px (modern rounded corners)
Shadow: Large elevated shadow
Animation: Slide up + fade in
```

### **Header**
```css
Background: Orange gradient
Height: ~70px
Content: Bot avatar + name + status
Controls: Minimize & Close buttons
```

### **Message Bubbles**
```css
Bot Messages:
├─ Background: White
├─ Avatar: Orange gradient circle
└─ Alignment: Left

User Messages:
├─ Background: Orange gradient
├─ Avatar: Teal circle
└─ Alignment: Right
```

---

## 📱 **Responsive Design**

### **Mobile (<768px)**
```css
Popup becomes fullscreen
Width: 100%
Height: 100vh
Border radius: 0 (no rounded corners)
Fills entire viewport
```

### **Desktop (>768px)**
```css
Popup is floating window
Width: 400px
Height: 600px
Rounded corners
Positioned bottom-right
```

---

## 🔧 **API Integration**

### **Agent API Call**
```javascript
fetch('http://localhost:5000/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: userMessage,
        user_id: currentUser || 'guest',
        token: authToken  // Only sent if user is logged in
    })
});
```

### **Backend Handling (web_agent.py)**
```python
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    token = data.get('token')
    
    # Agent checks if function requires auth
    if function_name in auth_required_functions:
        if not token:
            return jsonify({
                "response": "🔒 Please login first to place an order!"
            })
        # Add token to function call
        function_args['token'] = token
    
    # Execute function with AI
    result = call_gemini_function(function_name, function_args)
    return jsonify({"response": result})
```

---

## 🎯 **Example User Journeys**

### **Journey 1: Guest Browsing**
```
1. User opens website
2. Sees floating chat button with pulse
3. Clicks chat button
4. Sees welcome screen with quick actions
5. Clicks "Browse Restaurants"
6. Bot shows all restaurants (no login needed)
7. User asks "Tell me about Pizza Palace"
8. Bot shows details (no login needed)
9. User closes chat and continues browsing
```

### **Journey 2: First-Time Ordering**
```
1. User opens chat
2. Types "I want to order pizza"
3. Bot: "🔒 Please login first to place an order!"
4. Login modal auto-opens
5. User sees they need account
6. Clicks "Sign up" link
7. Fills registration form
8. Returns to login modal
9. Logs in successfully
10. Bot: "Welcome back! 🎉"
11. User: "Order pizza from Pizza Palace"
12. Bot: "✅ Order placed!"
```

### **Journey 3: Returning User**
```
1. User opens website (already logged in from before)
2. Token exists in localStorage
3. User opens chat
4. Types "Order pizza from Pizza Palace"
5. Bot processes immediately (no login prompt)
6. Bot: "✅ Order placed successfully!"
7. User: "Show my orders"
8. Bot: [Shows order history including new order]
```

---

## 🚀 **Deployment Checklist**

### **Before Going Live:**

1. ✅ **Backend Running**
   ```bash
   cd food_api
   uvicorn app.main:app --reload
   # Should be on http://localhost:8000
   ```

2. ✅ **Agent Running**
   ```bash
   cd food_api_agent
   python web_agent.py
   # Should be on http://localhost:5000
   ```

3. ✅ **MongoDB Connected**
   - Check connection in logs
   - Verify "✅ Database connection established"

4. ✅ **Test Authentication**
   - Register new user
   - Login
   - Verify token stored in localStorage
   - Try protected action

5. ✅ **Test All Functions**
   - Browse restaurants (no login)
   - Search restaurant (no login)
   - Place order (login required)
   - View orders (login required)
   - Create restaurant (login required)
   - Update restaurant (login required)

---

## 🎨 **Customization Options**

### **Change Colors**
Edit `popup_styles.css`:
```css
:root {
    --primary: #FF6B35;      /* Main orange */
    --primary-dark: #E85A2A;  /* Darker orange */
    --secondary: #4ECDC4;     /* Teal accent */
}
```

### **Change Bot Name**
Edit `popup_widget.html`:
```html
<h3>FoodieBot</h3>  <!-- Change to your bot name -->
```

### **Change Welcome Message**
Edit `popup_widget.html`:
```html
<h2>Hi there! 👋</h2>
<p>I'm FoodieBot, your AI assistant...</p>
```

### **Change Position**
Edit `popup_styles.css`:
```css
.chat-widget-button {
    bottom: 24px;  /* Distance from bottom */
    right: 24px;   /* Distance from right */
}
```

---

## 🔗 **Integration with Main Website**

### **Embed Widget in Any Page**
```html
<!-- Add these to your existing website -->
<link rel="stylesheet" href="http://localhost:5000/static/popup_styles.css">
<script src="http://localhost:5000/static/popup_widget.js"></script>

<!-- Widget will appear automatically -->
```

### **Share Login State**
If your main website already has user authentication:
```javascript
// When user logs in on main site:
localStorage.setItem('authToken', userToken);
localStorage.setItem('currentUser', username);

// Widget will automatically detect and use it
```

### **Custom Integration**
```javascript
// Check if user is logged in on main site
if (mainSiteAuth.isLoggedIn()) {
    // Pass auth to widget
    localStorage.setItem('authToken', mainSiteAuth.token);
    localStorage.setItem('currentUser', mainSiteAuth.username);
}
```

---

## 📊 **Performance**

### **Load Time**
- Initial load: <1 second
- Chat open/close: Instant (CSS animation)
- Message send: 1-2 seconds (AI processing)

### **Storage**
- LocalStorage: ~200 bytes (auth token + username)
- Session storage: Chat history (auto-clears on close)

### **Network**
- Each message: ~1KB request/response
- No polling - only sends when user types
- WebSocket optional for real-time updates

---

## 🎉 **What Makes This Like Swiggy**

✅ **Floating Button**: Always visible, non-intrusive
✅ **Popup Modal**: Doesn't navigate away from page
✅ **Smart Auth**: Only asks for login when needed
✅ **Persistent Login**: Remembers you across sessions
✅ **Quick Actions**: Fast access to common tasks
✅ **Modern Design**: Clean, professional, branded
✅ **Responsive**: Works on mobile and desktop
✅ **Context Aware**: Understands conversation flow

---

## 🚀 **Next Steps**

1. **Open the widget**: http://localhost:5000/widget
2. **Test browsing**: Try "Show me all restaurants"
3. **Test ordering**: Try "Order pizza" (will prompt login)
4. **Register account**: Create a new user
5. **Test with auth**: Order food after logging in
6. **Check persistence**: Refresh page, should stay logged in

---

## 💬 **Support**

For questions or issues:
- Check console logs (F12 in browser)
- Verify Flask server is running
- Ensure MongoDB is connected
- Check API backend is accessible

---

**Enjoy your Swiggy-style AI chatbot! 🎉🤖**
