from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth_middleware import get_current_user
from app.database.connection import db_manager
from pydantic import BaseModel

router = APIRouter(prefix="/user", tags=["User Profile"])

class UpdatePreferencesRequest(BaseModel):
    currency: str = "INR"
    diet: str = "Vegetarian"
    luxury_level: str = "Moderate"
    model_provider: str = "openai"

@router.put("/preferences")
async def update_user_preferences(
    payload: UpdatePreferencesRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update travel & system preferences for logged in user."""
    u_id = str(current_user.get("_id") or current_user.get("id"))
    new_prefs = payload.model_dump()
    
    if db_manager.use_fallback:
        for u in db_manager.in_memory_store["users"]:
            if str(u.get("_id")) == u_id or str(u.get("id")) == u_id:
                u["preferences"] = new_prefs
                break
    else:
        await db_manager.db["users"].update_one(
            {"_id": u_id},
            {"$set": {"preferences": new_prefs}}
        )
        
    return {"status": "success", "preferences": new_prefs}
