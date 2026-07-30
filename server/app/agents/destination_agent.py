"""
Destination Agent — resolves destination details and coordinates using location_service (Nominatim / Photon / Open-Meteo / Offline DB).
Stores latitude, longitude, country, state, and formatting details in shared state.
"""
from typing import Dict, Any
from app.utils.logger import logger
from app.services.location_service import search_place

class DestinationAgent:
    """
    Geocodes the destination city or region using location_service.
    Populates standard coordinates and geographic metadata in the shared state.
    """

    def __init__(self):
        self.name = "Destination Agent"

    async def run_async(self, state: Any = None) -> Dict[str, Any]:
        try:
            return self.run(state)
        except Exception as e:
            logger.error(f"[DestinationAgent] Error during execution: {e}", exc_info=True)
            return {
                "geocoding_failed": True,
                "error": "Unable to locate the destination."
            }

    def run(self, state: Any = None) -> Dict[str, Any]:
        try:
            if isinstance(state, dict):
                req = state.get("request", {})
                destination = state.get("destination") or req.get("destination") or "Goa, India"
            elif isinstance(state, str):
                destination = state
            else:
                destination = "Goa, India"
            
            logger.info(f"[DestinationAgent] Resolving details for requested destination: '{destination}'...")

            geo_data = search_place(destination)
            if not geo_data:
                logger.error(f"[DestinationAgent] Could not resolve coordinates for '{destination}'. Full response is None.")
                return {
                    "destination": destination,
                    "geocoding_failed": True,
                    "error": f"Unable to locate coordinates for '{destination}'."
                }

            lat = geo_data["latitude"]
            lon = geo_data["longitude"]

            logger.info(
                f"[DestinationAgent] Geocoding SUCCESS for destination: '{destination}' | "
                f"Returned Lat: {lat}, Returned Lng: {lon} | Display Name: '{geo_data['display_name']}'"
            )

            osm_embed = f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.03}%2C{lat-0.03}%2C{lon+0.03}%2C{lat+0.03}&layer=mapnik&marker={lat}%2C{lon}"

            result = {
                "destination":           destination,
                "latitude":              lat,
                "longitude":             lon,
                "destination_lat":       lat,
                "destination_lng":       lon,
                "destination_country":   geo_data["country"],
                "destination_state":     geo_data["state"],
                "display_name":          geo_data["display_name"],
                "geocoding_failed":      False,
                "bounding_box":          geo_data.get("boundingbox", []),
                "destination_details": {
                    "latitude":      lat,
                    "longitude":     lon,
                    "display_name":  geo_data["display_name"],
                    "country":       geo_data["country"],
                    "state":         geo_data["state"],
                    "bounding_box":  geo_data.get("boundingbox", []),
                    "map_info": {
                        "map_embed_url": osm_embed
                    }
                }
            }
            
            return result
        except Exception as e:
            logger.error(f"[DestinationAgent] Exception in run for '{destination}': {e}", exc_info=True)
            return {
                "destination": destination,
                "geocoding_failed": True,
                "error": "Unable to locate the destination."
            }


destination_agent = DestinationAgent()
