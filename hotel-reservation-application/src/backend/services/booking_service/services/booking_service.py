import httpx
import os
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
from kafka import KafkaProducer
import logging

logger = logging.getLogger(__name__)

class BookingService:
    """
    Service to handle booking-related operations
    """
    
    def __init__(self, db):
        self.db = db
        self.search_service_url = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8000")
        
        # Initialize Kafka producer
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
    
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
        try:
            logger.info(f"Starting booking for hotel_id: {booking_request.get('hotel_id')}")
            logger.info(f"Booking request data: {booking_request}")
            
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
                        # Calculate totals
                        total_nights = (booking_request['checkout_date'] - booking_request['checkin_date']).days
                        total_rooms = sum(room['rooms_count'] for room in booking_request['rooms'])
                        total_amount = sum(room['rooms_count'] * room['cost_per_room_per_night'] for room in booking_request['rooms'])
                        
                        # Calculate cancellation deadline
                        checkin_datetime = datetime.combine(booking_request['checkin_date'], datetime.min.time())
                        cancellation_deadline = checkin_datetime - timedelta(hours=booking_request['cancellation_policy']['free_cancellation_hours'])
                        
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
                        
                        # Send booking event to Kafka for post-processing
                        booking_event = {
                            "message_version": "v1",
                            "event_type": "booking_created",
                            "timestamp": datetime.now().isoformat(),
                            "source_service": "booking-service",
                            "booking_id": booking_id,
                            "hotel_id": booking_request['hotel_id'],
                            "user_id": booking_request['user_id'],
                            "checkin_date": booking_request['checkin_date'].isoformat(),
                            "checkout_date": booking_request['checkout_date'].isoformat(),
                            "total_nights": total_nights,
                            "total_guests": booking_request['total_guests'],
                            "total_amount": float(total_amount),
                            "currency": booking_request['currency'],
                            "booking_status": "CONFIRMED",
                            "guest_details": booking_request['guest_details'],
                            "rooms": [
                                {
                                    "room_type_code": room['room_type_code'],
                                    "booking_date": room['booking_date'].isoformat() if hasattr(room['booking_date'], 'isoformat') else room['booking_date'],
                                    "rooms_count": room['rooms_count'],
                                    "cost_per_room_per_night": float(room['cost_per_room_per_night'])
                                }
                                for room in booking_request['rooms']
                            ],
                            "special_requests": booking_request.get('special_requests'),
                            "cancellation_policy": {
                                "cancellation_policy_type": booking_request['cancellation_policy']['cancellation_policy_type'],
                                "free_cancellation_hours": booking_request['cancellation_policy']['free_cancellation_hours'],
                                "cancellation_fee_percentage": float(booking_request['cancellation_policy']['cancellation_fee_percentage']),
                                "refund_policy": booking_request['cancellation_policy']['refund_policy']
                            }
                        }
                        
                        # Send to Kafka
                        self.kafka_producer.send(
                            'booking-events',
                            key=str(booking_id),
                            value=booking_event
                        )
                        self.kafka_producer.flush()
                        
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
        except Exception as e:
            logger.error(f"Booking failed with error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise Exception(f"Booking failed: {str(e)}")

    async def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get basic booking information from booking_info table
        """
        query = """
            SELECT 
                booking_id, hotel_id, checkin_date, checkout_date,
                total_guests, total_amount, currency, booking_status
            FROM booking_info
            WHERE user_id = $1
            ORDER BY checkin_date DESC
        """
        
        rows = await self.db.fetch(query, user_id)
        
        current_bookings = []
        past_bookings = []
        today = datetime.now().date()
        
        for row in rows:
            booking = {
                "booking_id": row["booking_id"],
                "hotel_id": row["hotel_id"],
                "checkin_date": row["checkin_date"].isoformat(),
                "checkout_date": row["checkout_date"].isoformat(),
                "total_guests": row["total_guests"],
                "total_amount": float(row["total_amount"]),
                "currency": row["currency"],
                "booking_status": row["booking_status"]
            }
            
            if row["checkin_date"] >= today:
                current_bookings.append(booking)
            else:
                past_bookings.append(booking)
        
        return {
            "current_bookings": current_bookings,
            "past_bookings": past_bookings
        }

    async def get_booking_details(self, booking_id: int, user_id: str) -> Dict[str, Any]:
        """
        Get complete booking details from booking_details table
        """
        query = """
            SELECT * FROM booking_details
            WHERE booking_id = $1 AND user_id = $2
        """
        
        row = await self.db.fetchrow(query, booking_id, user_id)
        
        if not row:
            return None
        
        # Convert row to dict and handle data type conversions
        booking_details = dict(row)
        
        # Convert dates to ISO format
        if booking_details.get('checkin_date'):
            booking_details['checkin_date'] = booking_details['checkin_date'].isoformat()
        if booking_details.get('checkout_date'):
            booking_details['checkout_date'] = booking_details['checkout_date'].isoformat()
        if booking_details.get('cancellation_deadline'):
            booking_details['cancellation_deadline'] = booking_details['cancellation_deadline'].isoformat()
        if booking_details.get('created_at'):
            booking_details['created_at'] = booking_details['created_at'].isoformat()
        if booking_details.get('updated_at'):
            booking_details['updated_at'] = booking_details['updated_at'].isoformat()
        
        # Convert Decimal to float
        if booking_details.get('total_amount'):
            booking_details['total_amount'] = float(booking_details['total_amount'])
        if booking_details.get('cancellation_fee_percentage'):
            booking_details['cancellation_fee_percentage'] = float(booking_details['cancellation_fee_percentage'])
        
        return booking_details



