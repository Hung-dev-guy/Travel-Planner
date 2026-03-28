import React from 'react';

const DestinationCard = ({ destination }) => {
  return (
    <div className="card-premium" style={{ overflow: 'hidden', padding: 0 }}>
      <div style={{ height: '180px', background: 'var(--border-light)', position: 'relative', overflow: 'hidden' }}>
          {destination.image ? (
              <img 
                src={destination.image} 
                alt={destination.name} 
                style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
              />
          ) : (
              <div style={{ width: '100%', height: '100%', background: 'var(--border-light)' }}></div>
          )}
          <div style={{ position: 'absolute', top: '12px', right: '12px', background: 'rgba(0,0,0,0.6)', padding: '4px 8px', borderRadius: '4px', color: 'white', fontSize: '0.75rem', fontWeight: 600 }}>
              4.8 ★
          </div>
      </div>
      <div style={{ padding: '20px' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem' }}>{destination?.name || 'Beautiful Destination'}</h3>
        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Discover the magic of this amazing place.</p>
        <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 700, color: 'var(--primary)' }}>$450+</span>
            <button className="btn-premium btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>View Details</button>
        </div>
      </div>
    </div>
  );
};

export default DestinationCard;
