#!/bin/bash

echo "Testing Search Service APIs..."
echo "================================"

# Wait for service to be ready
echo "Waiting for service to start..."
sleep 5

# Health check
echo -e "\n1. Health Check:"
curl -s http://localhost:8000/health | jq '.'

# Search hotels
echo -e "\n2. Search Hotels (Mumbai):"
curl -s "http://localhost:8000/search/hotels?location=Mumbai&checkin_date=2024-01-01&checkout_date=2024-01-02&guests=2&rooms=1&page=1&limit=3" | jq '.'

# Get filters
echo -e "\n3. Get Filters (Mumbai):"
curl -s "http://localhost:8000/search/filters?location=Mumbai&checkin_date=2024-01-01&checkout_date=2024-01-02&guests=2&rooms=1" | jq '.'

echo -e "\nAPI tests completed!"