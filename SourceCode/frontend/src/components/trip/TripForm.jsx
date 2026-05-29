import React from 'react';
import { FiMapPin, FiCalendar, FiUsers, FiDollarSign } from 'react-icons/fi';

/**
 * TripForm — controlled form collecting core trip parameters.
 *
 * Props:
 *   formData  { startingLocation, destination, startDate, endDate, groupSize, budget }
 *   onChange  (field, value) => void
 *   onSubmit  (e) => void
 *   loading   boolean
 */
const TripForm = ({ formData = {}, onChange, onSubmit, loading }) => {
  const { startingLocation = '', destination = '', startDate = '', endDate = '', groupSize = 2, budget = 2000000 } = formData;

  const field = (key) => ({
    value: formData[key] ?? '',
    onChange: (e) => onChange?.(key, e.target.value),
  });

  return (
    <div className="card-premium">
      <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-primary)' }}>
        <FiMapPin className="text-secondary" /> Plan Your Journey
      </h3>

      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

        {/* Row 1: Starting Location + Destination */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              📍 Starting Location
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Hà Nội, Hồ Chí Minh…"
              required
              {...field('startingLocation')}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              🎯 Destination
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Quảng Ninh, Đà Nẵng, Hội An…"
              required
              {...field('destination')}
            />
          </div>
        </div>

        {/* Row 2: Dates */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiCalendar style={{ verticalAlign: 'middle', marginRight: 4 }} /> Start Date
            </label>
            <input
              type="date"
              className="input-field"
              required
              {...field('startDate')}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiCalendar style={{ verticalAlign: 'middle', marginRight: 4 }} /> End Date
            </label>
            <input
              type="date"
              className="input-field"
              required
              {...field('endDate')}
            />
          </div>
        </div>

        {/* Row 3: Group size + Budget */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiUsers style={{ verticalAlign: 'middle', marginRight: 4 }} /> Group Size
            </label>
            <input
              type="number"
              min={1}
              max={20}
              className="input-field"
              placeholder="2"
              {...field('groupSize')}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiDollarSign style={{ verticalAlign: 'middle', marginRight: 4 }} /> Total Budget (VNĐ)
            </label>
            <input
              type="number"
              min={100000}
              step={100000}
              className="input-field"
              placeholder="2000000"
              {...field('budget')}
            />
          </div>
        </div>

        {/* Row 4: Description (optional) */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
            ✍️ Describe your ideal trip <span style={{ color: 'var(--text-secondary)' }}>(optional)</span>
          </label>
          <textarea
            className="input-field"
            rows={3}
            placeholder="e.g. I want a relaxing trip near the sea with great seafood and scenic views…"
            style={{ resize: 'vertical', fontFamily: 'inherit' }}
            {...field('userDesInput')}
          />
        </div>

        <button
          type="submit"
          className="btn-premium btn-primary"
          style={{ width: '100%', fontSize: '1rem', padding: '14px', position: 'relative' }}
          disabled={loading}
        >
          {loading ? (
            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
              <span className="spinner" />  Generating your trip plan… (this takes ~30 s)
            </span>
          ) : '✨ Generate Trip Plan'}
        </button>
      </form>
    </div>
  );
};

export default TripForm;
