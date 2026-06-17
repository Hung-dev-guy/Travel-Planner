import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FiSend, FiTrash2, FiRefreshCw, FiMapPin, FiCalendar, FiDollarSign,
         FiMessageSquare, FiChevronRight, FiLoader, FiZap } from 'react-icons/fi';
import chatbotService from '../../services/chatbotService';

// ── Markdown-lite renderer ──────────────────────────────────────────────────
function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code style="background:rgba(16,185,129,0.12);padding:2px 6px;border-radius:4px;font-size:0.88em">$1</code>')
    .replace(/\n(#{1,3}) (.+)/g, (_, h, t) => `<h${h.length} style="margin:12px 0 6px;color:var(--primary)">${t}</h${h.length}>`)
    .replace(/\n- (.+)/g, '<li style="margin:3px 0">$1</li>')
    .replace(/(<li[^>]*>.*<\/li>)/s, '<ul style="padding-left:18px;margin:6px 0">$1</ul>')
    .replace(/\n\n/g, '</p><p style="margin:8px 0">')
    .replace(/\n/g, '<br/>');
}

// ── Typing indicator ──────────────────────────────────────────────────────
const TypingIndicator = () => (
  <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 16 }}>
    <div style={{
      display: 'flex', alignItems: 'center', gap: 6,
      padding: '14px 18px', borderRadius: '18px 18px 18px 4px',
      background: 'var(--bg-sidebar)', border: '1px solid var(--border-light)',
      boxShadow: 'var(--shadow-sm)'
    }}>
      <BotAvatar small />
      {[0, 0.2, 0.4].map((d, i) => (
        <div key={i} style={{
          width: 7, height: 7, borderRadius: '50%',
          background: 'var(--primary)',
          animation: 'bounce 1.2s ease-in-out infinite',
          animationDelay: `${d}s`
        }} />
      ))}
    </div>
  </div>
);

const BotAvatar = ({ small }) => (
  <div style={{
    width: small ? 18 : 30, height: small ? 18 : 30, flexShrink: 0,
    borderRadius: '50%', background: 'linear-gradient(135deg,#10b981,#06b6d4)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: small ? '0.6rem' : '0.85rem', color: '#fff', fontWeight: 700
  }}>🤖</div>
);

// ── Single message bubble ─────────────────────────────────────────────────
const MessageBubble = ({ msg }) => {
  const isBot = msg.sender === 'bot';
  return (
    <div style={{
      display: 'flex', justifyContent: isBot ? 'flex-start' : 'flex-end',
      marginBottom: 20, gap: 10, alignItems: 'flex-end'
    }}>
      {isBot && <BotAvatar />}
      <div style={{ maxWidth: '72%' }}>
        {/* Images from search_destination_info */}
        {msg.images?.length > 0 && (
          <div style={{ display: 'flex', gap: 6, marginBottom: 8, flexWrap: 'wrap' }}>
            {msg.images.map((src, i) => (
              <img key={i} src={src} alt="" loading="lazy"
                style={{ width: 100, height: 70, objectFit: 'cover', borderRadius: 8,
                         border: '1px solid var(--border-light)' }}
                onError={e => e.target.style.display = 'none'}
              />
            ))}
          </div>
        )}
        <div style={{
          padding: '13px 18px',
          borderRadius: isBot ? '18px 18px 18px 4px' : '18px 18px 4px 18px',
          background: isBot ? 'var(--bg-sidebar)' : 'linear-gradient(135deg,#10b981,#059669)',
          color: isBot ? 'var(--text-primary)' : '#fff',
          boxShadow: 'var(--shadow-sm)',
          border: isBot ? '1px solid var(--border-light)' : 'none',
          fontSize: '0.93rem', lineHeight: 1.65,
          animation: 'fadeInUp 0.25s ease'
        }}>
          {isBot
            ? <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.text) }} />
            : msg.text}
          {/* Source link */}
          {msg.url && (
            <a href={msg.url} target="_blank" rel="noopener noreferrer"
              style={{ display: 'block', marginTop: 8, fontSize: '0.78rem',
                       color: isBot ? 'var(--primary)' : 'rgba(255,255,255,0.8)',
                       textDecoration: 'underline' }}>
              🔗 Xem thêm
            </a>
          )}
        </div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)',
                      marginTop: 4, textAlign: isBot ? 'left' : 'right', paddingInline: 4 }}>
          {msg.time}
        </div>
      </div>
    </div>
  );
};

