import React from 'react';
import ChatBot from './components/ChatBot';
import { Utensils, Store, ShoppingBag, Star } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800">
      {/* Demo Website Header */}
      <header className="bg-white/95 backdrop-blur-sm shadow-lg">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Utensils className="w-8 h-8 text-primary" />
            <span className="text-2xl font-bold text-gray-800">FoodieExpress</span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#" className="text-gray-700 hover:text-primary font-medium transition">
              Home
            </a>
            <a href="#" className="text-gray-700 hover:text-primary font-medium transition">
              Restaurants
            </a>
            <a href="#" className="text-gray-700 hover:text-primary font-medium transition">
              Orders
            </a>
            <button className="bg-primary text-white px-6 py-2 rounded-full hover:bg-primary-dark transition font-medium">
              Login
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-16 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 drop-shadow-lg">
          Order Your Favorite Food Online
        </h1>
        <p className="text-xl text-white/90 mb-8">
          Delicious meals delivered to your doorstep in minutes
        </p>
        <div className="max-w-2xl mx-auto bg-white rounded-full shadow-2xl p-2 flex gap-2">
          <input
            type="text"
            placeholder="Search for restaurants or cuisines..."
            className="flex-1 px-6 py-3 rounded-full outline-none text-gray-700"
          />
          <button className="bg-primary text-white px-8 py-3 rounded-full hover:bg-primary-dark transition font-medium">
            Search
          </button>
        </div>
      </div>

      {/* Features */}
      <div className="container mx-auto px-6 py-12">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            {
              icon: <Store className="w-12 h-12" />,
              title: 'Wide Selection',
              description: 'Choose from hundreds of restaurants',
            },
            {
              icon: <ShoppingBag className="w-12 h-12" />,
              title: 'Easy Ordering',
              description: 'Simple checkout and secure payment',
            },
            {
              icon: <Star className="w-12 h-12" />,
              title: 'Quality Service',
              description: 'Fast delivery and great support',
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 text-center text-white hover:bg-white/20 transition cursor-pointer"
            >
              <div className="flex justify-center mb-4 text-accent">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-white/80">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Restaurant Cards */}
      <div className="container mx-auto px-6 py-12">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Popular Restaurants
        </h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[
            {
              name: 'Pizza Palace',
              cuisine: 'Italian',
              area: 'Downtown',
              color: 'from-red-500 to-orange-500',
            },
            {
              name: 'Spice Haven',
              cuisine: 'Indian',
              area: 'Uptown',
              color: 'from-green-500 to-teal-500',
            },
            {
              name: 'Burger King',
              cuisine: 'American',
              area: 'Central',
              color: 'from-yellow-500 to-amber-500',
            },
          ].map((restaurant, index) => (
            <div
              key={index}
              className="bg-white rounded-2xl overflow-hidden shadow-2xl hover:shadow-primary/50 transition-all hover:-translate-y-2 cursor-pointer"
            >
              <div className={`h-48 bg-gradient-to-br ${restaurant.color} flex items-center justify-center`}>
                <span className="text-white text-6xl font-bold opacity-50">
                  {restaurant.name[0]}
                </span>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-2">
                  {restaurant.name}
                </h3>
                <p className="text-gray-600 mb-1 flex items-center gap-2">
                  <Utensils className="w-4 h-4" />
                  {restaurant.cuisine}
                </p>
                <p className="text-gray-600 flex items-center gap-2">
                  <Store className="w-4 h-4" />
                  {restaurant.area}
                </p>
                <button className="mt-4 w-full bg-primary text-white py-2 rounded-lg hover:bg-primary-dark transition font-medium">
                  Order Now
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Chatbot */}
      <ChatBot />

      {/* Info Banner */}
      <div className="fixed bottom-24 left-6 bg-white rounded-2xl shadow-2xl p-4 max-w-xs z-30 animate-bounce-slow">
        <p className="text-sm text-gray-700">
          💬 <strong>Need help?</strong> Chat with our AI assistant in the bottom-right corner!
        </p>
      </div>
    </div>
  );
}

export default App;
