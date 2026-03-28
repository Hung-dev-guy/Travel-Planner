import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FiMapPin } from 'react-icons/fi';

const TripForm = () => {
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate generation delay
    setTimeout(() => {
        navigate('/trip-plan');
    }, 500);
  };
  return (
    <div className="card-premium">
      <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <FiMapPin className="text-secondary" /> Plan Your Journey
      </h3>
      <form className="trip-form" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem' }}>Destination</label>
            <input type="text" className="input-field" placeholder="e.g. Paris, France" />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem' }}>Travel Dates</label>
            <input type="date" className="input-field" />
          </div>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem' }}>Traveler Details</label>
          <div style={{ display: 'flex', gap: '12px' }}>
            <input type="number" className="input-field" placeholder="Adults" style={{ flex: 1 }} />
            <input type="number" className="input-field" placeholder="Children" style={{ flex: 1 }} />
          </div>
        </div>
        <button type="submit" className="btn-premium btn-primary" style={{ width: '100%' }}>
          Generate Trip Plan
        </button>
      </form>
    </div>
  );
};

export default TripForm;
