
from elasticsearch import Elasticsearch
import json
from datetime import datetime

# Elasticsearch connection
es = Elasticsearch("http://localhost:9200")

# Test connection first
print("Testing Elasticsearch connection...")
try:
    info = es.info()
    print(f"✅ Connected to Elasticsearch: {info}")
except Exception as e:
    print(f"❌ Elasticsearch connection failed: {e}")
    print("Make sure Elasticsearch is running on localhost:9200")
    exit(1)

# Load hotel mapping from file
def load_hotel_mapping():
    """Load hotel mapping from mappings/hotel_mappings.json"""
    with open('../mappings/hotel_mappings.json', 'r') as f:
        return json.load(f)

# Sample hotel data with pricing and rating
hotels_data = [
    {
        "id": "hotel_001",
        "name": "The Taj Mahal Palace Mumbai",
        "description": "Iconic luxury hotel overlooking the Gateway of India",
        "city": "Mumbai",
        "address": "Apollo Bunder, Colaba, Mumbai, Maharashtra 400001",
        "phone": "+91-22-6665-3366",
        "email": "reservations.mumbai@tajhotels.com",
        "check_in_time": "15:00",
        "check_out_time": "12:00",
        "current_pricing": {
            "min_price": 8000.0,
            "max_price": 25000.0,
            "currency": "INR"
        },
        "current_rating": {
            "avg_rating": 4.5,
            "total_reviews": 1250
        },
        "hotel_policies": {
            "free_cancellation": True,
            "prepayment_needed": True,
            "cancellation_hours": 24,
            "pets_allowed": True
        },
        "hotel_amenities": {
            "complementary_breakfast": True,
            "parking_available": True,
            "wifi": True,
            "pool": True,
            "gym": True,
            "restaurant": True,
            "bar": True,
            "room_service": True
        },
        "room_types": [
            {
                "type": "deluxe",
                "name": "Deluxe Room",
                "description": "Spacious room with city view",
                "total_rooms": 20,
                "price_per_night_per_room": 8000.0,
                "max_occupancy": 2,
                "size_sqft": 450,
                "bed_configuration": {
                    "bed_type": "king",
                    "bed_count": 1,
                    "bed_size": "king",
                    "sofa_bed": False,
                    "extra_bed_available": True
                },
                "room_amenities": {
                    "air_conditioning": True,
                    "wifi": True,
                    "tv": True,
                    "minibar": True,
                    "safe": True,
                    "balcony": True,
                    "kitchenette": False
                }
            },
            {
                "type": "suite",
                "name": "Premium Suite",
                "description": "Luxury suite with harbor view",
                "total_rooms": 10,
                "price_per_night_per_room": 15000.0,
                "max_occupancy": 4,
                "size_sqft": 800,
                "bed_configuration": {
                    "bed_type": "king",
                    "bed_count": 1,
                    "bed_size": "king",
                    "sofa_bed": True,
                    "extra_bed_available": True
                },
                "room_amenities": {
                    "air_conditioning": True,
                    "wifi": True,
                    "tv": True,
                    "minibar": True,
                    "safe": True,
                    "balcony": True,
                    "kitchenette": True
                }
            },
            {
                "type": "presidential",
                "name": "Presidential Suite",
                "description": "Ultimate luxury with panoramic views",
                "total_rooms": 2,
                "price_per_night_per_room": 25000.0,
                "max_occupancy": 6,
                "size_sqft": 1200,
                "bed_configuration": {
                    "bed_type": "king",
                    "bed_count": 2,
                    "bed_size": "king",
                    "sofa_bed": True,
                    "extra_bed_available": True
                },
                "room_amenities": {
                    "air_conditioning": True,
                    "wifi": True,
                    "tv": True,
                    "minibar": True,
                    "safe": True,
                    "balcony": True,
                    "kitchenette": True
                }
            }
        ],
        "is_sponsored": True,
        "sponsorship": {"priority": 1},
        "last_updated": datetime.now().isoformat()
    },
    {
        "id": "hotel_002", 
        "name": "Grand Hyatt Mumbai",
        "description": "Modern luxury hotel in Bandra Kurla Complex",
        "city": "Mumbai",
        "address": "Off Western Express Highway, Santacruz East, Mumbai 400055",
        "phone": "+91-22-6676-1234",
        "email": "mumbai.grand@hyatt.com",
        "check_in_time": "15:00",
        "check_out_time": "12:00",
        "current_pricing": {
            "min_price": 6500.0,
            "max_price": 18000.0,
            "currency": "INR"
        },
        "current_rating": {
            "avg_rating": 4.3,
            "total_reviews": 890
        },
        "hotel_policies": {
            "free_cancellation": True,
            "prepayment_needed": False,
            "cancellation_hours": 48,
            "pets_allowed": False
        },
        "hotel_amenities": {
            "complementary_breakfast": False,
            "parking_available": True,
            "wifi": True,
            "pool": True,
            "gym": True,
            "restaurant": True,
            "bar": True,
            "room_service": True
        },
        "room_types": [
            {
                "type": "standard",
                "name": "Standard Room", 
                "description": "Comfortable room with modern amenities",
                "total_rooms": 25,
                "price_per_night_per_room": 6500.0,
                "max_occupancy": 2,
                "size_sqft": 400,
                "bed_configuration": {
                    "bed_type": "queen",
                    "bed_count": 1,
                    "bed_size": "queen",
                    "sofa_bed": False,
                    "extra_bed_available": False
                },
                "room_amenities": {
                    "air_conditioning": True,
                    "wifi": True,
                    "tv": True,
                    "minibar": True,
                    "safe": True,
                    "balcony": False,
                    "kitchenette": False
                }
            },
            {
                "type": "deluxe",
                "name": "Deluxe Room",
                "description": "Spacious room with city view",
                "total_rooms": 15,
                "price_per_night_per_room": 9500.0,
                "max_occupancy": 3,
                "size_sqft": 500,
                "bed_configuration": {
                    "bed_type": "king",
                    "bed_count": 1,
                    "bed_size": "king",
                    "sofa_bed": False,
                    "extra_bed_available": True
                },
                "room_amenities": {
                    "air_conditioning": True,
                    "wifi": True,
                    "tv": True,
                    "minibar": True,
                    "safe": True,
                    "balcony": True,
                    "kitchenette": False
                }
            },
            {
                "type": "suite",
                "name": "Executive Suite",
                "description": "Premium suite with separate living area",
                "total_rooms": 8,
                "price_per_night_per_room": 18000.0,
                "max_occupancy": 4,
                "size_sqft": 750,
                "bed_configuration": {
                    "bed_type": "king",
                    "bed_count": 1,
                    "bed_size": "king",
                    "sofa_bed": True,
                    "extra_bed_available": True
                },
                "room_amenities": {
                    "air_conditioning": True,
                    "wifi": True,
                    "tv": True,
                    "minibar": True,
                    "safe": True,
                    "balcony": True,
                    "kitchenette": True
                }
            }
        ],
        "is_sponsored": False,
        "last_updated": datetime.now().isoformat()
    }
]

