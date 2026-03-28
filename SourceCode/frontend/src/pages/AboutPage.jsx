import React from 'react';

const AboutPage = () => {
  return (
    <div className="about-page" style={{ maxWidth: '800px', margin: '0 auto', padding: '60px 20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '60px' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '24px', color: 'var(--primary)' }}>Our Mission</h1>
        <div style={{ width: '80px', height: '4px', background: 'var(--primary)', margin: '0 auto 24px auto', borderRadius: '2px' }}></div>
        <p style={{ fontSize: '1.4rem', lineHeight: '1.8', color: 'var(--text-primary)', fontWeight: 500 }}>
          "To make every journey seamless, personalized, and unforgettable through the power of artificial intelligence."
        </p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '60px' }}>
        <section>
          <h2 style={{ marginBottom: '20px', color: 'var(--primary)' }}>Who We Are</h2>
          <p style={{ fontSize: '1.1rem', lineHeight: '1.7', color: 'var(--text-secondary)' }}>
            Traplanner was founded by a group of passionate travelers and tech enthusiasts who believed that planning a trip shouldn't be a chore. We saw a world of fragmented information and endless tabs, and we decided to build a better way.
          </p>
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
            <div className="card-premium">
                <h3 style={{ marginBottom: '16px' }}>Our Vision</h3>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    A world where travel planning is as exciting as the trip itself, and where AI empowers humans to explore the globe with confidence and curiosity.
                </p>
            </div>
            <div className="card-premium">
                <h3 style={{ marginBottom: '16px' }}>Our Values</h3>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    Integrity, Innovation, and Interconnection. We believe in being honest with our users and constantly pushing the boundaries of what's possible.
                </p>
            </div>
        </section>

        <section style={{ textAlign: 'center', marginTop: '40px' }}>
          <h2 style={{ marginBottom: '30px' }}>Meet the Team</h2>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '30px', flexWrap: 'wrap' }}>
            {[1, 2, 3].map(i => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: 'var(--border-light)', margin: '0 auto 16px auto', overflow: 'hidden' }}>
                    {/* Placeholder for team member image */}
                    <div style={{ width: '100%', height: '100%', background: 'var(--primary)', opacity: 0.1, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem' }}>👤</div>
                </div>
                <div style={{ fontWeight: 600 }}>Team Member {i}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Founding Engineer</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default AboutPage;
