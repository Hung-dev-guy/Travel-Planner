import React from 'react';
import { FiGlobe, FiCalendar, FiFlag, FiStar, FiMap, FiSend } from 'react-icons/fi';

const DashboardPage = () => {
  const stats = [
    { label: 'Total Trips', value: '12', icon: <FiGlobe size={24} /> },
    { label: 'Upcoming', value: '2', icon: <FiCalendar size={24} /> },
    { label: 'Countries Visited', value: '8', icon: <FiFlag size={24} /> },
    { label: 'Saved Places', value: '45', icon: <FiStar size={24} /> },
  ];

  return (
    <div className="dashboard-page">
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          Welcome back, Explorer! <FiSend style={{ color: 'var(--primary)', transform: 'rotate(-45deg)' }} />
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>You have 2 trips planned for the next 30 days.</p>
      </header>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
        {stats.map((stat) => (
          <div key={stat.label} className="card-premium" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>{stat.icon}</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary)' }}>{stat.value}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '40px', display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '40px' }}>
          <div className="card-premium">
              <h3 style={{ marginBottom: '20px' }}>Recent Planning Activity</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {[1, 2, 3].map(i => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', paddingBottom: '16px', borderBottom: '1px solid var(--border-light)' }}>
                          <div style={{ width: '48px', height: '48px', background: 'var(--bg-main)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)', fontSize: '1.2rem' }}>
                            <FiMap />
                          </div>
                          <div style={{ flex: 1 }}>
                              <div style={{ fontWeight: 600 }}>Trip to Swiss Alps</div>
                              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Last edited 2 hours ago</div>
                          </div>
                          <button className="btn-premium btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Open</button>
                      </div>
                  ))}
              </div>
          </div>
          
          <div className="card-premium">
              <h3 style={{ marginBottom: '20px' }}>Travel Tips</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                      Did you know? Booking your flights on Tuesdays can save you up to 15% on average.
                  </p>
                  <button className="btn-premium btn-primary" style={{ width: '100%' }}>Explore More Tips</button>
              </div>
          </div>
      </div>
    </div>
  );
};

export default DashboardPage;