// ── Trip card in sidebar ──────────────────────────────────────────────────
const TripCard = ({ trip, isSelected, onSelect }) => {
  const fmt = (n) => Number(n || 0).toLocaleString('vi-VN');
  return (
    <div
      onClick={() => onSelect(trip)}
      style={{
        padding: '12px 14px', borderRadius: 10, cursor: 'pointer',
        background: isSelected ? 'var(--primary-light)' : 'transparent',
        border: `1px solid ${isSelected ? 'var(--primary)' : 'var(--border-light)'}`,
        transition: 'all 0.2s', marginBottom: 8
      }}
      onMouseEnter={e => { if (!isSelected) { e.currentTarget.style.background = 'var(--bg-main)'; } }}
      onMouseLeave={e => { if (!isSelected) { e.currentTarget.style.background = 'transparent'; } }}
    >
      <div style={{ fontWeight: 600, fontSize: '0.9rem', color: isSelected ? 'var(--primary)' : 'var(--text-primary)',
                    marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
        <FiMapPin size={12} style={{ flexShrink: 0 }} /> {trip.destination || 'Chưa xác định'}
      </div>
      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', gap: 12 }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <FiDollarSign size={10} /> {fmt(trip.totalBudget)} ₫
        </span>
        <span style={{
          padding: '1px 6px', borderRadius: 4, fontSize: '0.7rem',
          background: trip.status === 'CONFIRMED' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
          color: trip.status === 'CONFIRMED' ? '#10b981' : '#f59e0b',
          fontWeight: 600
        }}>{trip.status}</span>
      </div>
    </div>
  );
};

// ── Quick-action chips ───────────────────────────────────────────────────
const QUICK_ACTIONS = [
  'Tóm tắt lịch trình cho tôi',
  'Phân tích chi phí chi tiết',
  'Gợi ý địa điểm nổi bật',
  'Tìm khách sạn thay thế',
];

// ── Main ChatContainer ────────────────────────────────────────────────────
const ChatContainer = ({ userId, onUserMessage }) => {
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [selectedDayDetails, setSelectedDayDetails] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingTrips, setLoadingTrips] = useState(false);
  const [tripsLoaded, setTripsLoaded] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const now = () => new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

  // Load trips for this user
  useEffect(() => {
    if (!userId) return;
    setLoadingTrips(true);
    chatbotService.listTrips(userId)
      .then(res => {
        setTrips(res.data.trips || []);
        setTripsLoaded(true);
      })
      .catch(err => {
        console.error('listTrips error:', err);
        setTripsLoaded(true);
      })
      .finally(() => setLoadingTrips(false));
  }, [userId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Select a trip → fetch greeting
  const handleSelectTrip = useCallback(async (trip) => {
    setSelectedTrip(trip);
    setSelectedDayDetails([]);
    setMessages([]);
    setError('');
    setLoading(true);
    try {
      const res = await chatbotService.getTrip(trip.tripId);
      const greeting = res.data.greeting ||
        `Xin chào! Bạn đã chọn chuyến đi tới **${trip.destination}**. Tôi có thể giúp gì cho bạn?`;
      setMessages([{ id: 1, text: greeting, sender: 'bot', time: now() }]);
      if (res.data.day_details) {
        setSelectedDayDetails(res.data.day_details);
      }
      if (onUserMessage) onUserMessage();
    } catch (err) {
      setMessages([{
        id: 1,
        text: `Đã chọn chuyến đi **${trip.destination}**. Bạn muốn tôi hỗ trợ gì?`,
        sender: 'bot', time: now()
      }]);
    } finally {
      setLoading(false);
    }
    setTimeout(() => inputRef.current?.focus(), 300);
  }, [onUserMessage]);

  const addMessage = (text, sender, extras = {}) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      text, sender, time: now(), ...extras
    }]);
  };

  const handleSend = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput('');
    setError('');
    if (onUserMessage) onUserMessage();

    addMessage(msg, 'user');
    setLoading(true);

    try {
      const res = await chatbotService.sendMessage(msg, userId, selectedTrip?.tripId || '');
      const data = res.data;
      addMessage(data.response, 'bot', {
        images: data.images || [],
        url: data.url || '',
      });
    } catch (err) {
      const errMsg = err.response?.data?.error || err.message || 'Lỗi kết nối tới server.';
      setError(errMsg);
      addMessage('Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại! 🙏', 'bot');
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleClear = async () => {
    if (!userId) return;
    try { await chatbotService.clearMemory(userId); } catch {}
    setMessages([]);
    setSelectedTrip(null);
  };

  // ── Render ──
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '260px 1fr',
      height: '100%',
      background: 'var(--bg-sidebar)',
      borderRadius: 'var(--card-radius)',
      boxShadow: 'var(--shadow-premium)',
      border: '1px solid var(--border-light)',
      overflow: 'hidden',
    }}>
      {/* ── Left Sidebar: trip list ── */}
      <div style={{
        borderRight: '1px solid var(--border-light)',
        display: 'flex', flexDirection: 'column',
        background: 'var(--bg-sidebar)', overflow: 'hidden'
      }}>
        <div style={{ padding: '20px 16px 12px', borderBottom: '1px solid var(--border-light)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <FiMessageSquare size={16} style={{ color: 'var(--primary)' }} />
            <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
              Kế hoạch của bạn
            </span>
          </div>
          <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Chọn chuyến đi để bắt đầu tư vấn
          </p>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
          {selectedTrip ? (
            <div>
              <button 
                onClick={() => setSelectedTrip(null)}
                style={{ 
                  background: 'none', border: 'none', color: 'var(--primary)', 
                  cursor: 'pointer', fontSize: '0.85rem', marginBottom: '12px',
                  display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600,
                  padding: 0
                }}
              >
                ← Quay lại danh sách
              </button>
              <TripCard
                trip={selectedTrip}
                isSelected={true}
                onSelect={() => {}}
              />
              <div style={{ marginTop: '16px', fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '0 4px' }}>
                <div style={{ marginBottom: '8px' }}><strong>Điểm đến:</strong> {selectedTrip.destination}</div>
                <div style={{ marginBottom: '8px' }}><strong>Ngân sách:</strong> {Number(selectedTrip.totalBudget || 0).toLocaleString('vi-VN')} ₫</div>
                <div style={{ marginBottom: '8px' }}><strong>Trạng thái:</strong> {selectedTrip.status || 'PLANNING'}</div>
              </div>
              
              {selectedDayDetails && selectedDayDetails.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                  <h4 style={{ color: 'var(--primary)', marginBottom: '10px', fontSize: '0.9rem' }}>Lịch trình chi tiết</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {selectedDayDetails.map(day => (
                      <div key={day.dayNumber} style={{ 
                        background: 'var(--bg-main)', 
                        padding: '10px', 
                        borderRadius: '8px',
                        border: '1px solid var(--border-light)' 
                      }}>
                        <div style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '8px', color: 'var(--text-primary)' }}>Ngày {day.dayNumber}: {new Date(day.date).toLocaleDateString('vi-VN')}</div>
                        <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {(day.dayActs || []).map((act, i) => (
                            <li key={i}>
                              <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{act.name || act.type}</span>
                              {act.cost > 0 && <span> - {Number(act.cost).toLocaleString('vi-VN')}₫</span>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : loadingTrips ? (
            <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              <FiRefreshCw size={18} style={{ animation: 'spin 1s linear infinite', display: 'block', margin: '0 auto 8px' }} />
              Đang tải...
            </div>
          ) : trips.length === 0 && tripsLoaded ? (
            <div style={{ textAlign: 'center', padding: '30px 12px', color: 'var(--text-muted)', fontSize: '0.82rem', lineHeight: 1.6 }}>
              <FiMapPin size={24} style={{ color: 'var(--border-light)', display: 'block', margin: '0 auto 10px' }} />
              Bạn chưa có kế hoạch du lịch nào.<br />
              Hãy tạo chuyến đi đầu tiên!
            </div>
          ) : (
            trips.map(t => (
              <TripCard
                key={t.tripId}
                trip={t}
                isSelected={false}
                onSelect={handleSelectTrip}
              />
            ))
          )}
        </div>

        {/* Clear button */}
        {messages.length > 0 && (
          <div style={{ padding: '12px', borderTop: '1px solid var(--border-light)' }}>
            <button onClick={handleClear} style={{
              width: '100%', padding: '8px', border: '1px solid var(--border-light)',
              borderRadius: 8, background: 'transparent', cursor: 'pointer',
              color: 'var(--text-muted)', fontSize: '0.8rem', display: 'flex',
              alignItems: 'center', justifyContent: 'center', gap: 6,
              transition: 'all 0.2s'
            }}
              onMouseEnter={e => e.currentTarget.style.color = '#ef4444'}
              onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
            >
              <FiTrash2 size={13} /> Xoá hội thoại
            </button>
          </div>
        )}
      </div>

      {/* ── Right: Chat area ── */}
      <div style={{ display: 'flex', flexDirection: 'column', background: 'var(--bg-main)', minWidth: 0 }}>

        {/* Header */}
        <div style={{
          padding: '16px 24px', borderBottom: '1px solid var(--border-light)',
          display: 'flex', alignItems: 'center', gap: 12,
          background: 'var(--bg-sidebar)'
        }}>
          <BotAvatar />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)' }}>
              TrapBot · AI Travel Advisor
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981' }} />
              {selectedTrip
                ? `Đang tư vấn: ${selectedTrip.destination}`
                : 'Chọn một chuyến đi để bắt đầu'}
            </div>
          </div>
          <FiZap size={16} style={{ color: 'var(--primary)', opacity: 0.7 }} />
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {/* Empty state */}
          {messages.length === 0 && !loading && (
            <div style={{ textAlign: 'center', paddingTop: '60px' }}>
              <div style={{ fontSize: '3rem', marginBottom: 16 }}>🌏</div>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: 8 }}>
                Chào mừng tới TrapBot
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: 320, margin: '0 auto 32px' }}>
                Chọn một kế hoạch du lịch bên trái hoặc hỏi tôi bất kỳ điều gì về hành trình của bạn.
              </p>
              {/* Quick action chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                {QUICK_ACTIONS.map(q => (
                  <button key={q} onClick={() => handleSend(q)} style={{
                    padding: '8px 16px', borderRadius: 20,
                    border: '1px solid var(--primary)', background: 'var(--primary-light)',
                    color: 'var(--primary)', fontSize: '0.82rem', cursor: 'pointer',
                    transition: 'all 0.2s', fontWeight: 500
                  }}
                    onMouseEnter={e => { e.currentTarget.style.background = 'var(--primary)'; e.currentTarget.style.color = '#fff'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'var(--primary-light)'; e.currentTarget.style.color = 'var(--primary)'; }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map(m => <MessageBubble key={m.id} msg={m} />)}
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Error */}
        {error && (
          <div style={{ margin: '0 24px 8px', padding: '10px 14px', background: 'rgba(239,68,68,0.1)',
                        border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8,
                        fontSize: '0.82rem', color: '#ef4444' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Quick action chips (when chatting) */}
        {messages.length > 0 && !loading && (
          <div style={{ padding: '0 24px 8px', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {QUICK_ACTIONS.slice(0, 2).map(q => (
              <button key={q} onClick={() => handleSend(q)} style={{
                padding: '5px 12px', borderRadius: 14,
                border: '1px solid var(--border-light)',
                background: 'var(--bg-sidebar)', color: 'var(--text-secondary)',
                fontSize: '0.78rem', cursor: 'pointer', transition: 'all 0.2s'
              }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--primary)'; e.currentTarget.style.color = 'var(--primary)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-light)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-light)', background: 'var(--bg-sidebar)' }}>
          <div style={{
            display: 'flex', gap: 10, alignItems: 'flex-end',
            background: 'var(--bg-main)', borderRadius: 12,
            border: '1px solid var(--border-light)', padding: '6px 8px 6px 16px',
            boxShadow: 'var(--shadow-sm)', transition: 'border-color 0.2s',
          }}
            onFocusCapture={e => e.currentTarget.style.borderColor = 'var(--primary)'}
            onBlurCapture={e => e.currentTarget.style.borderColor = 'var(--border-light)'}
          >
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={e => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px';
              }}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
              placeholder={selectedTrip
                ? `Hỏi về chuyến đi ${selectedTrip.destination}...`
                : 'Hỏi TrapBot về kế hoạch du lịch...'}
              disabled={loading}
              style={{
                flex: 1, border: 'none', outline: 'none', resize: 'none',
                background: 'transparent', color: 'var(--text-primary)',
                fontSize: '0.93rem', lineHeight: 1.5, maxHeight: 140,
                fontFamily: 'inherit', padding: '8px 0',
              }}
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              style={{
                width: 40, height: 40, borderRadius: 10, border: 'none',
                background: loading || !input.trim() ? 'var(--border-light)' : 'var(--primary)',
                color: loading || !input.trim() ? 'var(--text-muted)' : '#fff',
                cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0, transition: 'all 0.2s',
                transform: loading || !input.trim() ? 'none' : undefined,
              }}
            >
              {loading
                ? <FiRefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                : <FiSend size={16} />}
            </button>
          </div>
          <div style={{ fontSize: '0.71rem', color: 'var(--text-muted)', marginTop: 6, textAlign: 'center' }}>
            Enter để gửi · Shift+Enter xuống dòng
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
          40%            { transform: scale(1);   opacity: 1; }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ChatContainer;
