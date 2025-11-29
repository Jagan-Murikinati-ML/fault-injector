from fastapi import APIRouter, Query, Depends, HTTPException
from auth import verify_token
from services.booking_service import BookingService
from database import db
from models.booking_models import BookHotelRequest, BookHotelResponse

router = APIRouter(prefix="/booking", tags=["booking"])

def get_booking_service():
    """
    Dependency to get booking service instance
    """
    return BookingService(db)

@router.get("/booked-rooms")
async def get_booked_rooms(
    hotel_id: str = Query(..., description="Hotel ID"),
    checkin_date: str = Query(..., description="Check-in date (YYYY-MM-DD)"),
    checkout_date: str = Query(..., description="Check-out date (YYYY-MM-DD)"),
    room_types: str = Query(..., description="Comma-separated room type codes"),
    booking_service: BookingService = Depends(get_booking_service),
    current_user: dict = Depends(verify_token)
):
    """
    Get booked rooms count for a hotel within a date range.
    Returns sparse data - only dates and room types that have bookings.
    """
    try:
        # Parse room types from comma-separated string
        room_types_list = [rt.strip() for rt in room_types.split(",")]

        # Get booked rooms from database
        booked_rooms = await booking_service.get_booked_rooms(
            hotel_id=hotel_id,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            room_types=room_types_list
        )

        return {
            "success": True,
            "data": booked_rooms,
            "message": "Booked rooms retrieved successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/book-hotel")
async def book_hotel(
    booking_request: BookHotelRequest,
    booking_service: BookingService = Depends(get_booking_service),
    current_user: dict = Depends(verify_token)
):
    """
    Book a hotel with room details for each day
    """
    try:
        # Convert Pydantic model to dict for service
        booking_data = booking_request.dict()
        
        # Book hotel
        result = await booking_service.book_hotel(booking_data)
        
        return {
            "success": True,
            "data": result,
            "message": "Hotel booked successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")










