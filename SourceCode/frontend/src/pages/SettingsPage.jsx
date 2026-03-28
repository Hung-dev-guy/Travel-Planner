import React from 'react';

const SettingsPage = () => {
  return (
    <div className="settings-page" style={{ maxWidth: '600px' }}>
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', color: 'var(--primary)' }}>Account Settings</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manage your profile, notifications, and integration preferences.</p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
        <section className="card-premium">
            <h3 style={{ marginBottom: '20px' }}>Profile Information</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Full Name</label>
                    <input type="text" className="input-field" defaultValue="John Doe" />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Email Address</label>
                    <input type="email" className="input-field" defaultValue="john@example.com" />
                </div>
                <button className="btn-premium btn-primary" style={{ width: 'fit-content' }}>Save Changes</button>
            </div>
        </section>

        <section className="card-premium">
            <h3 style={{ marginBottom: '20px' }}>Preferences</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <div style={{ fontWeight: 600 }}>Enable AI Suggestions</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Get personalized travel tips via AI.</div>
                    </div>
                    <div style={{ width: '40px', height: '20px', background: 'var(--primary)', borderRadius: '10px' }}></div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <div style={{ fontWeight: 600 }}>Email Notifications</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Receive updates about your trip status.</div>
                    </div>
                    <div style={{ width: '40px', height: '20px', background: 'var(--border-light)', borderRadius: '10px' }}></div>
                </div>
            </div>
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;
