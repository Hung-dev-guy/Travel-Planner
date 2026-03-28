import React from 'react';

const ServiceCard = ({ service }) => {
  return (
    <div className="service-card">
      <h3>{service?.name}</h3>
    </div>
  );
};

export default ServiceCard;
