import React from 'react';

const TravelPreferenceInput = () => {
  const preferences = ['Budget', 'Balanced', 'Luxury', 'Adventure', 'Family', 'Solo'];

  return (
    <div className="card-premium" style={{ marginTop: '24px' }}>
      <label style={{ display: 'block', marginBottom: '16px', fontWeight: 600 }}>What's your travel style?</label>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
        {preferences.map((pref) => (
          <div
            key={pref}
            style={{
              padding: '8px 16px',
              borderRadius: '20px',
              border: '1px solid var(--border-light)',
              cursor: 'pointer',
              fontSize: '0.9rem',
              transition: 'all 0.2s',
              background: 'white'
            }}
            onMouseOver={(e) => {
                e.currentTarget.style.borderColor = 'var(--primary)';
                e.currentTarget.style.color = 'var(--primary)';
            }}
            onMouseOut={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-light)';
                e.currentTarget.style.color = 'inherit';
            }}
          >
            {pref}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TravelPreferenceInput;
