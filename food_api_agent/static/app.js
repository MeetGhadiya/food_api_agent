// Configuration
const API_BASE_URL = 'http://localhost:8000';
const AGENT_API_URL = 'http://localhost:5000';

// State Management
let authToken = localStorage.getItem('authToken') || null;
let currentUser = localStorage.getItem('currentUser') || null;

// DOM Elements
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const closeLoginModal = document.getElementById('closeLoginModal');
const closeRegisterModal = document.getElementById('closeRegisterModal');
const showRegister = document.getElementById('showRegister');
const showLogin = document.getElementById('showLogin');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.getElementById('typingIndicator');
const authSection = document.getElementById('authSection');
const userInfo = document.getElementById('userInfo');
const userName = document.getElementById('userName');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    if (authToken && currentUser) {
        showUserInfo();
    }
}

function setupEventListeners() {
    // Modal controls
    loginBtn.addEventListener('click', () => openModal(loginModal));
    closeLoginModal.addEventListener('click', () => closeModal(loginModal));
    closeRegisterModal.addEventListener('click', () => closeModal(registerModal));
    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal(loginModal);
        openModal(registerModal);
    });
    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal(registerModal);
        openModal(loginModal);
    });

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) closeModal(loginModal);
        if (e.target === registerModal) closeModal(registerModal);
    });

    // Forms
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    chatForm.addEventListener('submit', handleSendMessage);
    logoutBtn.addEventListener('click', handleLogout);

    // Quick actions
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', () => {
            const message = btn.getAttribute('data-message');
            messageInput.value = message;
            handleSendMessage(new Event('submit'));
        });
    });
}

// Modal Functions
function openModal(modal) {
    modal.classList.add('active');
}

function closeModal(modal) {
    modal.classList.remove('active');
}

// Auth Functions
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.access_token;
            currentUser = username;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', username);
            
            showUserInfo();
            closeModal(loginModal);
            addMessage('agent', `Welcome back, ${username}! How can I help you today?`);
            loginForm.reset();
        } else {
            showError(loginForm, data.detail || 'Login failed');
        }
    } catch (error) {
        showError(loginForm, 'Network error. Please try again.');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/users/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(registerForm, 'Registration successful! Please login.');
            setTimeout(() => {
                closeModal(registerModal);
                openModal(loginModal);
            }, 1500);
            registerForm.reset();
        } else {
            showError(registerForm, data.detail || 'Registration failed');
        }
    } catch (error) {
        showError(registerForm, 'Network error. Please try again.');
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    authSection.style.display = 'flex';
    userInfo.style.display = 'none';
    
    // Clear chat and show welcome
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h2>👋 Welcome to Food Delivery AI!</h2>
            <p>I can help you discover restaurants, browse menus, and place orders. Just ask me anything!</p>
            <div class="quick-actions">
                <button class="quick-action" data-message="Show me all restaurants">🏪 Browse Restaurants</button>
                <button class="quick-action" data-message="Tell me about Pizza Palace">🍕 Search Restaurant</button>
                <button class="quick-action" data-message="I want to order a Margherita pizza from Pizza Palace">🛒 Place Order</button>
            </div>
        </div>
    `;
    
    // Re-attach event listeners to new quick actions
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', () => {
            const message = btn.getAttribute('data-message');
            messageInput.value = message;
            handleSendMessage(new Event('submit'));
        });
    });
}

function showUserInfo() {
    authSection.style.display = 'none';
    userInfo.style.display = 'flex';
    userName.textContent = currentUser;
}

// Chat Functions
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;

    // Remove welcome message if present
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    // Add user message
    addMessage('user', message);
    messageInput.value = '';

    // Show typing indicator
    typingIndicator.style.display = 'flex';

    try {
        // Send to agent backend
        const response = await fetch(`${AGENT_API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken && { 'Authorization': `Bearer ${authToken}` })
            },
            body: JSON.stringify({ 
                message,
                token: authToken 
            })
        });

        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.style.display = 'none';

        if (response.ok) {
            addMessage('agent', data.response);
        } else {
            addMessage('agent', data.error || 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        // If agent backend is not available, try direct API calls
        await handleDirectAPICall(message);
    }
}

async function handleDirectAPICall(message) {
    const lowerMessage = message.toLowerCase();

    try {
        // Show all restaurants
        if (lowerMessage.includes('show') && (lowerMessage.includes('restaurant') || lowerMessage.includes('all'))) {
            const response = await fetch(`${API_BASE_URL}/restaurants/`);
            const restaurants = await response.json();
            
            if (restaurants.length === 0) {
                addMessage('agent', 'No restaurants found. Would you like to add one?');
            } else {
                let msg = `I found ${restaurants.length} restaurant(s):\n\n`;
                restaurants.forEach(r => {
                    msg += `🏪 **${r.name}**\n`;
                    msg += `📍 Area: ${r.area}\n`;
                    msg += `🍽️ Cuisine: ${r.cuisine}\n\n`;
                });
                addMessage('agent', msg);
            }
            return;
        }

        // Search for specific restaurant
        const restaurantMatch = message.match(/about (.+)|tell me (.+)|info (.+)/i);
        if (restaurantMatch) {
            const restaurantName = restaurantMatch[1] || restaurantMatch[2] || restaurantMatch[3];
            const response = await fetch(`${API_BASE_URL}/restaurants/${restaurantName.trim()}`);
            
            if (response.ok) {
                const restaurant = await response.json();
                let msg = `Here's what I found about **${restaurant.name}**:\n\n`;
                msg += `📍 Location: ${restaurant.area}\n`;
                msg += `🍽️ Cuisine: ${restaurant.cuisine}\n\n`;
                msg += `Would you like to place an order?`;
                addMessage('agent', msg);
            } else {
                addMessage('agent', `Sorry, I couldn't find a restaurant named "${restaurantName}". Try browsing all restaurants!`);
            }
            return;
        }

        // Place order
        if (lowerMessage.includes('order') && authToken) {
            addMessage('agent', 'To place an order, I need the restaurant name and the item you want. For example: "Order Margherita Pizza from Pizza Palace"');
            return;
        }

        if (lowerMessage.includes('order') && !authToken) {
            addMessage('agent', 'Please login first to place an order! Click the Login button at the top.');
            return;
        }

        // Default response
        addMessage('agent', 'I can help you with:\n\n🏪 Browse all restaurants\n🔍 Search for specific restaurants\n🛒 Place orders (requires login)\n\nWhat would you like to do?');

    } catch (error) {
        addMessage('agent', 'Sorry, I\'m having trouble connecting to the server. Please make sure the API is running on http://localhost:8000');
    }
}

function addMessage(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = formatMessage(text);
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    content.appendChild(textDiv);
    content.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(text) {
    // Convert markdown-style bold to HTML
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Convert newlines to <br>
    text = text.replace(/\n/g, '<br>');
    return text;
}

function showError(form, message) {
    // Remove existing error
    const existingError = form.querySelector('.error-message');
    if (existingError) existingError.remove();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    form.insertBefore(errorDiv, form.firstChild);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(form, message) {
    // Remove existing success
    const existingSuccess = form.querySelector('.success-message');
    if (existingSuccess) existingSuccess.remove();
    
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    form.insertBefore(successDiv, form.firstChild);
    
    setTimeout(() => successDiv.remove(), 5000);
}
