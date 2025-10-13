import React from 'react';
import { Bot, User } from 'lucide-react';

const Message = ({ message, isBot }) => {
  const formatMessage = (text) => {
    if (!text) return '';
    
    // Convert markdown-style bold
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-orange-600">$1</strong>');
    text = text.replace(/__(.*?)__/g, '<strong class="font-bold text-orange-600">$1</strong>');
    
    // Convert emojis to larger size
    text = text.replace(/([\u{1F300}-\u{1F9FF}])/gu, '<span class="text-xl inline-block mr-1">$1</span>');
    
    // Split into lines for processing
    let lines = text.split('\n');
    let formatted = [];
    
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      
      // Skip empty lines
      if (line.trim() === '') {
        formatted.push('<br/>');
        continue;
      }
      
      // Check line type and format accordingly
      if (line.match(/^━+$/)) {
        // Separator line
        formatted.push('<hr class="border-gray-300 my-2" />');
      } else if (line.match(/^─+$/)) {
        // Separator line (lighter)
        formatted.push('<hr class="border-gray-200 my-1" />');
      } else if (line.match(/^[•✓✗→←↑↓★☆♥♦♣♠\*]/)) {
        // Bullet points (including • and *) or special symbols
        formatted.push(`<div class="ml-4">${line}</div>`);
      } else if (line.match(/^\d+\./)) {
        // Numbered lists
        formatted.push(`<div class="ml-4">${line}</div>`);
      } else if (line.trim().endsWith(':') && line.length < 50 && !line.includes(',')) {
        // Section headers (short lines ending with :)
        formatted.push(`<div class="font-semibold text-gray-700 mt-2 mb-1">${line}</div>`);
      } else {
        // Regular text - just add line break
        formatted.push(line + '<br/>');
      }
    }
    
    return formatted.join('');
  };

  return (
    <div
      className={`flex gap-3 mb-4 message-enter ${
        isBot ? 'justify-start' : 'justify-end'
      }`}
    >
      {isBot && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl ${
          isBot
            ? 'bg-white text-gray-800 shadow-md rounded-bl-none'
            : 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg rounded-br-none'
        }`}
      >
        <div
          className="text-sm leading-relaxed break-words"
          dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
        />
      </div>
      
      {!isBot && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};

export default Message;
