from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from elasticsearch import Elasticsearch
from services.hotel_search_service import HotelSearchService
from auth import verify_token
import os

router = APIRouter()

def get_elasticsearch_client():
    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    return Elasticsearch(es_url)

def get_hotel_search_service():
    es_client = get_elasticsearch_client()
    return HotelSearchService(es_client)

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "search-service"}

@router.get("/search/hotels")
async def search_hotels(
    location: str = Query(..., description="City or location"),
    checkin_date: str = Query(..., description="Check-in date (YYYY-MM-DD)"),
    checkout_date: str = Query(..., description="Check-out date (YYYY-MM-DD)"),
    guests: int = Query(1, description="Number of guests"),
    rooms: int = Query(1, description="Number of rooms"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Results per page"),
    sort_by: Optional[str] = Query("rating", description="Sort by: rating, price_low, price_high"),
    amenities: Optional[List[str]] = Query(None, description="Filter by amenities"),
    rating_min: Optional[float] = Query(None, description="Minimum rating"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    room_type: Optional[List[str]] = Query(None, description="Filter by room types"),
    hotel_service: HotelSearchService = Depends(get_hotel_search_service),
    current_user: dict = Depends(verify_token)
):
    search_params = {
        "location": location,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "guests": guests,
        "rooms": rooms,
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "amenities": amenities,
        "rating_min": rating_min,
        "price_min": price_min,
        "price_max": price_max,
        "room_type": room_type
    }
    
    return await hotel_service.search_hotels(
        city=location,
        checkin=checkin_date,
        checkout=checkout_date,
        guests=guests,
        min_price=price_min,
        max_price=price_max,
        amenities=amenities
    )

@router.get("/search/filters")
async def get_filters(
    location: str = Query(..., description="City name"),
    checkin_date: str = Query(..., description="Check-in date"),
    checkout_date: str = Query(..., description="Check-out date"),
    guests: int = Query(2, description="Number of guests"),
    hotel_service: HotelSearchService = Depends(get_hotel_search_service),
    current_user: dict = Depends(verify_token)
):
    return await hotel_service.get_filters(location)

@router.get("/search/cities")
async def search_cities(
    q: str = Query(..., description="City search query"),
    limit: int = Query(10, description="Max results"),
    hotel_service: HotelSearchService = Depends(get_hotel_search_service),
    current_user: dict = Depends(verify_token)
):
    return await hotel_service.search_cities(q, limit)

@router.get("/hotels/{hotel_id}")
async def get_hotel_details(
    hotel_id: str,
    hotel_service: HotelSearchService = Depends(get_hotel_search_service)
):
    return await hotel_service.get_hotel_by_id(hotel_id)




