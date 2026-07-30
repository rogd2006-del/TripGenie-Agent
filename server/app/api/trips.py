import uuid
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List, Dict, Any
from app.middleware.auth_middleware import get_current_user
from app.database.connection import db_manager
from app.tools.pdf_tool import generate_pdf_report
from datetime import datetime

router = APIRouter(prefix="/trip", tags=["Trips"])

@router.get("/history")
async def get_trip_history(current_user: dict = Depends(get_current_user)):
    """Fetch user's previous generated trips."""
    u_id = str(current_user.get("_id") or current_user.get("id"))
    
    if db_manager.use_fallback:
        user_trips = [t for t in db_manager.in_memory_store["trips"] if t.get("user_id") == u_id or t.get("user_id") == "user-demo-1"]
        return user_trips
    else:
        cursor = db_manager.db["trips"].find({"user_id": u_id})
        trips = await cursor.to_list(length=100)
        for t in trips:
            t["id"] = str(t.pop("_id"))
        return trips

@router.get("/{trip_id}")
async def get_trip_by_id(trip_id: str):
    """Retrieve specific trip details by ID."""
    if db_manager.use_fallback:
        for t in db_manager.in_memory_store["trips"]:
            if str(t.get("_id")) == trip_id or str(t.get("id")) == trip_id:
                t["id"] = str(t.get("_id") or t.get("id"))
                return t
        raise HTTPException(status_code=404, detail="Trip not found.")
    else:
        trip = await db_manager.db["trips"].find_one({"_id": trip_id})
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found.")
        trip["id"] = str(trip.pop("_id"))
        return trip

@router.post("/save/{trip_id}")
async def save_trip(trip_id: str, current_user: dict = Depends(get_current_user)):
    """Bookmark/save a trip to user's saved list."""
    u_id = str(current_user.get("_id") or current_user.get("id"))
    
    if db_manager.use_fallback:
        for t in db_manager.in_memory_store["trips"]:
            if str(t.get("_id")) == trip_id or str(t.get("id")) == trip_id:
                t["is_saved"] = True
                return {"status": "saved", "trip_id": trip_id}
        raise HTTPException(status_code=404, detail="Trip not found.")
    else:
        await db_manager.db["trips"].update_one({"_id": trip_id}, {"$set": {"is_saved": True}})
        return {"status": "saved", "trip_id": trip_id}

@router.delete("/{trip_id}")
async def delete_trip(trip_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a trip from database."""
    if db_manager.use_fallback:
        db_manager.in_memory_store["trips"] = [
            t for t in db_manager.in_memory_store["trips"] 
            if str(t.get("_id")) != trip_id and str(t.get("id")) != trip_id
        ]
        return {"status": "deleted", "trip_id": trip_id}
    else:
        await db_manager.db["trips"].delete_one({"_id": trip_id})
        return {"status": "deleted", "trip_id": trip_id}

@router.get("/{trip_id}/pdf")
async def download_trip_pdf(trip_id: str):
    """Generate and stream printable PDF document for trip."""
    trip_data = None
    if db_manager.use_fallback:
        for t in db_manager.in_memory_store["trips"]:
            if str(t.get("_id")) == trip_id or str(t.get("id")) == trip_id:
                trip_data = t
                break
    else:
        trip_data = await db_manager.db["trips"].find_one({"_id": trip_id})
        
    if not trip_data:
        # Fallback to default demo trip data
        trip_data = {
            "title": "Goa Autonomous AI Trip",
            "destination": "Goa, India",
            "budget": 20000,
            "currency": "INR",
            "duration_days": 4,
            "summary": "4-Day Tropical Goa Adventure featuring beach sports and cultural walks.",
            "itinerary": [
                {"day": 1, "title": "Baga Beach Stroll", "weather": "30°C Sunny", "activities": [{"time": "10:00 AM", "activity": "Arrive at Baga Beach", "location": "North Goa"}]}
            ],
            "budget_breakdown": {"stay": 9000, "food": 4500, "activities": 3000, "transport": 2000, "contingency": 1500, "total": 20000}
        }
        
    pdf_bytes = generate_pdf_report(trip_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=TripGenie_{trip_id}.pdf"}
    )
