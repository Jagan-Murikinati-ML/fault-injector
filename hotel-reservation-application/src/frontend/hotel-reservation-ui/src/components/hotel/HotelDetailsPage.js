import React, { useState } from 'react';

const HotelDetailsPage = ({ hotel, searchParams, onClose, onBookingConfirm }) => {
  const [activeTab, setActiveTab] = useState('rooms');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'rooms', label: 'Rooms & Booking' },
    { id: 'amenities', label: 'Amenities' },
    { id: 'reviews', label: 'Reviews' }
  ];

  // Use real room types from hotel data
  const roomTypes = hotel.room_types || [];

  const renderOverview = () => (
    <div className="tab-content">
      <div className="hotel-overview">
        <h2>{hotel.name}</h2>
        <div className="hotel-rating-large">
          ⭐ {hotel.current_rating?.avg_rating?.toFixed(1) || 'N/A'} 
          ({hotel.current_rating?.total_reviews || 0} reviews)
        </div>
        <p className="hotel-address">📍 {hotel.address}</p>
        
        <div className="hotel-description">
          <h3>About this hotel</h3>
          <p>{hotel.description || `Experience luxury and comfort at ${hotel.name}. Located in the heart of the city, our hotel offers modern amenities and exceptional service to make your stay memorable.`}</p>
        </div>

        <div className="hotel-contact">
          <h3>Contact Information</h3>
          <p>📞 {hotel.phone}</p>
          <p>✉️ {hotel.email}</p>
          <p>🕐 Check-in: {hotel.check_in_time} | Check-out: {hotel.check_out_time}</p>
        </div>
      </div>
    </div>
  );

  const renderRoomsAndBooking = () => (
    <div className="tab-content">
      <div className="booking-section">
        <h3>Select Rooms</h3>
        <div className="booking-info">
          <p><strong>Check-in:</strong> {searchParams.checkin_date}</p>
          <p><strong>Check-out:</strong> {searchParams.checkout_date}</p>
          <p><strong>Guests:</strong> {searchParams.guests}</p>
        </div>
        
        <div className="room-types">
          {roomTypes.map((room, index) => (
            <div key={index} className="room-card">
              <div className="room-info">
                <h4>{room.name || room.type || 'Room'}</h4>
                <p>{room.description || ''}</p>
                {room.bed_configuration && (
                  <p>Bed: {room.bed_configuration.bed_type} ({room.bed_configuration.bed_count})</p>
                )}
                {room.size_sqft && <p>Size: {room.size_sqft} sq ft</p>}
                {room.max_occupancy && <p>Max Occupancy: {room.max_occupancy} guests</p>}
                
                {room.room_amenities && (
                  <div className="room-amenities">
                    {Object.entries(room.room_amenities).map(([key, value]) => 
                      value && <span key={key} className="room-amenity">{key.replace(/_/g, ' ')}</span>
                    )}
                  </div>
                )}
                
                <div className="room-price">
                  {/* No per-room pricing available yet */}
                  Price: Contact hotel
                </div>
              </div>
              <div className="room-selection">
                <label>Rooms:</label>
                <select defaultValue="0">
                  {[...Array(6)].map((_, i) => (
                    <option key={i} value={i}>{i}</option>
                  ))}
                </select>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAmenities = () => (
    <div className="tab-content">
      <div className="amenities-grid">
        {hotel.hotel_amenities?.complementary_breakfast !== undefined && (
          <div className="amenity-item">
            🍳 <span>Complimentary Breakfast</span>
            <span className={hotel.hotel_amenities.complementary_breakfast ? 'available' : 'unavailable'}>
              {hotel.hotel_amenities.complementary_breakfast ? 'Yes' : 'No'}
            </span>
          </div>
        )}
        
        {hotel.hotel_amenities?.parking_available !== undefined && (
          <div className="amenity-item">
            🚗 <span>Parking</span>
            <span className={hotel.hotel_amenities.parking_available ? 'available' : 'unavailable'}>
              {hotel.hotel_amenities.parking_available ? 'Yes' : 'No'}
            </span>
          </div>
        )}
        
        {hotel.hotel_policies?.pets_allowed !== undefined && (
          <div className="amenity-item">
            🐕 <span>Pet Friendly</span>
            <span className={hotel.hotel_policies.pets_allowed ? 'available' : 'unavailable'}>
              {hotel.hotel_policies.pets_allowed ? 'Yes' : 'No'}
            </span>
          </div>
        )}
        
        {hotel.hotel_amenities?.wifi !== undefined && (
          <div className="amenity-item">
            📶 <span>WiFi</span>
            <span className={hotel.hotel_amenities.wifi ? 'available' : 'unavailable'}>
              {hotel.hotel_amenities.wifi ? 'Yes' : 'No'}
            </span>
          </div>
        )}
        
        {hotel.hotel_amenities?.pool !== undefined && (
          <div className="amenity-item">
            🏊 <span>Pool</span>
            <span className={hotel.hotel_amenities.pool ? 'available' : 'unavailable'}>
              {hotel.hotel_amenities.pool ? 'Yes' : 'No'}
            </span>
          </div>
        )}
        
        {hotel.hotel_amenities?.gym !== undefined && (
          <div className="amenity-item">
            � <span>Gym</span>
            <span className={hotel.hotel_amenities.gym ? 'available' : 'unavailable'}>
              {hotel.hotel_amenities.gym ? 'Yes' : 'No'}
            </span>
          </div>
        )}
      </div>
    </div>
  );

  const renderReviews = () => (
    <div className="tab-content">
      <div className="reviews-section">
        <h3>Guest Reviews</h3>
        <div className="overall-rating">
          <div className="rating-score">
            ⭐ {hotel.current_rating?.avg_rating?.toFixed(1) || 'No rating'}
          </div>
          <div className="rating-details">
            <p>Based on {hotel.current_rating?.total_reviews || 0} reviews</p>
          </div>
        </div>
        <p>Individual reviews not available</p>
      </div>
    </div>
  );

  return (
    <div className="hotel-details-overlay">
      <div className="hotel-details-modal">
        <div className="modal-header">
          <h2>{hotel.name}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        <div className="tab-content-container">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'rooms' && renderRoomsAndBooking()}
          {activeTab === 'amenities' && renderAmenities()}
          {activeTab === 'reviews' && renderReviews()}
        </div>
      </div>
    </div>
  );
};

export default HotelDetailsPage;








