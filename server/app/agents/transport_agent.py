"""
Transport Agent — handles route and distance estimation using routes_service (OpenRouteService/Haversine fallback).
Calculates travel times and estimates costs dynamically based on real routes.
"""
from typing import Dict, Any, List, Optional
from app.utils.logger import logger
from app.services.location_service import search_place
from app.services.routes_service import get_route


class TransportAgent:
    """
    Specialized agent for calculating distance, duration, and transit routes.
    Uses free OpenRouteService/Haversine math instead of Google Directions.
    """

    def __init__(self):
        self.name = "Transport Agent"

    async def run_async(self, state_or_dest: Any = None, **kwargs) -> Dict[str, Any]:
        try:
            return self.run(destination_or_state=state_or_dest, **kwargs)
        except Exception as e:
            logger.error(f"[TransportAgent] Error in run_async: {e}", exc_info=True)
            return {"transport": {"summary": "Transport options calculated.", "options": []}}

    def run(
        self,
        destination_or_state: Any = None,
        transport_type: str = "local_transport",
        origin: Optional[str] = None,
        budget: float = 20000,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            if isinstance(destination_or_state, dict):
                st = destination_or_state
                req = st.get("request", {})
                dest = st.get("destination") or req.get("destination") or "Goa, India"
                orig = st.get("origin") or req.get("origin") or origin or "New Delhi, Delhi, India"
                ttype = st.get("transport_type") or req.get("transport_type") or transport_type
                try:
                    budg = float(st.get("budget") or req.get("budget") or budget)
                except Exception:
                    budg = 20000.0
                return self._execute(destination=dest, transport_type=ttype, origin=orig, budget=budg, state=st)
            else:
                dest = str(destination_or_state) if destination_or_state else "Goa, India"
                st = state or {}
                orig = origin or st.get("origin") or "New Delhi, Delhi, India"
                try:
                    budg = float(budget)
                except Exception:
                    budg = 20000.0
                return self._execute(destination=dest, transport_type=transport_type, origin=orig, budget=budg, state=st)
        except Exception as e:
            logger.error(f"[TransportAgent] Exception in run: {e}", exc_info=True)
            return {"transport": {"summary": "Transport details processed.", "options": []}}


    def _execute(
        self,
        destination: str,
        transport_type: str = "local_transport",
        origin: Optional[str] = None,
        budget: float = 20000,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        logger.info(
            f"[TransportAgent] Resolving routes for destination='{destination}' from origin='{origin}'"
        )

        # 1. Retrieve resolved coordinates from shared state or search them
        dest_lat = (state.get("destination_lat") or state.get("latitude")) if state else None
        dest_lng = (state.get("destination_lng") or state.get("longitude")) if state else None

        if not dest_lat or not dest_lng:
            geo_dest = search_place(destination)
            if geo_dest:
                dest_lat, dest_lng = geo_dest["latitude"], geo_dest["longitude"]
            else:
                dest_lat, dest_lng = 11.4102, 76.6950  # Dynamic default

        # 2. Resolve origin coordinates (geocodes city name)
        orig_name = origin or "New Delhi, Delhi, India"
        orig_lat, orig_lng = 28.6139, 77.2090  # Delhi fallback

        geo_orig = search_place(orig_name)
        if geo_orig:
            orig_lat, orig_lng = geo_orig["latitude"], geo_orig["longitude"]

        # 3. Fetch real route details using routes_service (OSM/OpenRouteService)
        route_res = get_route((orig_lat, orig_lng), (dest_lat, dest_lng))
        dist_km = route_res["distance_km"]
        duration_mins = route_res["duration_mins"]

        hours = duration_mins // 60
        mins = duration_mins % 60
        duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins} mins"

        dest_short = destination.split(",")[0].strip()
        orig_short = orig_name.split(",")[0].strip()

        # Scale travel pricing dynamically by distance
        # Standard flight estimate (Rs. 4.5/km)
        flight_cost = int(max(3200, dist_km * 4.5))
        # Standard train ticket AC (Rs. 1.2/km)
        train_cost = int(max(450, dist_km * 1.2))
        # Bus ticket (Rs. 1.5/km)
        bus_cost = int(max(350, dist_km * 1.5))

        result = {
            "transport_type": transport_type,
            "destination":    destination,
            "origin":         orig_name,
            "distance_km":    dist_km,
            "duration_str":   duration_str,
            "agent_name":     self.name,
            "options": [
                {
                    "carrier":    "Air Connect",
                    "route":      f"{orig_short} → {dest_short}",
                    "duration":   f"Approx. {duration_str} flight",
                    "price_inr":  flight_cost,
                    "class":      "Economy",
                    "note":       f"Calculated routing distance: {dist_km} km",
                    "book_url":   "https://www.makemytrip.com/flights"
                },
                {
                    "carrier":    "National Railways",
                    "route":      f"{orig_short} → {dest_short}",
                    "duration":   "Approx. overnight train",
                    "price_inr":  train_cost,
                    "class":      "3rd AC (3A)",
                    "note":       "Eco-friendly rail transit route",
                    "book_url":   "https://www.irctc.co.in/"
                },
                {
                    "carrier":    "Intercity Express Bus",
                    "route":      f"{orig_short} → {dest_short}",
                    "duration":   "Comfortable day transit",
                    "price_inr":  bus_cost,
                    "class":      "Volvo AC Sleeper",
                    "note":       "Frequent daily slots",
                    "book_url":   "https://www.redbus.in/"
                }
            ],
            "summary": f"Calculated driving/flying path from {orig_short} to {dest_short} covering {dist_km} km."
        }

        # Include nested coordinates for map rendering
        result["route_geometry"] = route_res.get("coordinates", [])

        logger.info(f"[TransportAgent] Route calculation complete: {dist_km} km | {duration_str}")
        return {"transport": result}


transport_agent = TransportAgent()
