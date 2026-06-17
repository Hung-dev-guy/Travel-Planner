import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FiGlobe, FiCalendar, FiMapPin, FiStar, FiMap, FiSend,
  FiRefreshCw, FiArrowRight, FiTrendingUp, FiMessageSquare, FiPlus, FiTrash2
} from 'react-icons/fi';
import dashboardService from '../services/dashboardService';
import tripService from '../services/tripService';

const MOCK_USER_ID = 'U001';

// ── Helpers ───────────────────────────────────────────────────────────────
const fmt = (n) => Number(n || 0).toLocaleString('vi-VN');

const statusBadge = (status) => {
  const map = {
    PLANNING: { bg: 'rgba(245,158,11,0.12)', color: '#f59e0b', label: 'Đang lên kế hoạch' },
    CONFIRMED: { bg: 'rgba(16,185,129,0.12)', color: '#10b981', label: 'Đã xác nhận' },
    COMPLETED: { bg: 'rgba(100,116,139,0.12)', color: '#64748b', label: 'Hoàn thành' },
  };
  const s = map[status] || map.PLANNING;
  return (
    <span style={{
      padding: '2px 10px', borderRadius: 20, fontSize: '0.75rem', fontWeight: 600,
      background: s.bg, color: s.color
    }}>{s.label}</span>
  );
};

// ── Stat Card ─────────────────────────────────────────────────────────────
const StatCard = ({ icon, value, label, sub, accent = 'var(--primary)' }) => (
  <div className="card-premium" style={{ position: 'relative', overflow: 'hidden' }}>
    <div style={{
      position: 'absolute', top: -10, right: -10, width: 70, height: 70,
      borderRadius: '50%', background: accent, opacity: 0.07
    }} />
    <div style={{
      width: 44, height: 44, borderRadius: 12, background: `${accent}1a`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: accent, marginBottom: 14, fontSize: '1.2rem'
    }}>
      {icon}
    </div>
    <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
      {value}
    </div>
    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 6 }}>{label}</div>
    {sub && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{sub}</div>}
  </div>
);

// ── Recent Trip Row ────────────────────────────────────────────────────────
const TripRow = ({ trip, onChat, onView, onDelete }) => (
  <div style={{
    display: 'flex', alignItems: 'center', gap: 14,
    padding: '14px 0', borderBottom: '1px solid var(--border-light)'
  }}>
    <div style={{
      width: 42, height: 42, borderRadius: 10,
      background: 'var(--primary-light)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: 'var(--primary)', flexShrink: 0
    }}>
      <FiMap size={18} />
    </div>
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-primary)',
                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
        {trip.destination || 'Chuyến đi'}
      </div>
      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2, display: 'flex', gap: 10 }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <FiMapPin size={10} /> {trip.tripId}
        </span>
        <span>{fmt(trip.totalBudget)} ₫</span>
      </div>
    </div>
    <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
      <button
        onClick={() => onDelete(trip.tripId)}
        style={{
          padding: '6px 12px', borderRadius: 8, border: '1px solid #ef4444',
          background: 'rgba(239,68,68,0.1)', color: '#ef4444',
          cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
          display: 'flex', alignItems: 'center', gap: 5, transition: 'all 0.2s'
        }}
        onMouseEnter={e => { e.currentTarget.style.background = '#ef4444'; e.currentTarget.style.color = '#fff'; }}
        onMouseLeave={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.1)'; e.currentTarget.style.color = '#ef4444'; }}
      >
        <FiTrash2 size={12} /> Xóa
      </button>
      <button
        onClick={() => onView(trip.tripId)}
        style={{
          padding: '6px 12px', borderRadius: 8, border: '1px solid var(--primary)',
          background: 'var(--primary)', color: '#fff',
          cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
          display: 'flex', alignItems: 'center', gap: 5, transition: 'all 0.2s'
        }}
        onMouseEnter={e => { e.currentTarget.style.opacity = 0.9; }}
        onMouseLeave={e => { e.currentTarget.style.opacity = 1; }}
      >
        <FiMap size={12} /> Chi tiết
      </button>
      <button
        onClick={() => onChat(trip.tripId)}
        style={{
          padding: '6px 12px', borderRadius: 8, border: '1px solid var(--primary)',
          background: 'var(--primary-light)', color: 'var(--primary)',
          cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
          display: 'flex', alignItems: 'center', gap: 5, transition: 'all 0.2s'
        }}
        onMouseEnter={e => { e.currentTarget.style.background = 'var(--primary)'; e.currentTarget.style.color = '#fff'; }}
        onMouseLeave={e => { e.currentTarget.style.background = 'var(--primary-light)'; e.currentTarget.style.color = 'var(--primary)'; }}
      >
        <FiMessageSquare size={12} /> Chat
      </button>
    </div>
  </div>
);

