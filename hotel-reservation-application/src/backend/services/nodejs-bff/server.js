const express = require('express');
const axios = require('axios');
const cors = require('cors');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 3000;
const SEARCH_SERVICE_URL = process.env.SEARCH_SERVICE_URL || 'http://localhost:8000';
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://localhost:9000';
const JWT_SECRET = process.env.JWT_SECRET || 'MyApp-Super-Secret-Key-2024';
const BOOKING_SERVICE_URL = process.env.BOOKING_SERVICE_URL || 'http://localhost:7000';

app.use(cors());
app.use(express.json());

// JWT Authentication middleware
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json(createResponse(false, null, 'Access token required', 'MISSING_TOKEN'));
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json(createResponse(false, null, 'Invalid or expired token', 'INVALID_TOKEN'));
  }
};

// Common response wrapper
const createResponse = (success, data = null, message = '', error = null) => ({
  success,
  message,
  data,
  error,
  timestamp: new Date().toISOString()
});

// Hotel search API - Protected
app.get('/api/hotels/search', authenticateToken, async (req, res) => {
  try {
    const response = await axios.get(`${SEARCH_SERVICE_URL}/search/hotels`, {
      params: req.query,
      headers: {
        'Authorization': req.headers['authorization']
      }
    });
    
    res.json(createResponse(true, response.data, 'Hotels retrieved successfully'));
  } catch (error) {
    console.error('Search API error:', error.message);
    res.status(500).json(createResponse(false, null, 'Failed to search hotels', error.message));
  }
});

// Hotel filters API - Protected
app.get('/api/hotels/filters', authenticateToken, async (req, res) => {
  try {
    const response = await axios.get(`${SEARCH_SERVICE_URL}/search/filters`, {
      params: req.query,
      headers: {
        'Authorization': req.headers['authorization']
      }
    });
    
    res.json(createResponse(true, response.data, 'Filters retrieved successfully'));
  } catch (error) {
    console.error('Filters API error:', error.message);
    res.status(500).json(createResponse(false, null, 'Failed to get filters', error.message));
  }
});

// Cities search API - Protected
app.get('/api/cities/search', authenticateToken, async (req, res) => {
  try {
    const response = await axios.get(`${SEARCH_SERVICE_URL}/search/cities`, {
      params: req.query,
      headers: {
        'Authorization': req.headers['authorization']
      }
    });
    
    res.json(createResponse(true, response.data, 'Cities retrieved successfully'));
  } catch (error) {
    console.error('Cities API error:', error.message);
    res.status(500).json(createResponse(false, null, 'Failed to search cities', error.message));
  }
});

// Get booked rooms API - Protected
app.get('/api/booking/booked-rooms', authenticateToken, async (req, res) => {
  try {
    // Forward request to booking service
    const response = await axios.get(`${BOOKING_SERVICE_URL}/booking/booked-rooms`, {
      params: req.query,
      headers: {
        'Authorization': req.headers['authorization']
      }
    });
    
    // Get sparse data from booking service
    const sparseData = response.data.data || [];
    
    // Parse request parameters to fill gaps
    const { checkin_date, checkout_date, room_types } = req.query;
    const roomTypesArray = room_types.split(',').map(rt => rt.trim());
    
    // Generate all dates in range
    const dates = [];
    const start = new Date(checkin_date);
    const end = new Date(checkout_date);
    
    for (let d = new Date(start); d < end; d.setDate(d.getDate() + 1)) {
      dates.push(d.toISOString().split('T')[0]);
    }
    
    // Create complete data structure
    const completeData = [];
    
    // Create lookup for existing bookings
    const bookingLookup = {};
    sparseData.forEach(booking => {
      const key = `${booking.booking_date}_${booking.room_type_code}`;
      bookingLookup[key] = booking.booked_count;
    });
    
    // Fill complete data for all dates and room types
    dates.forEach(date => {
      roomTypesArray.forEach(roomType => {
        const key = `${date}_${roomType}`;
        const bookedCount = bookingLookup[key] || 0;
        
        completeData.push({
          booking_date: date,
          room_type_code: roomType,
          booked_count: bookedCount
        });
      });
    });
    
    res.json(createResponse(true, completeData, 'Booked rooms retrieved successfully'));
    
  } catch (error) {
    console.error('Booked rooms API error:', error.message);
    res.status(500).json(createResponse(false, null, 'Failed to get booked rooms', error.message));
  }
});

// Book hotel API - Protected
app.post('/api/booking/book-hotel', authenticateToken, async (req, res) => {
  try {
    // Basic validation - check if request body exists
    if (!req.body || Object.keys(req.body).length === 0) {
      return res.status(400).json(createResponse(false, null, 'Request body is required', 'MISSING_BODY'));
    }

    // Forward request to booking service
    const response = await axios.post(`${BOOKING_SERVICE_URL}/booking/book-hotel`, req.body, {
      headers: {
        'Authorization': req.headers['authorization'],
        'Content-Type': 'application/json'
      }
    });
    
    res.json(createResponse(true, response.data, 'Hotel booked successfully'));
    
  } catch (error) {
    console.error('Book hotel API error:', error.message);
    
    // Forward booking service errors with proper status codes
    if (error.response) {
      res.status(error.response.status).json(createResponse(false, null, 'Booking failed', error.response.data));
    } else {
      res.status(500).json(createResponse(false, null, 'Failed to book hotel', error.message));
    }
  }
});

// Health check - Unprotected
app.get('/health', (req, res) => {
  res.json(createResponse(true, { service: 'nodejs-bff', status: 'healthy' }, 'Service is running'));
});

app.listen(PORT, () => {
  console.log(`BFF server running on port ${PORT}`);
});

















