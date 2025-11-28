import React, { useState, useEffect, useRef } from 'react';
import { hotelService } from '../../services/hotelService';

const CityAutocomplete = ({ value, onChange, placeholder = "Enter city name" }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  useEffect(() => {
    const searchCities = async () => {
      if (value.length < 2) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      setLoading(true);
      try {
        const response = await hotelService.searchCities(value);
        const cities = response.data?.cities || response.cities || [];
        setSuggestions(cities);
        setShowSuggestions(cities.length > 0);
      } catch (error) {
        console.error('Error fetching cities:', error);
        setSuggestions([]);
        setShowSuggestions(false);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(searchCities, 300); // Debounce
    return () => clearTimeout(timeoutId);
  }, [value]);

  const handleSuggestionClick = (city) => {
    onChange(city);
    setShowSuggestions(false);
  };

  const handleInputChange = (e) => {
    onChange(e.target.value);
  };

  const handleInputBlur = () => {
    // Delay hiding to allow click on suggestions
    setTimeout(() => setShowSuggestions(false), 200);
  };

  return (
    <div className="autocomplete-container">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={handleInputChange}
        onBlur={handleInputBlur}
        onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
        placeholder={placeholder}
        autoComplete="off"
      />
      
      {showSuggestions && (
        <div ref={suggestionsRef} className="suggestions-dropdown">
          {loading && <div className="suggestion-item loading">Searching...</div>}
          {!loading && suggestions.map((city, index) => (
            <div
              key={index}
              className="suggestion-item"
              onClick={() => handleSuggestionClick(city)}
            >
              {city}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CityAutocomplete;