import React from 'react';
import DestinationCard from './DestinationCard';
import ServiceCard from './ServiceCard';

const SearchResultList = ({ results }) => {
  // Dummy results if none provided
  const displayResults = results || [
      { type: 'destination', name: 'Kyoto, Japan', image: '/src/assets/images/kyoto.jpg' },
      { type: 'destination', name: 'Bali, Indonesia', image: '/src/assets/images/bali.jpg' },
      { type: 'destination', name: 'Swiss Alps', image: '/src/assets/images/swiss.jpg' },
      { type: 'destination', name: 'Amalfi Coast', image: '/src/assets/images/amalfi.jpg' },
  ];

  return (
    <div className="search-result-list" style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
        gap: '24px',
        marginTop: '30px'
    }}>
      {displayResults.map((res, index) => (
          <div key={index}>
              {res.type === 'destination' ? <DestinationCard destination={res} /> : <ServiceCard service={res} />}
          </div>
      ))}
    </div>
  );
};

export default SearchResultList;
