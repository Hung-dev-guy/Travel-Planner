import React from 'react';
import { FiHelpCircle } from 'react-icons/fi';
import TripForm from '../../components/trip/TripForm';
import TravelPreferenceInput from '../../components/trip/TravelPreferenceInput';

const TripPlannerPage = () => {
  return (
    <div className="trip-planner-page" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '8px', color: 'var(--primary)' }}>Create Your Next Adventure</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
          Tell us where you want to go and what you love, and we'll handle the rest.
        </p>
      </header>
      
      <TripForm />
      <TravelPreferenceInput />
      
      <div style={{ marginTop: '40px', padding: '20px', background: 'var(--primary)', borderRadius: 'var(--card-radius)', color: 'white', display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ fontSize: '2rem', display: 'flex', alignItems: 'center' }}>
            <FiHelpCircle />
          </div>
          <div>
              <h4 style={{ margin: 0 }}>Pro Tip:</h4>
              <p style={{ margin: '4px 0 0 0', opacity: 0.9 }}>Connect your calendar to sync trips automatically.</p>
          </div>
      </div>
    </div>
  );
};

export default TripPlannerPage;
