import React from 'react';
import { FiFeather, FiBookOpen, FiCompass, FiCoffee, FiStar, FiDollarSign, FiUsers, FiUser, FiActivity, FiWind, FiHeart, FiSmile, FiTarget, FiClock } from 'react-icons/fi';

/**
 * TravelPreferenceInput — controlled travel-style chip selector.
 *
 * Props:
 *   selected  {string[]}              — currently selected styles
 *   onChange  {(styles: string[]) => void} — called whenever selection changes
 */
const STYLE_OPTIONS = [
  { value: 'nature',    label: <><FiFeather style={{ marginRight: 6, verticalAlign: 'middle' }} /> Thiên nhiên</> },
  { value: 'cultural',  label: <><FiBookOpen style={{ marginRight: 6, verticalAlign: 'middle' }} /> Văn hoá</> },
  { value: 'adventure', label: <><FiCompass style={{ marginRight: 6, verticalAlign: 'middle' }} /> Khám phá</> },
  { value: 'relaxation',label: <><FiCoffee style={{ marginRight: 6, verticalAlign: 'middle' }} /> Thư giãn</> },
  { value: 'luxury',    label: <><FiStar style={{ marginRight: 6, verticalAlign: 'middle' }} /> Sang trọng</> },
  { value: 'budget',    label: <><FiDollarSign style={{ marginRight: 6, verticalAlign: 'middle' }} /> Tiết kiệm</> },
  { value: 'family',    label: <><FiUsers style={{ marginRight: 6, verticalAlign: 'middle' }} /> Gia đình</> },
  { value: 'solo',      label: <><FiUser style={{ marginRight: 6, verticalAlign: 'middle' }} /> Đi một mình</> },
];

const PACE_OPTIONS = [
  { value: 'thong thả', label: <><FiCoffee style={{ marginRight: 6, verticalAlign: 'middle' }} /> Thong thả</> },
  { value: 'moderate',  label: <><FiActivity style={{ marginRight: 6, verticalAlign: 'middle' }} /> Vừa phải</> },
  { value: 'fast',      label: <><FiWind style={{ marginRight: 6, verticalAlign: 'middle' }} /> Nhanh nhẹn</> },
];

const COMPANION_OPTIONS = [
  { value: 'Couples',   label: <><FiHeart style={{ marginRight: 6, verticalAlign: 'middle' }} /> Cặp đôi</> },
  { value: 'Family',    label: <><FiUsers style={{ marginRight: 6, verticalAlign: 'middle' }} /> Gia đình</> },
  { value: 'Friends',   label: <><FiSmile style={{ marginRight: 6, verticalAlign: 'middle' }} /> Bạn bè</> },
  { value: 'Solo',      label: <><FiUser style={{ marginRight: 6, verticalAlign: 'middle' }} /> Đi một mình</> },
  { value: 'Group',     label: <><FiUsers style={{ marginRight: 6, verticalAlign: 'middle' }} /> Nhóm</> },
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
          <FiTarget style={{ verticalAlign: 'middle', marginRight: 4 }} /> Phong cách du lịch <span style={{ color: 'var(--text-secondary)', fontWeight: 400, fontSize: '0.85rem' }}>(chọn tất cả những gì bạn thích)</span>
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
            <FiClock style={{ verticalAlign: 'middle', marginRight: 4 }} /> Nhịp độ chuyến đi
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
            <FiUsers style={{ verticalAlign: 'middle', marginRight: 4 }} /> Đi cùng ai
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
