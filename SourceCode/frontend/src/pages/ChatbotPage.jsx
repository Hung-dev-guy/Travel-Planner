import React, { useState } from 'react';
import ChatContainer from '../components/chatbot/ChatContainer';

const ChatbotPage = () => {
  const [isChatting, setIsChatting] = useState(false);

  return (
    <div className="chatbot-page" style={{ 
      height: isChatting ? 'calc(100vh - var(--navbar-height) - 40px)' : 'calc(100vh - var(--navbar-height) - 60px)', 
      maxWidth: '1400px',
      margin: '0 auto',
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden',
      transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)'
    }}>
      <h1 style={{ 
        color: 'var(--primary)', 
        marginBottom: isChatting ? '0' : '16px', 
        flexShrink: 0, 
        fontSize: isChatting ? '0' : '1.75rem',
        opacity: isChatting ? 0 : 1,
        height: isChatting ? '0' : 'auto',
        overflow: 'hidden',
        transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)'
      }}>
        Chat with Traplanner AI
      </h1>
      <ChatContainer onUserMessage={() => setIsChatting(true)} />
    </div>
  );
};

export default ChatbotPage;
