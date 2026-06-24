import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FiGlobe, FiCalendar, FiMapPin, FiStar, FiMap, FiSend,
  FiRefreshCw, FiArrowRight, FiTrendingUp, FiMessageSquare, FiPlus, FiTrash2,
  FiPieChart, FiBarChart2, FiDollarSign, FiChevronDown
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

// ── Stat Item (Grouped) ─────────────────────────────────────────────────────
const StatItem = ({ icon, value, label, sub, accent = 'var(--primary)' }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
    <div style={{
      width: 56, height: 56, borderRadius: 16, background: `${accent}15`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: accent, fontSize: '1.5rem', flexShrink: 0
    }}>
      {icon}
    </div>
    <div>
      <div style={{ fontSize: typeof value === 'string' && value.length > 8 ? '1.5rem' : '2rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
        {value}
      </div>
      <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: 6, fontWeight: 500 }}>{label}</div>
      {sub && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{sub}</div>}
    </div>
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
      <div style={{
        fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-primary)',
        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
      }}>
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

// ── Promo Videos ───────────────────────────────────────────────────────────
const PROMO_VIDEOS = [
  '/33077-395456634_medium.mp4',
  '/140664-775595953_medium.mp4',
  '/215448_medium.mp4'
];

// ── Posters ────────────────────────────────────────────────────────────────
const POSTERS = [
  { title: 'Khách sạn ở Bali', img: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở Bangkok', img: 'https://images.unsplash.com/photo-1508009603885-247a5b34bc25?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở Singapore', img: 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở TP.Hồ Chí Minh', img: 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở Sydney', img: 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở Melbourne', img: 'https://images.unsplash.com/photo-1514395462725-fb4566210144?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở Vũng Tàu', img: 'https://images.unsplash.com/photo-1580979685954-52d3a94fb118?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở Đà Lạt', img: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=400&q=80' },
  { title: 'Khách sạn ở Hà Nội', img: 'https://images.unsplash.com/photo-1599708153386-62bf3f034e62?auto=format&fit=crop&w=400&q=80' }
];

// ── FAQs ───────────────────────────────────────────────────────────────────
const FAQS = [
  { q: 'Cách đặt chuyến đi trên Traplanner?', a: 'Rất đơn giản, bạn chỉ cần chọn "Lên kế hoạch mới", nhập điểm đến và sở thích, AI của chúng tôi sẽ tự động tạo lịch trình tối ưu nhất cho bạn.' },
  { q: 'Làm thế nào để nhận ưu đãi trên Traplanner?', a: 'Hệ thống tự động so sánh giá và đưa ra các lựa chọn khách sạn, chuyến bay, và nhà hàng phù hợp nhất với ngân sách bạn đã nhập.' },
  { q: 'Traplanner hỗ trợ bao nhiêu điểm đến?', a: 'Chúng tôi hỗ trợ hàng ngàn điểm đến trên toàn thế giới với dữ liệu luôn được cập nhật liên tục.' },
  { q: 'Tôi có thể chia sẻ lịch trình với bạn bè không?', a: 'Có, bạn có thể dễ dàng chia sẻ lịch trình đã tạo cho bạn bè qua tính năng chia sẻ liên kết.' },
  { q: 'Làm thế nào để liên hệ bộ phận hỗ trợ?', a: 'Bạn có thể chat trực tiếp với AI Trợ lý của chúng tôi hoặc gửi email về địa chỉ support@traplanner.vn để được hỗ trợ 24/7.' }
];

// ── Guide Articles ───────────────────────────────────────────────────────────
const GUIDE_ARTICLES = [
  { title: "Bí quyết tối ưu hóa hành lý", img: "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1200&q=80", excerpt: "Khám phá nghệ thuật cuộn quần áo thay vì gấp, cách tận dụng các khoảng trống nhỏ nhất và nguyên tắc 'chỉ mang đồ thiết yếu' để biến chiếc vali nhỏ thành chiếc tủ di động hoàn hảo." },
  { title: "Bản đồ ẩm thực: Ăn gì ở đâu?", img: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80", excerpt: "Đừng chỉ ăn ở các nhà hàng đắt đỏ gần khu du lịch. Hãy bước vào các khu chợ truyền thống, nơi ẩn chứa tinh hoa ẩm thực địa phương thực sự với mức giá cực kỳ phải chăng." },
  { title: "Cẩm nang an toàn khi du lịch", img: "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80", excerpt: "Lưu bản sao giấy tờ tùy thân lên đám mây, luôn chia sẻ vị trí với người thân và ghi nhớ số điện thoại khẩn cấp của đại sứ quán là những điều kiện sống còn." }
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
  const [currentUser, setCurrentUser] = useState(null);
  const [videoIdx, setVideoIdx] = useState(0);
  const [currentView, setCurrentView] = useState('posters'); // 'posters' | 'stats' | 'guide'
  const [openFaq, setOpenFaq] = useState(null);
  const [articleIdx, setArticleIdx] = useState(0);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        setCurrentUser(JSON.parse(userStr));
      } catch (e) { }
    }
    loadDashboard();
    const tipInterval = setInterval(() => setTipIdx(i => (i + 1) % TIPS.length), 8000);
    const articleInterval = setInterval(() => setArticleIdx(i => (i + 1) % GUIDE_ARTICLES.length), 5000);
    return () => {
      clearInterval(tipInterval);
      clearInterval(articleInterval);
    };
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError('');
    try {
      const userStr = localStorage.getItem('user');
      const userId = userStr ? JSON.parse(userStr).userId : MOCK_USER_ID;
      const res = await dashboardService.getStats(userId);
      const data = res.data;
      setStats(data.stats || {});

      const uniqueTrips = (data.recent_trips || []).filter((trip, index, self) =>
        index === self.findIndex((t) => t.tripId === trip.tripId)
      );
      setRecentTrips(uniqueTrips);
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
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        height: '60vh', gap: 16, color: 'var(--text-muted)'
      }}>
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
    { icon: <FiDollarSign />, value: `${fmt(stats?.total_budget ?? 0)} ₫`, label: 'Tổng ngân sách', accent: '#f59e0b' },
  ];

  // Prepare chart data
  const tripsPerMonth = stats?.trips_per_month || [];
  const maxTripCount = Math.max(...tripsPerMonth.map(t => t.count), 1);
  const costDist = stats?.cost_distribution || [];
  const totalCost = costDist.reduce((acc, curr) => acc + curr.amount, 0);
  const pieColors = ['#10b981', '#06b6d4', '#8b5cf6', '#f59e0b', '#ef4444', '#ec4899'];
  let currentAngle = 0;
  const conicGradients = totalCost > 0 ? costDist.map((item, index) => {
    const angle = (item.amount / totalCost) * 360;
    const start = currentAngle;
    currentAngle += angle;
    return `${pieColors[index % pieColors.length]} ${start}deg ${currentAngle}deg`;
  }).join(', ') : '#e2e8f0 0deg 360deg';

  return (
    <div className="dashboard-page" style={{ maxWidth: 1100, margin: '0 auto' }}>
      <style>{`
        @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>

      {/* ── Promo Hero Banner ── */}
      <div
        onClick={() => navigate('/destinations')}
        style={{
          position: 'relative', width: '100%', height: 260, borderRadius: 24, overflow: 'hidden',
          marginBottom: 36, cursor: 'pointer', boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease'
        }}
        onMouseEnter={e => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.boxShadow = '0 15px 35px rgba(0,0,0,0.2)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.15)';
        }}
      >
        <video
          key={videoIdx}
          src={PROMO_VIDEOS[videoIdx]}
          autoPlay muted playsInline
          onEnded={() => setVideoIdx(i => (i + 1) % PROMO_VIDEOS.length)}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
        <div style={{
          position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
          background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.1) 100%)',
          display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '30px 40px'
        }}>
          <h2 style={{ color: '#fbbf24', fontSize: '1.8rem', fontWeight: 800, margin: '0 0 8px', textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>
            Điểm đến tiếp theo của bạn? Lên kế hoạch giá tốt với <span style={{ color: 'var(--primary)' }}>Traplanner</span>
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '1.1rem', margin: 0, fontWeight: 500, textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}>
            Khám phá nhiều lựa chọn từ điểm tham quan, nhà hàng, khách sạn và hơn thế nữa.
          </p>
        </div>
      </div>

      {/* ── Introduction Header ── */}
      <div
        className="intro-banner"
        style={{
          position: 'relative',
          overflow: 'hidden',
          background: '#fff',
          borderRadius: 24,
          padding: '40px',
          marginBottom: 36,
          boxShadow: '0 8px 30px rgba(0,0,0,0.06)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          border: '1px solid var(--border-light)'
        }}
      >
        {/* Decor SVGs */}
        <svg style={{ position: 'absolute', top: 20, left: 30, opacity: 0.1, transform: 'rotate(-15deg)' }} width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 2L11 13"></path>
          <path d="M22 2L15 22L11 13L2 9L22 2Z"></path>
        </svg>
        <svg style={{ position: 'absolute', bottom: -15, left: 80, opacity: 0.08 }} width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M2 12h20"></path>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
        </svg>
        <svg style={{ position: 'absolute', top: 30, right: 40, opacity: 0.15 }} width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
        <svg style={{ position: 'absolute', bottom: 10, right: 100, opacity: 0.08 }} width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
        </svg>

        <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h1 style={{ fontSize: '2.4rem', color: 'var(--primary)', margin: '0 0 16px', fontWeight: 800 }}>
            Traplanner - Trợ lý du lịch thông minh
          </h1>
          <p style={{ fontSize: '1.15rem', color: '#475569', margin: '0 0 32px', maxWidth: '800px', lineHeight: 1.6 }}>
            Nền tảng lập kế hoạch du lịch bằng AI. Khám phá các điểm đến tuyệt vời, tự động tối ưu hóa lịch trình và quản lý ngân sách một cách nhanh chóng, dễ dàng nhất.
          </p>
          <button
            onClick={() => navigate('/planner')}
            style={{
              background: 'var(--primary)',
              color: '#fff',
              border: 'none',
              padding: '16px 36px',
              borderRadius: 30,
              fontSize: '1.15rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              boxShadow: '0 8px 25px rgba(1, 148, 243, 0.4)',
              animation: 'pulse-btn 2s infinite'
            }}
          >
            Hãy lên kế hoạch ngay <FiArrowRight size={22} />
          </button>
        </div>
        <style>
          {`
            @keyframes pulse-btn {
              0% { box-shadow: 0 0 0 0 rgba(1, 148, 243, 0.5); transform: scale(1); }
              50% { box-shadow: 0 0 0 20px rgba(1, 148, 243, 0); transform: scale(1.04); }
              100% { box-shadow: 0 0 0 0 rgba(1, 148, 243, 0); transform: scale(1); }
            }
          `}
        </style>
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div style={{
          marginBottom: 24, padding: '12px 16px', background: 'rgba(239,68,68,0.1)',
          border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, fontSize: '0.875rem',
          color: '#ef4444', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
        }}>
          ⚠️ {error}
          <button onClick={loadDashboard} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444', textDecoration: 'underline', fontSize: '0.82rem' }}>
            Thử lại
          </button>
        </div>
      )}

      {/* ── Main Layout: Sidebar & Content ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: 30, alignItems: 'start' }}>

        {/* Left Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20, position: 'sticky', top: 100, height: 'calc(100vh - 130px)' }}>

          {/* Display Options -> Stats Toggle */}
          <div
            className="card-premium"
            style={{
              position: 'relative', overflow: 'hidden', padding: '30px 20px', flex: 1,
              display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
              boxShadow: currentView === 'stats' ? '0 0 0 3px var(--primary), 0 4px 15px rgba(0,0,0,0.1)' : '0 4px 15px rgba(0,0,0,0.1)',
              transition: 'transform 0.2s',
            }}
            onClick={() => setCurrentView(currentView === 'stats' ? 'posters' : 'stats')}
            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
            onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=400&q=80" alt="Stats" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 100%)' }}></div>
            <div style={{ position: 'relative', zIndex: 1, textAlign: 'center', width: '100%' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 48, height: 48, borderRadius: '50%', background: currentView === 'stats' ? 'var(--primary)' : 'rgba(255,255,255,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', backdropFilter: 'blur(4px)', transition: 'background 0.3s' }}>
                  <FiPieChart size={22} />
                </div>
                <h3 style={{ margin: 0, color: '#fff', fontSize: '1.15rem', fontWeight: 700, lineHeight: 1.4, textShadow: '0 2px 4px rgba(0,0,0,0.6)' }}>
                  {currentView === 'stats' ? 'Ẩn thống kê' : 'Thống kê về chuyến đi của bạn'}
                </h3>
              </div>
            </div>
          </div>

          {/* Travel Guide */}
          <div
            className="card-premium"
            style={{
              position: 'relative', overflow: 'hidden', padding: '24px 20px', flex: 1, display: 'flex', flexDirection: 'column',
              cursor: 'pointer',
              boxShadow: currentView === 'guide' ? '0 0 0 3px #fcd34d, 0 4px 15px rgba(0,0,0,0.1)' : '0 4px 15px rgba(0,0,0,0.1)',
              transition: 'transform 0.2s',
            }}
            onClick={() => setCurrentView(currentView === 'guide' ? 'posters' : 'guide')}
            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
            onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <img src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=400&q=80" alt="Guide" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 100%)' }}></div>

            <div style={{ position: 'relative', zIndex: 1, height: '100%', display: 'flex', flexDirection: 'column', flex: 1 }}>
              <h3 style={{ margin: '0 0 20px', color: '#fcd34d', display: 'flex', alignItems: 'center', gap: 8, fontSize: '1.1rem', fontWeight: 800, textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>
                <FiStar /> Cẩm nang du lịch
              </h3>
              <div style={{ position: 'relative', flex: 1, minHeight: 120 }}>
                {TIPS.map((tip, i) => (
                  <p key={i} style={{
                    position: 'absolute', top: 0, left: 0, right: 0,
                    margin: 0, fontSize: '0.95rem', color: 'rgba(255,255,255,0.95)', lineHeight: 1.6,
                    opacity: tipIdx === i ? 1 : 0,
                    transform: tipIdx === i ? 'translateY(0)' : 'translateY(8px)',
                    transition: 'opacity 0.5s ease, transform 0.5s ease',
                    pointerEvents: tipIdx === i ? 'auto' : 'none',
                    fontWeight: 500, textShadow: '0 2px 4px rgba(0,0,0,0.8)'
                  }}>
                    {tip}
                  </p>
                ))}
              </div>
              <div style={{ display: 'flex', gap: 6, marginTop: 16 }}>
                {TIPS.map((_, i) => (
                  <div key={i} onClick={() => setTipIdx(i)} style={{
                    width: tipIdx === i ? 24 : 8, height: 4, borderRadius: 2, cursor: 'pointer',
                    background: tipIdx === i ? '#fcd34d' : 'rgba(255,255,255,0.4)',
                    transition: 'all 0.3s'
                  }} />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Content */}
        <div>
          {currentView === 'stats' && (
            <div style={{ animation: 'fadeIn 0.4s ease-out' }}>
              {/* ── Stat cards (Grouped) ── */}
              <div className="card-premium" style={{ marginBottom: 36, padding: '30px', background: '#fff' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '30px' }}>
                  {statCards.map(s => <StatItem key={s.label} {...s} />)}
                </div>
              </div>

              {/* ── Main content grid ── */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 28, alignItems: 'stretch' }}>

                {/* Left column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>

                  {/* Charts Row */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                    {/* Bar Chart */}
                    <div className="card-premium" style={{ display: 'flex', flexDirection: 'column', background: '#fff' }}>
                      <h3 style={{ margin: '0 0 20px', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <FiBarChart2 style={{ color: 'var(--primary)' }} /> Chuyến đi theo tháng
                      </h3>
                      {tripsPerMonth.length > 0 ? (
                        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'flex-end', gap: 12, height: 160, paddingBottom: 24, position: 'relative' }}>
                          {tripsPerMonth.map((data, i) => (
                            <div key={i} style={{ flex: 1, maxWidth: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, height: '100%' }}>
                              <div style={{ width: '100%', backgroundColor: 'var(--primary-light)', borderRadius: '6px 6px 0 0', position: 'relative', height: '100%', display: 'flex', alignItems: 'flex-end' }}>
                                <div style={{
                                  width: '100%',
                                  backgroundColor: 'var(--primary)',
                                  borderRadius: '6px 6px 0 0',
                                  height: `${(data.count / maxTripCount) * 100}%`,
                                  transition: 'height 0.5s ease-out'
                                }}></div>
                                <span style={{ position: 'absolute', top: -20, left: '50%', transform: 'translateX(-50%)', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{data.count}</span>
                              </div>
                              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', position: 'absolute', bottom: 0 }}>{data.month.split('-')[1]}/{data.month.split('-')[0].slice(2)}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Chưa có dữ liệu</div>
                      )}
                    </div>

                    {/* Pie Chart */}
                    <div className="card-premium" style={{ display: 'flex', flexDirection: 'column', background: '#fff' }}>
                      <h3 style={{ margin: '0 0 20px', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <FiPieChart style={{ color: 'var(--primary)' }} /> Phân bổ chi phí
                      </h3>
                      {totalCost > 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                          <div style={{
                            width: 120, height: 120, borderRadius: '50%', flexShrink: 0,
                            background: `conic-gradient(${conicGradients})`,
                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                          }}></div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                            {costDist.map((item, i) => (
                              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                <span style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: pieColors[i % pieColors.length] }}></span>
                                <span style={{ flex: 1, textTransform: 'capitalize' }}>{item.category}</span>
                                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{Math.round((item.amount / totalCost) * 100)}%</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Chưa có dữ liệu</div>
                      )}
                    </div>
                  </div>

                  {/* Recent trips */}
                  <div className="card-premium" style={{ background: '#fff' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                      <h3 style={{ margin: 0, color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <FiTrendingUp style={{ color: 'var(--primary)' }} /> Chuyến đi gần đây
                      </h3>
                      <button onClick={loadDashboard} style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.82rem'
                      }}>
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
                </div>

                {/* Right column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

                  {/* Destinations visited */}
                  {stats?.destinations?.length > 0 && (
                    <div className="card-premium" style={{ background: '#fff' }}>
                      <h3 style={{ margin: '0 0 16px', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <FiMapPin style={{ color: 'var(--primary)' }} /> Điểm đến
                      </h3>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {stats.destinations.map(d => <DestTag key={d} name={d} />)}
                      </div>
                    </div>
                  )}

                  {/* AI Chatbot CTA */}
                  <div className="card-premium" style={{
                    position: 'relative', overflow: 'hidden', flex: 1, display: 'flex', flexDirection: 'column', padding: '30px 20px',
                    borderColor: 'var(--primary)', minHeight: 280
                  }}>
                    <img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=400&q=80" alt="AI" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 100%)' }}></div>

                    <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                        <div style={{
                          width: 48, height: 48, borderRadius: 14, background: 'var(--primary)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem', color: '#fff', boxShadow: '0 4px 15px rgba(1,148,243,0.4)'
                        }}>
                          🤖
                        </div>
                        <h3 style={{ margin: 0, color: '#fff', fontSize: '1.3rem', fontWeight: 800, textShadow: '0 2px 4px rgba(0,0,0,0.6)' }}>TrapBot AI</h3>
                      </div>
                      <p style={{ fontSize: '1.05rem', color: 'rgba(255,255,255,0.95)', lineHeight: 1.6, margin: '0 0 24px', textShadow: '0 1px 3px rgba(0,0,0,0.5)' }}>
                        Hỏi AI về lịch trình, địa điểm, chi phí và nhận gợi ý cá nhân hoá cho chuyến đi của bạn.
                      </p>
                      <button onClick={() => navigate('/chat')} className="btn-premium btn-primary" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '14px', fontSize: '1rem', marginTop: 'auto' }}>
                        <FiMessageSquare /> Mở TrapBot
                      </button>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          )}

          {currentView === 'guide' && (
            <div style={{ animation: 'fadeIn 0.4s ease-out', height: 'calc(100vh - 130px)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative', width: '100%', flex: 1, borderRadius: 20, overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
                {GUIDE_ARTICLES.map((article, idx) => (
                  <div key={idx} style={{
                    position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
                    opacity: articleIdx === idx ? 1 : 0, transition: 'opacity 1s ease-in-out',
                    zIndex: articleIdx === idx ? 1 : 0
                  }}>
                    <img src={article.img} alt={article.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '80px 40px 40px', background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 60%, transparent 100%)' }}>
                      <h3 style={{ margin: '0 0 16px', fontSize: '2.2rem', color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>{article.title}</h3>
                      <p style={{ margin: 0, fontSize: '1.15rem', color: 'rgba(255,255,255,0.95)', lineHeight: 1.6, maxWidth: '90%', textShadow: '0 1px 3px rgba(0,0,0,0.5)' }}>{article.excerpt}</p>
                    </div>
                  </div>
                ))}

                {/* Dots indicator */}
                <div style={{ position: 'absolute', bottom: 20, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 8, zIndex: 10 }}>
                  {GUIDE_ARTICLES.map((_, idx) => (
                    <div key={idx} onClick={() => setArticleIdx(idx)} style={{
                      width: articleIdx === idx ? 32 : 10, height: 6, borderRadius: 3, cursor: 'pointer',
                      background: articleIdx === idx ? 'var(--primary)' : 'rgba(255,255,255,0.5)',
                      transition: 'all 0.3s'
                    }} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentView === 'posters' && (
            <div style={{ animation: 'fadeIn 0.4s ease-out' }}>
              <h2 style={{ fontSize: '1.5rem', color: 'var(--primary)', margin: '0 0 20px', fontWeight: 800 }}>
                Ưu đãi khách sạn tốt nhất tại các điểm đến phổ biến
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
                {POSTERS.map(p => (
                  <div key={p.title} style={{
                    position: 'relative', height: 160, borderRadius: 16, overflow: 'hidden', cursor: 'pointer',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.1)', transition: 'transform 0.2s'
                  }}
                    onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
                    onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
                    onClick={() => navigate('/destinations')}
                  >
                    <img src={p.img} alt={p.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, transparent 100%)', padding: 16 }}>
                      <div style={{ color: '#fff', fontWeight: 700, fontSize: '1.05rem', textShadow: '0 2px 4px rgba(0,0,0,0.6)' }}>{p.title}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── FAQ Section ── */}
      <div style={{ marginTop: 60, marginBottom: 40 }}>
        <h2 style={{ fontSize: '1.6rem', color: 'var(--primary)', margin: '0 0 24px', fontWeight: 800 }}>
          Câu hỏi thường gặp
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {FAQS.map((faq, i) => (
            <div key={i} style={{
              background: 'var(--bg-glass)', border: '1px solid var(--border-light)', borderRadius: 12, overflow: 'hidden'
            }}>
              <div
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                style={{
                  padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  cursor: 'pointer', fontWeight: 600, color: 'var(--text-primary)', fontSize: '1.05rem',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-default)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                {faq.q}
                <div style={{
                  width: 28, height: 28, borderRadius: '50%', background: 'var(--primary-light)', color: 'var(--primary)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'transform 0.3s',
                  transform: openFaq === i ? 'rotate(180deg)' : 'rotate(0deg)'
                }}>
                  <FiChevronDown size={16} />
                </div>
              </div>
              <div style={{
                maxHeight: openFaq === i ? 200 : 0, opacity: openFaq === i ? 1 : 0, transition: 'all 0.3s ease-in-out',
                padding: openFaq === i ? '0 24px 20px' : '0 24px', color: 'var(--text-secondary)', lineHeight: 1.6
              }}>
                {faq.a}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