def create_hotel_index():
    """Create hotels index with mapping from file"""
    try:
        # Check if index exists with error handling
        print(f"Checking if hotels index exists...")
        try:
            index_exists = es.indices.exists(index="hotels")
            print(f"Index exists check result: {index_exists}")
        except Exception as check_error:
            print(f"❌ Error checking if index exists: {check_error}")
            return False
        
        if index_exists:
            print(f"deleting old index now")
            es.indices.delete(index="hotels")
            print("Deleted existing hotels index")
        else:
            print("Hotels index does not exist")
        
        # Load mapping and create index
        hotel_mapping = load_hotel_mapping()
        print(f"📋 Mapping loaded successfully")
        print(f"📋 Mapping keys: {list(hotel_mapping.keys())}")
        
        # Try to create index
        response = es.indices.create(index="hotels", body=hotel_mapping)
        print(f"✅ Hotels index created successfully! Response: {response}")
        
    except FileNotFoundError:
        print("❌ Mapping file not found at ../mappings/hotel_mappings.json")
        return False
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        print(f"❌ Error type: {type(e)}")
        return False
    return True

def populate_hotels():
    """Populate hotels with sample data"""
    success_count = 0
    error_count = 0
    
    print("\nPopulating hotels...")
    print("=" * 50)
    
    for hotel in hotels_data:
        try:
            es.index(index="hotels", id=hotel["id"], body=hotel)
            print(f"✅ Added: {hotel['name']} - ₹{hotel['current_pricing']['min_price']}-{hotel['current_pricing']['max_price']} - {hotel['current_rating']['avg_rating']}⭐")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error adding {hotel['name']}: {e}")
            error_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully added: {success_count} hotels")
    print(f"❌ Failed: {error_count} hotels")

if __name__ == "__main__":
    print("Creating Hotels Index and Populating Data...")
    print("=" * 60)
    
    if create_hotel_index():
        populate_hotels()
        print(f"\n🎉 Hotel setup completed!")
    else:
        print("❌ Failed to create index.")








