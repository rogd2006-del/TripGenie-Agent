from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_token
from app.database.connection import db_manager

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to extract authenticated current user from JWT token."""
    if not credentials:
        # Fallback demo user if unauthenticated for quick developer testing
        return {
            "id": "user-demo-1",
            "email": "demo@tripgenie.ai",
            "full_name": "Alex Traveler",
            "preferences": {"currency": "INR", "diet": "Vegetarian"}
        }

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
    
    user_id = payload.get("sub")
    if db_manager.use_fallback:
        for u in db_manager.in_memory_store["users"]:
            if str(u.get("_id")) == str(user_id) or str(u.get("id")) == str(user_id):
                return u
        return {"id": user_id, "email": "user@tripgenie.ai", "full_name": "TripGenie User"}
    else:
        user = await db_manager.db["users"].find_one({"_id": user_id})
        if not user:
            return {"id": user_id, "email": "user@tripgenie.ai", "full_name": "TripGenie User"}
        user["id"] = str(user.pop("_id"))
        return user
