import os
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# Force load .env from current directory or parent directories
load_dotenv(find_dotenv(usecwd=True))

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    try:
        from pydantic import BaseModel as BaseSettings
        SettingsConfigDict = None
    except ImportError:
        class BaseSettings:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        SettingsConfigDict = None

class Settings(BaseSettings):
    PROJECT_NAME: str = "TripGenie API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "tripgenie_super_secret_jwt_key_2026_change_in_production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

    # Database
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "tripgenie_db")

    # LLM Settings
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")  # options: openai, ollama, fallback
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # Third Party Tools
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY", "")
    OPENROUTE_SERVICE_API_KEY: Optional[str] = os.getenv("OPENROUTE_SERVICE_API_KEY", "")
    OPENTRIPMAP_API_KEY: Optional[str] = os.getenv("OPENTRIPMAP_API_KEY", "")
    AMADEUS_API_KEY: Optional[str] = os.getenv("AMADEUS_API_KEY", "")
    AMADEUS_API_SECRET: Optional[str] = os.getenv("AMADEUS_API_SECRET", "")

    if SettingsConfigDict:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

settings = Settings()

def validate_openai_key() -> bool:
    """Verify OpenAI API Key loading and return status."""
    key = settings.OPENAI_API_KEY or ""
    if not key or key.strip() == "your_openai_api_key_here":
        return False
    return True

