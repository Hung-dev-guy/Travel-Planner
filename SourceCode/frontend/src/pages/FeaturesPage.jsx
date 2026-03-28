import React from 'react';
import { FiCpu, FiMap, FiPieChart } from 'react-icons/fi';

const FeaturesPage = () => {
  const features = [
    {
      title: 'AI Trip Planner',
      description: 'Our advanced AI analyzes your preferences to create a perfectly balanced itinerary in seconds.',
      icon: <FiCpu />,
      color: 'var(--primary)'
    },
    {
      title: 'Customizable Routes',
      description: 'Add, remove, or rearrange activities with our intuitive drag-and-drop interface.',
      icon: <FiMap />,
      color: 'var(--secondary)'
    },
    {
      title: 'Budget Optimizer',
      description: 'Keep track of your spending with real-time price estimation and cost-saving tips.',
      icon: <FiPieChart />,
      color: 'var(--accent)'
    },
    {
      title: 'Interactive Travel Maps',
      description: 'Visualize your journey with our integrated mapping system and offline support.',
      icon: '🗺️',
      color: '#10b981'
    }
  ];

  return (
    <div className="features-page" style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '60px' }}>
        <h1 style={{ 
          fontSize: '3.5rem', 
          marginBottom: '16px', 
          background: 'linear-gradient(to right, var(--primary), var(--secondary))', 
          WebkitBackgroundClip: 'text', 
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          color: 'transparent',
          lineHeight: '1.2',
          paddingBottom: '10px'
        }}>
          Elevate Your Travel Experience
        </h1>
        <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '700px', margin: '0 auto' }}>
          Discover the powerful features that make Traplanner the only companion you need for your next adventure.
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
        {features.map((feature, index) => (
          <div key={index} className="card-premium" style={{ borderTop: `4px solid ${feature.color}` }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '20px' }}>{feature.icon}</div>
            <h3 style={{ marginBottom: '12px' }}>{feature.title}</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>{feature.description}</p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '80px', textAlign: 'center', padding: '60px', background: 'white', borderRadius: 'var(--card-radius)', boxShadow: 'var(--shadow-premium)' }}>
          <h2 style={{ marginBottom: '20px', color: 'var(--primary)' }}>Ready to start planning?</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '30px' }}>Join thousands of travelers who trust Traplanner for their journeys.</p>
          <button className="btn-premium btn-primary" style={{ padding: '16px 40px', fontSize: '1.1rem' }}>Create Your Free Account</button>
      </div>
    </div>
  );
};

export default FeaturesPage;
