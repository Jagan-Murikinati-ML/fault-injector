import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000/api/hotels';
const CITIES_API_URL = 'http://localhost:3000/api/cities';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const hotelService = {
  searchHotels: async (searchParams) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/search`, {
        params: searchParams,
        headers: getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error searching hotels:', error);
      throw error;
    }
  },

  getFilters: async (searchParams) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/filters`, {
        params: searchParams,
        headers: getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error getting filters:', error);
      throw error;
    }
  },

  searchCities: async (query) => {
    try {
      const response = await axios.get(`${CITIES_API_URL}/search`, {
        params: { q: query },
        headers: getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error searching cities:', error);
      throw error;
    }
  }
};





