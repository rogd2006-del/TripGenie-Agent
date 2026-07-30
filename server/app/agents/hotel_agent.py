"""
Hotel Agent — generates realistic lodging options tailored to the destination, budget, and luxury preferences.
"""
from typing import Dict, Any, List
from app.utils.logger import logger
from app.tools.hotel_tool import search_hotels

class HotelAgent:
    """
    Generates realistic fake hotels tailored to the target destination, budget, and luxury level.
    """

    def __init__(self):
        self.name = "Hotel Agent"

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        req = state.get("request", {}) if isinstance(state, dict) else {}
        dest = (state.get("destination") if isinstance(state, dict) else None) or req.get("destination") or "Goa, India"
        luxury = (state.get("luxury_level") if isinstance(state, dict) else None) or req.get("luxury_level") or "Moderate"
        
        user_budget = state.get("budget") if isinstance(state, dict) else None
        if user_budget is None and isinstance(req, dict):
            user_budget = req.get("budget")

        try:
            user_budget = float(user_budget) if user_budget else 20000.0
        except (ValueError, TypeError):
            user_budget = 20000.0

        logger.info(f"[HotelAgent] Generating realistic hotels for '{dest}' with budget ₹{user_budget}...")
        generated_hotels = search_hotels(destination=dest, luxury_level=str(luxury), budget=user_budget)

        return {
            "hotels": generated_hotels,
            "hotel_message": f"Curated top {len(generated_hotels)} accommodations matching your budget of ₹{int(user_budget):,}."
        }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(self.run_async(state))
        except RuntimeError:
            return asyncio.run(self.run_async(state))


hotel_agent = HotelAgent()