// ── Destination Tag ───────────────────────────────────────────────────────
const DestTag = ({ name }) => (
  <div style={{
    padding: '6px 14px', borderRadius: 20,
    background: 'var(--primary-light)', color: 'var(--primary)',
    fontSize: '0.82rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 5
  }}>
    <FiMapPin size={11} /> {name}
  </div>
);

// ── Travel Tips ────────────────────────────────────────────────────────────
const TIPS = [
  '✈️ Đặt vé máy bay vào thứ Ba thường rẻ hơn 15% so với cuối tuần.',
  '🌧️ Mùa mưa (tháng 9-11) có giá khách sạn ở Đà Nẵng rẻ hơn 30%.',
  '🍜 Ăn sáng ở chợ địa phương giúp tiết kiệm và trải nghiệm văn hoá thực sự.',
  '🎫 Mua vé tham quan combo thường tiết kiệm 20-40% so với mua lẻ.',
  '📱 Tải bản đồ offline trước chuyến đi để tiết kiệm data khi di chuyển.',
];

// ── Main Dashboard ─────────────────────────────────────────────────────────
const DashboardPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentTrips, setRecentTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tipIdx, setTipIdx] = useState(0);
  const [showAllTrips, setShowAllTrips] = useState(false);

  useEffect(() => {
    loadDashboard();
    const tipInterval = setInterval(() => setTipIdx(i => (i + 1) % TIPS.length), 8000);
    return () => clearInterval(tipInterval);
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await dashboardService.getStats(MOCK_USER_ID);
      const data = res.data;
      setStats(data.stats || {});
      setRecentTrips(data.recent_trips || []);
    } catch (err) {
      setError('Không thể tải dữ liệu. Vui lòng kiểm tra kết nối server.');
      // Show fallback empty state
      setStats({ total_trips: 0, upcoming: 0, destinations_count: 0, destinations: [] });
    } finally {
      setLoading(false);
    }
  };

  const handleChat = (tripId) => navigate('/chat', { state: { tripId } });
  const handleView = (tripId) => navigate('/trip-plan', { state: { tripId } });
  const handleNewTrip = () => navigate('/planner');

  const handleDeleteTrip = async (tripId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa chuyến đi này?')) return;
    try {
      await tripService.deleteTrip(tripId);
      loadDashboard();
    } catch (err) {
      alert('Lỗi khi xóa chuyến đi');
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                    height: '60vh', gap: 16, color: 'var(--text-muted)' }}>
        <FiRefreshCw size={32} style={{ animation: 'spin 1s linear infinite', color: 'var(--primary)' }} />
        <p style={{ margin: 0, fontSize: '0.95rem' }}>Đang tải dashboard...</p>
        <style>{`@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>
      </div>
    );
  }

  const statCards = [
    { icon: <FiGlobe />, value: stats?.total_trips ?? 0, label: 'Tổng chuyến đi', accent: '#10b981' },
    { icon: <FiCalendar />, value: stats?.upcoming ?? 0, label: 'Sắp tới', sub: 'trong 30 ngày tới', accent: '#06b6d4' },
    { icon: <FiMapPin />, value: stats?.destinations_count ?? 0, label: 'Điểm đến đã khám phá', accent: '#8b5cf6' },
    { icon: <FiStar />, value: recentTrips.length, label: 'Chuyến đi gần đây', accent: '#f59e0b' },
  ];

  return (
    <div className="dashboard-page" style={{ maxWidth: 1100, margin: '0 auto' }}>
      <style>{`@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>

      {/* ── Header ── */}
      <header style={{ marginBottom: 36, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: '2rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 10, margin: '0 0 6px' }}>
            Chào mừng trở lại, {stats?.userName || 'Explorer'}! <FiSend style={{ transform: 'rotate(-45deg)' }} />
          </h1>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
            {stats?.upcoming > 0
              ? `Bạn có ${stats.upcoming} chuyến đi sắp tới. Hãy tận hưởng hành trình!`
              : 'Hãy bắt đầu kế hoạch chuyến đi tiếp theo của bạn ngay hôm nay! 🌏'}
          </p>
        </div>
        <button
          onClick={handleNewTrip}
          className="btn-premium btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px' }}
        >
          <FiPlus /> Lên kế hoạch mới
        </button>
      </header>

      {/* ── Error banner ── */}
      {error && (
        <div style={{ marginBottom: 24, padding: '12px 16px', background: 'rgba(239,68,68,0.1)',
                      border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, fontSize: '0.875rem',
                      color: '#ef4444', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          ⚠️ {error}
          <button onClick={loadDashboard} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444', textDecoration: 'underline', fontSize: '0.82rem' }}>
            Thử lại
          </button>
        </div>
      )}

      {/* ── Stat cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px,1fr))', gap: 20, marginBottom: 36 }}>
        {statCards.map(s => <StatCard key={s.label} {...s} />)}
      </div>

      {/* ── Main content grid ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 28, alignItems: 'start' }}>

        {/* Left: Recent trips */}
        <div className="card-premium">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h3 style={{ margin: 0, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <FiTrendingUp style={{ color: 'var(--primary)' }} /> Chuyến đi gần đây
            </h3>
            <button onClick={loadDashboard} style={{ background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.82rem' }}>
              <FiRefreshCw size={13} /> Làm mới
            </button>
          </div>

          {recentTrips.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
              <FiMap size={36} style={{ display: 'block', margin: '0 auto 12px', opacity: 0.3 }} />
              <p style={{ margin: '0 0 16px', fontSize: '0.9rem' }}>Chưa có chuyến đi nào.</p>
              <button onClick={handleNewTrip} className="btn-premium btn-primary"
                style={{ padding: '8px 20px', fontSize: '0.85rem' }}>
                Tạo chuyến đi đầu tiên
              </button>
            </div>
          ) : (
            <div>
              {(showAllTrips ? recentTrips : recentTrips.slice(0, 5)).map(t => (
                <TripRow key={t.tripId} trip={t} onChat={handleChat} onView={handleView} onDelete={handleDeleteTrip} />
              ))}
              {recentTrips.length > 5 && (
                <div style={{ textAlign: 'center', marginTop: 16 }}>
                  <button onClick={() => setShowAllTrips(!showAllTrips)} style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    color: 'var(--primary)', fontSize: '0.85rem', display: 'flex',
                    alignItems: 'center', gap: 4, margin: '0 auto'
                  }}>
                    {showAllTrips ? 'Thu gọn' : 'Xem tất cả chuyến đi'} <FiArrowRight size={13} style={{ transform: showAllTrips ? 'rotate(-90deg)' : 'none', transition: 'transform 0.2s' }} />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* Destinations visited */}
          {stats?.destinations?.length > 0 && (
            <div className="card-premium">
              <h3 style={{ margin: '0 0 16px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <FiMapPin style={{ color: 'var(--primary)' }} /> Điểm đến
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {stats.destinations.map(d => <DestTag key={d} name={d} />)}
              </div>
            </div>
          )}

          {/* AI Chatbot CTA */}
          <div className="card-premium" style={{
            background: 'linear-gradient(135deg,rgba(16,185,129,0.12),rgba(6,182,212,0.08))',
            borderColor: 'var(--primary)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--primary)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem' }}>
                🤖
              </div>
              <h3 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1rem' }}>TrapBot AI</h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: '0 0 16px' }}>
              Hỏi AI về lịch trình, địa điểm, chi phí và nhận gợi ý cá nhân hoá cho chuyến đi của bạn.
            </p>
            <button onClick={() => navigate('/chat')} className="btn-premium btn-primary" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              <FiMessageSquare /> Mở TrapBot
            </button>
          </div>

          {/* Travel Tips (rotating) */}
          <div className="card-premium">
            <h3 style={{ margin: '0 0 14px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <FiStar style={{ color: '#f59e0b' }} /> Mẹo du lịch
            </h3>
            <div style={{ position: 'relative', minHeight: 80 }}>
              {TIPS.map((tip, i) => (
                <p key={i} style={{
                  position: 'absolute', top: 0, left: 0, right: 0,
                  margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.65,
                  opacity: tipIdx === i ? 1 : 0,
                  transform: tipIdx === i ? 'translateY(0)' : 'translateY(8px)',
                  transition: 'opacity 0.5s ease, transform 0.5s ease',
                  pointerEvents: tipIdx === i ? 'auto' : 'none',
                }}>
                  {tip}
                </p>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 4, marginTop: 80 }}>
              {TIPS.map((_, i) => (
                <div key={i} onClick={() => setTipIdx(i)} style={{
                  width: tipIdx === i ? 16 : 6, height: 6, borderRadius: 3, cursor: 'pointer',
                  background: tipIdx === i ? 'var(--primary)' : 'var(--border-light)',
                  transition: 'all 0.3s'
                }} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
