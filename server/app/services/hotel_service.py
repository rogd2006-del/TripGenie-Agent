import asyncio
from typing import List, Dict, Any
from app.tools.hotel_tool import search_hotels
from app.utils.logger import logger

class HotelService:
    """Service to generate realistic hotel search results per destination."""

    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    async def get_hotels_for_destination(
        self,
        destination: str,
        radius_meters: int = 5000,
        budget: float = 20000.0,
        luxury_level: str = "Moderate"
    ) -> List[Dict[str, Any]]:
        """Return generated realistic hotels for destination."""
        logger.info(f"Generating realistic hotels for destination '{destination}'...")
        hotels = search_hotels(destination=destination, luxury_level=luxury_level, budget=budget)
        return hotels

hotel_service = HotelService()
