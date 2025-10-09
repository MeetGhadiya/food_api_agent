import React from 'react';
import { Bot, User } from 'lucide-react';

const Message = ({ message, isBot }) => {
  const formatMessage = (text) => {
    // Convert markdown-style bold to HTML
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br/>');
    
    return text;
  };

  return (
    <div
      className={`flex gap-3 mb-4 message-enter ${
        isBot ? 'justify-start' : 'justify-end'
      }`}
    >
      {isBot && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div
        className={`max-w-[75%] px-4 py-3 rounded-2xl ${
          isBot
            ? 'bg-white text-gray-800 shadow-md rounded-bl-none'
            : 'bg-gradient-to-r from-primary to-primary-dark text-white shadow-lg rounded-br-none'
        }`}
      >
        <div
          className="text-sm leading-relaxed"
          dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
        />
      </div>
      
      {!isBot && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};

export default Message;
