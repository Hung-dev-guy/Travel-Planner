import React from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiMapPin } from 'react-icons/fi';

const fmt = (n) => Number(n || 0).toLocaleString('vi-VN');

const itemIcon = (type) => {
  const map = { activity: '🎯', meal: '🍽️', accommodation: '🏨', transportation: '🚌', transport: '🚌' };
  return map[type] || '•';
};

const typeBadgeColor = (type) => {
  const map = {
    activity:      { bg: 'rgba(16,185,129,0.12)', color: '#10b981' },
    meal:          { bg: 'rgba(245,158,11,0.12)',  color: '#f59e0b' },
    accommodation: { bg: 'rgba(139,92,246,0.12)',  color: '#8b5cf6' },
    transportation: { bg: 'rgba(59,130,246,0.12)', color: '#3b82f6' },
    transport:      { bg: 'rgba(59,130,246,0.12)', color: '#3b82f6' },
  };
  return map[type] || { bg: 'rgba(100,116,139,0.12)', color: '#64748b' };
};

const TripDayDetailPage = () => {
  const { dayId }  = useParams();
  const navigate   = useNavigate();
  const location   = useLocation();

  // Prefer real day data from router state; fall back to placeholder
  const dayData     = location.state?.dayData;
  const tripOverview = location.state?.tripOverview;

  // ── Fallback placeholder ────────────────────────────────────────────────────
  if (!dayData) {
    return (
      <div style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 16 }}>Day {dayId} details not found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
          Navigate here from the trip plan page to see real schedule data.
        </p>
        <button className="btn-premium btn-primary" onClick={() => navigate('/trip-plan')}>
          ← Back to Itinerary
        </button>
      </div>
    );
  }

  const { day, date, title, items = [], day_summary = {} } = dayData;

  return (
    <div className="content" style={{ paddingBottom: '60px' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>

        {/* Back button */}
        <button
          onClick={() => navigate('/trip-plan', { state: location.state })}
          style={{
            marginBottom: 24,
            background: 'transparent',
            border: '1px solid var(--border-light)',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '8px 16px',
            borderRadius: 8,
            fontSize: '0.875rem',
          }}
        >
          <FiArrowLeft /> Back to Itinerary
        </button>

        {/* Header */}
        <header style={{ marginBottom: 32 }}>
          <div style={{ display: 'inline-block', background: 'var(--primary)', color: '#fff', padding: '4px 16px', borderRadius: 8, fontSize: '0.875rem', marginBottom: 12, fontWeight: 600 }}>
            Day {day} · {date}
          </div>
          <h1 style={{ fontSize: '2rem', color: 'var(--text-primary)', marginBottom: 8 }}>{title}</h1>
          {tripOverview && (
            <p style={{ color: 'var(--text-secondary)' }}>
              📍 {tripOverview.destination} · {tripOverview.group_size} {Number(tripOverview.group_size) === 1 ? 'person' : 'people'}
            </p>
          )}
        </header>

        {/* Day summary bar */}
        <div style={{
          display: 'flex',
          gap: 16,
          flexWrap: 'wrap',
          marginBottom: 28,
          padding: '14px 18px',
          background: 'rgba(16,185,129,0.08)',
          border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: 12,
          fontSize: '0.875rem',
        }}>
          <span>💰 <strong>{fmt(day_summary.total_cost)} ₫</strong></span>
          <span>🎯 <strong>{day_summary.activities_count}</strong> activities</span>
          <span>🍽️ <strong>{day_summary.meals_count}</strong> meals</span>
          <span>🕐 <strong>{day_summary.travel_time_hours}h</strong> travel</span>
          <span>⚡ <strong style={{ textTransform: 'capitalize' }}>{day_summary.energy_level}</strong> energy</span>
        </div>

        {/* Schedule items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {items.map((item, idx) => {
            const badge = typeBadgeColor(item.type);
            return (
              <div
                key={idx}
                className="card-premium"
                style={{ display: 'flex', gap: 20, alignItems: 'flex-start' }}
              >
                {/* Time column */}
                <div style={{ minWidth: 90, textAlign: 'center', flexShrink: 0 }}>
                  <div style={{ fontSize: '1.5rem' }}>{itemIcon(item.type)}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 700, marginTop: 4 }}>
                    {item.time_start}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                    → {item.time_end}
                  </div>
                </div>

                {/* Content */}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8, marginBottom: 6 }}>
                    <div>
                      <h3 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.05rem' }}>{item.name}</h3>
                      <span style={{
                        display: 'inline-block',
                        marginTop: 4,
                        padding: '2px 10px',
                        borderRadius: 10,
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        background: badge.bg,
                        color: badge.color,
                      }}>
                        {item.type}
                      </span>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 700, color: 'var(--primary)', fontSize: '1rem' }}>
                        {fmt(item.cost)} ₫
                      </div>
                      {item.duration_minutes > 0 && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 4, justifyContent: 'flex-end', marginTop: 2 }}>
                          <FiClock /> {Math.round(item.duration_minutes / 60 * 10) / 10}h
                        </div>
                      )}
                    </div>
                  </div>

                  {item.location && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 8 }}>
                      <FiMapPin /> {item.location}
                    </div>
                  )}

                  {item.description && (
                    <p style={{ margin: '8px 0 0', fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {item.description}
                    </p>
                  )}

                  {item.notes && (
                    <div style={{
                      marginTop: 10,
                      padding: '10px 14px',
                      background: 'rgba(16,185,129,0.08)',
                      borderRadius: 8,
                      borderLeft: '4px solid var(--primary)',
                      fontSize: '0.85rem',
                      color: 'var(--text-primary)',
                    }}>
                      <strong>💡 Note:</strong> {item.notes}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TripDayDetailPage;
