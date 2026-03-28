import React from 'react';
import SearchResultList from '../components/search/SearchResultList';

const SearchPage = () => {
  return (
    <div className="search-page">
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', color: 'var(--primary)' }}>Discover Destinations</h1>
        <div style={{ position: 'relative', marginTop: '20px' }}>
          <input 
            type="text" 
            className="input-field" 
            placeholder="Search flights, hotels, or countries..." 
            style={{ paddingLeft: '48px', height: '56px', fontSize: '1.1rem', boxShadow: 'var(--shadow-md)' }}
          />
          <span style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', fontSize: '1.4rem' }}>🔍</span>
        </div>
      </header>
      
      <div style={{ display: 'flex', gap: '12px', marginBottom: '30px' }}>
          {['All', 'Flights', 'Hotels', 'Activities', 'Rentals'].map(f => (
              <button key={f} className="btn-premium btn-secondary" style={{ padding: '8px 20px' }}>{f}</button>
          ))}
      </div>

      <SearchResultList />
    </div>
  );
};

export default SearchPage;
