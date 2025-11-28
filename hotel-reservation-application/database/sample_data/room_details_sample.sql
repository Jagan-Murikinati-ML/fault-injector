-- Sample room details for the 2 hotels from Elasticsearch
INSERT INTO room_details (hotel_id, room_type_code, total_rooms, base_price_per_night, currency, room_type_name, max_occupancy, is_active) VALUES

-- Grand Mumbai Hotel (hotel_1) - min_total_price: 5000
('hotel_1', 'standard', 20, 5000.00, 'INR', 'Standard Room', 2, TRUE),
('hotel_1', 'deluxe', 15, 7500.00, 'INR', 'Deluxe Room', 3, TRUE),
('hotel_1', 'suite', 5, 12000.00, 'INR', 'Suite Room', 4, TRUE),

-- Luxury Delhi Resort (hotel_2) - min_total_price: 8000
('hotel_2', 'standard', 25, 8000.00, 'INR', 'Standard Room', 2, TRUE),
('hotel_2', 'deluxe', 18, 12000.00, 'INR', 'Deluxe Room', 3, TRUE),
('hotel_2', 'suite', 8, 20000.00, 'INR', 'Suite Room', 4, TRUE),
('hotel_2', 'presidential', 2, 35000.00, 'INR', 'Presidential Suite', 6, TRUE);
