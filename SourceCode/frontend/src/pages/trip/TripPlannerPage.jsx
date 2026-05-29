import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiHelpCircle, FiAlertCircle } from 'react-icons/fi';
import TripForm from '../../components/trip/TripForm';
import TravelPreferenceInput from '../../components/trip/TravelPreferenceInput';
import tripService from '../../services/tripService';

const TripPlannerPage = () => {
  const navigate = useNavigate();

  // ── Form state ─────────────────────────────────────────────────────────────
  const [formData, setFormData] = useState({
    destination:  '',
    startDate:    '',
    endDate:      '',
    groupSize:    2,
    budget:       2_000_000,
    userDesInput: '',
  });

  // ── Preference state ───────────────────────────────────────────────────────
  const [travelStyle,    setTravelStyle]    = useState(['nature', 'cultural']);
  const [travelPace,     setTravelPace]     = useState('moderate');
  const [companionType,  setCompanionType]  = useState('Couples');

  // ── UI state ───────────────────────────────────────────────────────────────
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  const handleFieldChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Basic validation
    if (!formData.destination.trim()) { setError('Please enter a destination.'); return; }
    if (!formData.startDate)          { setError('Please choose a start date.'); return; }
    if (!formData.endDate)            { setError('Please choose an end date.');   return; }
    if (formData.endDate < formData.startDate) {
      setError('End date must be after start date.');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        user_des_input:      formData.userDesInput || `Trip to ${formData.destination}`,
        destination:         formData.destination.trim(),
        start_date:          formData.startDate,
        end_date:            formData.endDate,
        group_size:          Number(formData.groupSize) || 2,
        budget:              Number(formData.budget)    || 2_000_000,
        travel_style:        travelStyle,
        travel_pace:         travelPace,
        companion_type:      companionType,
        accommodation_style: 'comfortable',
        health_limitations:  [],
      };

      const { data } = await tripService.generatePlan(payload);
      // Navigate to result page, passing the full result as router state
      navigate('/trip-plan', { state: { result: data, formData } });

    } catch (err) {
      console.error('Pipeline error:', err);
      const msg = err.response?.data?.error
        || (err.code === 'ECONNABORTED' ? 'Request timed out — the server may still be starting. Please try again.' : '')
        || 'Could not connect to the server. Make sure the Django backend is running on port 5000.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="trip-planner-page" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '8px', color: 'var(--primary)' }}>
          Create Your Next Adventure
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
          Tell us where you want to go and what you love, and our AI will handle the rest.
        </p>
      </header>

      {/* Error banner */}
      {error && (
        <div style={{
          marginBottom: '20px',
          padding: '14px 18px',
          background: 'rgba(239,68,68,0.1)',
          border: '1px solid rgba(239,68,68,0.4)',
          borderRadius: '10px',
          color: '#ef4444',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '10px',
          fontSize: '0.9rem',
        }}>
          <FiAlertCircle style={{ marginTop: 2, flexShrink: 0 }} />
          {error}
        </div>
      )}

      <TripForm
        formData={formData}
        onChange={handleFieldChange}
        onSubmit={handleSubmit}
        loading={loading}
      />

      <TravelPreferenceInput
        selected={travelStyle}
        onChange={setTravelStyle}
        pace={travelPace}
        onPaceChange={setTravelPace}
        companion={companionType}
        onCompanionChange={setCompanionType}
      />

      <div style={{
        marginTop: '32px',
        padding: '20px',
        background: 'var(--primary)',
        borderRadius: 'var(--card-radius)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
      }}>
        <div style={{ fontSize: '2rem' }}><FiHelpCircle /></div>
        <div>
          <h4 style={{ margin: 0 }}>Pro Tip:</h4>
          <p style={{ margin: '4px 0 0 0', opacity: 0.9 }}>
            The AI planner works best for Vietnamese destinations — try Quảng Ninh, Đà Nẵng, or Hội An!
          </p>
        </div>
      </div>
    </div>
  );
};

export default TripPlannerPage;
