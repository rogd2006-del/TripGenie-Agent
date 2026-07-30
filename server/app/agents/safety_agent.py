"""
Safety Agent — provides safety tips, emergency contacts, hospitals and pharmacies
for a given destination using Google Places (hospitals/pharmacies) + LLM knowledge.
"""
import asyncio
from typing import Dict, Any, List

from app.utils.logger import logger
from app.tools.google_places_tool import google_places_tool


# Hardcoded emergency numbers for major countries/regions
_EMERGENCY_NUMBERS = {
    "india":         {"police": "100", "ambulance": "108", "fire": "101", "tourist_helpline": "1800-111-363"},
    "usa":           {"police": "911", "ambulance": "911", "fire": "911"},
    "uk":            {"police": "999", "ambulance": "999", "fire": "999"},
    "europe":        {"police": "112", "ambulance": "112", "fire": "112"},
    "australia":     {"police": "000", "ambulance": "000", "fire": "000"},
    "uae":           {"police": "999", "ambulance": "998", "fire": "997"},
    "thailand":      {"police": "191", "ambulance": "1669", "tourist": "1155"},
    "france":        {"police": "17", "ambulance": "15", "fire": "18"},
    "default":       {"police": "112", "ambulance": "112", "fire": "112"},
}


def _get_emergency_numbers(destination: str) -> Dict[str, str]:
    """Return emergency numbers based on destination country."""
    dest_lower = destination.lower()
    for country, numbers in _EMERGENCY_NUMBERS.items():
        if country in dest_lower:
            return numbers
    # Check for Indian states
    indian_states = [
        "goa", "kerala", "rajasthan", "himachal", "uttarakhand", "kashmir",
        "sikkim", "meghalaya", "mumbai", "delhi", "bangalore", "chennai",
        "kolkata", "hyderabad", "pune", "jaipur", "agra", "manali", "shimla",
        "ooty", "munnar", "varkala", "mysore", "varanasi", "udaipur", "jaisalmer",
    ]
    if any(state in dest_lower for state in indian_states):
        return _EMERGENCY_NUMBERS["india"]
    return _EMERGENCY_NUMBERS["default"]


class SafetyAgent:
    """
    Returns safety information, emergency contacts, nearby hospitals and pharmacies.
    Uses Google Places for real hospital/pharmacy listings.
    """

    def __init__(self):
        self.name = "Safety Agent"

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        dest = state.get("destination") or "Varkala, Kerala, India"
        return await self.run(destination=dest)

    async def run(
        self,
        destination: str,
        query_type: str = "safety",  # "safety" | "hospital" | "pharmacy" | "emergency"
    ) -> Dict[str, Any]:
        """
        Fetch safety information and/or nearby medical/emergency places.
        Returns:
            {
                "emergency_numbers": { police, ambulance, fire, ... },
                "hospitals":         [ {name, address, maps_url, ...} ],
                "pharmacies":        [ {name, address, maps_url, ...} ],
                "safety_tips":       str,        # LLM-generated or template
                "agent_name":        str,
            }
        """
        logger.info(f"[SafetyAgent] Query type: '{query_type}' for destination: '{destination}'")

        emergency_numbers = _get_emergency_numbers(destination)
        hospitals: List[Dict[str, Any]] = []
        pharmacies: List[Dict[str, Any]] = []

        # Fetch hospitals and pharmacies in parallel
        try:
            if query_type in ("hospital", "emergency", "safety"):
                hospitals = await google_places_tool.search_places_by_type(
                    destination=destination,
                    place_type="hospital",
                    limit=5,
                )
            if query_type in ("pharmacy", "safety"):
                pharmacies = await google_places_tool.search_places_by_type(
                    destination=destination,
                    place_type="pharmacy",
                    limit=5,
                )
        except Exception as e:
            logger.error(f"[SafetyAgent] Places search error: {e}", exc_info=True)

        return {
            "emergency_numbers": emergency_numbers,
            "hospitals":         hospitals,
            "pharmacies":        pharmacies,
            "destination":       destination,
            "agent_name":        self.name,
        }


safety_agent = SafetyAgent()
