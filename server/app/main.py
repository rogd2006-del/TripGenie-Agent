import os
import json
import uuid
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from app.config.settings import settings, validate_openai_key
from app.database.connection import db_manager
from app.database.seed import seed_data
from app.utils.logger import logger
from app.api import auth, users, trips, planner, booking

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup & shutdown events."""
    logger.info("Initializing TripGenie Backend Service...")
    
    # Verify OpenAI API Key loading
    if validate_openai_key():
        logger.info(f"✅ OpenAI API Key loaded successfully. Model: {settings.OPENAI_MODEL}")
    else:
        logger.error("❌ CRITICAL STARTUP WARNING: OPENAI_API_KEY is missing or set to placeholder in .env! LLM requests will use dynamic reasoning generator until a valid key is provided.")

    await db_manager.connect_db()
    await seed_data()
    yield
    logger.info("Shutting down TripGenie Backend Service...")
    await db_manager.close_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(trips.router, prefix=settings.API_V1_STR)
app.include_router(planner.router, prefix=settings.API_V1_STR)
app.include_router(booking.router)

@app.get("/")
async def root():
    return {
        "title": "TripGenie Autonomous AI Travel Planner API",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs",
        "multi_agent_framework": "LangGraph"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if not db_manager.use_fallback else "in-memory fallback active"
    }
