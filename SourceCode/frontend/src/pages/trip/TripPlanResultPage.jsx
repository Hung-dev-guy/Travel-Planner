import React from 'react';
import { Link } from 'react-router-dom';
import { FiShare2 } from 'react-icons/fi';
import tokyoNight from '../../assets/images/tokyo_night.jpg';

const TripPlanResultPage = () => {
  const itinerary = [
    { day: 1, title: 'Arrival & City Exploration', activities: ['Arrive at Tokyo Narita', 'Check-in at Shinjuku hotel', 'Evening walk in Memory Lane (Omoide Yokocho)'] },
    { day: 2, title: 'Cultural Immersion', activities: ['Senso-ji Temple visits', 'Asakusa market tour', 'Ueno Park museum exploration'] },
    { day: 3, title: 'Modern Wonders', activities: ['Shibuya Crossing', 'Harajuku fashion street', 'Meiji Jingu Shrine'] },
  ];

  return (
    <div className="content" style={{ 
      minHeight: '100vh',
      backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url(${tokyoNight})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed',
      paddingBottom: '60px'
    }}>
      <div className="trip-plan-result" style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>
        <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h1 style={{ fontSize: '2.5rem', color: '#fff', marginBottom: '8px', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>Your 5-Day Tokyo Adventure</h1>
            <p style={{ color: 'rgba(255, 255, 255, 0.9)' }}>Planned for 2 Adults • Nov 15 - Nov 20</p>
          </div>
          <button className="btn-premium btn-secondary" style={{ marginBottom: '8px', background: 'rgba(255,255,255,0.2)', color: '#fff', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.3)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Share Plan <FiShare2 />
          </button>
        </header>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {itinerary.map((day) => (
              <Link key={day.day} to={`/trip-plan/day/${day.day}`} style={{ textDecoration: 'none' }}>
                <div className="card-premium" style={{ 
                  cursor: 'pointer', 
                  transition: 'all 0.2s',
                  background: 'var(--bg-glass)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid var(--border-light)'
                }} onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--primary)'} onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-light)'}>
                  <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ background: 'var(--primary)', color: 'white', padding: '4px 12px', borderRadius: '8px', fontSize: '0.9rem' }}>Day {day.day}</span>
                    <span style={{ color: 'var(--text-primary)', margin: 0 }}>{day.title}</span>
                  </h2>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {day.activities.map((act, i) => (
                      <div key={i} style={{ display: 'flex', gap: '12px', alignItems: 'center', paddingBottom: '12px', borderBottom: i < day.activities.length - 1 ? '1px solid var(--border-light)' : 'none' }}>
                        <div style={{ width: '8px', height: '8px', background: 'var(--primary)', borderRadius: '50%' }}></div>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>{act}</span>
                      </div>
                    ))}
                    <div style={{ marginTop: '8px', textAlign: 'right', fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 600 }}>
                      View Full Day Schedule →
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="card-premium" style={{ background: 'var(--bg-glass)', backdropFilter: 'blur(10px)' }}>
              <h3 style={{ marginBottom: '20px', color: 'var(--text-primary)' }}>Estimated Budget</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Flights</span>
                  <span style={{ fontWeight: 600 }}>$1,200</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Hotel</span>
                  <span style={{ fontWeight: 600 }}>$850</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Activities</span>
                  <span style={{ fontWeight: 600 }}>$400</span>
                </div>
                <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '2px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', fontSize: '1.1rem' }}>
                  <span style={{ fontWeight: 700 }}>Total</span>
                  <span style={{ fontWeight: 700, color: 'var(--primary)' }}>$2,450</span>
                </div>
              </div>
            </div>

            <div className="card-premium" style={{ background: 'rgba(16, 185, 129, 0.15)', borderColor: 'var(--primary)', backdropFilter: 'blur(10px)' }}>
              <h3 style={{ marginBottom: '12px', color: 'var(--text-primary)' }}>Traplanner AI Tip</h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: '1.6' }}>
                "Since you're visiting in November, be sure to check out the fall foliage in Rikugien Garden. It's stunning this time of year!"
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripPlanResultPage;
