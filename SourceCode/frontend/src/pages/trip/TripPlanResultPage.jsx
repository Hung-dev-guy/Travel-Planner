import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FiShare2, FiArrowLeft, FiCheckCircle, FiAlertCircle, FiXCircle } from 'react-icons/fi';

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

  // Pull result from router state (set by TripPlannerPage after API call)
  const result    = location.state?.result;
  const formData  = location.state?.formData;

  // ── Guard: no data → redirect back ──────────────────────────────────────────
  if (!result) {
    return (
      <div style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 16 }}>No trip data found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
          Please fill in the planner form to generate a trip.
        </p>
        <button className="btn-premium btn-primary" onClick={() => navigate('/')}>← Back to Planner</button>
      </div>
    );
  }

  const { trip_overview: overview, scheduling, validation, status_message } = result;
  const { overall_score = 0, status, category_scores = {}, issues = [], recommendations = [] } = validation || {};

  return (
    <div className="content" style={{ paddingBottom: '60px' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>

        {/* ── Header ── */}
        <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <button
              onClick={() => navigate('/')}
              style={{ marginBottom: 12, background: 'transparent', border: '1px solid var(--border-light)', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 8, fontSize: '0.85rem' }}
            >
              <FiArrowLeft /> Back to Planner
            </button>
            <h1 style={{ fontSize: '2rem', marginBottom: 6, color: 'var(--primary)' }}>
              Your {overview?.total_days}-Day {overview?.destination} Adventure
            </h1>
            <p style={{ color: 'var(--text-secondary)' }}>
              {overview?.start_date} → {overview?.end_date} · {overview?.group_size} {Number(overview?.group_size) === 1 ? 'person' : 'people'}
            </p>
          </div>
          <button
            className="btn-premium btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 8 }}
            onClick={() => navigator.clipboard?.writeText(window.location.href)}
          >
            Share Plan <FiShare2 />
          </button>
        </header>

        {/* ── Status message ── */}
        <div style={{
          marginBottom: 24,
          padding: '14px 18px',
          borderRadius: 10,
          background: status === 'APPROVED' ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)',
          border: `1px solid ${status === 'APPROVED' ? 'rgba(16,185,129,0.4)' : 'rgba(245,158,11,0.4)'}`,
          color: 'var(--text-primary)',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}>
          {statusIcon(status)} {status_message}
        </div>

        {/* ── Main two-column grid ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 30, alignItems: 'start' }}>

          {/* ── Left: Day cards ── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {(scheduling || []).map((day) => (
              <Link
                key={day.day}
                to={`/trip-plan/day/${day.day}`}
                state={{ dayData: day, tripOverview: overview }}
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
                    <span>🎯 {day.day_summary?.activities_count} activities</span>
                    <span>🍽️ {day.day_summary?.meals_count} meals</span>
                    <span style={{ color: 'var(--primary)', fontWeight: 600 }}>View full schedule →</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* ── Right: Sidebar ── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {/* Budget card */}
            <div className="card-premium">
              <h3 style={{ marginBottom: 16, color: 'var(--text-primary)' }}>💰 Budget Summary</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Total Budget</span>
                  <span style={{ fontWeight: 600 }}>{fmt(overview?.travel_budget)} ₫</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Estimated Cost</span>
                  <span style={{ fontWeight: 600 }}>{fmt(overview?.total_estimated_cost)} ₫</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Per Person</span>
                  <span style={{ fontWeight: 600 }}>
                    {fmt(Math.round((overview?.total_estimated_cost || 0) / Math.max(overview?.group_size || 1, 1)))} ₫
                  </span>
                </div>
                {/* Utilization bar */}
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Budget used</span>
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
              <h3 style={{ marginBottom: 16, color: 'var(--text-primary)' }}>📊 Plan Score</h3>
              {/* Big score */}
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <div style={{ fontSize: '3rem', fontWeight: 800, color: scoreColor(overall_score), lineHeight: 1 }}>
                  {Math.round(overall_score)}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 4 }}>out of 100</div>
                <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontSize: '0.85rem', fontWeight: 600 }}>
                  {statusIcon(status)} {status?.replace('_', ' ')}
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
                <h3 style={{ marginBottom: 12, color: 'var(--text-primary)' }}>🌟 Highlights</h3>
                {overview.highlights.map((h, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    <span>•</span><span>{h}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div className="card-premium">
                <h3 style={{ marginBottom: 12, color: 'var(--text-primary)' }}>💡 Suggestions</h3>
                {recommendations.slice(0, 3).map((r, i) => (
                  <div key={i} style={{ marginBottom: 10, fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: 8, borderLeft: '3px solid var(--primary)' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>[{r.priority}]</strong> {r.suggestion}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripPlanResultPage;
