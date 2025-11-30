import React, { useState, useEffect, useCallback } from 'react';
import { bookingService } from '../../services/bookingService';
import './BookingComponents.css';

const BookingDetailsPage = ({ booking, onClose }) => {
  const [bookingDetails, setBookingDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBookingDetails = useCallback(async () => {
    try {
      setLoading(true);
      const response = await bookingService.getBookingDetails(booking.booking_id);
      setBookingDetails(response.data);
    } catch (err) {
      setError('Failed to load booking details');
      console.error('Error fetching booking details:', err);
    } finally {
      setLoading(false);
    }
  }, [booking.booking_id]);

  useEffect(() => {
    if (booking?.booking_id) {
      fetchBookingDetails();
    }
  }, [booking, fetchBookingDetails]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="booking-details-overlay">
        <div className="booking-details-modal">
          <div className="loading">Loading booking details...</div>
        </div>
      </div>
    );
  }

  if (error || !bookingDetails) {
    return (
      <div className="booking-details-overlay">
        <div className="booking-details-modal">
          <div className="modal-header">
            <h2>Booking Details</h2>
            <button className="close-button" onClick={onClose}>×</button>
          </div>
          <div className="error-message">{error || 'Booking details not found'}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="booking-details-overlay">
      <div className="booking-details-modal">
        <div className="modal-header">
          <h2>Booking Details</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="booking-details-content">
          {/* Booking Summary */}
          <div className="details-section">
            <h3>Booking Summary</h3>
            <div className="details-grid">
              <div className="detail-item">
                <label>Booking ID:</label>
                <span>{bookingDetails.booking_id}</span>
              </div>
              <div className="detail-item">
                <label>Hotel:</label>
                <span>{bookingDetails.hotel_name}</span>
              </div>
              <div className="detail-item">
                <label>Status:</label>
                <span className={`status ${bookingDetails.booking_status.toLowerCase()}`}>
                  {bookingDetails.booking_status}
                </span>
              </div>
              <div className="detail-item">
                <label>Invoice Number:</label>
                <span>{bookingDetails.invoice_number || 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* Stay Details */}
          <div className="details-section">
            <h3>Stay Details</h3>
            <div className="details-grid">
              <div className="detail-item">
                <label>Check-in Date:</label>
                <span>{formatDate(bookingDetails.checkin_date)}</span>
              </div>
              <div className="detail-item">
                <label>Check-out Date:</label>
                <span>{formatDate(bookingDetails.checkout_date)}</span>
              </div>
              <div className="detail-item">
                <label>Total Guests:</label>
                <span>{bookingDetails.total_guests}</span>
              </div>
              <div className="detail-item">
                <label>Total Amount:</label>
                <span className="amount">
                  {bookingDetails.currency} {bookingDetails.total_amount.toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {/* Guest Information */}
          <div className="details-section">
            <h3>Guest Information</h3>
            <div className="details-grid">
              <div className="detail-item">
                <label>Guest Name:</label>
                <span>{bookingDetails.guest_name}</span>
              </div>
              <div className="detail-item">
                <label>Email:</label>
                <span>{bookingDetails.guest_email}</span>
              </div>
              <div className="detail-item">
                <label>Phone:</label>
                <span>{bookingDetails.guest_phone || 'N/A'}</span>
              </div>
              {bookingDetails.special_requests && (
                <div className="detail-item full-width">
                  <label>Special Requests:</label>
                  <span>{bookingDetails.special_requests}</span>
                </div>
              )}
            </div>
          </div>

          {/* Payment Information */}
          <div className="details-section">
            <h3>Payment Information</h3>
            <div className="details-grid">
              <div className="detail-item">
                <label>Payment Status:</label>
                <span className={`status ${bookingDetails.payment_status?.toLowerCase()}`}>
                  {bookingDetails.payment_status || 'N/A'}
                </span>
              </div>
              <div className="detail-item">
                <label>Payment Method:</label>
                <span>{bookingDetails.payment_method || 'N/A'}</span>
              </div>
              <div className="detail-item">
                <label>Payment Reference:</label>
                <span>{bookingDetails.payment_reference || 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* Cancellation Policy */}
          <div className="details-section">
            <h3>Cancellation Policy</h3>
            <div className="details-grid">
              <div className="detail-item">
                <label>Policy Type:</label>
                <span>{bookingDetails.cancellation_policy_type || 'N/A'}</span>
              </div>
              {bookingDetails.free_cancellation_hours && (
                <div className="detail-item">
                  <label>Free Cancellation:</label>
                  <span>{bookingDetails.free_cancellation_hours} hours before check-in</span>
                </div>
              )}
              {bookingDetails.cancellation_fee_percentage && (
                <div className="detail-item">
                  <label>Cancellation Fee:</label>
                  <span>{bookingDetails.cancellation_fee_percentage}%</span>
                </div>
              )}
              {bookingDetails.cancellation_deadline && (
                <div className="detail-item">
                  <label>Cancellation Deadline:</label>
                  <span>{formatDateTime(bookingDetails.cancellation_deadline)}</span>
                </div>
              )}
              {bookingDetails.refund_policy && (
                <div className="detail-item full-width">
                  <label>Refund Policy:</label>
                  <span>{bookingDetails.refund_policy}</span>
                </div>
              )}
            </div>
          </div>

          {/* Booking Timeline */}
          <div className="details-section">
            <h3>Booking Timeline</h3>
            <div className="details-grid">
              <div className="detail-item">
                <label>Booking Created:</label>
                <span>{formatDateTime(bookingDetails.created_at)}</span>
              </div>
              <div className="detail-item">
                <label>Last Updated:</label>
                <span>{formatDateTime(bookingDetails.updated_at)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingDetailsPage;

