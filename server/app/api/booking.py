import io
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.database.connection import db_manager
from app.tools.pdf_tool import (
    generate_transport_ticket_pdf,
    generate_hotel_voucher_pdf,
    generate_payment_receipt_pdf
)
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/booking", tags=["Booking & Payment"])


class CreateBookingRequest(BaseModel):
    trip_id: Optional[str] = None
    destination: Optional[str] = "Goa, India"
    hotel: Optional[Dict[str, Any]] = None
    transport: Optional[Dict[str, Any]] = None
    duration_days: Optional[int] = 4
    food_cost: Optional[float] = 3000.0
    sightseeing_cost: Optional[float] = 1500.0
    max_budget: Optional[float] = 20000.0



class ProcessPaymentRequest(BaseModel):
    payment_method: Optional[str] = "Credit Card / UPI"


async def get_booking_by_id(booking_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve booking by ID from MongoDB or in-memory fallback."""
    if db_manager.use_fallback:
        bookings = db_manager.in_memory_store.get("bookings", {})
        return bookings.get(booking_id)
    else:
        try:
            return await db_manager.db["bookings"].find_one({"_id": booking_id})
        except Exception as e:
            logger.error(f"Error fetching booking from DB: {e}")
            bookings = db_manager.in_memory_store.get("bookings", {})
            return bookings.get(booking_id)


async def save_booking(booking: Dict[str, Any]):
    """Save or update booking in database."""
    booking_id = booking["_id"]
    if "bookings" not in db_manager.in_memory_store:
        db_manager.in_memory_store["bookings"] = {}
    db_manager.in_memory_store["bookings"][booking_id] = booking

    if not db_manager.use_fallback:
        try:
            await db_manager.db["bookings"].replace_one(
                {"_id": booking_id}, booking, upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving booking to MongoDB: {e}")


@router.post("/create")
async def create_booking(req: CreateBookingRequest):
    """Create a confirmed booking with user-selected hotel, transport, and itemized budget calculations."""
    try:
        rand_hex = uuid.uuid4().hex[:8].upper()
        booking_id = f"BK-{rand_hex}"
        hotel_booking_id = f"HTL-{rand_hex}"
        transport_booking_id = f"TRP-{rand_hex}"

        # Selected hotel fallback
        hotel = req.hotel or {
            "name": "Grand Horizon Resort",
            "rating": 4.6,
            "price_per_night": 3200,
            "address": f"Beach Road, {req.destination}",
            "amenities": ["Pool", "Free WiFi", "Breakfast Included"]
        }

        # Selected transport fallback
        transport = req.transport or {
            "id": "trp-1",
            "transport_type": "Bus",
            "operator_name": "Express Coastal Travels",
            "vehicle_number": "EX-09-V-7711",
            "departure_time": "08:00 AM",
            "arrival_time": "04:30 PM",
            "travel_duration": "8h 30m",
            "price": 1200,
            "available_seats": 15,
            "rating": 4.7
        }

        duration = req.duration_days or 4
        nightly_rate = hotel.get("price_per_night") or hotel.get("price") or 2500
        hotel_cost = float(nightly_rate * duration)
        transport_cost = float(transport.get("price", 1200))
        food_cost = float(req.food_cost or 3000.0)
        sightseeing_cost = float(req.sightseeing_cost or 1500.0)
        
        subtotal = hotel_cost + transport_cost + food_cost + sightseeing_cost
        taxes = round(subtotal * 0.05, 2)
        grand_total = round(subtotal + taxes, 2)
        max_budget = float(req.max_budget or 20000.0)
        remaining_budget = round(max(0, max_budget - grand_total), 2)

        booking = {
            "_id": booking_id,
            "booking_id": booking_id,
            "hotel_booking_id": hotel_booking_id,
            "transport_booking_id": transport_booking_id,
            "trip_id": req.trip_id or "trip-demo",
            "destination": req.destination or "Goa, India",
            "hotel": hotel,
            "transport": transport,
            "duration_days": duration,
            "hotel_cost": hotel_cost,
            "transport_cost": transport_cost,
            "food_cost": food_cost,
            "sightseeing_cost": sightseeing_cost,
            "taxes": taxes,
            "grand_total": grand_total,
            "max_budget": max_budget,
            "remaining_budget": remaining_budget,
            "status": "Confirmed",
            "booking_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        await save_booking(booking)
        logger.info(f"Created confirmed booking: {booking_id} | Total: ₹{grand_total} / Max: ₹{max_budget}")
        return booking

    except Exception as e:
        logger.error(f"Error creating booking: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{booking_id}")
async def get_booking(booking_id: str):
    """Retrieve details for a specific booking."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking


@router.post("/{booking_id}/pay")
async def process_payment(booking_id: str, req: ProcessPaymentRequest):
    """Simulate successful payment for booking and update status to Paid."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    rand_hex = uuid.uuid4().hex[:8].upper()
    payment_id = f"PAY-{rand_hex}"

    booking["payment_id"] = payment_id
    booking["status"] = "Paid"
    booking["payment_method"] = req.payment_method or "Credit Card / UPI"
    booking["payment_date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    await save_booking(booking)
    logger.info(f"Payment successful for booking {booking_id} | Payment ID: {payment_id}")
    return booking


@router.get("/{booking_id}/pdf/ticket")
async def download_transport_ticket_pdf(booking_id: str):
    """Generate and stream Transport Ticket PDF."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    pdf_bytes = generate_transport_ticket_pdf(booking)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Transport_Ticket_{booking_id}.pdf"}
    )


@router.get("/{booking_id}/pdf/hotel-voucher")
async def download_hotel_voucher_pdf(booking_id: str):
    """Generate and stream Hotel Voucher PDF."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    pdf_bytes = generate_hotel_voucher_pdf(booking)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Hotel_Voucher_{booking_id}.pdf"}
    )


@router.get("/{booking_id}/pdf/receipt")
async def download_payment_receipt_pdf(booking_id: str):
    """Generate and stream Payment Receipt PDF."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    pdf_bytes = generate_payment_receipt_pdf(booking)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Payment_Receipt_{booking_id}.pdf"}
    )
