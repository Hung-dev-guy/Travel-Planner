import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ChatHistory from './ChatHistory';

const ChatContainer = ({ onUserMessage }) => {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your Traplanner AI. How can I help you today?", sender: 'bot' },
    { text: "I'm looking for a 5-day trip to Japan on a budget of $2000.", sender: 'user' },
    { text: "Excellent choice! Japan has amazing options for budget travelers. Would you like me to focus on Tokyo, Kyoto, or a mix of both?", sender: 'bot' },
  ]);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (text) => {
    if (!text) return;
    setMessages(prev => [...prev, { text, sender: 'user' }]);
    if (onUserMessage) onUserMessage();
    
    // Fake bot response
    setTimeout(() => {
      setMessages(prev => [...prev, { text: "That sounds like a great plan! Let me gather some options for you.", sender: 'bot' }]);
    }, 1000);
  };

  return (
    <div style={{ 
      display: 'grid', 
      gridTemplateColumns: '220px 1fr', 
      height: '100%',
      background: 'var(--bg-sidebar)',
      borderRadius: 'var(--card-radius)',
      boxShadow: 'var(--shadow-premium)',
      overflow: 'hidden',
      border: '1px solid var(--border-light)',
      transition: 'all 0.3s ease'
    }}>
      <ChatHistory />
      <div style={{ display: 'flex', flexDirection: 'column', background: 'var(--bg-main)', position: 'relative', minWidth: 0 }}>
        <div style={{ flex: 1, padding: '30px', overflowY: 'auto', minHeight: 0 }}>
            {messages.map((m, i) => (
                <ChatMessage key={i} message={m.text} sender={m.sender} />
            ))}
            <div ref={messagesEndRef} />
        </div>
        <div style={{ padding: '20px', borderTop: '1px solid var(--border-light)', flexShrink: 0 }}>
          <ChatInput onSend={handleSendMessage} />
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;
