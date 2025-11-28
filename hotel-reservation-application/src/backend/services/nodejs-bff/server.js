const express = require('express');
const axios = require('axios');
const cors = require('cors');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 3000;
const SEARCH_SERVICE_URL = process.env.SEARCH_SERVICE_URL || 'http://localhost:8000';
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://localhost:9000';
const JWT_SECRET = process.env.JWT_SECRET || 'MyApp-Super-Secret-Key-2024';

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

// Health check - Unprotected
app.get('/health', (req, res) => {
  res.json(createResponse(true, { service: 'nodejs-bff', status: 'healthy' }, 'Service is running'));
});

app.listen(PORT, () => {
  console.log(`BFF server running on port ${PORT}`);
});












