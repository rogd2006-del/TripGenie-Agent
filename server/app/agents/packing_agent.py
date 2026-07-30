from typing import Dict, Any

from app.utils.logger import logger

class PackingAgent:
    def __init__(self):
        self.name = "Packing Agent"

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.run(state)
        except Exception as e:
            logger.error(f"[PackingAgent] Error in run_async: {e}", exc_info=True)
            return {"packing_list": [], "emergency_contacts": []}

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            dest = state.get("destination") or "Varkala, Kerala, India"
            weather_cond = state.get("weather", {}).get("condition", "").lower()
            temp = state.get("weather", {}).get("temp_celsius", 25)
            
            items = [
                f"Weather-appropriate clothing for {dest} ({temp}°C)",
                "Comfortable walking shoes & sandals for sightseeing",
                "Sunscreen (SPF 50+) & polarized sunglasses",
                "Universal power bank & phone charger",
                "Reusable water bottle & personal hydrators",
                "Compact umbrella or light rain shell",
                "Personal medical kit, hand sanitizer & essentials"
            ]
            
            if temp < 18 or "mountain" in dest.lower() or "crisp" in weather_cond:
                items[0] = f"Warm fleece/jacket & thermal layers for {dest} ({temp}°C)"
                items.append("Warm socks & beanie/scarf")

            return {
                "packing_list": items,
                "emergency_contacts": [
                    {"name": f"{dest.split(',')[0]} Tourist Helpline", "phone": "1364"},
                    {"name": "Police Emergency Control", "phone": "100"},
                    {"name": "Medical Emergency Helpline", "phone": "108"}
                ]
            }
        except Exception as e:
            logger.error(f"[PackingAgent] Exception in run: {e}", exc_info=True)
            return {"packing_list": [], "emergency_contacts": []}

packing_agent = PackingAgent()


