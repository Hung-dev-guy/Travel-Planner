import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FiShare2, FiArrowLeft, FiCheckCircle, FiAlertCircle, FiXCircle, FiSave } from 'react-icons/fi';
import tripService from '../../services/tripService';

// ── Helpers ───────────────────────────────────────────────────────────────────

const fmt = (n) => Number(n || 0).toLocaleString('vi-VN');

const itemIcon = (type) => {
  const map = { activity: '🎯', meal: '🍽️', accommodation: '🏨', transportation: '🚌', transport: '🚌' };
  return map[type] || '•';
};

const statusIcon = (status) => {
  if (status === 'APPROVED')          return <FiCheckCircle  color="#10b981" />;
  if (status === 'NEEDS_IMPROVEMENT') return <FiAlertCircle  color="#f59e0b" />;
  return                                     <FiXCircle      color="#ef4444" />;
};

const scoreColor = (s) => s >= 70 ? '#10b981' : s >= 50 ? '#f59e0b' : '#ef4444';

// ── Main Component ─────────────────────────────────────────────────────────────

const TripPlanResultPage = () => {
  const location = useLocation();
  const navigate  = useNavigate();
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [fetchedResult, setFetchedResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showToast, setShowToast] = useState(true);

  // Pull result from router state (set by TripPlannerPage after API call)
  const initialResult = location.state?.result;
  const formData  = location.state?.formData;
  const tripIdToFetch = location.state?.tripId;

  useEffect(() => {
    if (!initialResult && tripIdToFetch) {
      setLoading(true);
      tripService.getTripById(tripIdToFetch)
        .then(res => {
          if (res.data?.success) {
            setFetchedResult(res.data.result);
            setIsSaved(true); // Already saved since it's from DB
          } else {
            setError('Không tìm thấy chuyến đi');
          }
        })
        .catch(err => {
          console.error(err);
          setError('Lỗi khi tải dữ liệu chuyến đi');
        })
        .finally(() => setLoading(false));
    }
  }, [initialResult, tripIdToFetch]);

  const result = initialResult || fetchedResult;

  useEffect(() => {
    if (result?.status_message) {
      setShowToast(true);
      const timer = setTimeout(() => setShowToast(false), 4000);
      return () => clearTimeout(timer);
    }
  }, [result?.status_message]);

  const handleSavePlan = async () => {
    if (!result?.db_schema || isSaving || isSaved) return;
    setIsSaving(true);
    try {
      const response = await tripService.savePlan({
        db_schema: result.db_schema,
        user_id: 'U001'
      });
      if (response.data?.success) {
        setIsSaved(true);
      }
    } catch (err) {
      console.error('Failed to save plan:', err);
      alert('Lưu kế hoạch thất bại. Vui lòng thử lại!');
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40, borderWidth: 4, borderColor: 'var(--primary)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <style>{`@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>
      </div>
    );
  }

  // ── Guard: no data → redirect back ──────────────────────────────────────────
  if (error || (!result && !loading)) {
    return (
      <div style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 16 }}>{error || 'Không tìm thấy dữ liệu chuyến đi'}</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
          Vui lòng điền form để tạo kế hoạch chuyến đi.
        </p>
        <button className="btn-premium btn-primary" onClick={() => navigate('/planner')}>← Quay lại trang lập kế hoạch</button>
      </div>
    );
  }

  const { trip_overview: overview, scheduling: rawScheduling, validation, status_message } = result;
  const { overall_score = 0, status, category_scores = {}, issues = [], recommendations = [] } = validation || {};

  // Lọc trùng lặp các ngày (đề phòng LLM ảo giác trả về 2 ngày giống hệt nhau)
  const scheduling = (rawScheduling || []).filter((day, index, self) =>
    index === self.findIndex((d) => d.day === day.day)
  );

  return (
    <div className="content" style={{ paddingBottom: '60px' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>

        {/* ── Header ── */}
        <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <button
              onClick={() => navigate('/dashboard')}
              style={{ marginBottom: 12, background: 'transparent', border: '1px solid var(--border-light)', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 8, fontSize: '0.85rem' }}
            >
              <FiArrowLeft /> Quay lại Dashboard
            </button>
            <h1 style={{ fontSize: '2rem', marginBottom: 6, color: 'var(--primary)' }}>
              Hành trình {overview?.total_days} ngày khám phá {overview?.destination}
            </h1>
            <p style={{ color: 'var(--text-secondary)' }}>
              {overview?.start_date} → {overview?.end_date} · {overview?.group_size} người
            </p>
          </div>
          
          <div style={{ display: 'flex', gap: 12 }}>
            {result?.db_schema && (
              <button
                className="btn-premium btn-secondary"
                style={{ 
                  display: 'flex', alignItems: 'center', gap: 8,
                  background: isSaved ? 'var(--primary)' : undefined,
                  color: isSaved ? '#fff' : undefined,
                  borderColor: isSaved ? 'var(--primary)' : undefined
                }}
                onClick={handleSavePlan}
                disabled={isSaving || isSaved}
              >
                {isSaving ? 'Đang lưu...' : isSaved ? 'Đã lưu vào Dashboard' : 'Lưu Kế Hoạch'} <FiSave />
              </button>
            )}
            <button
              className="btn-premium btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: 8 }}
              onClick={() => navigator.clipboard?.writeText(window.location.href)}
            >
              Chia sẻ <FiShare2 />
            </button>
          </div>
        </header>

        {/* ── Status message (Push Notification / Toast) ── */}
        {showToast && status_message && (
          <div style={{
            position: 'fixed', top: 30, right: 30, zIndex: 9999,
            padding: '14px 20px', borderRadius: 8, boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
            background: status === 'APPROVED' ? '#10b981' : '#f59e0b',
            color: '#fff', display: 'flex', alignItems: 'center', gap: 10,
            animation: 'toastSlideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
          }}>
            {statusIcon(status)} <span style={{fontWeight: 600, fontSize: '0.95rem'}}>{status_message}</span>
            <style>{`@keyframes toastSlideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`}</style>
          </div>
        )}

        {/* ── Main two-column grid ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 30, alignItems: 'start' }}>

          {/* ── Left: Day cards ── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {(scheduling || []).map((day) => (
              <Link
                key={day.day}
                to={`/trip-plan/day/${day.day}`}
                state={{ ...location.state, result, dayData: day, tripOverview: overview }}
                style={{ textDecoration: 'none' }}
              >
                <div
                  className="card-premium"
                  style={{ cursor: 'pointer', transition: 'border-color 0.2s' }}
                  onMouseOver={e  => e.currentTarget.style.borderColor = 'var(--primary)'}
                  onMouseOut={e   => e.currentTarget.style.borderColor = 'var(--border-light)'}
                >
                  {/* Day header */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span style={{ background: 'var(--primary)', color: '#fff', padding: '3px 12px', borderRadius: 8, fontSize: '0.85rem', fontWeight: 600 }}>
                        Day {day.day}
                      </span>
                      <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{day.title}</span>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{day.date}</span>
                  </div>

                  {/* Items */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {(day.items || []).map((item, i) => (
                      <div
                        key={i}
                        style={{
                          display: 'flex',
                          gap: 12,
                          alignItems: 'flex-start',
                          paddingBottom: i < day.items.length - 1 ? 10 : 0,
                          borderBottom: i < day.items.length - 1 ? '1px solid var(--border-light)' : 'none',
                        }}
                      >
                        <span style={{ fontSize: '1.1rem', width: 24, flexShrink: 0 }}>{itemIcon(item.type)}</span>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 4 }}>
                            <span style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{item.name}</span>
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                              {item.time_start} – {item.time_end}
                            </span>
                          </div>
                          {item.location && (
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>📍 {item.location}</span>
                          )}
                        </div>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary)', flexShrink: 0 }}>
                          {fmt(item.cost)} ₫
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Day summary row */}
                  <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    <span>💰 {fmt(day.day_summary?.total_cost)} ₫</span>
                    <span>🎯 {day.day_summary?.activities_count} hoạt động</span>
                    <span>🍽️ {day.day_summary?.meals_count} bữa ăn</span>
                    <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Xem chi tiết →</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* ── Right: Sidebar ── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {/* Budget card */}
            <div className="card-premium">
              <h3 style={{ marginBottom: 16, color: 'var(--text-primary)' }}>💰 Tóm tắt Ngân sách</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Tổng Ngân sách</span>
                  <span style={{ fontWeight: 600 }}>{fmt(overview?.travel_budget)} ₫</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Chi phí ước tính</span>
                  <span style={{ fontWeight: 600 }}>{fmt(overview?.total_estimated_cost)} ₫</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Mỗi người</span>
                  <span style={{ fontWeight: 600 }}>
                    {fmt(Math.round((overview?.total_estimated_cost || 0) / Math.max(overview?.group_size || 1, 1)))} ₫
                  </span>
                </div>
                {/* Utilization bar */}
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Ngân sách đã dùng</span>
                    <span style={{ fontWeight: 600, color: scoreColor(100 - (overview?.budget_utilization_pct || 0)) }}>
                      {overview?.budget_utilization_pct?.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ height: 6, background: 'var(--border-light)', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${Math.min(overview?.budget_utilization_pct || 0, 100)}%`,
                      background: (overview?.budget_utilization_pct || 0) > 100 ? '#ef4444' : 'var(--primary)',
                      borderRadius: 3,
                      transition: 'width 0.5s ease',
                    }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Validation score card */}
            <div className="card-premium">
              <h3 style={{ marginBottom: 16, color: 'var(--text-primary)' }}>📊 Điểm Kế Hoạch</h3>
              {/* Big score */}
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <div style={{ fontSize: '3rem', fontWeight: 800, color: scoreColor(overall_score), lineHeight: 1 }}>
                  {Math.round(overall_score)}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 4 }}>trên 100</div>
                <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontSize: '0.85rem', fontWeight: 600 }}>
                  {statusIcon(status)} {status === 'APPROVED' ? 'TỐT' : status === 'NEEDS_IMPROVEMENT' ? 'CẦN CẢI THIỆN' : 'CẦN TỐI ƯU'}
                </div>
              </div>
              {/* Category bars */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {Object.entries(category_scores).map(([cat, raw]) => {
                  const maxPts = { budget: 20, time: 15, activity_suitability: 20, accommodation: 15, transport: 10, balance: 10, health: 10 }[cat] || 10;
                  const pct = Math.round((raw / maxPts) * 100);
                  return (
                    <div key={cat}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 3 }}>
                        <span style={{ color: 'var(--text-secondary)' }}>{cat.replace('_', ' ')}</span>
                        <span style={{ fontWeight: 600 }}>{pct}%</span>
                      </div>
                      <div style={{ height: 5, background: 'var(--border-light)', borderRadius: 3, overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${pct}%`, background: scoreColor(pct), borderRadius: 3 }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Highlights */}
            {overview?.highlights?.length > 0 && (
              <div className="card-premium" style={{ background: 'rgba(16,185,129,0.08)', borderColor: 'var(--primary)' }}>
                <h3 style={{ marginBottom: 12, color: 'var(--text-primary)' }}>🌟 Điểm nổi bật</h3>
                {overview.highlights.map((h, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    <span>•</span><span>{h}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Removed Recommendations block to hide internal AI feedback from users */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripPlanResultPage;
