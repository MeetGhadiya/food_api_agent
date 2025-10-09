// Configuration
const API_BASE_URL = 'http://localhost:8000';
const AGENT_API_URL = 'http://localhost:5000';

// State Management
let authToken = localStorage.getItem('authToken') || null;
let currentUser = localStorage.getItem('currentUser') || null;
let isWidgetOpen = false;

// DOM Elements
const chatWidgetBtn = document.getElementById('chatWidgetBtn');
const chatWidgetPopup = document.getElementById('chatWidgetPopup');
const closeWidgetBtn = document.getElementById('closeWidgetBtn');
const minimizeBtn = document.getElementById('minimizeBtn');
const widgetChatForm = document.getElementById('widgetChatForm');
const widgetMessageInput = document.getElementById('widgetMessageInput');
const widgetMessages = document.getElementById('widgetMessages');
const widgetTyping = document.getElementById('widgetTyping');
const demoLoginBtn = document.getElementById('demoLoginBtn');
const authModal = document.getElementById('authModal');
const registerAuthModal = document.getElementById('registerAuthModal');
const closeAuthModal = document.getElementById('closeAuthModal');
const closeRegisterAuthModal = document.getElementById('closeRegisterAuthModal');
const authLoginForm = document.getElementById('authLoginForm');
const authRegisterForm = document.getElementById('authRegisterForm');
const showAuthRegister = document.getElementById('showAuthRegister');
const showAuthLogin = document.getElementById('showAuthLogin');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAuthStatus();
});

function setupEventListeners() {
    // Widget toggle
    chatWidgetBtn.addEventListener('click', toggleWidget);
    closeWidgetBtn.addEventListener('click', closeWidget);
    minimizeBtn.addEventListener('click', closeWidget);

    // Chat form
    widgetChatForm.addEventListener('submit', handleSendMessage);

    // Demo login button
    if (demoLoginBtn) {
        demoLoginBtn.addEventListener('click', () => {
            if (authToken && currentUser) {
                handleLogout();
            } else {
                openAuthModal(authModal);
            }
        });
    }

    // Auth modals
    if (closeAuthModal) closeAuthModal.addEventListener('click', () => closeAuthModal_(authModal));
    if (closeRegisterAuthModal) closeRegisterAuthModal.addEventListener('click', () => closeAuthModal_(registerAuthModal));
    
    if (showAuthRegister) {
        showAuthRegister.addEventListener('click', (e) => {
            e.preventDefault();
            closeAuthModal_(authModal);
            openAuthModal(registerAuthModal);
        });
    }
    
    if (showAuthLogin) {
        showAuthLogin.addEventListener('click', (e) => {
            e.preventDefault();
            closeAuthModal_(registerAuthModal);
            openAuthModal(authModal);
        });
    }

    // Auth forms
    if (authLoginForm) authLoginForm.addEventListener('submit', handleLogin);
    if (authRegisterForm) authRegisterForm.addEventListener('submit', handleRegister);

    // Action buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            handleQuickAction(action);
        });
    });

    // Suggestion chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const message = chip.getAttribute('data-message');
            widgetMessageInput.value = message;
            handleSendMessage(new Event('submit'));
        });
    });
}

function checkAuthStatus() {
    if (authToken && currentUser) {
        updateUIForLoggedIn();
    }
}

function updateUIForLoggedIn() {
    if (demoLoginBtn) {
        demoLoginBtn.textContent = 'Logout';
        demoLoginBtn.innerHTML = `<i class="fas fa-user"></i> ${currentUser}`;
    }
}

function toggleWidget() {
    isWidgetOpen = !isWidgetOpen;
    chatWidgetPopup.classList.toggle('active', isWidgetOpen);
    
    if (isWidgetOpen) {
        widgetMessageInput.focus();
    }
}

function closeWidget() {
    isWidgetOpen = false;
    chatWidgetPopup.classList.remove('active');
}

function openAuthModal(modal) {
    modal.style.display = 'flex';
}

function closeAuthModal_(modal) {
    modal.style.display = 'none';
}

// Handle quick actions
function handleQuickAction(action) {
    const messages = {
        browse: 'Show me all restaurants',
        order: 'I want to order food',
        orders: 'Show my orders'
    };
    
    widgetMessageInput.value = messages[action] || '';
    handleSendMessage(new Event('submit'));
}

// Handle send message
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = widgetMessageInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    widgetMessageInput.value = '';

    // Show typing indicator
    widgetTyping.style.display = 'flex';
    widgetMessages.scrollTop = widgetMessages.scrollHeight;

    try {
        const response = await fetch(`${AGENT_API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: currentUser || 'guest',
                token: authToken
            })
        });

        const data = await response.json();
        widgetTyping.style.display = 'none';

        // Check if login is required
        if (data.response && data.response.includes('🔒 Please login first')) {
            addMessage(data.response, 'bot');
            setTimeout(() => {
                openAuthModal(authModal);
            }, 1000);
        } else {
            addMessage(data.response, 'bot');
        }

    } catch (error) {
        widgetTyping.style.display = 'none';
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Error:', error);
    }
}

// Add message to chat
function addMessage(text, sender) {
    // Remove welcome screen if exists
    const welcomeScreen = widgetMessages.querySelector('.welcome-screen');
    if (welcomeScreen) {
        welcomeScreen.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(text);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    widgetMessages.appendChild(messageDiv);
    widgetMessages.scrollTop = widgetMessages.scrollHeight;
}

// Format message with markdown-like syntax
function formatMessage(text) {
    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Convert emoji shortcuts
    const emojiMap = {
        ':pizza:': '🍕',
        ':burger:': '🍔',
        ':check:': '✅',
        ':lock:': '🔒',
        ':star:': '⭐'
    };
    
    Object.keys(emojiMap).forEach(key => {
        text = text.replace(new RegExp(key, 'g'), emojiMap[key]);
    });
    
    return text;
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('authUsername').value;
    const password = document.getElementById('authPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
            authToken = data.access_token;
            currentUser = username;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', currentUser);
            
            closeAuthModal_(authModal);
            updateUIForLoggedIn();
            addMessage(`Welcome back, ${currentUser}! 🎉 You're now logged in. How can I help you?`, 'bot');
        } else {
            alert(data.detail || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred during login. Please try again.');
    }
}

// Handle register
async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('authRegUsername').value;
    const email = document.getElementById('authRegEmail').value;
    const password = document.getElementById('authRegPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/users/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Registration successful! Please login.');
            closeAuthModal_(registerAuthModal);
            openAuthModal(authModal);
            
            // Pre-fill login form
            document.getElementById('authUsername').value = username;
        } else {
            alert(data.detail || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Register error:', error);
        alert('An error occurred during registration. Please try again.');
    }
}

// Handle logout
function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    if (demoLoginBtn) {
        demoLoginBtn.textContent = 'Login';
        demoLoginBtn.innerHTML = 'Login';
    }
    
    addMessage('You have been logged out successfully. 👋', 'bot');
}

// Auto-resize message input (if needed in future)
widgetMessageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 100) + 'px';
});
