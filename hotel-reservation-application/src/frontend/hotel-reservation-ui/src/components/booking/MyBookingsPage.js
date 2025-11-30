import React, { useState, useEffect } from 'react';
import { bookingService } from '../../services/bookingService';
import './BookingComponents.css';

const MyBookingsPage = ({ onClose, onViewDetails }) => {
  const [bookings, setBookings] = useState({ current_bookings: [], past_bookings: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMyBookings();
  }, []);

  const fetchMyBookings = async () => {
    try {
      setLoading(true);
      const response = await bookingService.getMyBookings();
      setBookings(response.data);
    } catch (err) {
      setError('Failed to load bookings');
      console.error('Error fetching bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderBookingCard = (booking) => (
    <div key={booking.booking_id} className="booking-card">
      <div className="booking-header">
        <h4>{booking.hotel_name}</h4>
        <span className={`booking-status ${booking.booking_status.toLowerCase()}`}>
          {booking.booking_status}
        </span>
      </div>
      
      <div className="booking-info">
        <div className="booking-dates">
          <span>Check-in: {formatDate(booking.checkin_date)}</span>
          <span>Check-out: {formatDate(booking.checkout_date)}</span>
        </div>
        
        <div className="booking-details">
          <span>Guests: {booking.total_guests}</span>
          <span>Amount: {booking.currency} {booking.total_amount.toLocaleString()}</span>
        </div>
      </div>
      
      <button 
        className="view-details-btn"
        onClick={() => onViewDetails(booking)}
      >
        View Details
      </button>
    </div>
  );

  if (loading) {
    return (
      <div className="my-bookings-overlay">
        <div className="my-bookings-modal">
          <div className="loading">Loading your bookings...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="my-bookings-overlay">
      <div className="my-bookings-modal">
        <div className="modal-header">
          <h2>My Bookings</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="bookings-content">
          {error && <div className="error-message">{error}</div>}
          
          <div className="bookings-section">
            <h3>Current Bookings ({bookings.current_bookings.length})</h3>
            {bookings.current_bookings.length === 0 ? (
              <p className="no-bookings">No current bookings</p>
            ) : (
              <div className="bookings-list">
                {bookings.current_bookings.map(renderBookingCard)}
              </div>
            )}
          </div>
          
          <div className="bookings-section">
            <h3>Past Bookings ({bookings.past_bookings.length})</h3>
            {bookings.past_bookings.length === 0 ? (
              <p className="no-bookings">No past bookings</p>
            ) : (
              <div className="bookings-list">
                {bookings.past_bookings.map(renderBookingCard)}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyBookingsPage;
