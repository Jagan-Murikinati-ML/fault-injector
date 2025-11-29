import httpx
import os
import time
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta

class BookingService:
    """
    Service to handle booking-related operations
    """
    
    def __init__(self, db):
        self.db = db
        self.search_service_url = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8000")
    
    async def check_room_availability(self, hotel_id: str, checkin_date: str, checkout_date: str, rooms_needed: List[Dict]) -> bool:
        """Check if requested rooms are available"""
        try:
            # Get hotel details from search service
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.search_service_url}/hotels/{hotel_id}")
                
                if response.status_code != 200:
                    raise ValueError("Failed to get hotel data")
                
                hotel_data = response.json()
                hotel = hotel_data.get("hotel")
                
                if not hotel:
                    raise ValueError(f"Hotel {hotel_id} not found")
                
                room_types = hotel.get("room_types", [])
            
            # Get booked rooms for the date range
            room_type_codes = list(set(room['room_type_code'] for room in rooms_needed))
            booked_rooms = await self.get_booked_rooms(hotel_id, checkin_date, checkout_date, room_type_codes)
            
            # Create booked rooms lookup by date and room type
            booked_lookup = {}
            for booking in booked_rooms:
                key = f"{booking['booking_date']}_{booking['room_type_code']}"
                booked_lookup[key] = booking['booked_count']
            
            # Check availability for each requested room
            for room_request in rooms_needed:
                room_type_code = room_request['room_type_code']
                booking_date = room_request['booking_date']
                rooms_count = room_request['rooms_count']
                
                # Find room type in hotel data
                room_type_info = next((rt for rt in room_types if rt['type'] == room_type_code), None)
                if not room_type_info:
                    raise ValueError(f"Room type {room_type_code} not available at this hotel")
                
                total_rooms = room_type_info.get('total_rooms', 0)
                key = f"{booking_date}_{room_type_code}"
                booked_count = booked_lookup.get(key, 0)
                available_rooms = total_rooms - booked_count
                
                if rooms_count > available_rooms:
                    raise ValueError(f"Only {available_rooms} {room_type_code} rooms available on {booking_date}")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Availability check failed: {str(e)}")
    
    async def get_booked_rooms(
        self, 
        hotel_id: str, 
        checkin_date: str, 
        checkout_date: str,
        room_types: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get booked rooms count for a hotel within a date range.
        Returns sparse data - only dates and room types that have bookings.
        
        Args:
            hotel_id: Hotel ID
            checkin_date: Check-in date (YYYY-MM-DD)
            checkout_date: Check-out date (YYYY-MM-DD)
            room_types: List of room type codes
            
        Returns:
            List of dictionaries with booking_date, room_type_code, and booked_count
        """
        
        # Validate dates
        try:
            checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
            checkout = datetime.strptime(checkout_date, "%Y-%m-%d")
            
            # Check if checkin date is in the past
            if checkin.date() < datetime.now().date():
                raise ValueError("Check-in date cannot be in the past")
            
            if checkout <= checkin:
                raise ValueError("Checkout date must be after checkin date")
                
        except ValueError as e:
            raise ValueError(f"Invalid date format: {str(e)}")
        
        # SQL query to get booked rooms
        # Only returns rows where bookings exist
        query = """
            SELECT 
                booking_date,
                room_type_code,
                SUM(rooms_booked) as booked_count
            FROM 
                booked_rooms
            WHERE 
                hotel_id = $1
                AND booking_date >= $2
                AND booking_date < $3
                AND room_type_code = ANY($4)
            GROUP BY 
                booking_date, 
                room_type_code
            ORDER BY 
                booking_date, 
                room_type_code;
        """
        
        # Execute query
        rows = await self.db.fetch(
            query, 
            hotel_id, 
            checkin,  # Use datetime object instead of string
            checkout, # Use datetime object instead of string
            room_types
        )
        
        # Convert to list of dictionaries
        result = []
        for row in rows:
            result.append({
                "booking_date": row["booking_date"].isoformat(),
                "room_type_code": row["room_type_code"],
                "booked_count": row["booked_count"]
            })
            
        return result

    async def book_hotel(self, booking_request: dict) -> dict:
        """
        Book a hotel with transaction support and availability validation
        """
        # Validate room availability before booking
        await self.check_room_availability(
            booking_request['hotel_id'],
            booking_request['checkin_date'].isoformat(),
            booking_request['checkout_date'].isoformat(),
            booking_request['rooms']
        )
        
        async with self.db.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    # Calculate total amount and other details
                    total_nights = (booking_request['checkout_date'] - booking_request['checkin_date']).days
                    total_rooms = sum(room['rooms_count'] for room in booking_request['rooms'])
                    total_amount = sum(room['rooms_count'] * room['cost_per_room_per_night'] for room in booking_request['rooms'])
                    
                    # Generate invoice number
                    invoice_number = f"INV-{booking_request['hotel_id']}-{int(time.time())}"
                    
                    # Calculate cancellation deadline BEFORE using it
                    checkin_datetime = datetime.combine(booking_request['checkin_date'], datetime.min.time())
                    cancellation_deadline = checkin_datetime - timedelta(hours=booking_request['cancellation_policy']['free_cancellation_hours'])
                    
                    # Create detailed invoice data
                    invoice_details = {
                        "invoice_number": invoice_number,
                        "issue_date": datetime.now().isoformat(),
                        "due_date": booking_request['checkin_date'].isoformat(),
                        "billing_details": {
                            "guest_name": booking_request['guest_details']['guest_name'],
                            "guest_email": booking_request['guest_details']['guest_email'],
                            "guest_phone": booking_request['guest_details'].get('guest_phone')
                        },
                        "hotel_details": {
                            "hotel_id": booking_request['hotel_id'],
                            "checkin_date": booking_request['checkin_date'].isoformat(),
                            "checkout_date": booking_request['checkout_date'].isoformat(),
                            "total_nights": total_nights
                        },
                        "room_breakdown": [
                            {
                                "room_type": room['room_type_code'],
                                "booking_date": room['booking_date'].isoformat(),
                                "rooms_count": room['rooms_count'],
                                "rate_per_room": float(room['cost_per_room_per_night']),
                                "subtotal": float(room['rooms_count'] * room['cost_per_room_per_night'])
                            }
                            for room in booking_request['rooms']
                        ],
                        "pricing_summary": {
                            "subtotal": float(total_amount),
                            "taxes": 0.0,
                            "total_amount": float(total_amount),
                            "currency": booking_request['currency']
                        },
                        "payment_info": {
                            "payment_status": "PAID",
                            "payment_method": "ONLINE",
                            "transaction_id": f"TXN-{int(time.time())}"
                        },
                        "cancellation_info": {
                            "policy_type": booking_request['cancellation_policy']['cancellation_policy_type'],
                            "free_cancellation_hours": booking_request['cancellation_policy']['free_cancellation_hours'],
                            "cancellation_fee_percentage": float(booking_request['cancellation_policy']['cancellation_fee_percentage']),
                            "cancellation_deadline": cancellation_deadline.isoformat(),
                            "refund_policy": booking_request['cancellation_policy']['refund_policy'],
                            "cancellation_status": "NOT_CANCELLED",
                            "potential_refund_amount": float(total_amount) if booking_request['cancellation_policy']['cancellation_policy_type'] == 'FREE' else 0.0,
                            "cancellation_terms": f"Free cancellation until {cancellation_deadline.strftime('%Y-%m-%d %H:%M:%S')}. After that, {float(booking_request['cancellation_policy']['cancellation_fee_percentage'])}% cancellation fee applies."
                        }
                    }
                    
                    # Insert into booking_info
                    booking_query = """
                        INSERT INTO booking_info (
                            hotel_id, user_id, checkin_date, checkout_date, 
                            total_nights, total_rooms, total_guests, total_amount, currency, 
                            booking_status, payment_status
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        RETURNING booking_id
                    """
                    
                    booking_id = await conn.fetchval(
                        booking_query,
                        booking_request['hotel_id'],
                        booking_request['user_id'],
                        booking_request['checkin_date'],
                        booking_request['checkout_date'],
                        total_nights,
                        total_rooms,
                        booking_request['total_guests'],
                        total_amount,
                        booking_request['currency'],
                        'CONFIRMED',
                        'PAID'
                    )
                    
                    # Insert into booking_details
                    # TODO: Send complete booking data to Kafka topic instead
                    details_query = """
                        INSERT INTO booking_details (
                            booking_id, user_id, hotel_id, checkin_date, checkout_date,
                            total_guests, total_amount, currency, booking_status,
                            guest_name, guest_email, guest_phone, special_requests,
                            invoice_number, invoice_details, payment_status,
                            cancellation_policy_type, free_cancellation_hours,
                            cancellation_fee_percentage, cancellation_deadline, refund_policy
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
                    """
                    
                    await conn.execute(
                        details_query,
                        booking_id,
                        booking_request['user_id'],
                        booking_request['hotel_id'],
                        booking_request['checkin_date'],
                        booking_request['checkout_date'],
                        booking_request['total_guests'],
                        total_amount,
                        booking_request['currency'],
                        'CONFIRMED',
                        booking_request['guest_details']['guest_name'],
                        booking_request['guest_details']['guest_email'],
                        booking_request['guest_details'].get('guest_phone'),
                        booking_request.get('special_requests'),
                        invoice_number,
                        json.dumps(invoice_details),
                        'PAID',
                        booking_request['cancellation_policy']['cancellation_policy_type'],
                        booking_request['cancellation_policy']['free_cancellation_hours'],
                        booking_request['cancellation_policy']['cancellation_fee_percentage'],
                        cancellation_deadline,
                        booking_request['cancellation_policy']['refund_policy']
                    )
                    
                    # Insert into booked_rooms for each room booking
                    rooms_query = """
                        INSERT INTO booked_rooms (
                            hotel_id, room_type_code, booking_date, rooms_booked,
                            cost_per_room_per_night, booking_id
                        ) VALUES ($1, $2, $3, $4, $5, $6)
                    """
                    
                    for room in booking_request['rooms']:
                        await conn.execute(
                            rooms_query,
                            booking_request['hotel_id'],
                            room['room_type_code'],
                            room['booking_date'],
                            room['rooms_count'],
                            room['cost_per_room_per_night'],
                            booking_id
                        )
                    
                    return {
                        "booking_id": booking_id,
                        "hotel_id": booking_request['hotel_id'],
                        "user_id": booking_request['user_id'],
                        "checkin_date": booking_request['checkin_date'].isoformat(),
                        "checkout_date": booking_request['checkout_date'].isoformat(),
                        "total_nights": total_nights,
                        "total_rooms": total_rooms,
                        "total_amount": float(total_amount),
                        "currency": booking_request['currency'],
                        "booking_status": "CONFIRMED",
                        "payment_status": "PAID"
                    }
                    
                except Exception as e:
                    raise Exception(f"Booking failed: {str(e)}")























