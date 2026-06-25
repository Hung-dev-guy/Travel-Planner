import React, { useState } from 'react';
import ChatContainer from '../components/chatbot/ChatContainer';
import { FiMessageSquare } from 'react-icons/fi';

// Use a fixed mock userId until real auth is wired up.
// In production, replace this with the authenticated user's ID from AuthContext.
const MOCK_USER_ID = 'U001';

const ChatbotPage = () => {
  const [isChatting, setIsChatting] = useState(false);

  return (
    <div style={{
      height: 'calc(100vh - var(--navbar-height) - 40px)',
      maxWidth: '1400px',
      margin: '0 auto',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Page header — collapses once user starts chatting */}
      <div style={{
        flexShrink: 0,
        overflow: 'hidden',
        maxHeight: isChatting ? 0 : '70px',
        opacity: isChatting ? 0 : 1,
        transition: 'max-height 0.5s cubic-bezier(0.4,0,0.2,1), opacity 0.4s ease',
        marginBottom: isChatting ? 0 : 16,
      }}>
        <h1 style={{
          margin: 0, fontSize: '1.75rem', color: 'var(--primary)',
          display: 'flex', alignItems: 'center', gap: 10
        }}>
          <FiMessageSquare /> Trợ lý AI Traplanner
        </h1>
        <p style={{ margin: '4px 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>
          Chọn một kế hoạch du lịch và bắt đầu trò chuyện với Travel Bot.
        </p>
      </div>

      {/* Chat UI — fills remaining space */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ChatContainer
          userId={MOCK_USER_ID}
          onUserMessage={() => setIsChatting(true)}
        />
      </div>
    </div>
  );
};

export default ChatbotPage;
