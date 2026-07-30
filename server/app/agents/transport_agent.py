"""
Transport Agent — generates destination-specific simulated transport options (Bus, Train, Flight)
and calculates travel duration & distance without external booking links.
"""
import random
from typing import Dict, Any, List, Optional
from app.utils.logger import logger
from app.services.location_service import search_place
from app.services.routes_service import get_route


def generate_destination_transport_options(destination: str, dist_km: float) -> List[Dict[str, Any]]:
    """
    Generate 3 realistic, destination-tailored fake transport options (Bus, Train, Flight).
    Includes operator name, vehicle number, departure, arrival, duration, price, seats, rating.
    """
    dest_clean = destination.split(",")[0].strip().lower()

    # Base pricing logic based on distance
    flight_price = int(max(2800, dist_km * 4.2))
    train_price = int(max(450, dist_km * 1.3))
    bus_price = int(max(350, dist_km * 1.5))

    duration_mins = int(max(60, dist_km * 1.2))
    hours = duration_mins // 60
    mins = duration_mins % 60
    duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins} mins"

    if "ooty" in dest_clean or "nilgiri" in dest_clean:
        return [
            {
                "id": "trp-ooty-1",
                "transport_type": "Bus",
                "operator_name": "TN Express Travels",
                "vehicle_number": "TN-43-N-8821",
                "departure_time": "07:00 AM",
                "arrival_time": "03:15 PM",
                "travel_duration": "8h 15m",
                "price": max(650, int(bus_price * 1.1)),
                "available_seats": 18,
                "rating": 4.6
            },
            {
                "id": "trp-ooty-2",
                "transport_type": "Bus",
                "operator_name": "Nilgiri Tourist Bus",
                "vehicle_number": "TN-43-B-4412",
                "departure_time": "09:30 PM",
                "arrival_time": "06:00 AM",
                "travel_duration": "8h 30m",
                "price": max(580, bus_price),
                "available_seats": 24,
                "rating": 4.5
            },
            {
                "id": "trp-ooty-3",
                "transport_type": "Train",
                "operator_name": "Mountain Rider",
                "vehicle_number": "16615-MTR",
                "departure_time": "06:15 AM",
                "arrival_time": "01:45 PM",
                "travel_duration": "7h 30m",
                "price": max(420, train_price),
                "available_seats": 12,
                "rating": 4.8
            }
        ]

    elif "chennai" in dest_clean or "madras" in dest_clean:
        return [
            {
                "id": "trp-chn-1",
                "transport_type": "Bus",
                "operator_name": "Parveen Travels",
                "vehicle_number": "TN-01-A-9900",
                "departure_time": "10:00 PM",
                "arrival_time": "05:30 AM",
                "travel_duration": "7h 30m",
                "price": max(750, bus_price),
                "available_seats": 15,
                "rating": 4.7
            },
            {
                "id": "trp-chn-2",
                "transport_type": "Train",
                "operator_name": "Chennai Express",
                "vehicle_number": "12626-MAS",
                "departure_time": "08:30 PM",
                "arrival_time": "04:15 AM",
                "travel_duration": "7h 45m",
                "price": max(520, train_price),
                "available_seats": 32,
                "rating": 4.6
            },
            {
                "id": "trp-chn-3",
                "transport_type": "Flight",
                "operator_name": "AirConnect",
                "vehicle_number": "AC-402",
                "departure_time": "11:15 AM",
                "arrival_time": "12:25 PM",
                "travel_duration": "1h 10m",
                "price": max(3200, flight_price),
                "available_seats": 8,
                "rating": 4.9
            }
        ]

    elif "goa" in dest_clean or "panaji" in dest_clean:
        return [
            {
                "id": "trp-goa-1",
                "transport_type": "Bus",
                "operator_name": "Konkan Travels",
                "vehicle_number": "GA-03-X-1122",
                "departure_time": "08:00 PM",
                "arrival_time": "07:00 AM",
                "travel_duration": "11h 00m",
                "price": max(850, bus_price),
                "available_seats": 14,
                "rating": 4.6
            },
            {
                "id": "trp-goa-2",
                "transport_type": "Train",
                "operator_name": "Coastal Express",
                "vehicle_number": "10111-CST",
                "departure_time": "06:00 AM",
                "arrival_time": "04:30 PM",
                "travel_duration": "10h 30m",
                "price": max(620, train_price),
                "available_seats": 20,
                "rating": 4.7
            },
            {
                "id": "trp-goa-3",
                "transport_type": "Flight",
                "operator_name": "SkyJet Airways",
                "vehicle_number": "SJ-881",
                "departure_time": "02:20 PM",
                "arrival_time": "03:35 PM",
                "travel_duration": "1h 15m",
                "price": max(3500, flight_price),
                "available_seats": 10,
                "rating": 4.8
            }
        ]

    elif "bangalore" in dest_clean or "bengaluru" in dest_clean:
        return [
            {
                "id": "trp-blr-1",
                "transport_type": "Bus",
                "operator_name": "KSRTC FlyBus",
                "vehicle_number": "KA-01-F-7001",
                "departure_time": "06:00 AM",
                "arrival_time": "12:30 PM",
                "travel_duration": "6h 30m",
                "price": max(700, bus_price),
                "available_seats": 22,
                "rating": 4.7
            },
            {
                "id": "trp-blr-2",
                "transport_type": "Train",
                "operator_name": "Shatabdi Express",
                "vehicle_number": "12007-SBC",
                "departure_time": "06:00 AM",
                "arrival_time": "11:00 AM",
                "travel_duration": "5h 00m",
                "price": max(780, train_price),
                "available_seats": 28,
                "rating": 4.8
            },
            {
                "id": "trp-blr-3",
                "transport_type": "Flight",
                "operator_name": "Deccan Air",
                "vehicle_number": "DA-310",
                "departure_time": "09:45 AM",
                "arrival_time": "10:50 AM",
                "travel_duration": "1h 05m",
                "price": max(3100, flight_price),
                "available_seats": 12,
                "rating": 4.6
            }
        ]

    else:
        # Dynamic generator for any global city
        city_title = destination.split(",")[0].strip()
        return [
            {
                "id": f"trp-{dest_clean[:3]}-1",
                "transport_type": "Bus",
                "operator_name": f"{city_title} Intercity Lines",
                "vehicle_number": f"{dest_clean[:2].upper()}-07-E-{random.randint(1000, 9999)}",
                "departure_time": "07:30 AM",
                "arrival_time": "03:45 PM",
                "travel_duration": duration_str,
                "price": max(500, bus_price),
                "available_seats": 19,
                "rating": 4.6
            },
            {
                "id": f"trp-{dest_clean[:3]}-2",
                "transport_type": "Train",
                "operator_name": f"{city_title} Superfast Express",
                "vehicle_number": f"{random.randint(12000, 19000)}-EXP",
                "departure_time": "09:15 PM",
                "arrival_time": "06:30 AM",
                "travel_duration": duration_str,
                "price": max(450, train_price),
                "available_seats": 35,
                "rating": 4.7
            },
            {
                "id": f"trp-{dest_clean[:3]}-3",
                "transport_type": "Flight",
                "operator_name": f"{city_title} Skyways",
                "vehicle_number": f"SW-{random.randint(100, 999)}",
                "departure_time": "01:20 PM",
                "arrival_time": "02:35 PM",
                "travel_duration": "1h 15m",
                "price": max(3200, flight_price),
                "available_seats": 9,
                "rating": 4.8
            }
        ]


