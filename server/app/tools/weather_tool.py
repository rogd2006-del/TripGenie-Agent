try:
    import httpx
except ImportError:
    httpx = None

from typing import Dict, Any
from app.config.settings import settings
from app.utils.logger import logger

async def fetch_weather_forecast(destination: str, duration_days: int) -> Dict[str, Any]:
    """Fetch weather forecast via OpenWeather API or fallback simulation."""
    if settings.WEATHER_API_KEY and httpx:
        try:
            async with httpx.AsyncClient() as client:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={settings.WEATHER_API_KEY}&units=metric"
                res = await client.get(url, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"].capitalize()
                    return {
                        "destination": destination,
                        "temp_celsius": temp,
                        "condition": desc,
                        "forecast": [f"Day {i+1}: {temp}°C - {desc}" for i in range(duration_days)]
                    }
        except Exception as e:
            logger.warning(f"OpenWeather API error: {e}")

    # Try Open-Meteo free API first if httpx available
    if httpx:
        try:
            async with httpx.AsyncClient() as client:
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=1&language=en&format=json"
                geo_res = await client.get(geo_url, timeout=4.0)
                if geo_res.status_code == 200:
                    geo_data = geo_res.json()
                    if geo_data.get("results"):
                        lat = geo_data["results"][0]["latitude"]
                        lon = geo_data["results"][0]["longitude"]
                        
                        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                        w_res = await client.get(weather_url, timeout=4.0)
                        if w_res.status_code == 200:
                            w_data = w_res.json().get("current_weather", {})
                            temp = round(w_data.get("temperature", 25), 1)
                            code = w_data.get("weathercode", 0)
                            
                            cond_map = {
                                0: "Clear & Sunny", 1: "Mainly Clear", 2: "Partly Cloudy",
                                3: "Overcast", 45: "Foggy", 51: "Light Drizzle", 61: "Slight Rain",
                                80: "Rain Showers", 95: "Thunderstorm"
                            }
                            cond = cond_map.get(code, "Pleasant & Clear")
                            return {
                                "destination": destination,
                                "temp_celsius": temp,
                                "condition": cond,
                                "forecast": [f"Day {i+1}: {round(temp + (i*0.5) - 1, 1)}°C - {cond}" for i in range(duration_days)]
                            }
        except Exception as e:
            logger.warning(f"Open-Meteo weather fetch error: {e}")

    # Dynamic location hash fallback for offline mode
    h = abs(hash(destination))
    temp = 18 + (h % 14)  # 18°C to 31°C reasonable range
    conditions = ["Clear & Sunny", "Pleasant & Breeze", "Partly Cloudy with Coastal Breeze", "Crisp & Clear", "Mild & Warm"]
    cond = conditions[h % len(conditions)]

    return {
        "destination": destination,
        "temp_celsius": temp,
        "condition": cond,
        "forecast": [f"Day {i+1}: {temp + (i % 3)}°C - {cond}" for i in range(duration_days)]
    }
