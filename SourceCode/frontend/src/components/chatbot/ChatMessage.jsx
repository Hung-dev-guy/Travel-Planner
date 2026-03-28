import React from 'react';

const ChatMessage = ({ message, sender = 'bot' }) => {
  const isBot = sender === 'bot';
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: isBot ? 'flex-start' : 'flex-end',
      marginBottom: '16px'
    }}>
      <div style={{ 
        maxWidth: '70%',
        padding: '12px 18px',
        borderRadius: isBot ? '16px 16px 16px 4px' : '16px 16px 4px 16px',
        background: isBot ? 'var(--bg-sidebar)' : 'var(--primary)',
        color: isBot ? 'var(--text-primary)' : 'white',
        boxShadow: 'var(--shadow-sm)',
        border: isBot ? '1px solid var(--border-light)' : 'none',
        fontSize: '0.95rem',
        lineHeight: '1.5',
        transition: 'all 0.2s ease'
      }}>
        {message}
      </div>
    </div>
  );
};

export default ChatMessage;
