import React from 'react';
import { MessageCircle, X } from 'lucide-react';

const ChatButton = ({ isOpen, onClick, unreadCount = 0 }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-br from-primary to-primary-dark rounded-full shadow-2xl hover:shadow-primary/50 transition-all duration-300 hover:scale-110 active:scale-95 flex items-center justify-center z-50 group"
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
    >
      {/* Pulse ring animation */}
      {!isOpen && (
        <div className="absolute inset-0 rounded-full border-4 border-primary animate-pulse-ring"></div>
      )}
      
      {/* Icon */}
      <div className="relative">
        {isOpen ? (
          <X className="w-7 h-7 text-white" />
        ) : (
          <MessageCircle className="w-7 h-7 text-white" />
        )}
        
        {/* Unread badge */}
        {!isOpen && unreadCount > 0 && (
          <span className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-bounce">
            {unreadCount}
          </span>
        )}
      </div>
    </button>
  );
};

export default ChatButton;
