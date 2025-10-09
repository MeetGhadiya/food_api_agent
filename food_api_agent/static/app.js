// Configuration
const API_BASE_URL = 'http://localhost:8000';
const AGENT_API_URL = 'http://localhost:5000';

// State Management
let authToken = localStorage.getItem('authToken') || null;
let currentUser = localStorage.getItem('currentUser') || null;
let currentView = 'chat';

// DOM Elements
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const loginCard = document.getElementById('loginCard');
const userCard = document.getElementById('userCard');
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
const sidebarUserName = document.getElementById('sidebarUserName');
const sidebarLogout = document.getElementById('sidebarLogout');
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.querySelector('.sidebar');

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
    loginCard.addEventListener('click', () => openModal(loginModal));
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
    if (sidebarLogout) {
        sidebarLogout.addEventListener('click', handleLogout);
    }

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => switchView(item.dataset.view));
    });

    // Menu toggle for mobile
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Quick suggestion chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const message = chip.getAttribute('data-message');
            messageInput.value = message;
            handleSendMessage(new Event('submit'));
        });
    });
}

// View Switching
function switchView(viewName) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

    // Update views
    document.querySelectorAll('.view-container').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(`${viewName}View`).classList.add('active');

    // Update page title
    const titles = {
        chat: 'Chat with FoodieBot',
        restaurants: 'Browse Restaurants',
        orders: 'My Orders',
        profile: 'My Profile'
    };
    document.querySelector('.page-title').textContent = titles[viewName];

    currentView = viewName;
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
            addMessage('agent', `Welcome back, ${username}! 👋 How can I help you today?`);
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
    
    loginCard.style.display = 'flex';
    userCard.style.display = 'none';
    
    // Clear chat
    chatMessages.innerHTML = `
        <div class="bot-intro">
            <div class="bot-avatar-large">
                <i class="fas fa-robot"></i>
            </div>
            <h2>Hey! I'm FoodieBot 🍔</h2>
            <p>Your personal AI food assistant. I can help you discover restaurants, explore menus, and place orders instantly!</p>
            
            <div class="feature-cards">
                <div class="feature-card">
                    <i class="fas fa-search"></i>
                    <h3>Discover</h3>
                    <p>Find the best restaurants near you</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-utensils"></i>
                    <h3>Explore</h3>
                    <p>Browse menus and cuisines</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-bolt"></i>
                    <h3>Order Fast</h3>
                    <p>Quick and easy ordering</p>
                </div>
            </div>

            <div class="quick-suggestions">
                <h3>Try asking me:</h3>
                <div class="suggestion-chips">
                    <button class="chip" data-message="Show me all restaurants">
                        <i class="fas fa-store"></i> Browse All
                    </button>
                    <button class="chip" data-message="Tell me about Pizza Palace">
                        <i class="fas fa-info-circle"></i> Restaurant Info
                    </button>
                    <button class="chip" data-message="I want to order Margherita pizza from Pizza Palace">
                        <i class="fas fa-shopping-cart"></i> Order Food
                    </button>
                    <button class="chip" data-message="Show my orders">
                        <i class="fas fa-list"></i> My Orders
                    </button>
                    <button class="chip" data-message="Create a new restaurant called Burger King in Downtown serving American food">
                        <i class="fas fa-plus-circle"></i> Add Restaurant
                    </button>
                    <button class="chip" data-message="Update Pizza Palace to Pizza Palace Premium in Uptown serving Italian food">
                        <i class="fas fa-edit"></i> Update Restaurant
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Re-attach event listeners
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const message = chip.getAttribute('data-message');
            messageInput.value = message;
            handleSendMessage(new Event('submit'));
        });
    });
}

function showUserInfo() {
    loginCard.style.display = 'none';
    userCard.style.display = 'flex';
    sidebarUserName.textContent = currentUser;
}

// Chat Functions
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;

    // Remove intro if present
    const intro = chatMessages.querySelector('.bot-intro');
    if (intro) {
        intro.remove();
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
    avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = formatMessage(text);
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    content.appendChild(bubble);
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
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    form.insertBefore(errorDiv, form.firstChild);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(form, message) {
    // Remove existing success
    const existingSuccess = form.querySelector('.success-message');
    if (existingSuccess) existingSuccess.remove();
    
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    form.insertBefore(successDiv, form.firstChild);
    
    setTimeout(() => successDiv.remove(), 5000);
}
