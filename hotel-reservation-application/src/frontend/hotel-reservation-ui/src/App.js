import React, { useState, useEffect } from 'react';
import './styles/App.css';
import SearchForm from './components/search/SearchForm';
import HotelList from './components/hotel/HotelList';
import FilterPanel from './components/search/FilterPanel';
import { hotelService } from './services/hotelService';
import HotelDetailsPage from './components/hotel/HotelDetailsPage';
import AuthContainer from './components/auth/AuthContainer';

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Existing hotel search state
  const [hotels, setHotels] = useState([]);
  const [filteredHotels, setFilteredHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [lastSearchParams, setLastSearchParams] = useState(null);
  const [activeFilters, setActiveFilters] = useState({
    price_min: '',
    price_max: '',
    rating_min: '',
    room_types: [],
    amenities: [],
    policies: [],
    guests: 0
  });

  const [filters, setFilters] = useState({
    priceRanges: [],
    ratings: [],
    amenities: {},
    policies: {},
    roomTypes: [],
    maxGuests: 0
  });

  const fetchFilters = async (searchParams) => {
    try {
      const filtersData = await hotelService.getFilters(searchParams);
      // Extract data from BFF response wrapper
      setFilters(filtersData.data || filtersData);
    } catch (error) {
      console.error('Failed to fetch filters:', error);
    }
  };

  // Check if user is already logged in on app load
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        setIsAuthenticated(true);
        setUser(JSON.parse(userData));
      } catch (error) {
        // Invalid user data, clear storage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setAuthLoading(false);
  }, []);

  // Handle successful authentication
  const handleAuthSuccess = (authData) => {
    setIsAuthenticated(true);
    setUser(authData.user);
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
    // Reset search state
    setHotels([]);
    setFilteredHotels([]);
    setHasSearched(false);
    setSelectedHotel(null);
    // Reset filters
    setFilters({
      priceRanges: [],
      ratings: [],
      amenities: {},
      policies: {},
      roomTypes: [],
      maxGuests: 0
    });
    setActiveFilters({
      price_min: '',
      price_max: '',
      rating_min: '',
      room_types: [],
      amenities: [],
      policies: [],
      guests: 0
    });
  };

  // Existing hotel search functions
  const handleSearch = async (searchParams) => {
    setLoading(true);
    setLastSearchParams(searchParams);
    
    try {
      const results = await hotelService.searchHotels(searchParams);
      // Extract hotels from nested BFF response structure
      const hotelsData = results.data?.hotels || results.hotels || results.data || results;
      setHotels(hotelsData);
      setFilteredHotels(hotelsData);
      setHasSearched(true);
      
      // Fetch filters with full search params including active filters
      await fetchFilters({...searchParams, ...activeFilters});
    } catch (error) {
      console.error('Search failed:', error);
      setHotels([]);
      setFilteredHotels([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setActiveFilters(newFilters);
    
    let filtered = hotels.filter(hotel => {
      const price = hotel.current_pricing?.min_price;
      const rating = hotel.current_rating?.avg_rating;
      
      // Price filter
      if (newFilters.price_min && price < newFilters.price_min) {
        return false;
      }
      if (newFilters.price_max && price > newFilters.price_max) {
        return false;
      }
      
      // Rating filter
      if (newFilters.rating_min && rating < newFilters.rating_min) {
        return false;
      }
      
      // Amenities filter
      if (newFilters.amenities && newFilters.amenities.length > 0) {
        const hasAllAmenities = newFilters.amenities.every(amenity => {
          switch(amenity) {
            case 'breakfast':
              return hotel.hotel_amenities?.complementary_breakfast;
            case 'parking':
              return hotel.hotel_amenities?.parking_available;
            case 'wifi':
              return hotel.hotel_amenities?.wifi;
            case 'pool':
              return hotel.hotel_amenities?.pool;
            case 'gym':
              return hotel.hotel_amenities?.gym;
            default:
              return false;
          }
        });
        if (!hasAllAmenities) {
          return false;
        }
      }
      
      // Policies filter
      if (newFilters.policies && newFilters.policies.length > 0) {
        const hasAllPolicies = newFilters.policies.every(policy => {
          switch(policy) {
            case 'free_cancellation':
              return hotel.hotel_policies?.free_cancellation;
            case 'no_prepayment':
              return !hotel.hotel_policies?.prepayment_needed;
            case 'pets_allowed':
              return hotel.hotel_policies?.pets_allowed;
            default:
              return false;
          }
        });
        if (!hasAllPolicies) {
          return false;
        }
      }
      
      // Room type filter
      if (newFilters.room_types && newFilters.room_types.length > 0) {
        const hasRoomType = newFilters.room_types.some(roomType => 
          hotel.room_types?.some(room => room.type === roomType)
        );
        if (!hasRoomType) {
          return false;
        }
      }
      
      // Guests/occupancy filter
      if (newFilters.guests) {
        const maxOccupancy = Math.max(...(hotel.room_types?.map(room => room.max_occupancy) || [0]));
        if (maxOccupancy < newFilters.guests) {
          return false;
        }
      }
      
      return true;
    });
    
    setFilteredHotels(filtered);
  };

  const handleCheckAvailability = (hotel) => {
    setSelectedHotel(hotel);
  };

  const handleCloseDetails = () => {
    setSelectedHotel(null);
  };

  const handleBookingConfirm = (bookingData) => {
    console.log('Booking confirmed:', bookingData);
    setSelectedHotel(null);
    // Here you would typically send booking data to backend
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Show auth pages if not authenticated
  if (!isAuthenticated) {
    return <AuthContainer onAuthSuccess={handleAuthSuccess} />;
  }

  // Show hotel search interface if authenticated
  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>Hotel Reservation Application</h1>
          <div className="user-info">
            <span className="welcome-text">Welcome, {user?.firstName || user?.username}!</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>
      
      <main className="main-container">
        <SearchForm onSearch={handleSearch} loading={loading} />
        
        {selectedHotel && (
          <HotelDetailsPage
            hotel={selectedHotel}
            searchParams={lastSearchParams}
            onClose={handleCloseDetails}
            onBookingConfirm={handleBookingConfirm}
          />
        )}
        
        {hasSearched && (
          <div className="results-container">
            <FilterPanel 
              filters={filters}
              activeFilters={activeFilters}
              onFilterChange={handleFilterChange}
              hotelCount={filteredHotels.length}
            />
            
            <HotelList 
              hotels={filteredHotels}
              loading={loading}
              onCheckAvailability={handleCheckAvailability}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;















