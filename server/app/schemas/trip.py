from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TripCreateRequest(BaseModel):
    title: str
    destination: str
    budget: float
    duration_days: int
    food_preference: Optional[str] = "Vegetarian"
    luxury_level: Optional[str] = "Moderate"

class TripResponse(BaseModel):
    id: str
    user_id: str
    title: str
    destination: str
    budget: float
    estimated_total: float
    currency: str
    duration_days: int
    travelers: int
    food_preference: str
    luxury_level: str
    adventure_level: str
    cover_image: Optional[str]
    is_saved: bool
    summary: str
    itinerary: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    restaurants: List[Dict[str, Any]]
    transport: Optional[Dict[str, Any]]
    budget_breakdown: Optional[Dict[str, Any]]
    packing_list: List[str]
    emergency_contacts: List[Dict[str, Any]]
    created_at: str
