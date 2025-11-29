# Booking Service Testing Guide

## Prerequisites

1. PostgreSQL database `hotel_booking_db` should exist
2. Tables `booking_info` and `booked_rooms` should be created
3. Booking service should be running on port 8001

## Starting the Booking Service

### Option 1: Using Docker Compose (Recommended)

```bash
# Start only the booking service and postgres
docker-compose up booking-service postgres

# Or start all services
docker-compose up
```

### Option 2: Running Locally (for development)

```bash
cd src/backend/services/booking_service

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=hotel_booking_db
export DB_USER=postgres
export DB_PASSWORD=password

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Testing with cURL

### 1. Health Check

```bash
curl http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "booking-service"
}
```

### 2. Get Booked Rooms (No Authentication Required - For Testing)

**Example 1: Basic Request**
```bash
curl -X GET "http://localhost:8001/booking/booked-rooms?hotel_id=H001&checkin_date=2024-12-01&checkout_date=2024-12-05&room_types=DELUXE,SUITE,STANDARD"
```

**Example 2: With Pretty Print (using jq)**
```bash
curl -X GET "http://localhost:8001/booking/booked-rooms?hotel_id=H001&checkin_date=2024-12-01&checkout_date=2024-12-05&room_types=DELUXE,SUITE,STANDARD" | jq
```

**Example 3: Different Hotel**
```bash
curl -X GET "http://localhost:8001/booking/booked-rooms?hotel_id=H002&checkin_date=2024-12-10&checkout_date=2024-12-15&room_types=DELUXE,SUITE"
```

**Expected Response (Sparse Data):**
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

**If No Bookings Found:**
```json
{
  "success": true,
  "data": [],
  "message": "Booked rooms retrieved successfully"
}
```

## Testing with PowerShell (Windows)

### Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
```

### Get Booked Rooms
```powershell
$uri = "http://localhost:8001/booking/booked-rooms?hotel_id=H001&checkin_date=2024-12-01&checkout_date=2024-12-05&room_types=DELUXE,SUITE,STANDARD"
Invoke-RestMethod -Uri $uri -Method Get | ConvertTo-Json -Depth 10
```

## Sample Test Data

To test the API, you need some data in the database. Here's a sample insert:

```sql
-- Insert a booking
INSERT INTO booking_info (hotel_id, user_id, checkin_date, checkout_date, total_nights, total_rooms, total_amount, booking_status)
VALUES ('H001', 1, '2024-12-01', '2024-12-05', 4, 2, 20000.00, 'CONFIRMED');

-- Get the booking_id (assuming it's 1)
-- Insert booked rooms
INSERT INTO booked_rooms (hotel_id, room_type_code, booking_date, rooms_booked, cost_per_room_per_night, booking_id)
VALUES 
  ('H001', 'DELUXE', '2024-12-01', 2, 2500.00, 1),
  ('H001', 'DELUXE', '2024-12-02', 2, 2500.00, 1),
  ('H001', 'DELUXE', '2024-12-03', 2, 2500.00, 1),
  ('H001', 'DELUXE', '2024-12-04', 2, 2500.00, 1);
```

## Checking Logs

### Docker Logs
```bash
# View booking service logs
docker-compose logs -f booking-service

# View last 100 lines
docker-compose logs --tail=100 booking-service
```

### Check if Service is Running
```bash
# Check running containers
docker-compose ps

# Check specific service
docker-compose ps booking-service
```

## Common Issues

### Issue 1: Connection Refused
**Problem:** `curl: (7) Failed to connect to localhost port 8001`

**Solution:**
- Check if service is running: `docker-compose ps`
- Check logs: `docker-compose logs booking-service`
- Restart service: `docker-compose restart booking-service`

### Issue 2: Database Connection Error
**Problem:** `asyncpg.exceptions.InvalidCatalogNameError: database "hotel_booking_db" does not exist`

**Solution:**
- Create the database manually:
```bash
docker exec -it hotel_postgres psql -U postgres -c "CREATE DATABASE hotel_booking_db;"
```

### Issue 3: Table Does Not Exist
**Problem:** `relation "booked_rooms" does not exist`

**Solution:**
- Run your existing schema script:
```bash
docker exec -i hotel_postgres psql -U postgres -d hotel_booking_db < database/schema/booked_rooms.sql
docker exec -i hotel_postgres psql -U postgres -d hotel_booking_db < database/schema/booking_info.sql
```

## API Documentation

Once the service is running, you can access the auto-generated API documentation:

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## Notes

- JWT authentication is currently **DISABLED** for testing purposes
- The API returns **sparse data** - only dates and room types with actual bookings
- Only bookings with status `CONFIRMED` are included in the results
- The BFF layer will fill in missing dates/room types with 0 booked count

