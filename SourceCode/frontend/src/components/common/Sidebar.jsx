import React, {useState} from 'react';
import { NavLink } from 'react-router-dom';
import { 
  FiLayout, 
  FiMap, 
  FiMessageSquare, 
  FiCompass, 
  FiSettings,
  FiChevronLeft,
  FiChevronRight
} from 'react-icons/fi';

const Sidebar = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const menuItems = [
    { name: 'Dashboard', icon: <FiLayout />, path: '/dashboard' },
    { name: 'Trip Planner', icon: <FiMap />, path: '/' },
    { name: 'AI Chatbot', icon: <FiMessageSquare />, path: '/chat' },
    { name: 'Destinations', icon: <FiCompass />, path: '/search' },
    { name: 'Settings', icon: <FiSettings />, path: '/settings' },
  ];

  return (
    <aside 
      className="sidebar" 
      style={{ 
        width: sidebarOpen ? 'var(--sidebar-width)' : '80px',
        padding: sidebarOpen ? '20px' : '20px 10px',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        overflowX: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}
    >
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{
          alignSelf: sidebarOpen ? 'flex-end' : 'center',
          background: 'var(--bg-main)',
          border: '1px solid var(--border-light)',
          borderRadius: '8px',
          padding: '8px',
          cursor: 'pointer',
          color: 'var(--primary)',
          transition: 'all 0.2s',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {sidebarOpen ? <FiChevronLeft size={20} /> : <FiChevronRight size={20} />}
      </button>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {menuItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            style={({ isActive }) => ({
              padding: '12px',
              borderRadius: 'var(--button-radius)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: sidebarOpen ? 'flex-start' : 'center',
              gap: sidebarOpen ? '12px' : '0',
              transition: 'all 0.2s',
              fontWeight: 500,
              textDecoration: 'none',
              background: isActive ? 'var(--primary-light)' : 'transparent',
              color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
              minHeight: '48px'
            })}
            title={!sidebarOpen ? item.name : ''}
          >
            <span style={{ fontSize: '1.2rem', minWidth: '24px', textAlign: 'center' }}>{item.icon}</span>
            {sidebarOpen && <span style={{ whiteSpace: 'nowrap' }}>{item.name}</span>}
          </NavLink>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
