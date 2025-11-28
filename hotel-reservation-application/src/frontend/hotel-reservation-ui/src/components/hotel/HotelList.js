import React from 'react';
import HotelCard from './HotelCard';

const HotelList = ({ hotels, loading, onCheckAvailability }) => {
  if (loading) {
    return <div className="loading">Searching hotels...</div>;
  }

  if (!hotels || hotels.length === 0) {
    return (
      <div className="no-results">
        <h3>No hotels found</h3>
        <p>Try adjusting your search criteria or filters</p>
      </div>
    );
  }

  return (
    <div className="hotel-list">
      <div className="results-header">
        <h3>{hotels.length} hotels found</h3>
      </div>
      
      <div className="hotels-container">
        {hotels.map((hotel, index) => (
          <HotelCard 
            key={hotel.id || index} 
            hotel={hotel} 
            onCheckAvailability={onCheckAvailability}
          />
        ))}
      </div>
    </div>
  );
};

export default HotelList;




