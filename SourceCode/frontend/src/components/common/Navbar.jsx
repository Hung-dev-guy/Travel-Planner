import React from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import { FiSun, FiMoon } from 'react-icons/fi';

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="navbar glass">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
            <div style={{ width: '32px', height: '32px', background: 'var(--primary)', borderRadius: '8px' }}></div>
            <h1 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--primary)' }}>Traplanner</h1>
        </Link>
      </div>
      <div style={{ marginLeft: 'auto', display: 'flex', gap: '24px', alignItems: 'center' }}>
        <button 
          onClick={toggleTheme} 
          style={{ 
            background: 'none', 
            border: 'none', 
            cursor: 'pointer', 
            fontSize: '1.25rem',
            padding: '8px',
            borderRadius: '50%',
            transition: 'background 0.2s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-primary)'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-main)'}
          onMouseOut={(e) => e.currentTarget.style.background = 'none'}
        >
          {theme === 'light' ? <FiMoon size={20} /> : <FiSun size={20} />}
        </button>
        <Link to="/features" style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-secondary)' }}>Features</Link>
        <Link to="/about" style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-secondary)' }}>About</Link>
        <Link to="/login" className="btn-premium btn-primary" style={{ padding: '8px 24px', textDecoration: 'none', color: 'white' }}>Get Started</Link>
      </div>
    </nav>
  );
};

export default Navbar;
