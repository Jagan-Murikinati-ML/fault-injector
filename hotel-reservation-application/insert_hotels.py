from elasticsearch import Elasticsearch
import json

# Use the container network hostname
es = Elasticsearch("http://elasticsearch:9200")

# Extended hotel data from different locations
hotels_data = [
    # India - Mumbai
    {
        "id": "hotel_3",
        "name": "The Taj Mahal Palace Mumbai",
        "city": "Mumbai",
        "rating": {"avg_rating": 9.5},
        "pricing": {"min_total_price": 15000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Pool", "Gym", "Restaurant", "Bar"],
        "is_sponsored": True,
        "sponsorship": {"priority": 1}
    },
    # India - Delhi
    {
        "id": "hotel_4",
        "name": "The Imperial New Delhi",
        "city": "Delhi",
        "rating": {"avg_rating": 9.0},
        "pricing": {"min_total_price": 12000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Business Center"],
        "is_sponsored": False
    },
    # India - Bangalore
    {
        "id": "hotel_5",
        "name": "The Leela Palace Bangalore",
        "city": "Bangalore",
        "rating": {"avg_rating": 8.8},
        "pricing": {"min_total_price": 9000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Pool", "Spa", "Gym"],
        "is_sponsored": False
    },
    # India - Goa
    {
        "id": "hotel_6",
        "name": "Grand Hyatt Goa",
        "city": "Goa",
        "rating": {"avg_rating": 8.6},
        "pricing": {"min_total_price": 7500},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Beach Access", "Pool", "Spa"],
        "is_sponsored": True,
        "sponsorship": {"priority": 2}
    },
    # USA - New York
    {
        "id": "hotel_7",
        "name": "The Plaza New York",
        "city": "New York",
        "rating": {"avg_rating": 9.3},
        "pricing": {"min_total_price": 25000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": False,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Concierge"],
        "is_sponsored": True,
        "sponsorship": {"priority": 1}
    },
    # USA - Los Angeles
    {
        "id": "hotel_8",
        "name": "Beverly Hills Hotel",
        "city": "Los Angeles",
        "rating": {"avg_rating": 9.1},
        "pricing": {"min_total_price": 22000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Pool", "Spa", "Tennis Court"],
        "is_sponsored": False
    },
    # UK - London
    {
        "id": "hotel_9",
        "name": "The Ritz London",
        "city": "London",
        "rating": {"avg_rating": 9.4},
        "pricing": {"min_total_price": 30000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": False,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": False,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Restaurant", "Bar", "Concierge"],
        "is_sponsored": True,
        "sponsorship": {"priority": 1}
    },
    # France - Paris
    {
        "id": "hotel_10",
        "name": "Hotel Plaza Athénée Paris",
        "city": "Paris",
        "rating": {"avg_rating": 9.2},
        "pricing": {"min_total_price": 28000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Bar"],
        "is_sponsored": False
    },
    # Japan - Tokyo
    {
        "id": "hotel_11",
        "name": "The Peninsula Tokyo",
        "city": "Tokyo",
        "rating": {"avg_rating": 9.0},
        "pricing": {"min_total_price": 20000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": True,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Business Center"],
        "is_sponsored": False
    },
    # Australia - Sydney
    {
        "id": "hotel_12",
        "name": "Park Hyatt Sydney",
        "city": "Sydney",
        "rating": {"avg_rating": 8.9},
        "pricing": {"min_total_price": 18000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Pool", "Spa", "Harbor View"],
        "is_sponsored": True,
        "sponsorship": {"priority": 2}
    },
    # Budget hotels
    {
        "id": "hotel_13",
        "name": "Budget Inn Mumbai",
        "city": "Mumbai",
        "rating": {"avg_rating": 6.5},
        "pricing": {"min_total_price": 2000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": False,
            "pets_allowed": False,
            "lift_available": False,
            "alcohol_allowed": False
        },
        "policies": {
            "free_cancellation": False,
            "prepayment_needed": False
        },
        "facilities": ["WiFi"],
        "is_sponsored": False
    },
    {
        "id": "hotel_14",
        "name": "City Lodge Delhi",
        "city": "Delhi",
        "rating": {"avg_rating": 7.2},
        "pricing": {"min_total_price": 3500},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": False
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Restaurant"],
        "is_sponsored": False
    },
    # More Mumbai hotels
    {
        "id": "hotel_27",
        "name": "The Oberoi Mumbai",
        "city": "Mumbai",
        "rating": {"avg_rating": 9.3},
        "pricing": {"min_total_price": 18000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Pool", "Business Center"],
        "is_sponsored": False
    },
    {
        "id": "hotel_28",
        "name": "ITC Grand Central Mumbai",
        "city": "Mumbai",
        "rating": {"avg_rating": 8.7},
        "pricing": {"min_total_price": 11000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Bar"],
        "is_sponsored": True,
        "sponsorship": {"priority": 2}
    },
    # More Delhi hotels
    {
        "id": "hotel_29",
        "name": "The Leela Palace New Delhi",
        "city": "Delhi",
        "rating": {"avg_rating": 9.1},
        "pricing": {"min_total_price": 14000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Pool", "Restaurant"],
        "is_sponsored": False
    },
    {
        "id": "hotel_30",
        "name": "ITC Maurya Delhi",
        "city": "Delhi",
        "rating": {"avg_rating": 8.9},
        "pricing": {"min_total_price": 10000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Business Center"],
        "is_sponsored": True,
        "sponsorship": {"priority": 1}
    },
    # More New York hotels
    {
        "id": "hotel_31",
        "name": "The St. Regis New York",
        "city": "New York",
        "rating": {"avg_rating": 9.2},
        "pricing": {"min_total_price": 28000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": False,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Butler Service"],
        "is_sponsored": True,
        "sponsorship": {"priority": 1}
    },
    {
        "id": "hotel_32",
        "name": "The Carlyle New York",
        "city": "New York",
        "rating": {"avg_rating": 8.8},
        "pricing": {"min_total_price": 24000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Restaurant", "Bar", "Art Gallery"],
        "is_sponsored": False
    },
    {
        "id": "hotel_33",
        "name": "Pod Hotel Times Square",
        "city": "New York",
        "rating": {"avg_rating": 7.5},
        "pricing": {"min_total_price": 8000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": False,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Restaurant", "Rooftop Bar"],
        "is_sponsored": False
    },
    # More London hotels
    {
        "id": "hotel_34",
        "name": "The Savoy London",
        "city": "London",
        "rating": {"avg_rating": 9.3},
        "pricing": {"min_total_price": 32000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": False,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Theatre", "River View"],
        "is_sponsored": True,
        "sponsorship": {"priority": 1}
    },
    {
        "id": "hotel_35",
        "name": "Claridge's London",
        "city": "London",
        "rating": {"avg_rating": 9.1},
        "pricing": {"min_total_price": 29000},
        "amenities": {
            "complementary_breakfast": True,
            "parking_available": False,
            "pets_allowed": True,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": True
        },
        "facilities": ["WiFi", "Spa", "Restaurant", "Bar"],
        "is_sponsored": False
    },
    {
        "id": "hotel_36",
        "name": "Premier Inn London City",
        "city": "London",
        "rating": {"avg_rating": 7.8},
        "pricing": {"min_total_price": 6000},
        "amenities": {
            "complementary_breakfast": False,
            "parking_available": False,
            "pets_allowed": False,
            "lift_available": True,
            "alcohol_allowed": True
        },
        "policies": {
            "free_cancellation": True,
            "prepayment_needed": False
        },
        "facilities": ["WiFi", "Restaurant"],
        "is_sponsored": False
    }
]

# Insert hotels
for hotel in hotels_data:
    try:
        es.index(index="hotels", id=hotel["id"], body=hotel)
        print(f"Inserted: {hotel['name']} in {hotel['city']}")
    except Exception as e:
        print(f"Error inserting {hotel['name']}: {e}")

print(f"\nInserted {len(hotels_data)} additional hotels!")
print("Cities with 4+ hotels: Mumbai (4), Delhi (4), New York (4), London (4)")
print("All cities covered: Mumbai, Delhi, Bangalore, Goa, New York, Los Angeles, London, Paris, Tokyo, Sydney, Berlin, Rome, Barcelona, Toronto, Rio de Janeiro, Singapore, Bangkok, Dubai, Cape Town, Shanghai, Cancun, Moscow")
