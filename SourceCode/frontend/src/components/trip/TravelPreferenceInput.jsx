import React from 'react';

/**
 * TravelPreferenceInput — controlled travel-style chip selector.
 *
 * Props:
 *   selected  {string[]}              — currently selected styles
 *   onChange  {(styles: string[]) => void} — called whenever selection changes
 */
const STYLE_OPTIONS = [
  { value: 'nature',    label: '🌿 Nature' },
  { value: 'cultural',  label: '🏛️ Cultural' },
  { value: 'adventure', label: '⛰️ Adventure' },
  { value: 'relaxation',label: '🏖️ Relaxation' },
  { value: 'luxury',    label: '💎 Luxury' },
  { value: 'budget',    label: '💰 Budget' },
  { value: 'family',    label: '👨‍👩‍👧 Family' },
  { value: 'solo',      label: '🎒 Solo' },
];

const PACE_OPTIONS = [
  { value: 'thong thả', label: '🐢 Leisurely' },
  { value: 'moderate',  label: '🚶 Moderate' },
  { value: 'fast',      label: '🏃 Fast-paced' },
];

const COMPANION_OPTIONS = [
  { value: 'Couples',   label: '💑 Couples' },
  { value: 'Family',    label: '👨‍👩‍👧 Family' },
  { value: 'Friends',   label: '👯 Friends' },
  { value: 'Solo',      label: '🎒 Solo' },
  { value: 'Group',     label: '👥 Group' },
];

const Chip = ({ label, active, onClick }) => (
  <div
    onClick={onClick}
    style={{
      padding: '8px 16px',
      borderRadius: '20px',
      border: `2px solid ${active ? 'var(--primary)' : 'var(--border-light)'}`,
      background: active ? 'var(--primary)' : 'transparent',
      color: active ? '#fff' : 'var(--text-secondary)',
      cursor: 'pointer',
      fontSize: '0.875rem',
      fontWeight: active ? 600 : 400,
      transition: 'all 0.18s ease',
      userSelect: 'none',
    }}
  >
    {label}
  </div>
);

const TravelPreferenceInput = ({ selected = [], onChange, pace, onPaceChange, companion, onCompanionChange }) => {

  const toggle = (value) => {
    const next = selected.includes(value)
      ? selected.filter(s => s !== value)
      : [...selected, value];
    onChange?.(next);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '24px' }}>
      {/* Travel style */}
      <div className="card-premium">
        <label style={{ display: 'block', marginBottom: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
          🎯 Travel Style <span style={{ color: 'var(--text-secondary)', fontWeight: 400, fontSize: '0.85rem' }}>(pick all that apply)</span>
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {STYLE_OPTIONS.map(opt => (
            <Chip
              key={opt.value}
              label={opt.label}
              active={selected.includes(opt.value)}
              onClick={() => toggle(opt.value)}
            />
          ))}
        </div>
      </div>

      {/* Pace + Companion row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Travel Pace */}
        <div className="card-premium">
          <label style={{ display: 'block', marginBottom: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
            ⏱️ Travel Pace
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {PACE_OPTIONS.map(opt => (
              <Chip
                key={opt.value}
                label={opt.label}
                active={pace === opt.value}
                onClick={() => onPaceChange?.(opt.value)}
              />
            ))}
          </div>
        </div>

        {/* Companion Type */}
        <div className="card-premium">
          <label style={{ display: 'block', marginBottom: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
            👥 Traveling With
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {COMPANION_OPTIONS.map(opt => (
              <Chip
                key={opt.value}
                label={opt.label}
                active={companion === opt.value}
                onClick={() => onCompanionChange?.(opt.value)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TravelPreferenceInput;
