#!/bin/bash

# Test script for Booking Service API

BASE_URL="http://localhost:8001"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Hotel Booking Service API Tests ===${NC}\n"

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
curl -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

# Test 2: Get Booked Rooms (JWT authentication disabled for testing)
echo -e "${YELLOW}Test 2: Get Booked Rooms${NC}"
echo "Note: JWT authentication is currently disabled for testing"

curl -X GET "$BASE_URL/booking/booked-rooms?hotel_id=H001&checkin_date=2024-12-01&checkout_date=2024-12-05&room_types=DELUXE,SUITE,STANDARD" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo -e "${GREEN}Tests completed!${NC}"

