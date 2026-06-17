import React, { useState } from 'react';

const RegisterForm = () => {
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/user/api/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, full_name: fullName })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        window.location.href = '/login';
      } else {
        setError(data.error || 'Đăng ký thất bại');
      }
    } catch (err) {
      setError('Lỗi kết nối');
    }
  };

  return (
    <form className="register-form" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {error && <div style={{ color: 'red', fontSize: '0.9rem' }}>{error}</div>}
      <div>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>Họ và tên</label>
        <input type="text" className="input-field" value={fullName} onChange={e => setFullName(e.target.value)} required placeholder="Nguyễn Văn A" />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>Tên đăng nhập</label>
        <input type="text" className="input-field" value={username} onChange={e => setUsername(e.target.value)} required placeholder="nguyenvana" />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 500 }}>Mật khẩu</label>
        <input type="password" className="input-field" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••" />
      </div>
      <button type="submit" className="btn-premium btn-primary" style={{ marginTop: '8px' }}>
        Tạo Tài Khoản
      </button>
      <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Đã có tài khoản? <a href="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>Đăng Nhập</a>
      </div>
    </form>
  );
};

export default RegisterForm;
