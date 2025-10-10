import React from 'react';
import { MessageCircle, X, Sparkles } from 'lucide-react';

const ChatButton = ({ isOpen, onClick, unreadCount = 0 }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-full shadow-2xl hover:shadow-orange-500/50 transition-all duration-300 hover:scale-110 active:scale-95 flex items-center justify-center z-50 group"
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
    >
      {/* Pulse ring animation */}
      {!isOpen && (
        <>
          <div className="absolute inset-0 rounded-full border-4 border-orange-400 animate-pulse-ring opacity-75"></div>
          <div className="absolute -top-1 -right-1">
            <Sparkles className="w-5 h-5 text-yellow-300 animate-pulse" />
          </div>
        </>
      )}
      
      {/* Icon */}
      <div className="relative">
        {isOpen ? (
          <X className="w-7 h-7 text-white" />
        ) : (
          <MessageCircle className="w-7 h-7 text-white animate-bounce" />
        )}
        
        {/* Unread badge */}
        {!isOpen && unreadCount > 0 && (
          <span className="absolute -top-2 -right-2 w-5 h-5 bg-red-600 text-white text-xs font-bold rounded-full flex items-center justify-center animate-bounce">
            {unreadCount}
          </span>
        )}
      </div>

      {/* AI Label */}
      {!isOpen && (
        <div className="absolute -top-10 right-0 bg-white text-orange-600 px-3 py-1 rounded-full shadow-lg text-xs font-semibold whitespace-nowrap group-hover:scale-105 transition-transform">
          🤖 AI Assistant
        </div>
      )}
    </button>
  );
};

export default ChatButton;
