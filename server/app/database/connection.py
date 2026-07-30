import asyncio
from app.config.settings import settings
from app.utils.logger import logger

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    AsyncIOMotorClient = None

class DatabaseManager:
    client = None
    db = None
    in_memory_store = {
        "users": [],
        "trips": [],
        "savedTrips": [],
        "chatHistory": [],
        "preferences": []
    }
    use_fallback: bool = True

    async def connect_db(self):
        if not AsyncIOMotorClient:
            logger.info("Motor library not installed. Operating in high-speed in-memory store mode.")
            self.use_fallback = True
            return

        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
            # Ping database to check connection
            await self.client.admin.command('ping')
            self.db = self.client[settings.MONGO_DB_NAME]
            self.use_fallback = False
            logger.info(f"Connected to MongoDB at {settings.MONGO_URI} (DB: {settings.MONGO_DB_NAME})")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Switching to high-speed in-memory store.")
            self.use_fallback = True

    async def close_db(self):
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection.")

db_manager = DatabaseManager()

def get_db():
    return db_manager.db
