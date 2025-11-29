import React, { useState, useEffect, useMemo } from 'react';
import { hotelService } from '../../services/hotelService';

const HotelDetailsPage = ({ hotel, searchParams, onClose, onBookingConfirm }) => {
  const [activeTab, setActiveTab] = useState('rooms');
  const [roomSelections, setRoomSelections] = useState({});
  const [availableRooms, setAvailableRooms] = useState([]);
  const [loadingAvailability, setLoadingAvailability] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState(null);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [guestDetails, setGuestDetails] = useState({
    guest_name: '',
    guest_email: '',
    guest_phone: ''
  });
  const [totalGuests, setTotalGuests] = useState(2);
  const [showBookingForm, setShowBookingForm] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'rooms', label: 'Rooms & Booking' },
    { id: 'amenities', label: 'Hotel & Room Amenities' },
    { id: 'reviews', label: 'Reviews' }
  ];

  // Use real room types from hotel data
  const roomTypes = useMemo(() => hotel.room_types || [], [hotel.room_types]);

  // Calculate dates array
  const dates = useMemo(() => {
    const datesArray = [];
    const checkin = new Date(searchParams.checkin_date);
    const checkout = new Date(searchParams.checkout_date);

    for (let d = new Date(checkin); d < checkout; d.setDate(d.getDate() + 1)) {
      datesArray.push(new Date(d));
    }
    return datesArray;
  }, [searchParams.checkin_date, searchParams.checkout_date]);

  const totalNights = dates.length;

  // Format date for display
  const formatDate = (date) => {
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
  };

  // Format date for key
  const formatDateKey = (date) => {
    return date.toISOString().split('T')[0];
  };

  // Initialize room selections
  useEffect(() => {
    const initialSelections = {};
    dates.forEach(date => {
      const dateKey = formatDateKey(date);
      initialSelections[dateKey] = {};
      roomTypes.forEach(room => {
        initialSelections[dateKey][room.type] = 0;
      });
    });
    setRoomSelections(initialSelections);
  }, [dates, roomTypes]);

  // Handle room selection change
  const handleRoomChange = (dateKey, roomType, value) => {
    setRoomSelections(prev => ({
      ...prev,
      [dateKey]: {
        ...prev[dateKey],
        [roomType]: parseInt(value)
      }
    }));
  };

  // Apply first date selections to all dates
  const applyToAllDates = () => {
    if (dates.length === 0) return;

    const firstDateKey = formatDateKey(dates[0]);
    const firstDateSelections = roomSelections[firstDateKey] || {};

    const newSelections = {};
    dates.forEach(date => {
      const dateKey = formatDateKey(date);
      newSelections[dateKey] = { ...firstDateSelections };
    });

    setRoomSelections(newSelections);
  };

  // Calculate total cost
  const calculateTotalCost = () => {
    let total = 0;
    Object.keys(roomSelections).forEach(dateKey => {
      Object.keys(roomSelections[dateKey]).forEach(roomType => {
        const roomCount = roomSelections[dateKey][roomType];
        const room = roomTypes.find(r => r.type === roomType);
        if (room && roomCount > 0) {
          total += room.price_per_night_per_room * roomCount;
        }
      });
    });
    return total;
  };

  const totalCost = calculateTotalCost();

  // Get user ID from auth context
  const getUserId = () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.userId || payload.username || "guest_user";
      } catch (error) {
        return "guest_user";
      }
    }
    return "guest_user";
  };

  // Validate guest details
  const validateGuestDetails = () => {
    const { guest_name, guest_email, guest_phone } = guestDetails;
    
    if (!guest_name.trim()) {
      setBookingError('Guest name is required');
      return false;
    }
    
    if (!guest_email.trim()) {
      setBookingError('Guest email is required');
      return false;
    }
    
    if (!guest_phone.trim()) {
      setBookingError('Guest phone number is required');
      return false;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(guest_email)) {
      setBookingError('Please enter a valid email address');
      return false;
    }
    
    return true;
  };

  // Handle guest details change
  const handleGuestDetailsChange = (field, value) => {
    setGuestDetails(prev => ({
      ...prev,
      [field]: value
    }));
    setBookingError(null);
  };

  // Handle Book Now button click
  const handleBookNowClick = () => {
    if (totalCost === 0) {
      setBookingError('Please select at least one room');
      return;
    }
    setShowBookingForm(true);
    setBookingError(null);
  };

  // Handle actual booking submission
  const handleBookNow = async () => {
    if (!validateGuestDetails()) {
      return;
    }
    
    setBookingLoading(true);
    setBookingError(null);
    
    try {
      // Format room bookings for API
      const rooms = [];
      Object.keys(roomSelections).forEach(dateKey => {
        Object.keys(roomSelections[dateKey]).forEach(roomType => {
          const roomCount = roomSelections[dateKey][roomType];
          if (roomCount > 0) {
            const room = roomTypes.find(r => r.type === roomType);
            rooms.push({
              room_type_code: roomType,
              booking_date: dateKey,
              rooms_count: roomCount,
              cost_per_room_per_night: room.price_per_night_per_room
            });
          }
        });
      });
      
      const bookingData = {
        hotel_id: hotel.id,
        user_id: getUserId(),
        checkin_date: searchParams.checkin,
        checkout_date: searchParams.checkout,
        total_guests: totalGuests,
        rooms: rooms,
        currency: "INR",
        guest_details: {
          guest_name: guestDetails.guest_name.trim(),
          guest_email: guestDetails.guest_email.trim(),
          guest_phone: guestDetails.guest_phone.trim()
        },
        special_requests: null,
        cancellation_policy: {
          cancellation_policy_type: hotel.hotel_policies?.free_cancellation ? "FREE" : "NON_REFUNDABLE",
          free_cancellation_hours: hotel.hotel_policies?.cancellation_hours || 24,
          cancellation_fee_percentage: 0.00,
          refund_policy: hotel.hotel_policies?.free_cancellation ? 
            `Full refund if cancelled ${hotel.hotel_policies?.cancellation_hours || 24} hours before checkin` : 
            "Non-refundable booking"
        }
      };

      const response = await hotelService.bookHotel(bookingData);
      setBookingSuccess(true);
      setShowBookingForm(false);
      
    } catch (error) {
      console.error('Booking failed:', error);
      setBookingError(error.response?.data?.message || 'Booking failed. Please try again.');
    } finally {
      setBookingLoading(false);
    }
  };

  // Fetch available rooms when component loads or dates change
  useEffect(() => {
    if (hotel && searchParams?.checkin && searchParams?.checkout) {
      fetchAvailableRooms();
    }
  }, [hotel, searchParams?.checkin, searchParams?.checkout]);

  const fetchAvailableRooms = async () => {
    setLoadingAvailability(true);
    try {
      const roomTypes = hotel.room_types.map(room => room.type);
      const totalRoomsData = {};
      hotel.room_types.forEach(room => {
        totalRoomsData[room.type] = room.total_rooms;
      });
      
      const availabilityData = await hotelService.getAvailableRooms(
        hotel.id,
        searchParams.checkin,
        searchParams.checkout,
        roomTypes,
        totalRoomsData
      );
      
      setAvailableRooms(availabilityData);
    } catch (error) {
      console.error('Failed to fetch room availability:', error);
      setAvailableRooms([]);
    } finally {
      setLoadingAvailability(false);
    }
  };

  // Update room display to show available rooms
  const getAvailableRoomsForType = (roomType) => {
    const roomAvailability = availableRooms.filter(room => room.room_type_code === roomType);
    if (roomAvailability.length === 0) return 0;
    return Math.min(...roomAvailability.map(room => room.available_rooms));
  };

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
      <div className="booking-section-new">
        {/* Booking Header */}
        <div className="booking-header">
          <h3>{hotel.name} | Check-in: {formatDate(new Date(searchParams.checkin_date))} | Check-out: {formatDate(new Date(searchParams.checkout_date))} | {totalNights} {totalNights === 1 ? 'Night' : 'Nights'}</h3>
        </div>

        {/* Apply to All Dates Button */}
        <div className="apply-all-container">
          <button className="apply-all-button" onClick={applyToAllDates}>
            Apply First Date Selection to All Dates
          </button>
        </div>

        {/* Room Selection Table */}
        <div className="room-table-container">
          <table className="room-selection-table">
            <thead>
              <tr>
                <th className="date-column">Date</th>
                {roomTypes.map((room, index) => (
                  <th key={index} className="room-column">
                    <div className="room-header">
                      <div className="room-type-name">{room.name || room.type}</div>
                      <div className="room-price-header">₹{room.price_per_night_per_room?.toLocaleString() || 'N/A'} / night</div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dates.map((date, dateIndex) => {
                const dateKey = formatDateKey(date);
                return (
                  <tr key={dateIndex}>
                    <td className="date-cell">
                      <div className="date-display">{formatDate(date)}</div>
                    </td>
                    {roomTypes.map((room, roomIndex) => (
                      <td key={roomIndex} className="room-cell">
                        <div className="room-cell-content">
                          <div className="available-rooms">
                            {loadingAvailability ? (
                              'Loading availability...'
                            ) : (
                              `Available: ${getAvailableRoomsForType(room.type)}`
                            )}
                          </div>
                          <div className="room-select">
                            <label>Select Rooms:</label>
                            <select
                              value={roomSelections[dateKey]?.[room.type] || 0}
                              onChange={(e) => handleRoomChange(dateKey, room.type, e.target.value)}
                            >
                              {[...Array(Math.min((room.total_rooms || 5) + 1, 11))].map((_, i) => (
                                <option key={i} value={i}>{i}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Booking Summary */}
        <div className="booking-summary">
          <div className="summary-section">
            <h3>Booking Summary</h3>
            <div className="guest-count-section">
              <label>Total Guests:</label>
              <select 
                value={totalGuests} 
                onChange={(e) => setTotalGuests(parseInt(e.target.value))}
                style={{marginLeft: '10px', padding: '5px'}}
              >
                {[...Array(10)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>{i + 1} {i === 0 ? 'Guest' : 'Guests'}</option>
                ))}
              </select>
            </div>
            <div className="total-cost">
              <span className="cost-label">Total Cost:</span>
              <span className="cost-amount">₹{totalCost.toLocaleString()}</span>
            </div>
          </div>

          <div className="summary-section">
            <h3>Cancellation Policy</h3>
            <div className="cancellation-policy">
              {hotel.hotel_policies?.free_cancellation ? (
                <>
                  <p className="policy-highlight">✓ Free Cancellation</p>
                  <p>Cancel up to {hotel.hotel_policies.cancellation_hours || 24} hours before check-in for a full refund.</p>
                </>
              ) : (
                <p className="policy-highlight">Non-refundable booking</p>
              )}
              {hotel.hotel_policies?.prepayment_needed && (
                <p>Prepayment required at the time of booking.</p>
              )}
            </div>
          </div>

          {/* Guest Details Form */}
          {showBookingForm && (
            <div className="guest-details-section">
              <h3>Guest Details</h3>
              <div className="guest-form">
                <div className="form-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    value={guestDetails.guest_name}
                    onChange={(e) => handleGuestDetailsChange('guest_name', e.target.value)}
                    placeholder="Enter full name"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email Address *</label>
                  <input
                    type="email"
                    value={guestDetails.guest_email}
                    onChange={(e) => handleGuestDetailsChange('guest_email', e.target.value)}
                    placeholder="Enter email address"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Phone Number *</label>
                  <input
                    type="tel"
                    value={guestDetails.guest_phone}
                    onChange={(e) => handleGuestDetailsChange('guest_phone', e.target.value)}
                    placeholder="Enter phone number"
                    required
                  />
                </div>
              </div>
            </div>
          )}

          {/* Success Message */}
          {bookingSuccess && (
            <div className="booking-success" style={{color: 'green', marginBottom: '10px', padding: '10px', border: '1px solid green', borderRadius: '5px'}}>
              <h4>✓ Booking Confirmed Successfully!</h4>
              <p>Your reservation has been confirmed. You will receive a confirmation email shortly.</p>
              <button onClick={() => {setBookingSuccess(false); onClose();}} style={{marginTop: '10px', padding: '5px 15px'}}>
                Close
              </button>
            </div>
          )}

          {bookingError && (
            <div className="booking-error" style={{color: 'red', marginBottom: '10px'}}>
              {bookingError}
            </div>
          )}

          {!bookingSuccess && (
            <>
              {!showBookingForm ? (
                <button
                  className="book-now-button-final"
                  onClick={handleBookNowClick}
                  disabled={totalCost === 0}
                >
                  Proceed to Book
                </button>
              ) : (
                <div className="booking-actions">
                  <button
                    className="book-now-button-final"
                    onClick={handleBookNow}
                    disabled={bookingLoading}
                    style={{marginRight: '10px'}}
                  >
                    {bookingLoading ? 'Booking...' : 'Confirm Booking'}
                  </button>
                  <button
                    onClick={() => setShowBookingForm(false)}
                    disabled={bookingLoading}
                    style={{padding: '10px 20px', backgroundColor: '#ccc'}}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );

  const renderAmenities = () => (
    <div className="tab-content">
      {/* Hotel Amenities Section */}
      <div className="amenities-section">
        <h3 className="amenities-section-title">Hotel Amenities</h3>
        <div className="amenities-grid-three-col">
          {hotel.hotel_amenities?.complementary_breakfast !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">🍳</span>
              <span className="amenity-name">Complimentary Breakfast</span>
              <span className={hotel.hotel_amenities.complementary_breakfast ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.complementary_breakfast ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_amenities?.parking_available !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">🚗</span>
              <span className="amenity-name">Parking</span>
              <span className={hotel.hotel_amenities.parking_available ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.parking_available ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_policies?.pets_allowed !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">🐕</span>
              <span className="amenity-name">Pet Friendly</span>
              <span className={hotel.hotel_policies.pets_allowed ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_policies.pets_allowed ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_amenities?.wifi !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">📶</span>
              <span className="amenity-name">WiFi</span>
              <span className={hotel.hotel_amenities.wifi ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.wifi ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_amenities?.pool !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">🏊</span>
              <span className="amenity-name">Pool</span>
              <span className={hotel.hotel_amenities.pool ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.pool ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_amenities?.gym !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">💪</span>
              <span className="amenity-name">Gym</span>
              <span className={hotel.hotel_amenities.gym ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.gym ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_amenities?.restaurant !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">🍽️</span>
              <span className="amenity-name">Restaurant</span>
              <span className={hotel.hotel_amenities.restaurant ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.restaurant ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_amenities?.bar !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">🍸</span>
              <span className="amenity-name">Bar</span>
              <span className={hotel.hotel_amenities.bar ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.bar ? '✓' : '✗'}
              </span>
            </div>
          )}

          {hotel.hotel_amenities?.room_service !== undefined && (
            <div className="amenity-item-compact">
              <span className="amenity-icon">🛎️</span>
              <span className="amenity-name">Room Service</span>
              <span className={hotel.hotel_amenities.room_service ? 'amenity-check' : 'amenity-cross'}>
                {hotel.hotel_amenities.room_service ? '✓' : '✗'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Room Amenities Section */}
      <div className="amenities-section">
        <h3 className="amenities-section-title">Room Amenities by Room Type</h3>
        <div className="room-types-grid">
          {roomTypes.map((room, index) => (
            <div key={index} className="room-amenities-card">
              <h4 className="room-type-title-compact">{room.name || room.type}</h4>
              <div className="room-details-compact">
                {room.size_sqft && <span>📏 {room.size_sqft} sq ft</span>}
                {room.max_occupancy && <span>👥 {room.max_occupancy} guests</span>}
                {room.bed_configuration && (
                  <span>🛏️ {room.bed_configuration.bed_count} {room.bed_configuration.bed_type}</span>
                )}
              </div>
              {room.room_amenities && (
                <div className="room-amenities-list">
                  {room.room_amenities.air_conditioning !== undefined && (
                    <div className="amenity-item-compact">
                      <span className="amenity-icon">❄️</span>
                      <span className="amenity-name">AC</span>
                      <span className={room.room_amenities.air_conditioning ? 'amenity-check' : 'amenity-cross'}>
                        {room.room_amenities.air_conditioning ? '✓' : '✗'}
                      </span>
                    </div>
                  )}
                  {room.room_amenities.wifi !== undefined && (
                    <div className="amenity-item-compact">
                      <span className="amenity-icon">📶</span>
                      <span className="amenity-name">WiFi</span>
                      <span className={room.room_amenities.wifi ? 'amenity-check' : 'amenity-cross'}>
                        {room.room_amenities.wifi ? '✓' : '✗'}
                      </span>
                    </div>
                  )}
                  {room.room_amenities.tv !== undefined && (
                    <div className="amenity-item-compact">
                      <span className="amenity-icon">📺</span>
                      <span className="amenity-name">TV</span>
                      <span className={room.room_amenities.tv ? 'amenity-check' : 'amenity-cross'}>
                        {room.room_amenities.tv ? '✓' : '✗'}
                      </span>
                    </div>
                  )}
                  {room.room_amenities.minibar !== undefined && (
                    <div className="amenity-item-compact">
                      <span className="amenity-icon">🍷</span>
                      <span className="amenity-name">Minibar</span>
                      <span className={room.room_amenities.minibar ? 'amenity-check' : 'amenity-cross'}>
                        {room.room_amenities.minibar ? '✓' : '✗'}
                      </span>
                    </div>
                  )}
                  {room.room_amenities.safe !== undefined && (
                    <div className="amenity-item-compact">
                      <span className="amenity-icon">🔒</span>
                      <span className="amenity-name">Safe</span>
                      <span className={room.room_amenities.safe ? 'amenity-check' : 'amenity-cross'}>
                        {room.room_amenities.safe ? '✓' : '✗'}
                      </span>
                    </div>
                  )}
                  {room.room_amenities.balcony !== undefined && (
                    <div className="amenity-item-compact">
                      <span className="amenity-icon">🌅</span>
                      <span className="amenity-name">Balcony</span>
                      <span className={room.room_amenities.balcony ? 'amenity-check' : 'amenity-cross'}>
                        {room.room_amenities.balcony ? '✓' : '✗'}
                      </span>
                    </div>
                  )}
                  {room.room_amenities.kitchenette !== undefined && (
                    <div className="amenity-item-compact">
                      <span className="amenity-icon">🍳</span>
                      <span className="amenity-name">Kitchenette</span>
                      <span className={room.room_amenities.kitchenette ? 'amenity-check' : 'amenity-cross'}>
                        {room.room_amenities.kitchenette ? '✓' : '✗'}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
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


























