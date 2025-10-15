import React, { useState, useEffect } from 'react';
import ChatBot from './components/ChatBot';
import { Utensils, MessageCircle, Sparkles, Zap, User, LogOut } from 'lucide-react';
import authService from './services/auth';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  const [currentUser, setCurrentUser] = useState(authService.getUser());
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
    setCurrentUser(authService.getUser());
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username: formData.username,
          password: formData.password,
        }),
      });

      const data = await response.json();
      
      if (response.ok && data.access_token) {
        authService.setAuth(data.access_token, formData.username);
        setIsAuthenticated(true);
        setCurrentUser(formData.username);
        setShowLoginModal(false);
        setFormData({ username: '', email: '', password: '' });
      } else {
        setError('Invalid credentials. Please try again.');
      }
    } catch (err) {
      setError('Login failed. Please check if the server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        }),
      });

      if (response.ok) {
        // Auto-login after registration
        handleLogin(e);
      } else {
        const data = await response.json();
        setError(data.detail || 'Registration failed. Username might be taken.');
      }
    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Clean Header - Swiggy Style */}
      <header className="bg-white shadow-sm sticky top-0 z-20">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
              <Utensils className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
              FoodieExpress
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="hidden md:inline text-gray-600 text-sm">
              AI-Powered Food Ordering
            </span>
            
            {/* Login/Logout Buttons */}
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-full">
                  <User className="w-4 h-4" />
                  <span className="text-sm font-medium">{currentUser}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-full hover:bg-red-100 transition"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm font-medium">Logout</span>
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowLoginModal(true)}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full hover:shadow-lg transition font-medium"
              >
                <User className="w-4 h-4" />
                Login
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Login/Register Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
            <button
              onClick={() => {
                setShowLoginModal(false);
                setError('');
                setFormData({ username: '', email: '', password: '' });
              }}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>

            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {isRegistering ? 'Create Account' : 'Welcome Back'}
            </h2>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={isRegistering ? handleRegister : handleLogin}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none"
                    required
                  />
                </div>

                {isRegistering && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none"
                      required
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg font-medium hover:shadow-lg transition disabled:opacity-50"
              >
                {loading ? 'Please wait...' : (isRegistering ? 'Create Account' : 'Login')}
              </button>
            </form>

            <div className="mt-4 text-center">
              <button
                onClick={() => {
                  setIsRegistering(!isRegistering);
                  setError('');
                  setFormData({ username: '', email: '', password: '' });
                }}
                className="text-orange-600 hover:text-orange-700 text-sm font-medium"
              >
                {isRegistering ? 'Already have an account? Login' : "Don't have an account? Register"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hero Section - Clean & Modern */}
      <div className="container mx-auto px-6 py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-100 to-red-100 rounded-full mb-6">
            <Zap className="w-4 h-4 text-orange-600" />
            <span className="text-sm font-semibold text-orange-700">
              AI-Powered Ordering Assistant
            </span>
          </div>

          {/* Main Heading */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Order Food with
            <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
              {' '}AI Magic
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            Just chat with our AI assistant - no menus, no hassle. 
            Simply tell us what you want, and we'll handle the rest.
          </p>

          {/* CTA Button */}
          <button className="group relative px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white text-lg font-semibold rounded-full hover:shadow-2xl hover:shadow-orange-500/50 transition-all duration-300 hover:-translate-y-1">
            <span className="flex items-center gap-3">
              <MessageCircle className="w-6 h-6" />
              Start Chatting Now
              <span className="text-2xl group-hover:translate-x-1 transition-transform">→</span>
            </span>
          </button>
        </div>
      </div>

      {/* Features Section - Minimal & Clean */}
      <div className="bg-gradient-to-b from-gray-50 to-white py-20">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-16">
              Why Choose AI Ordering?
            </h2>
            <div className="grid md:grid-cols-3 gap-12">
              {[
                {
                  emoji: '🤖',
                  title: 'Smart AI Assistant',
                  description: 'Natural conversation - just say what you want like talking to a friend',
                },
                {
                  emoji: '⚡',
                  title: 'Lightning Fast',
                  description: 'Skip the menus and searching. Get exactly what you want in seconds',
                },
                {
                  emoji: '🎯',
                  title: 'Perfect Accuracy',
                  description: 'AI understands your preferences and suggests the best options',
                },
              ].map((feature, index) => (
                <div
                  key={index}
                  className="text-center group hover:scale-105 transition-transform duration-300"
                >
                  <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">
                    {feature.emoji}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* How It Works - Visual Flow */}
      <div className="container mx-auto px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-16">
            Three Simple Steps
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '1', title: 'Open Chat', desc: 'Click the chat button' },
              { step: '2', title: 'Tell AI', desc: 'Say what you want to eat' },
              { step: '3', title: 'Done!', desc: 'AI handles your order' },
            ].map((item, index) => (
              <div key={index} className="relative">
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mb-4 text-white text-2xl font-bold shadow-lg">
                    {item.step}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-gray-600">{item.desc}</p>
                </div>
                {index < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 text-4xl text-orange-300">
                    →
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Chatbot */}
      <ChatBot />

      {/* Floating Prompt - Attention Grabber */}
      <div className="fixed bottom-28 left-6 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-2xl shadow-2xl p-5 max-w-xs z-30 animate-pulse">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
            <MessageCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="font-semibold mb-1">Try our AI Assistant!</p>
            <p className="text-sm text-white/90">
              Click the chat button to order with AI →
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
