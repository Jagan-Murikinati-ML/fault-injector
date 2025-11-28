import React from 'react';

const FilterPanel = ({ filters, activeFilters, onFilterChange, hotelCount }) => {
  const handleFilterToggle = (filterType, filterValue) => {
    const newFilters = { ...activeFilters };
    
    if (!newFilters[filterType]) {
      newFilters[filterType] = [];
    }
    
    const index = newFilters[filterType].indexOf(filterValue);
    if (index > -1) {
      newFilters[filterType].splice(index, 1);
    } else {
      newFilters[filterType].push(filterValue);
    }
    
    onFilterChange(newFilters);
  };

  const handleRangeChange = (filterType, value) => {
    const newFilters = { ...activeFilters };
    newFilters[filterType] = value;
    onFilterChange(newFilters);
  };

  if (!filters) return null;

  return (
    <div className="filter-panel">
      <h3>Filters ({hotelCount} hotels found)</h3>
      
      {/* Price Range */}
      {filters.price_range && filters.price_range.max > 0 && (
        <div className="filter-section">
          <h4>Price Range</h4>
          <div className="range-inputs">
            <input
              type="number"
              placeholder="Min price"
              value={activeFilters.price_min || ''}
              onChange={(e) => handleRangeChange('price_min', e.target.value)}
            />
            <input
              type="number"
              placeholder="Max price"
              value={activeFilters.price_max || ''}
              onChange={(e) => handleRangeChange('price_max', e.target.value)}
            />
          </div>
          <p className="price-range-info">{filters.price_range.currency === 'INR' ? '₹' : filters.price_range.currency || '₹'}{filters.price_range.min} - {filters.price_range.currency === 'INR' ? '₹' : filters.price_range.currency || '₹'}{filters.price_range.max}</p>
        </div>
      )}

      {/* Rating Filter */}
      {filters.rating_range && filters.rating_range.max > 0 && (
        <div className="filter-section">
          <h4>Minimum Rating</h4>
          <select
            value={activeFilters.rating_min || ''}
            onChange={(e) => handleRangeChange('rating_min', e.target.value)}
          >
            <option value="">Any rating</option>
            <option value="1">1+ stars</option>
            <option value="2">2+ stars</option>
            <option value="3">3+ stars</option>
            <option value="4">4+ stars</option>
            <option value="5">5 stars</option>
          </select>
          <p>Available: {filters.rating_range.min} - {filters.rating_range.max} stars</p>
        </div>
      )}
      
      {/* Amenities Filters */}
      <div className="filter-section">
        <h4>Amenities</h4>
        
        {filters.amenities && (
          <div className="filter-options">
            {filters.amenities.breakfast > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.amenities?.includes('breakfast')}
                  onChange={() => handleFilterToggle('amenities', 'breakfast')}
                />
                Breakfast Included ({filters.amenities.breakfast})
              </label>
            )}
            
            {filters.amenities.parking > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.amenities?.includes('parking')}
                  onChange={() => handleFilterToggle('amenities', 'parking')}
                />
                Parking Available ({filters.amenities.parking})
              </label>
            )}
            
            {filters.amenities.wifi > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.amenities?.includes('wifi')}
                  onChange={() => handleFilterToggle('amenities', 'wifi')}
                />
                WiFi Available ({filters.amenities.wifi})
              </label>
            )}
            
            {filters.amenities.pool > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.amenities?.includes('pool')}
                  onChange={() => handleFilterToggle('amenities', 'pool')}
                />
                Pool Available ({filters.amenities.pool})
              </label>
            )}
            
            {filters.amenities.gym > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.amenities?.includes('gym')}
                  onChange={() => handleFilterToggle('amenities', 'gym')}
                />
                Gym Available ({filters.amenities.gym})
              </label>
            )}
          </div>
        )}
      </div>

      {/* Policies Filters */}
      <div className="filter-section">
        <h4>Policies</h4>
        
        {filters.policies && (
          <div className="filter-options">
            {filters.policies.free_cancellation > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.policies?.includes('free_cancellation')}
                  onChange={() => handleFilterToggle('policies', 'free_cancellation')}
                />
                Free Cancellation ({filters.policies.free_cancellation})
              </label>
            )}
            
            {filters.policies.no_prepayment > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.policies?.includes('no_prepayment')}
                  onChange={() => handleFilterToggle('policies', 'no_prepayment')}
                />
                No Prepayment ({filters.policies.no_prepayment})
              </label>
            )}
            
            {filters.policies.pets_allowed > 0 && (
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.policies?.includes('pets_allowed')}
                  onChange={() => handleFilterToggle('policies', 'pets_allowed')}
                />
                Pets Allowed ({filters.policies.pets_allowed})
              </label>
            )}
          </div>
        )}
      </div>

      {/* Room Type Filter */}
      <div className="filter-section">
        <h4>Room Type</h4>
        
        {filters.room_types && filters.room_types.length > 0 ? (
          <div className="filter-options">
            {filters.room_types.map(type => (
              <label key={type} className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={activeFilters.room_types?.includes(type)}
                  onChange={() => handleFilterToggle('room_types', type)}
                />
                {type}
              </label>
            ))}
          </div>
        ) : (
          <p className="no-filters">No room types available</p>
        )}
      </div>

      {/* Occupancy Filter */}
      <div className="filter-section">
        <h4>Maximum Guests</h4>
        <select
          value={activeFilters.guests || ''}
          onChange={(e) => handleRangeChange('guests', e.target.value)}
        >
          <option value="">Any occupancy</option>
          {[1,2,3,4,5,6,7,8].map(num => (
            <option key={num} value={num}>{num} Guest{num > 1 ? 's' : ''}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FilterPanel;








