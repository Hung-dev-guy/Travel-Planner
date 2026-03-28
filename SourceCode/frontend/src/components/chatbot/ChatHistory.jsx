import React from 'react';

const ChatHistory = () => {
  const history = [
    { id: 1, title: 'Trip to Tokyo', date: '2 days ago' },
    { id: 2, title: 'European Budget Trip', date: '1 week ago' },
    { id: 3, title: 'Paris Itinerary', date: 'Mar 15' },
  ];

  return (
    <div className="chat-history" style={{ padding: '20px', borderRight: '1px solid var(--border-light)', height: '100%', background: 'var(--bg-sidebar)', transition: 'background 0.3s ease' }}>
      <h4 style={{ margin: '0 0 20px 0', fontSize: '0.9rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>Recent Chats</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {history.map((chat) => (
          <div
            key={chat.id}
            style={{
              padding: '12px',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              fontSize: '0.9rem',
              border: '1px solid transparent'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'var(--bg-main)';
              e.currentTarget.style.borderColor = 'var(--border-light)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = 'transparent';
            }}
          >
            <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{chat.title}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{chat.date}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatHistory;
