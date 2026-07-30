from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserPreferences(BaseModel):
    currency: str = "INR"
    diet: str = "Vegetarian"
    luxury_level: str = "Moderate"
    model_provider: str = "openai"

class UserModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    full_name: str
    password: str
    avatar: Optional[str] = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
    preferences: UserPreferences = UserPreferences()
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True
