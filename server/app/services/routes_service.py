"""
Routes Service using free OpenRouteService (ORS) API.
Falls back to straight-line Haversine math if API key is missing or calls fail.
"""
import urllib.parse
import urllib.request
import json
import math
from typing import Dict, Any, List, Tuple, Optional
from app.config.settings import settings
from app.utils.logger import logger


def haversine_distance(coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
    """Calculate distance in km between two (lat, lon) coordinates."""
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    R = 6371.0  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def get_route(
    start_coords: Tuple[float, float],
    end_coords: Tuple[float, float]
) -> Dict[str, Any]:
    """
    Get route geometry and directions from OpenRouteService.
    start_coords and end_coords are (lat, lon) tuples.
    """
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords

    key = settings.OPENROUTE_SERVICE_API_KEY or ""
    if key and key.strip():
        # Coordinate order in ORS directions endpoint is (lon, lat)
        url = (
            f"https://api.openrouteservice.org/v2/directions/driving-car"
            f"?api_key={key}&start={lon1},{lat1}&end={lon2},{lat2}"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TripGenieApp/1.0"})
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    features = data.get("features", [])
                    if features:
                        geom = features[0].get("geometry", {})
                        summary = features[0].get("properties", {}).get("summary", {})
                        
                        # ORS coordinates are in [lon, lat] order — convert to [lat, lon] for Leaflet
                        raw_coords = geom.get("coordinates", [])
                        route_coords = [[c[1], c[0]] for c in raw_coords]
                        
                        dist_km = round(summary.get("distance", 0) / 1000.0, 1)
                        duration_mins = int(summary.get("duration", 0) / 60.0)

                        logger.info(f"[RoutesService] Resolved real route: {dist_km} km | {duration_mins} mins")
                        return {
                            "status":        "success",
                            "coordinates":   route_coords,
                            "distance_km":   dist_km,
                            "duration_mins": duration_mins,
                        }
        except Exception as e:
            logger.warning(f"[RoutesService] ORS API routing failed: {e}. Falling back to straight line.")

    # ── Fallback Heuristic Routing ─────────────────────────────────────────
    # Generates a simple multi-segment curve connecting start and end to look natural on a map
    dist_km = haversine_distance(start_coords, end_coords)
    # Driving speed estimate: 50 km/h average
    duration_mins = int((dist_km / 50.0) * 60)
    
    # Generate 5 intermediate points on a slight arc
    segment_coords = []
    steps = 10
    for i in range(steps + 1):
        t = i / steps
        # Linear interpolation
        curr_lat = lat1 + (lat2 - lat1) * t
        curr_lon = lon1 + (lon2 - lon1) * t
        # Add a slight perpendicular displacement for visual curvature
        offset = 0.05 * math.sin(t * math.pi) * (1 if (lon2 - lon1) >= 0 else -1)
        segment_coords.append([curr_lat + offset, curr_lon + offset])

    logger.info(f"[RoutesService] Calculated fallback route: {dist_km} km | {duration_mins} mins")
    return {
        "status":        "fallback",
        "coordinates":   segment_coords,
        "distance_km":   dist_km,
        "duration_mins": max(10, duration_mins),
    }


def estimate_travel_time(
    start_coords: Tuple[float, float],
    end_coords: Tuple[float, float]
) -> Dict[str, Any]:
    """Fast estimate of duration and distance without returning coordinates."""
    res = get_route(start_coords, end_coords)
    return {
        "distance_km":   res["distance_km"],
        "duration_mins": res["duration_mins"]
    }
