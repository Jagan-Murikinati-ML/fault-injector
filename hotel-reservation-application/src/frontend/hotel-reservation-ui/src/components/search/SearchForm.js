import React, { useState } from 'react';
import CityAutocomplete from './CityAutocomplete';

const SearchForm = ({ onSearch, loading }) => {
  // Helper function to format date as YYYY-MM-DD
  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };

  // Calculate default dates
  const today = new Date();
  const checkinDate = new Date(today);
  checkinDate.setDate(today.getDate() + 2);
  
  const checkoutDate = new Date(today);
  checkoutDate.setDate(today.getDate() + 4);

  const [searchParams, setSearchParams] = useState({
    location: 'Mumbai',
    checkin_date: formatDate(checkinDate),
    checkout_date: formatDate(checkoutDate),
    guests: 2
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLocationChange = (location) => {
    console.log('SearchForm: location changed to:', location);
    setSearchParams(prev => ({
      ...prev,
      location: location
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchParams.location && searchParams.checkin_date && searchParams.checkout_date) {
      onSearch(searchParams);
    }
  };

  return (
    <div className="search-card">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Location</label>
          <CityAutocomplete
            value={searchParams.location}
            onChange={handleLocationChange}
            placeholder="Enter city name"
          />
        </div>

        <div className="form-group">
          <label>Check-in Date</label>
          <input
            type="date"
            name="checkin_date"
            value={searchParams.checkin_date}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Check-out Date</label>
          <input
            type="date"
            name="checkout_date"
            value={searchParams.checkout_date}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Guests</label>
          <select
            name="guests"
            value={searchParams.guests}
            onChange={handleInputChange}
          >
            {[1,2,3,4,5,6,7,8].map(num => (
              <option key={num} value={num}>{num} Guest{num > 1 ? 's' : ''}</option>
            ))}
          </select>
        </div>
      </form>
      
      <button 
        type="submit" 
        className="search-button"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? 'Searching...' : 'Search Hotels'}
      </button>
    </div>
  );
};

export default SearchForm;







