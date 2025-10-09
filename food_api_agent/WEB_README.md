# 🍔 Food Delivery AI Agent - Web Interface

A beautiful, modern chat interface for interacting with your Food Delivery API using Google's Gemini AI.

## ✨ Features

### 🎨 Beautiful UI
- Modern gradient design with smooth animations
- Responsive layout for desktop and mobile
- Real-time chat interface with typing indicators
- User authentication with login/register modals

### 🤖 AI-Powered Chat
- Natural language understanding using Google Gemini
- Smart function calling to interact with the Food API
- Context-aware responses
- Quick action buttons for common tasks

### 🔐 User Authentication
- Secure login and registration
- JWT token-based authentication
- Protected endpoints for placing orders
- Session persistence

### 🏪 Restaurant Features
- Browse all available restaurants
- Search for specific restaurants
- View restaurant details (name, area, cuisine)
- Place orders (requires authentication)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API Key
- Running Food API server (http://localhost:8000)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
Create a `.env` file in the `food_api_agent` directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

3. **Start the FastAPI backend:**
```bash
cd food_api
uvicorn app.main:app --reload
```

4. **Start the Web Agent server:**
```bash
cd food_api_agent
python web_agent.py
```

5. **Open your browser:**
Navigate to http://localhost:5000

## 🎯 How to Use

### 1. Browse Restaurants
- Click "Browse Restaurants" or ask: "Show me all restaurants"
- View list of available restaurants with details

### 2. Search Restaurant
- Click "Search Restaurant" or ask: "Tell me about Pizza Palace"
- Get detailed information about a specific restaurant

### 3. Place Order (Requires Login)
- Click "Login" and enter your credentials
- Click "Place Order" or ask: "I want to order Margherita pizza from Pizza Palace"
- Confirm your order

### 4. Register New Account
- Click "Login" → "Register"
- Fill in username, email, and password
- Login with your new credentials

## 💬 Example Queries

Try asking the AI agent:
- "Show me all restaurants"
- "What restaurants are available?"
- "Tell me about Pizza Palace"
- "I want to order a Margherita pizza from Pizza Palace"
- "Place an order for Chicken Tikka from Spice Haven"
- "What cuisine does Pizza Palace serve?"

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (localhost:5000)│
└────────┬────────┘
         │
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Flask Server   │
│  (web_agent.py) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Gemini  │ │  FastAPI     │
│   AI    │ │  Backend     │
└─────────┘ │(localhost:8000)│
            └────────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │   MongoDB    │
              │    Atlas     │
              └──────────────┘
```

## 📁 Project Structure

```
food_api_agent/
├── static/
│   ├── index.html      # Main HTML file
│   ├── styles.css      # Modern CSS styling
│   └── app.js          # Frontend JavaScript
├── web_agent.py        # Flask backend with Gemini AI
├── agent.py            # CLI agent (original)
├── api_client.py       # API helper functions
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```

## 🎨 UI Components

### Header
- Logo and title
- Login/Register buttons
- User info display when logged in

### Chat Area
- Welcome message with quick actions
- Message bubbles (user and agent)
- Typing indicator
- Auto-scroll to latest message

### Input Area
- Text input field
- Send button
- Disabled when not ready

### Modals
- Login form
- Register form
- Error/Success messages

## 🔧 API Endpoints

### Web Agent API (localhost:5000)
- `GET /` - Serve web interface
- `POST /chat` - Send message to AI agent
- `GET /health` - Health check

### Food API (localhost:8000)
- `GET /` - Welcome message
- `GET /restaurants/` - List all restaurants
- `GET /restaurants/{name}` - Get restaurant by name
- `POST /restaurants/` - Create restaurant (auth required)
- `POST /users/register` - Register new user
- `POST /users/login` - Login user
- `POST /orders/` - Place order (auth required)

## 🎨 Customization

### Colors
Edit `styles.css` to change the color scheme:
```css
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    /* ... more variables ... */
}
```

### Quick Actions
Edit `index.html` to add/modify quick action buttons:
```html
<button class="quick-action" data-message="Your message">
    🎯 Your Action
</button>
```

## 🐛 Troubleshooting

### Web interface not loading
- Ensure Flask server is running on port 5000
- Check browser console for errors

### Can't login
- Verify FastAPI backend is running on port 8000
- Check MongoDB connection
- Ensure user is registered

### AI not responding
- Verify GOOGLE_API_KEY is set in .env
- Check Flask server logs
- Ensure Gemini API quota is available

### Orders not working
- Must be logged in first
- Check authentication token is valid
- Verify restaurant and item names are correct

## 📝 Development

### Running in Development Mode
```bash
# Backend API
cd food_api
uvicorn app.main:app --reload

# Web Agent
cd food_api_agent
python web_agent.py
```

### Testing
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all restaurants"}'
```

## 🚀 Production Deployment

For production, use a proper WSGI server:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_agent:app
```

## 📄 License

This project is part of the Food API Agent system.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📞 Support

For issues or questions, please contact the development team.

---

Made with ❤️ using Flask, Google Gemini AI, and FastAPI
