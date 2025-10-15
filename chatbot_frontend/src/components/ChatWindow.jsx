import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, RefreshCw, X, Loader2 } from 'lucide-react';
import Message from './Message';
import chatAPI from '../services/api';
import authService from '../services/auth';

const ChatWindow = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    {
      text: "👋 Hi! I'm your AI food delivery assistant.\n\n🏪 Browse restaurants\n🍕 Order food\n📝 Check your orders\n\nWhat would you like to do?",
      isBot: true,
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  const [currentUser, setCurrentUser] = useState(authService.getUser());
  const [userId, setUserId] = useState(() => authService.getUser() || 'guest_' + Date.now());
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Update auth status when window opens
  useEffect(() => {
    if (isOpen) {
      const authenticated = authService.isAuthenticated();
      const user = authService.getUser();
      
      setIsAuthenticated(authenticated);
      setCurrentUser(user);
      
      // Update userId if user is logged in
      if (user) {
        setUserId(user);
      }
    }
  }, [isOpen]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    const message = inputValue.trim();
    if (!message || isLoading) return;

    // Add user message
    setMessages((prev) => [...prev, { text: message, isBot: false }]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get fresh auth data on EVERY message
      const token = authService.getToken();
      const currentUserId = authService.getUser() || userId;
      
      console.log('🔍 DEBUG - Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NULL');
      console.log('🔍 DEBUG - Is Authenticated:', authService.isAuthenticated());
      console.log('🔍 DEBUG - User ID being sent:', currentUserId);
      
      const response = await chatAPI.sendMessage(message, currentUserId, token);
      console.log('🔍 DEBUG - Response:', response);

      // Handle authentication response
      if (response.token) {
        // Extract username from the message or use userId
        const username = userId.startsWith('guest_') ? 'user' : userId;
        authService.setAuth(response.token, username);
        setIsAuthenticated(true);
        setCurrentUser(username);
      }

      // Check if response requires auth
      if (response.requires_auth) {
        setMessages((prev) => [
          ...prev,
          { 
            text: "🔒 I can help with that! But first, I need you to log in or register.\n\nPlease use the **Login** button in the website header (top right corner).", 
            isBot: true 
          },
        ]);
        return;
      }

      // Add bot response
      setMessages((prev) => [
        ...prev,
        { text: response.response, isBot: true },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          text: "❌ I'm sorry, I encountered an error. Please try again or check if the backend services are running.",
          isBot: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    try {
      await chatAPI.clearSession(userId);
      setMessages([
        {
          text: "Chat cleared! How can I help you today?",
          isBot: true,
        },
      ]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-6 right-6 w-[400px] h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden z-40 animate-in fade-in slide-in-from-bottom-4 duration-300">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-5 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-orange-600" />
            </div>
            <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 border-2 border-white rounded-full"></span>
          </div>
          <div>
            <h3 className="font-semibold text-lg">FoodieBot</h3>
            <p className="text-xs text-white/80 flex items-center gap-1">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              {isAuthenticated ? `Logged in as ${currentUser}` : 'Online'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleClearChat}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            title="Refresh chat"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            title="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map((msg, index) => (
          <Message key={index} message={msg.text} isBot={msg.isBot} />
        ))}
        
        {/* Typing indicator */}
        {isLoading && (
          <div className="flex gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-none shadow-md">
              <div className="flex gap-1">
                <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-full focus:outline-none focus:border-orange-500 transition-colors text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full flex items-center justify-center hover:shadow-lg hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
        <p className="text-xs text-gray-400 text-center mt-2">
          Powered by AI • 🔒 Secure
        </p>
      </div>
    </div>
  );
};

export default ChatWindow;
