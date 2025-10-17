import React from 'react';
import ChatBot from './components/ChatBot';
import { Utensils, MessageCircle, Sparkles, Zap } from 'lucide-react';

function App() {
  // Authentication system removed - app now works without login

  const handleLogin = async (e) => {
    // Login system removed
  };

  const handleRegister = async (e) => {
    // Registration system removed
  };

  const handleLogout = () => {
    // Logout system removed
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
            
            {/* Login/Logout buttons removed - no authentication needed */}
          </div>
        </div>
      </header>

      {/* Login/Register Modal removed - no authentication needed */}

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