class TransportAgent:
    """Specialized agent for generating destination transport options."""

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
        logger.info(f"[TransportAgent] Resolving options for destination='{destination}' from origin='{origin}'")

        # 1. Coordinates lookup for route calculation
        dest_lat = (state.get("destination_lat") or state.get("latitude")) if state else None
        dest_lng = (state.get("destination_lng") or state.get("longitude")) if state else None

        if not dest_lat or not dest_lng:
            geo_dest = search_place(destination)
            if geo_dest:
                dest_lat, dest_lng = geo_dest["latitude"], geo_dest["longitude"]
            else:
                dest_lat, dest_lng = 11.4102, 76.6950

        orig_name = origin or "New Delhi, Delhi, India"
        orig_lat, orig_lng = 28.6139, 77.2090
        geo_orig = search_place(orig_name)
        if geo_orig:
            orig_lat, orig_lng = geo_orig["latitude"], geo_orig["longitude"]

        # Fetch route
        route_res = get_route((orig_lat, orig_lng), (dest_lat, dest_lng))
        dist_km = route_res["distance_km"]
        duration_mins = route_res["duration_mins"]

        hours = duration_mins // 60
        mins = duration_mins % 60
        duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins} mins"

        dest_short = destination.split(",")[0].strip()
        orig_short = orig_name.split(",")[0].strip()

        # Generate destination-tailored transport options
        options = generate_destination_transport_options(destination, dist_km)
        recommended = options[0]["operator_name"] if options else "Intercity Express"
        estimated_cost = options[0]["price"] if options else int(dist_km * 1.5)

        result = {
            "transport_type": transport_type,
            "destination": destination,
            "origin": orig_name,
            "distance_km": dist_km,
            "duration_str": duration_str,
            "recommended": f"{recommended} ({options[0]['transport_type'] if options else 'Transit'})",
            "estimated_cost": estimated_cost,
            "flight_train_note": f"Calculated driving/flying path from {orig_short} to {dest_short} covering {dist_km} km.",
            "options": options,
            "summary": f"Calculated transit path from {orig_short} to {dest_short} covering {dist_km} km."
        }

        result["route_geometry"] = route_res.get("coordinates", [])

        logger.info(f"[TransportAgent] Route calculation complete: {dist_km} km | {len(options)} options")
        return {"transport": result}


transport_agent = TransportAgent()

