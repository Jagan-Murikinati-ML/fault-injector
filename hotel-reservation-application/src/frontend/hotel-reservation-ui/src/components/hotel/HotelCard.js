import React from 'react';

const HotelCard = ({ hotel, onCheckAvailability }) => {
  return (
    <div className="hotel-card">
      <div className="hotel-header">
        <h3 className="hotel-name">{hotel.name}</h3>
        <div className="hotel-rating">
          ⭐ {hotel.current_rating?.avg_rating?.toFixed(1) || 'N/A'} 
          ({hotel.current_rating?.total_reviews || 0} reviews)
        </div>
      </div>
      
      <div className="hotel-details">
        <p className="hotel-location">{hotel.address}</p>
        
        {/* Amenities */}
        <div className="hotel-amenities">
          {hotel.hotel_amenities?.complementary_breakfast && <span className="amenity">🍳 Breakfast</span>}
          {hotel.hotel_amenities?.parking_available && <span className="amenity">🚗 Parking</span>}
          {hotel.hotel_policies?.pets_allowed && <span className="amenity">🐕 Pet Friendly</span>}
          {hotel.hotel_amenities?.wifi && <span className="amenity">📶 WiFi</span>}
          {hotel.hotel_amenities?.pool && <span className="amenity">🏊 Pool</span>}
          {hotel.hotel_amenities?.gym && <span className="amenity">💪 Gym</span>}
        </div>
      </div>

      <div className="hotel-info">
        <div className="hotel-price">
          {hotel.current_pricing?.currency === 'INR' ? '₹' : hotel.current_pricing?.currency || '₹'}{hotel.current_pricing?.min_price || 'N/A'}
          <span className="price-note">/night</span>
        </div>
        <button 
          className="book-now-button"
          onClick={() => onCheckAvailability(hotel)}
        >
          Check Availability
        </button>
      </div>
    </div>
  );
};

export default HotelCard;





