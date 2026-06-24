import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import { FiSun, FiMoon, FiCompass, FiSearch, FiX, FiCheck, FiChevronDown, FiHelpCircle, FiMessageSquare, FiMail, FiLayout, FiMap, FiMessageCircle, FiMapPin, FiSettings } from 'react-icons/fi';

const currencies = [
  { code: 'AED', label: 'Dirham của Các Tiểu Vương Quốc Ả Rập Thống Nhất', symbol: 'AED', flag: '🇦🇪' },
  { code: 'AUD', label: 'Đô la Úc', symbol: 'AU$', flag: '🇦🇺' },
  { code: 'BRL', label: 'Real Brazil', symbol: 'BRL', flag: '🇧🇷' },
  { code: 'CAD', label: 'Đô la Canada', symbol: 'CAD', flag: '🇨🇦' },
  { code: 'CHF', label: 'Franc Thụy Sĩ', symbol: 'CHF', flag: '🇨🇭' },
  { code: 'CNY', label: 'Nhân dân tệ (Trung Quốc) Yuan', symbol: 'CNY', flag: '🇨🇳' },
  { code: 'EGP', label: 'Pound Ai Cập', symbol: 'EGP', flag: '🇪🇬' },
  { code: 'EUR', label: 'Euro', symbol: '€', flag: '🇪🇺' },
  { code: 'GBP', label: 'Bảng Anh', symbol: 'GBP', flag: '🇬🇧' },
  { code: 'HKD', label: 'Đô la Hồng Kông', symbol: 'HKD', flag: '🇭🇰' },
  { code: 'IDR', label: 'Rupiah Indonesia', symbol: 'Rp', flag: '🇮🇩' },
  { code: 'INR', label: 'Rupee Ấn Độ', symbol: 'INR', flag: '🇮🇳' },
  { code: 'JPY', label: 'Yên Nhật', symbol: '円', flag: '🇯🇵' },
  { code: 'KRW', label: 'Won Hàn Quốc', symbol: '원', flag: '🇰🇷' },
  { code: 'MYR', label: 'Ringgit Malaysia', symbol: 'RM', flag: '🇲🇾' },
  { code: 'NZD', label: 'Đô la New Zealand', symbol: 'NZD', flag: '🇳🇿' },
  { code: 'PHP', label: 'Peso Philippines', symbol: '₱', flag: '🇵🇭' },
  { code: 'SGD', label: 'Đô la Singapore', symbol: 'S$', flag: '🇸🇬' },
  { code: 'THB', label: 'Baht Thái', symbol: 'THB', flag: '🇹🇭' },
  { code: 'TWD', label: 'Đô la Đài Loan mới', symbol: 'TWD', flag: '🇹🇼' },
  { code: 'USD', label: 'Đô la Mỹ', symbol: 'USD', flag: '🇺🇸' },
  { code: 'VND', label: 'Đồng Việt Nam', symbol: 'VND', flag: '🇻🇳' },
];

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();
  const [showCurrencyModal, setShowCurrencyModal] = useState(false);
  const [selectedCurrency, setSelectedCurrency] = useState('VND');
  const [showSupportMenu, setShowSupportMenu] = useState(false);
  const [isNavHovered, setIsNavHovered] = useState(false);
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('token') || !!localStorage.getItem('user');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const currentCurrencyObj = currencies.find(c => c.code === selectedCurrency) || currencies[21];

  return (
    <>
      <nav
        style={{ 
          background: 'var(--bg-main)', borderBottom: '1px solid var(--border-light)', position: 'sticky', top: 0, zIndex: 100, boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
          animation: 'navFadeIn 0.6s ease-out forwards'
        }}
        onMouseEnter={() => setIsNavHovered(true)}
        onMouseLeave={() => setIsNavHovered(false)}
      >
        {/* Top Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 24px', maxWidth: 1200, margin: '0 auto' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', height: '48px' }}>
              <img src={theme === 'dark' ? '/chedotoi.png' : '/logo_traveloka.png'} alt="Traplanner" style={{ height: '48px', objectFit: 'contain', transform: theme === 'dark' ? 'scale(1.3)' : 'none', transformOrigin: 'center' }} />
            </div>
          </Link>

          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <div
              onClick={() => setShowCurrencyModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', padding: '6px 10px', borderRadius: '8px', transition: 'background 0.2s' }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-main)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <span style={{ fontSize: '1rem' }}>{currentCurrencyObj.flag}</span>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{selectedCurrency} | VI</span>
            </div>
            <button
              onClick={toggleTheme}
              style={{
                background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.25rem',
                color: 'var(--text-secondary)', display: 'flex', alignItems: 'center'
              }}
            >
              {theme === 'light' ? <FiMoon size={20} /> : <FiSun size={20} />}
            </button>
            <div style={{ position: 'relative' }} onMouseLeave={() => setShowSupportMenu(false)}>
              <div
                onMouseEnter={() => setShowSupportMenu(true)}
                className="support-menu-trigger"
              >
                Hỗ trợ <FiChevronDown size={14} style={{ transform: showSupportMenu ? 'rotate(180deg)' : 'none', transition: 'transform 0.3s ease' }} />
              </div>
              {showSupportMenu && (
                <div style={{
                  position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: '0',
                  background: 'var(--bg-main)', borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
                  padding: '8px 0', minWidth: '220px', zIndex: 101, border: '1px solid var(--border-light)',
                  animation: 'fadeSlideIn 0.3s ease forwards'
                }}>
                  <Link to="/help" className="dropdown-item">
                    <FiHelpCircle size={20} style={{ color: 'var(--text-secondary)' }} /> Trợ giúp
                  </Link>
                  <Link to="/contact" className="dropdown-item">
                    <FiMessageSquare size={20} style={{ color: 'var(--text-secondary)' }} /> Liên hệ chúng tôi
                  </Link>
                  <Link to="/inbox" className="dropdown-item">
                    <FiMail size={20} style={{ color: 'var(--text-secondary)' }} /> Hộp thư của tôi
                  </Link>
                </div>
              )}
            </div>
            <Link to="/features" className="nav-link-top">Tính năng</Link>
            <Link to="/about" className="nav-link-top">Giới thiệu</Link>
            <div style={{ display: 'flex', gap: '10px' }}>
              {isLoggedIn ? (
                <button onClick={handleLogout} className="btn-logout">Đăng xuất</button>
              ) : (
                <>
                  <Link to="/login" className="btn-secondary" style={{ padding: '8px 16px', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem' }}>Đăng nhập</Link>
                  <Link to="/register" className="btn-primary" style={{ padding: '8px 16px', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem' }}>Đăng ký</Link>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Row (Navigation) */}
        <style>{`
          @keyframes fadeSlideIn {
            from { opacity: 0; transform: translate(-50%, 10px); }
            to { opacity: 1; transform: translate(-50%, 0); }
          }
          .dropdown-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 20px;
            text-decoration: none;
            color: var(--text-primary);
            font-size: 0.95rem;
            font-weight: 500;
            transition: background 0.2s;
          }
          .dropdown-item:hover {
            background: rgba(128, 128, 128, 0.1);
          }
          .nav-link-top {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.3s ease, opacity 0.3s ease;
          }
          .nav-link-top:hover {
            color: var(--primary);
            opacity: 0.8;
          }
          .support-menu-trigger {
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-secondary);
            padding: 6px 0;
            transition: color 0.3s ease;
          }
          .support-menu-trigger:hover {
            color: var(--primary);
          }
          .btn-logout {
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid var(--border-light);
            background: transparent;
            color: #ef4444;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
          }
          .btn-logout:hover {
            background: rgba(239, 68, 68, 0.1);
            border-color: #fca5a5;
          }
          @keyframes navFadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .nav-link-bottom {
            color: var(--text-primary);
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 8px;
            transition: all 0.3s ease;
          }
          .nav-link-bottom svg {
            transition: transform 0.3s ease;
          }
          .nav-link-bottom:hover {
            color: var(--primary);
            background: rgba(128, 128, 128, 0.1);
          }
          .nav-link-bottom:hover svg {
            transform: scale(1.1) translateY(-2px);
          }
        `}</style>
        <div style={{
          background: 'var(--bg-main)',
          maxHeight: isNavHovered ? '80px' : '0',
          opacity: isNavHovered ? 1 : 0,
          overflow: 'hidden',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          borderTop: isNavHovered ? '1px solid var(--border-light)' : '0px solid transparent'
        }}>
          <div style={{ display: 'flex', gap: '20px', padding: '12px 24px', maxWidth: 1200, margin: '0 auto', overflowX: 'auto', alignItems: 'center' }}>
            <Link to="/dashboard" className="nav-link-bottom">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>
              Bảng điều khiển
            </Link>
            <Link to="/planner" className="nav-link-bottom">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon><line x1="8" y1="2" x2="8" y2="18"></line><line x1="16" y1="6" x2="16" y2="22"></line></svg>
              Lên kế hoạch
            </Link>
            <Link to="/chat" className="nav-link-bottom">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>
              AI Trợ lý
            </Link>
            <Link to="/destinations" className="nav-link-bottom">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
              Điểm đến
            </Link>
            <Link to="/settings" className="nav-link-bottom">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
              Cài đặt
            </Link>
          </div>
        </div>
      </nav>

      {/* Currency Modal */}
      {showCurrencyModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
          background: 'rgba(0,0,0,0.5)', zIndex: 9999,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{
            background: '#fff', borderRadius: '12px', width: '90%', maxWidth: '800px',
            maxHeight: '85vh', display: 'flex', flexDirection: 'column',
            boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
          }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0, fontSize: '1.2rem', color: '#1e293b' }}>Chọn đơn vị tiền tệ</h2>
              <button
                onClick={() => setShowCurrencyModal(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.5rem', color: '#64748b' }}
              >
                <FiX />
              </button>
            </div>

            <div style={{ padding: '24px', overflowY: 'auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {currencies.map(curr => {
                const isSelected = selectedCurrency === curr.code;
                return (
                  <div
                    key={curr.code}
                    onClick={() => {
                      setSelectedCurrency(curr.code);
                      setShowCurrencyModal(false);
                    }}
                    style={{
                      display: 'flex', alignItems: 'center', padding: '12px', borderRadius: '8px', cursor: 'pointer',
                      background: isSelected ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={e => !isSelected && (e.currentTarget.style.background = '#f1f5f9')}
                    onMouseLeave={e => !isSelected && (e.currentTarget.style.background = 'transparent')}
                  >
                    <div style={{ width: '48px', height: '28px', background: '#f1f5f9', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem', fontWeight: 700, color: '#475569', marginRight: '16px' }}>
                      {curr.code}
                    </div>
                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '0.95rem', color: isSelected ? '#10b981' : '#1e293b', fontWeight: isSelected ? 600 : 400 }}>{curr.label}</span>
                      <span style={{ fontSize: '0.95rem', color: '#94a3b8' }}>({curr.symbol})</span>
                    </div>
                    {isSelected && <FiCheck style={{ color: '#10b981', marginLeft: 'auto' }} size={20} />}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
