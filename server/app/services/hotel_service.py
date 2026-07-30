import asyncio
from typing import List, Dict, Any
from app.tools.google_places_tool import google_places_tool
from app.utils.logger import logger

class HotelService:
    """Service to fetch, cache, and format real hotel search results."""

    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    async def get_hotels_for_destination(
        self,
        destination: str,
        radius_meters: int = 5000,
        budget: float = 20000.0,
        luxury_level: str = "Moderate"
    ) -> List[Dict[str, Any]]:
        """Fetch real hotels within radius_meters around destination with caching."""
        cache_key = f"{destination.lower().strip()}_{radius_meters}"
        
        if cache_key in self._cache:
            logger.info(f"Returning cached hotel results for destination '{destination}'")
            return self._cache[cache_key]

        logger.info(f"Fetching real hotels for destination '{destination}' (Radius: {radius_meters/1000} km)...")

        try:
            # Step 1: Geocode destination -> Lat & Lon
            lat, lng, formatted_addr = await google_places_tool.geocode_destination(destination)
            
            # Step 2: Nearby Search within 5 km radius
            hotels = await google_places_tool.search_nearby_hotels(
                lat=lat,
                lng=lng,
                radius_meters=radius_meters,
                destination_name=formatted_addr
            )

            # Step 3: Cache result if found
            if hotels:
                self._cache[cache_key] = hotels
                return hotels
            
            return []

        except Exception as e:
            logger.error(f"Error in HotelService for destination '{destination}': {e}")
            return []

hotel_service = HotelService()
