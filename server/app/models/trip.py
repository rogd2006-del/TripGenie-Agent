from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ActivityItem(BaseModel):
    time: str
    activity: str
    location: str

class DailyItinerary(BaseModel):
    day: int
    title: str
    weather: str
    activities: List[ActivityItem]

class HotelRecommendation(BaseModel):
    name: str
    rating: float
    price_per_night: float
    amenities: List[str]
    address: str
    image: str

class RestaurantRecommendation(BaseModel):
    name: str
    cuisine: str
    rating: float
    avg_cost_two: float
    specialty: str

class TransportRecommendation(BaseModel):
    recommended: str
    estimated_cost: float
    flight_train_note: str

class BudgetBreakdown(BaseModel):
    stay: float
    food: float
    activities: float
    transport: float
    contingency: float
    total: float

class EmergencyContact(BaseModel):
    name: str
    phone: str

class TripModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    title: str
    destination: str
    budget: float
    estimated_total: float
    currency: str = "INR"
    duration_days: int
    travelers: int = 1
    food_preference: str = "Vegetarian"
    luxury_level: str = "Moderate"
    adventure_level: str = "Medium"
    cover_image: Optional[str] = None
    is_saved: bool = False
    summary: str
    itinerary: List[DailyItinerary] = []
    hotels: List[HotelRecommendation] = []
    restaurants: List[RestaurantRecommendation] = []
    transport: Optional[TransportRecommendation] = None
    budget_breakdown: Optional[BudgetBreakdown] = None
    packing_list: List[str] = []
    emergency_contacts: List[EmergencyContact] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True
