from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import date
from decimal import Decimal

class RoomBooking(BaseModel):
    room_type_code: str
    booking_date: date
    rooms_count: int
    cost_per_room_per_night: Decimal

class GuestDetails(BaseModel):
    guest_name: str
    guest_email: str
    guest_phone: Optional[str] = None

class CancellationPolicy(BaseModel):
    cancellation_policy_type: str
    free_cancellation_hours: int
    cancellation_fee_percentage: Decimal
    refund_policy: str

class BookHotelRequest(BaseModel):
    hotel_id: str
    user_id: Optional[str] = None  # Changed from Optional[int] to Optional[str]
    checkin_date: date
    checkout_date: date
    total_guests: int
    rooms: List[RoomBooking]
    currency: str = "INR"
    guest_details: GuestDetails
    special_requests: Optional[str] = None
    cancellation_policy: CancellationPolicy
    
    @validator('checkin_date')
    def validate_checkin_date(cls, v):
        if v < date.today():
            raise ValueError('Check-in date cannot be in the past')
        return v
    
    @validator('checkout_date')
    def validate_dates(cls, v, values):
        if 'checkin_date' in values and v <= values['checkin_date']:
            raise ValueError('Checkout date must be after checkin date')
        return v

class BookHotelResponse(BaseModel):
    success: bool
    data: dict
    message: str

