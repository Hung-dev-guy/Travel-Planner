import React, { useState } from 'react';

const ChatInput = ({ onSend }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSend(text);
      setText('');
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      gap: '12px', 
      padding: '12px 16px', 
      background: 'var(--bg-sidebar)', 
      borderRadius: 'var(--card-radius)',
      boxShadow: 'var(--shadow-premium)',
      marginTop: 'auto',
      border: '1px solid var(--border-light)',
      transition: 'all 0.3s ease'
    }}>
      <input 
        type="text" 
        className="input-field" 
        placeholder="Ask Traplanner anything..." 
        style={{ flex: 1, border: 'none', background: 'transparent', padding: '12px' }} 
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
      />
      <button className="btn-premium btn-primary" onClick={handleSend} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        Send
      </button>
    </div>
  );
};

export default ChatInput;
