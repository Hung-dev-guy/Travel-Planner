import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft } from 'react-icons/fi';
import omoideImg from '../../assets/images/omoide.jpeg';

const TripDayDetailPage = () => {
  const { dayId } = useParams();
  const navigate = useNavigate();

  // Dummy detailed data
  const dayDetails = {
    '1': {
      title: 'Arrival & City Exploration',
      description: 'Your first day in Tokyo focuses on settling in and experiencing the vibrant atmosphere of Shinjuku.',
      schedule: [
        { time: '14:00', activity: 'Arrive at Tokyo Narita', location: 'Narita Terminal 1', tip: 'Follow signs for the Skyliner or Narita Express.' },
        { time: '16:00', task: 'Check-in at Shinjuku hotel', location: 'Keio Plaza Hotel', tip: 'The hotel offers a free shuttle to Tokyo Disneyland.' },
        { time: '19:00', task: 'Dinner at Omoide Yokocho', location: 'Memory Lane', tip: 'Try the yakitori! It is a tiny alley with a lot of history.' }
      ]
    },
    '2': {
      title: 'Cultural Immersion',
      description: 'Spend your second day diving deep into Japanese history and tradition.',
      schedule: [
        { time: '09:00', activity: 'Visit Senso-ji Temple', location: 'Asakusa', tip: 'Visit early to avoid the biggest crowds.' },
        { time: '11:00', task: 'Street food tour in Nakamise-dori', location: 'Nakamise Street', tip: 'Try the Ningyo-yaki cakes.' },
        { time: '14:00', task: 'Ueno Park & National Museum', location: 'Ueno', tip: 'The museum has the worlds largest collection of Japanese art.' }
      ]
    },
    '3': {
      title: 'Modern Wonders',
      description: 'Explore the modern side of Tokyo, from fashion hubs to the famous Shibuya crossing.',
      schedule: [
        { time: '10:00', activity: 'Meiji Jingu Shrine peaceful walk', location: 'Harajuku', tip: 'Write a wish on an Ema tablet.' },
        { time: '13:00', task: 'Lunch & Fashion in Harajuku', location: 'Takeshita Street', tip: 'The crepes here are legendary!' },
        { time: '17:00', task: 'Shibuya Crossing sunset view', location: 'Shibuya Sky', tip: 'Book tickets for Shibuya Sky in advance.' }
      ]
    }
  };

  const data = dayDetails[dayId] || dayDetails['1'];

  return (
    <div className="content" style={{ 
      minHeight: '100vh',
      backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url(${omoideImg})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed',
      paddingBottom: '60px'
    }}>
      <div className="trip-day-detail" style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>
        <button
          onClick={() => navigate('/trip-plan')}
          style={{ marginBottom: '24px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '8px', backdropFilter: 'blur(10px)' }}
        >
          <FiArrowLeft /> Back to Itinerary
        </button>

        <header style={{ marginBottom: '40px' }}>
          <div style={{ display: 'inline-block', background: 'var(--primary)', color: 'white', padding: '4px 16px', borderRadius: '8px', fontSize: '0.9rem', marginBottom: '16px', fontWeight: 600 }}>
            Day {dayId}
          </div>
          <h1 style={{ fontSize: '2.5rem', color: '#fff', marginBottom: '16px', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>{data.title}</h1>
          <p style={{ fontSize: '1.1rem', color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.6' }}>{data.description}</p>
        </header>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          {data.schedule.map((item, index) => (
            <div key={index} className="card-premium" style={{
              display: 'flex',
              gap: '24px',
              background: 'var(--bg-glass)',
              backdropFilter: 'blur(10px)',
              border: '1px solid var(--border-light)'
            }}>
              <div style={{ minWidth: '80px', fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)' }}>{item.time}</div>
              <div style={{ flex: 1 }}>
                <h3 style={{ marginBottom: '8px' }}>{item.activity || item.task}</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '12px' }}>
                  <span>📍</span> {item.location}
                </div>
                <div style={{ padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', borderLeft: '4px solid var(--primary)', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  <strong>Pro Tip:</strong> {item.tip}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TripDayDetailPage;
