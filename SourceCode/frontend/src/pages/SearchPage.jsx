import React, { useState, useEffect } from 'react';
import SearchResultList from '../components/search/SearchResultList';
import destinationService from '../services/destinationService';
import { FiRefreshCw } from 'react-icons/fi';

const SearchPage = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const filters = [
    { id: 'All', label: 'Tất cả' },
    { id: 'Flights', label: 'Chuyến bay' },
    { id: 'Hotels', label: 'Khách sạn' },
    { id: 'Activities', label: 'Hoạt động' },
    { id: 'Rentals', label: 'Thuê xe' }
  ];

  useEffect(() => {
    const fetchLocations = async () => {
      setLoading(true);
      try {
        const res = await destinationService.getLocations(category, searchQuery);
        setLocations(res.data.results || []);
      } catch (error) {
        console.error("Error fetching locations:", error);
      } finally {
        setLoading(false);
      }
    };
    
    // Add a small debounce for search query
    const timeoutId = setTimeout(() => {
      fetchLocations();
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [category, searchQuery]);

  return (
    <div className="search-page" style={{ maxWidth: 1200, margin: '0 auto' }}>
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', color: 'var(--primary)' }}>Khám phá các Điểm đến</h1>
        <div style={{ position: 'relative', marginTop: '20px' }}>
          <input 
            type="text" 
            className="input-field" 
            placeholder="Tìm kiếm chuyến bay, khách sạn, hoặc quốc gia..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '48px', height: '56px', fontSize: '1.1rem', boxShadow: 'var(--shadow-md)' }}
          />
          <span style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', fontSize: '1.4rem' }}>🔍</span>
        </div>
      </header>
      
      <div style={{ display: 'flex', gap: '12px', marginBottom: '30px', flexWrap: 'wrap' }}>
          {filters.map(f => (
              <button 
                key={f.id} 
                onClick={() => setCategory(f.id)}
                className={category === f.id ? "btn-premium btn-primary" : "btn-premium btn-secondary"} 
                style={{ padding: '8px 20px', transition: 'all 0.2s' }}
              >
                {f.label}
              </button>
          ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          <FiRefreshCw size={32} style={{ animation: 'spin 1s linear infinite', color: 'var(--primary)' }} />
          <p style={{ marginTop: '16px' }}>Đang tải dữ liệu...</p>
          <style>{`@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>
        </div>
      ) : (
        <SearchResultList results={locations} />
      )}
    </div>
  );
};

export default SearchPage;
