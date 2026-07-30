import uvicorn
from app.main import app
from app.config.settings import settings
from app.utils.logger import logger

if __name__ == "__main__":
    logger.info(f"Starting TripGenie Backend Server on {settings.HOST}:{settings.PORT}...")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
