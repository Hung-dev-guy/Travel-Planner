import React, { useState } from 'react';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/user/api/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        localStorage.setItem('user', JSON.stringify(data.user));
        window.location.href = '/dashboard';
      } else {
        setError(data.error || 'Đăng nhập thất bại');
      }
    } catch (err) {
      setError('Lỗi kết nối');
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {error && <div style={{ color: 'red', fontSize: '0.9rem' }}>{error}</div>}
      <div>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>Tên đăng nhập</label>
        <input type="text" className="input-field" value={username} onChange={e => setUsername(e.target.value)} required />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>Mật khẩu</label>
        <input type="password" className="input-field" value={password} onChange={e => setPassword(e.target.value)} required />
      </div>
      <button type="submit" className="btn-premium btn-primary" style={{ marginTop: '8px' }}>
        Đăng Nhập
      </button>
      <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Chưa có tài khoản? <a href="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>Đăng ký ngay</a>
      </div>
    </form>
  );
};

export default LoginForm;
