-- Tracks actual bookings per day per room type
CREATE TABLE booked_rooms (
    booked_room_id BIGSERIAL PRIMARY KEY,
    hotel_id VARCHAR(50) NOT NULL,
    room_type_code VARCHAR(50) NOT NULL,
    booking_date DATE NOT NULL,
    
    -- Booking details for this specific date
    rooms_booked INTEGER NOT NULL CHECK (rooms_booked > 0),
    cost_per_room_per_night DECIMAL(10,2) NOT NULL CHECK (cost_per_room_per_night > 0),
    
    -- Reference to main booking
    booking_id BIGINT NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(hotel_id, room_type_code, booking_date, booking_id)
);