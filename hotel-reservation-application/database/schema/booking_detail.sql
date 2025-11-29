
-- Complete booking information (all booking data + additional details)
CREATE TABLE booking_details (
    booking_detail_id BIGSERIAL PRIMARY KEY,
    booking_id BIGINT NOT NULL REFERENCES booking_info(booking_id) ON DELETE CASCADE,
    
    -- All booking info duplicated for complete record
    user_id VARCHAR(50), -- Changed from BIGINT to VARCHAR for username
    hotel_id VARCHAR(50) NOT NULL,
    checkin_date DATE NOT NULL,
    checkout_date DATE NOT NULL,
    total_guests INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    booking_status VARCHAR(20) NOT NULL,
    
    -- Contact info
    guest_name VARCHAR(100) NOT NULL,
    guest_email VARCHAR(100) NOT NULL,
    guest_phone VARCHAR(20),
    special_requests TEXT,
    
    -- Additional details
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_details JSONB DEFAULT '{}',
    payment_status VARCHAR(20) DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'PAID', 'FAILED', 'REFUNDED')),
    payment_method VARCHAR(30),
    payment_reference VARCHAR(100),
    
    -- Cancellation policy
    cancellation_policy_type VARCHAR(20) CHECK (cancellation_policy_type IN ('FREE', 'PARTIAL_REFUND', 'NON_REFUNDABLE')),
    free_cancellation_hours INTEGER,
    cancellation_fee_percentage DECIMAL(5,2),
    cancellation_deadline TIMESTAMP,
    refund_policy TEXT,
    
    -- Processing info
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_booking_details_booking_id ON booking_details(booking_id);
CREATE INDEX idx_booking_details_invoice ON booking_details(invoice_number);


