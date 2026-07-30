from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    sender: str  # "user" or "agent"
    agent_name: Optional[str] = None
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ChatSessionModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    trip_id: Optional[str] = None
    messages: List[ChatMessage] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True
