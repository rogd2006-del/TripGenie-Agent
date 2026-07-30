from typing import Dict, Any
import asyncio
from app.tools.weather_tool import fetch_weather_forecast

class WeatherAgent:
    def __init__(self):
        self.name = "Weather Agent"

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        dest = state.get("destination", "Goa, India")
        days = state.get("duration_days", 4)
        weather_data = await fetch_weather_forecast(dest, days)
        return {"weather": weather_data}

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self.run_async(state))

weather_agent = WeatherAgent()
