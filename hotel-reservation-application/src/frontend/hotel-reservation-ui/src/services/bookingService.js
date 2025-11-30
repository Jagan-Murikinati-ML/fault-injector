import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

export const bookingService = {
  getMyBookings: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/booking/my-bookings`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  getBookingDetails: async (bookingId) => {
    const response = await axios.get(`${API_BASE_URL}/api/booking/booking-details/${bookingId}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  }
};