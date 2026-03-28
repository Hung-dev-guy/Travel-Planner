import React from 'react';

const LoginForm = () => {
  return (
    <form className="login-form" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>Email Address</label>
        <input type="email" className="input-field" placeholder="name@example.com" />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>Password</label>
        <input type="password" className="input-field" placeholder="••••••••" />
      </div>
      <button type="submit" className="btn-premium btn-primary" style={{ marginTop: '8px' }}>
        Sign In
      </button>
      <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Don't have an account? <a href="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>Create one</a>
      </div>
    </form>
  );
};

export default LoginForm;
