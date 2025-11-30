import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000/api/hotels';
const CITIES_API_URL = 'http://localhost:3000/api/cities';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const apiCall = async (url, method = 'GET', data = null) => {
  const headers = getAuthHeaders();
  const config = {
    method,
    url: `http://localhost:3000${url}`,
    headers,
  };

  // For GET requests, add params to URL, for POST add to data
  if (method === 'GET' && data) {
    config.params = data;
  } else if (data) {
    config.data = data;
  }

  const response = await axios(config);
  return response;
};

export const hotelService = {
  searchHotels: async (searchParams) => {
    try {
      const response = await apiCall('/api/hotels/search', 'GET', searchParams);
      return response.data;
    } catch (error) {
      console.error('Error searching hotels:', error);
      throw error;
    }
  },

  getFilters: async (searchParams) => {
    try {
      const response = await apiCall('/api/hotels/filters', 'GET', searchParams);
      return response.data;
    } catch (error) {
      console.error('Error getting filters:', error);
      throw error;
    }
  },

  searchCities: async (query) => {
    try {
      const response = await apiCall('/api/cities/search', 'GET', { q: query });
      return response.data;
    } catch (error) {
      console.error('Error searching cities:', error);
      throw error;
    }
  },

  getAvailableRooms: async (hotelId, checkinDate, checkoutDate, roomTypes, totalRoomsData) => {
    try {
      const roomTypesString = roomTypes.join(',');
      const response = await apiCall(`/api/booking/booked-rooms?hotel_id=${hotelId}&checkin_date=${checkinDate}&checkout_date=${checkoutDate}&room_types=${roomTypesString}`);
      
      console.log('Booked rooms API response:', response.data);
      
      // Handle BFF response structure - extract the actual data
      const bookedRoomsData = response.data?.data || response.data || [];
      
      if (!Array.isArray(bookedRoomsData)) {
        console.error('Expected array but got:', bookedRoomsData);
        return [];
      }
      
      const availableRoomsData = bookedRoomsData.map(booking => {
        const totalRooms = totalRoomsData[booking.room_type_code] || 0;
        const availableCount = totalRooms - booking.booked_count;
        
        return {
          booking_date: booking.booking_date,
          room_type_code: booking.room_type_code,
          booked_count: booking.booked_count,
          total_rooms: totalRooms,
          available_rooms: Math.max(0, availableCount)
        };
      });
      
      return availableRoomsData;
    } catch (error) {
      console.error('Error getting available rooms:', error);
      throw error;
    }
  },

  bookHotel: async (bookingData) => {
    try {
      const response = await apiCall('/api/booking/book-hotel', 'POST', bookingData);
      return response;
    } catch (error) {
      console.error('Error booking hotel:', error);
      throw error;
    }
  }
};

export default hotelService;




