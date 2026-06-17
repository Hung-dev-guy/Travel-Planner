import React, { useState, useEffect } from 'react';

const SettingsPage = () => {
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [preferences, setPreferences] = useState('');
  const [message, setMessage] = useState('');
  const [isUpdatingAI, setIsUpdatingAI] = useState(false);

  useEffect(() => {
    const u = JSON.parse(localStorage.getItem('user'));
    if (u) {
      setUser(u);
      setUsername(u.username || '');
      setFullName(u.full_name || '');
      setPreferences((u.preferences || []).join('\n'));
    } else {
      window.location.href = '/login';
    }
  }, []);

  const handleUpdateProfile = async () => {
    setMessage('');
    try {
      const prefsArray = preferences.split('\n').map(p => p.trim()).filter(p => p);
      const res = await fetch('http://localhost:8000/user/api/update-profile/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          userId: user.userId, 
          username, 
          full_name: fullName, 
          password: password || undefined,
          preferences: prefsArray
        })
      });
      const data = await res.json();
      if (data.success) {
        setMessage('Cập nhật hồ sơ thành công!');
        const updatedUser = { ...user, username, full_name: fullName, preferences: prefsArray };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setUser(updatedUser);
      } else {
        setMessage(data.error || 'Lỗi cập nhật');
      }
    } catch (e) {
      setMessage('Lỗi kết nối');
    }
  };

  const handleAutoUpdatePreferences = async () => {
    setMessage('Đang nhờ AI phân tích lại lịch sử chuyến đi...');
    setIsUpdatingAI(true);
    try {
      const res = await fetch('http://localhost:8000/user/api/update-preferences/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user.username })
      });
      const data = await res.json();
      if (data.success) {
        setMessage('AI đã cập nhật thành công!');
        setPreferences((data.preferences || []).join('\n'));
        const updatedUser = { ...user, preferences: data.preferences, can_auto_update_preferences: false };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setUser(updatedUser);
      } else {
        setMessage(data.error || 'Lỗi cập nhật bằng AI');
      }
    } catch (e) {
      setMessage('Lỗi kết nối');
    }
    setIsUpdatingAI(false);
  };

  if (!user) return null;

  return (
    <div className="settings-page" style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', color: 'var(--primary)' }}>Cài đặt tài khoản</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Quản lý hồ sơ cá nhân và sở thích AI.</p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
        {message && <div style={{ padding: '10px', background: '#e3f2fd', color: '#1976d2', borderRadius: '8px' }}>{message}</div>}

        <section className="card-premium">
            <h3 style={{ marginBottom: '20px' }}>Thông tin cá nhân</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Tên đăng nhập</label>
                    <input type="text" className="input-field" value={username} onChange={e => setUsername(e.target.value)} />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Họ và tên</label>
                    <input type="text" className="input-field" value={fullName} onChange={e => setFullName(e.target.value)} />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Mật khẩu mới (Bỏ trống nếu không đổi)</label>
                    <input type="password" className="input-field" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
                </div>
                <button className="btn-premium btn-primary" style={{ width: 'fit-content' }} onClick={handleUpdateProfile}>Lưu thông tin</button>
            </div>
        </section>

        <section className="card-premium">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                <div>
                    <h3 style={{ marginBottom: '8px' }}>Sở thích Du lịch (AI Memory)</h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Sở thích này sẽ được AI sử dụng để lên lịch trình phù hợp với bạn.</p>
                </div>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Danh sách sở thích (Mỗi dòng 1 sở thích)</label>
                    <textarea 
                      className="input-field" 
                      style={{ height: '120px', resize: 'vertical' }} 
                      value={preferences} 
                      onChange={e => setPreferences(e.target.value)} 
                      placeholder="VD: Thích ăn hải sản..."
                    />
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button className="btn-premium btn-primary" style={{ flex: 1 }} onClick={handleUpdateProfile}>Lưu sở thích thủ công</button>
                </div>
            </div>
        </section>

        {user?.can_auto_update_preferences && (
            <section className="card-premium" style={{ border: '1px solid var(--primary)', background: 'rgba(59, 130, 246, 0.05)' }}>
                <h3 style={{ marginBottom: '10px', color: 'var(--primary)' }}>Đề xuất cập nhật AI 🌟</h3>
                <p style={{ fontSize: '0.9rem', marginBottom: '15px' }}>Bạn đã có nhiều chuyến đi mới! Bạn có muốn AI tự động phân tích lịch sử để tối ưu lại sở thích không?</p>
                <button className="btn-premium btn-primary" onClick={handleAutoUpdatePreferences} disabled={isUpdatingAI}>
                    {isUpdatingAI ? 'Đang phân tích...' : 'Cập nhật bằng AI ngay'}
                </button>
            </section>
        )}

      </div>
    </div>
  );
};

export default SettingsPage;
