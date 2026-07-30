import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, AuthTokenResponse, UserProfileResponse
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.database.connection import db_manager
from app.middleware.auth_middleware import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthTokenResponse)
async def register_user(payload: UserRegisterRequest):
    """Register a new user and generate JWT authentication token."""
    user_id = f"user-{uuid.uuid4().hex[:8]}"
    hashed_pwd = get_password_hash(payload.password)
    
    new_user = {
        "_id": user_id,
        "id": user_id,
        "email": payload.email.lower(),
        "full_name": payload.full_name,
        "password": hashed_pwd,
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        "preferences": {
            "currency": "INR",
            "diet": "Vegetarian",
            "luxury_level": "Moderate",
            "model_provider": "openai"
        },
        "created_at": datetime.utcnow().isoformat()
    }
    
    if db_manager.use_fallback:
        # Check duplicate email
        for u in db_manager.in_memory_store["users"]:
            if u["email"] == payload.email.lower():
                raise HTTPException(status_code=400, detail="User with this email already exists.")
        db_manager.in_memory_store["users"].append(new_user)
    else:
        existing = await db_manager.db["users"].find_one({"email": payload.email.lower()})
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
        await db_manager.db["users"].insert_one(new_user)
        
    token = create_access_token(subject=user_id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": payload.email,
            "full_name": payload.full_name,
            "avatar": new_user["avatar"],
            "preferences": new_user["preferences"]
        }
    }

@router.post("/login", response_model=AuthTokenResponse)
async def login_user(payload: UserLoginRequest):
    """Authenticate user with email and password."""
    target_user = None
    if db_manager.use_fallback:
        for u in db_manager.in_memory_store["users"]:
            if u["email"] == payload.email.lower():
                target_user = u
                break
    else:
        target_user = await db_manager.db["users"].find_one({"email": payload.email.lower()})
        
    if not target_user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    if not verify_password(payload.password, target_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    u_id = str(target_user.get("_id") or target_user.get("id"))
    token = create_access_token(subject=u_id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": u_id,
            "email": target_user["email"],
            "full_name": target_user["full_name"],
            "avatar": target_user.get("avatar", ""),
            "preferences": target_user.get("preferences", {})
        }
    }

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Fetch current logged-in user profile details."""
    u_id = str(current_user.get("_id") or current_user.get("id"))
    return {
        "id": u_id,
        "email": current_user.get("email", ""),
        "full_name": current_user.get("full_name", ""),
        "avatar": current_user.get("avatar", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"),
        "preferences": current_user.get("preferences", {"currency": "INR", "diet": "Vegetarian"})
    }
