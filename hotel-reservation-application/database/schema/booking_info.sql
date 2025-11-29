-- Main booking information
CREATE TABLE booking_info (
    booking_id BIGSERIAL PRIMARY KEY,
    
    -- Hotel and guest details
    hotel_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50), -- Changed from BIGINT to VARCHAR for username
    
    -- Stay details
    checkin_date DATE NOT NULL,
    checkout_date DATE NOT NULL,
    total_nights INTEGER NOT NULL CHECK (total_nights > 0),
    total_rooms INTEGER NOT NULL CHECK (total_rooms > 0),
    total_guests INTEGER NOT NULL CHECK (total_guests > 0),
    
    -- Pricing
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
    currency VARCHAR(3) DEFAULT 'INR',
    
    -- Status
    booking_status VARCHAR(20) DEFAULT 'CONFIRMED' CHECK (booking_status IN ('CONFIRMED', 'CANCELLED', 'FAILED')),
    payment_status VARCHAR(20) DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'PAID', 'FAILED', 'REFUNDED')),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_dates CHECK (checkout_date > checkin_date)
);

-- Indexes
CREATE INDEX idx_booking_info_user_id ON booking_info(user_id);
CREATE INDEX idx_booking_info_hotel_id ON booking_info(hotel_id);
CREATE INDEX idx_booking_info_status ON booking_info(booking_status);


