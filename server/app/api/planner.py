import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from app.schemas.planner import PlannerStartRequest, PlannerChatRequest
from app.middleware.auth_middleware import get_current_user
from app.services.langgraph_workflow import langgraph_planner_workflow
from app.database.connection import db_manager
from app.utils.logger import logger

router = APIRouter(prefix="/planner", tags=["Agentic AI Planner"])

@router.post("/start")
async def start_autonomous_planner(
    payload: PlannerStartRequest,
    current_user: dict = Depends(get_current_user)
):
    """Trigger LangGraph Multi-Agent network execution and stream event updates."""
    u_id = str(current_user.get("_id") or current_user.get("id"))
    req_dict = payload.model_dump()
    
    async def event_generator():
        final_trip = None
        async for event in langgraph_planner_workflow.execute_stream(req_dict):
            if event.get("status") == "completed" and "final_state" in event:
                state = event["final_state"]
                t_id = f"trip-{uuid.uuid4().hex[:8]}"
                
                final_trip = {
                    "_id": t_id,
                    "id": t_id,
                    "user_id": u_id,
                    "title": state.get("title", f"Trip to {state.get('destination', 'Goa')}"),
                    "destination": state.get("destination", "Goa, India"),
                    "latitude": state.get("destination_lat") or state.get("latitude"),
                    "longitude": state.get("destination_lng") or state.get("longitude"),
                    "destination_lat": state.get("destination_lat") or state.get("latitude"),
                    "destination_lng": state.get("destination_lng") or state.get("longitude"),
                    "destination_details": state.get("destination_details"),
                    "geocoding_failed": state.get("geocoding_failed", False),
                    "budget": state.get("budget", 20000),
                    "estimated_total": state.get("estimated_total", 18500),
                    "currency": "INR",
                    "duration_days": state.get("duration_days", 4),
                    "travelers": state.get("travelers", 2),
                    "food_preference": state.get("food_preference", "Vegetarian"),
                    "luxury_level": state.get("luxury_level", "Moderate"),
                    "adventure_level": state.get("adventure_level", "High"),
                    "cover_image": state.get("cover_image"),
                    "is_saved": False,
                    "summary": state.get("summary", ""),
                    "itinerary": state.get("itinerary", []),
                    "hotels": state.get("hotels", []),
                    "hotel_message": state.get("hotel_message"),
                    "restaurants": state.get("restaurants", []),
                    "transport": state.get("transport"),
                    "budget_breakdown": state.get("budget_breakdown"),
                    "packing_list": state.get("packing_list", []),
                    "emergency_contacts": state.get("emergency_contacts", []),
                    "hospitals": state.get("hospitals", []),
                    "pharmacies": state.get("pharmacies", []),
                    "places": state.get("places", []),
                    "created_at": datetime.utcnow().isoformat()
                }

                # Persist to database
                if db_manager.use_fallback:
                    db_manager.in_memory_store["trips"].insert(0, final_trip)
                else:
                    await db_manager.db["trips"].insert_one(final_trip)

                event["trip_id"] = t_id
                event["trip_data"] = final_trip

            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from app.services.chat_service import chat_service

@router.post("/chat")
async def planner_chat_assistant(
    payload: PlannerChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Refine trip plans via dynamic interactive conversational AI assistant."""
    logger.info(f"[Incoming Message] POST /api/v1/planner/chat - User: '{current_user.get('email', 'unknown')}' | Query: '{payload.message}' | Trip ID: {payload.trip_id}")
    try:
        res = await chat_service.process_chat_message(
            message=payload.message,
            trip_id=payload.trip_id,
            user_info=current_user
        )
        return res
    except Exception as e:
        logger.error(f"[Exceptions] Endpoint POST /planner/chat failed: {e}", exc_info=True)
        return {
            "reply": f"I apologize, but I encountered an error while processing your request: {str(e)}. How else may I assist you with your travel plans?",
            "agent_name": "TripGenie AI",
            "intent": "ERROR_RECOVERY",
            "agents_used": [],
            "timestamp": datetime.utcnow().isoformat(),
            "trip_id": payload.trip_id,
            "error": str(e)
        }


@router.get("/hotels")
async def get_hotels_endpoint(
    destination: str = "Goa, India",
    luxury_level: str = "Moderate",
    budget: float = 20000.0
):
    """Hotel API: Search lodging options tailored to target destination, luxury level, and budget."""
    from app.tools.hotel_tool import search_hotels
    hotels = search_hotels(destination=destination, luxury_level=luxury_level, budget=budget)
    return {"destination": destination, "hotels": hotels, "total": len(hotels)}

@router.get("/weather")
async def get_weather_endpoint(
    destination: str = "Goa, India",
    duration_days: int = 4
):
    """Weather API: Fetch weather forecast for a destination and duration."""
    from app.tools.weather_tool import fetch_weather_forecast
    weather = await fetch_weather_forecast(destination=destination, duration_days=duration_days)
    return weather
