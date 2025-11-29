# Hotel Booking Service

FastAPI-based microservice for managing hotel bookings and room availability.

## Features

- Get booked rooms count for hotels within a date range
- JWT authentication
- PostgreSQL database integration
- Async/await support with asyncpg

## API Endpoints

### GET /booking/booked-rooms

Get booked rooms count for a hotel within a date range.

**Query Parameters:**
- `hotel_id` (required): Hotel ID
- `checkin_date` (required): Check-in date (YYYY-MM-DD)
- `checkout_date` (required): Check-out date (YYYY-MM-DD)
- `room_types` (required): Comma-separated room type codes (e.g., "DELUXE,SUITE,STANDARD")

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`

**Response (Sparse - only existing bookings):**
```json
{
  "success": true,
  "data": [
    {
      "booking_date": "2024-12-01",
      "room_type_code": "DELUXE",
      "booked_count": 5
    },
    {
      "booking_date": "2024-12-03",
      "room_type_code": "SUITE",
      "booked_count": 2
    }
  ],
  "message": "Booked rooms retrieved successfully"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "booking-service"
}
```

## Environment Variables

- `DB_HOST`: PostgreSQL host (default: localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: Database name (default: hotel_booking_db)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: password)
- `JWT_SECRET`: JWT secret key (default: MyApp-Super-Secret-Key-2024)

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Running with Docker

```bash
# Build image
docker build -t booking-service .

# Run container
docker run -p 8001:8001 \
  -e DB_HOST=postgres \
  -e DB_NAME=hotel_booking_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=password \
  -e JWT_SECRET=MyApp-Super-Secret-Key-2024 \
  booking-service
```

## Database Schema

The service uses the following tables:

### booked_rooms
- `booked_room_id`: Primary key
- `hotel_id`: Hotel identifier
- `room_type_code`: Room type code
- `booking_date`: Date of booking
- `rooms_booked`: Number of rooms booked
- `cost_per_room_per_night`: Cost per room
- `booking_id`: Reference to booking_info table

### booking_info
- `booking_id`: Primary key
- `hotel_id`: Hotel identifier
- `user_id`: User identifier (nullable for guest bookings)
- `checkin_date`: Check-in date
- `checkout_date`: Check-out date
- `total_nights`: Total nights
- `total_rooms`: Total rooms
- `total_amount`: Total amount
- `currency`: Currency code
- `booking_status`: Status (CONFIRMED, CANCELLED, FAILED)

## Notes

- Only returns bookings with status 'CONFIRMED'
- Returns sparse data (only dates/room types with bookings)
- BFF layer is responsible for filling missing dates/room types with 0

