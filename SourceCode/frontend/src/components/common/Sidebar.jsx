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
    { name: 'Bảng điều khiển', icon: <FiLayout />, path: '/dashboard' },
    { name: 'Lên kế hoạch', icon: <FiMap />, path: '/planner' },
    { name: 'AI Trợ lý', icon: <FiMessageSquare />, path: '/chat' },
    { name: 'Điểm đến', icon: <FiCompass />, path: '/destinations' },
    { name: 'Cài đặt', icon: <FiSettings />, path: '/settings' },
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
      
      <div style={{ marginTop: 'auto' }}>
        <button
          onClick={() => {
            localStorage.removeItem('user');
            window.location.href = '/login';
          }}
          style={{
            padding: '12px',
            borderRadius: 'var(--button-radius)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: sidebarOpen ? 'flex-start' : 'center',
            gap: sidebarOpen ? '12px' : '0',
            transition: 'all 0.2s',
            fontWeight: 500,
            background: 'transparent',
            color: 'var(--danger, #ff4d4f)',
            border: 'none',
            width: '100%',
            minHeight: '48px'
          }}
          title={!sidebarOpen ? 'Đăng xuất' : ''}
        >
          <span style={{ fontSize: '1.2rem', minWidth: '24px', textAlign: 'center' }}>
            <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
          </span>
          {sidebarOpen && <span style={{ whiteSpace: 'nowrap' }}>Đăng xuất</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
