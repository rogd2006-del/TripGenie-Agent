from pydantic import BaseModel
from typing import Optional, Dict, Any

class PlannerStartRequest(BaseModel):
    prompt: Optional[str] = None
    destination: Optional[str] = None
    budget: Optional[float] = 20000
    duration_days: Optional[int] = 4
    travelers: Optional[int] = 2
    food_preference: Optional[str] = "Vegetarian"
    luxury_level: Optional[str] = "Moderate"
    adventure_level: Optional[str] = "Medium"
    has_children: Optional[bool] = False
    language: Optional[str] = "English"
    special_requirements: Optional[str] = ""

class PlannerChatRequest(BaseModel):
    message: str
    trip_id: Optional[str] = None

class AgentStreamStep(BaseModel):
    agent_name: str
    status: str  # "starting", "completed", "error"
    message: str
    data: Optional[Dict[str, Any]] = None
