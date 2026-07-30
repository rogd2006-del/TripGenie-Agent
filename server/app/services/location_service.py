"""
Location Service using free OpenStreetMap Nominatim, Photon Komoot, Open-Meteo, and curated offline fallback.
Features: caching search results, multi-provider fallback, robust headers, comprehensive logging.
"""
import urllib.parse
import urllib.request
import json
import time
from typing import Dict, Any, Optional, Tuple
from app.utils.logger import logger

USER_AGENT = "TripGenie-Travel-Planner-AgenticAI/2.0 (contact@tripgenie.ai)"

# In-memory cache to avoid duplicate API calls
_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}
_REVERSE_CACHE: Dict[Tuple[float, float], Dict[str, Any]] = {}

# Offline coordinate fallback table for top Indian & Global destinations to guarantee 100% resolution uptime
_OFFLINE_COORDINATES: Dict[str, Dict[str, Any]] = {
    "ooty": {"lat": 11.4102, "lng": 76.6950, "name": "Ooty (Udhagamandalam), Tamil Nadu, India", "state": "Tamil Nadu", "country": "India"},
    "udhagamandalam": {"lat": 11.4102, "lng": 76.6950, "name": "Ooty (Udhagamandalam), Tamil Nadu, India", "state": "Tamil Nadu", "country": "India"},
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "name": "Mumbai, Maharashtra, India", "state": "Maharashtra", "country": "India"},
    "chennai": {"lat": 13.0827, "lng": 80.2707, "name": "Chennai, Tamil Nadu, India", "state": "Tamil Nadu", "country": "India"},
    "goa": {"lat": 15.2993, "lng": 74.1240, "name": "Goa, India", "state": "Goa", "country": "India"},
    "panaji": {"lat": 15.4909, "lng": 73.8278, "name": "Panaji, Goa, India", "state": "Goa", "country": "India"},
    "varkala": {"lat": 8.7379, "lng": 76.7163, "name": "Varkala, Kerala, India", "state": "Kerala", "country": "India"},
    "mysore": {"lat": 12.2958, "lng": 76.6394, "name": "Mysuru (Mysore), Karnataka, India", "state": "Karnataka", "country": "India"},
    "mysuru": {"lat": 12.2958, "lng": 76.6394, "name": "Mysuru (Mysore), Karnataka, India", "state": "Karnataka", "country": "India"},
    "kodaikanal": {"lat": 10.2381, "lng": 77.4892, "name": "Kodaikanal, Tamil Nadu, India", "state": "Tamil Nadu", "country": "India"},
    "manali": {"lat": 32.2432, "lng": 77.1892, "name": "Manali, Himachal Pradesh, India", "state": "Himachal Pradesh", "country": "India"},
    "jaipur": {"lat": 26.9124, "lng": 75.7873, "name": "Jaipur, Rajasthan, India", "state": "Rajasthan", "country": "India"},
    "delhi": {"lat": 28.6139, "lng": 77.2090, "name": "New Delhi, Delhi, India", "state": "Delhi", "country": "India"},
    "new delhi": {"lat": 28.6139, "lng": 77.2090, "name": "New Delhi, Delhi, India", "state": "Delhi", "country": "India"},
    "bengaluru": {"lat": 12.9716, "lng": 77.5946, "name": "Bengaluru, Karnataka, India", "state": "Karnataka", "country": "India"},
    "bangalore": {"lat": 12.9716, "lng": 77.5946, "name": "Bengaluru, Karnataka, India", "state": "Karnataka", "country": "India"},
    "kochi": {"lat": 9.9312, "lng": 76.2673, "name": "Kochi, Kerala, India", "state": "Kerala", "country": "India"},
    "cochin": {"lat": 9.9312, "lng": 76.2673, "name": "Kochi, Kerala, India", "state": "Kerala", "country": "India"},
    "shimla": {"lat": 31.1048, "lng": 77.1734, "name": "Shimla, Himachal Pradesh, India", "state": "Himachal Pradesh", "country": "India"},
    "agra": {"lat": 27.1767, "lng": 78.0081, "name": "Agra, Uttar Pradesh, India", "state": "Uttar Pradesh", "country": "India"},
    "varanasi": {"lat": 25.3176, "lng": 82.9739, "name": "Varanasi, Uttar Pradesh, India", "state": "Uttar Pradesh", "country": "India"},
    "pondicherry": {"lat": 11.9416, "lng": 79.8083, "name": "Puducherry, India", "state": "Puducherry", "country": "India"},
    "puducherry": {"lat": 11.9416, "lng": 79.8083, "name": "Puducherry, India", "state": "Puducherry", "country": "India"},
    "munnar": {"lat": 10.0889, "lng": 77.0595, "name": "Munnar, Kerala, India", "state": "Kerala", "country": "India"},
    "udaipur": {"lat": 24.5854, "lng": 73.7125, "name": "Udaipur, Rajasthan, India", "state": "Rajasthan", "country": "India"},
    "darjeeling": {"lat": 27.0410, "lng": 88.2663, "name": "Darjeeling, West Bengal, India", "state": "West Bengal", "country": "India"},
    "rishikesh": {"lat": 30.0869, "lng": 78.2676, "name": "Rishikesh, Uttarakhand, India", "state": "Uttarakhand", "country": "India"},
    "alleppey": {"lat": 9.4981, "lng": 76.3388, "name": "Alappuzha (Alleppey), Kerala, India", "state": "Kerala", "country": "India"},
    "alappuzha": {"lat": 9.4981, "lng": 76.3388, "name": "Alappuzha (Alleppey), Kerala, India", "state": "Kerala", "country": "India"},
    "wayanad": {"lat": 11.6854, "lng": 76.1320, "name": "Wayanad, Kerala, India", "state": "Kerala", "country": "India"},
    "coorg": {"lat": 12.3375, "lng": 75.8069, "name": "Coorg (Kodagu), Karnataka, India", "state": "Karnataka", "country": "India"},
    "kodagu": {"lat": 12.3375, "lng": 75.8069, "name": "Coorg (Kodagu), Karnataka, India", "state": "Karnataka", "country": "India"},
    "leh": {"lat": 34.1526, "lng": 77.5771, "name": "Leh, Ladakh, India", "state": "Ladakh", "country": "India"},
    "srinagar": {"lat": 34.0837, "lng": 74.7973, "name": "Srinagar, Jammu and Kashmir, India", "state": "Jammu and Kashmir", "country": "India"},
    "paris": {"lat": 48.8566, "lng": 2.3522, "name": "Paris, France", "state": "Île-de-France", "country": "France"},
    "london": {"lat": 51.5074, "lng": -0.1278, "name": "London, United Kingdom", "state": "England", "country": "United Kingdom"},
    "tokyo": {"lat": 35.6762, "lng": 139.6503, "name": "Tokyo, Japan", "state": "Kanto", "country": "Japan"},
    "dubai": {"lat": 25.2048, "lng": 55.2708, "name": "Dubai, United Arab Emirates", "state": "Dubai", "country": "United Arab Emirates"},
    "singapore": {"lat": 1.3521, "lng": 103.8198, "name": "Singapore", "state": "Singapore", "country": "Singapore"},
    "new york": {"lat": 40.7128, "lng": -74.0060, "name": "New York, USA", "state": "New York", "country": "United States"}
}


def search_place(destination: str) -> Optional[Dict[str, Any]]:
    """
    Geocode a destination string into coordinates and metadata.
    Pipeline order:
    1. Check Cache
    2. Nominatim OpenStreetMap API (format=json, limit=1, User-Agent header)
    3. Photon Komoot OSM API fallback
    4. Open-Meteo Geocoding API fallback
    5. Curated Offline Location Dictionary fallback
    """
    clean_dest = destination.strip()
    if not clean_dest:
        return None

    if clean_dest in _GEOCODE_CACHE:
        cached = _GEOCODE_CACHE[clean_dest]
        logger.info(
            f"[LocationService] Cache hit for '{clean_dest}' -> Lat: {cached['latitude']}, Lng: {cached['longitude']}"
        )
        return cached

    encoded = urllib.parse.quote(clean_dest)

    # ------------------------------------------------------------------
    # Layer 1: Nominatim OpenStreetMap Geocoding API
    # ------------------------------------------------------------------
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&addressdetails=1&limit=1"
    req = urllib.request.Request(nominatim_url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.status
            if status_code == 200:
                raw_body = response.read().decode("utf-8")
                data = json.loads(raw_body)
                if data and isinstance(data, list) and len(data) > 0:
                    place = data[0]
                    addr = place.get("address", {})
                    state = addr.get("state") or addr.get("region") or addr.get("county") or ""
                    country = addr.get("country") or ""

                    bbox = place.get("boundingbox", [
                        str(float(place["lat"]) - 0.05),
                        str(float(place["lat"]) + 0.05),
                        str(float(place["lon"]) - 0.05),
                        str(float(place["lon"]) + 0.05)
                    ])

                    res = {
                        "destination":  clean_dest,
                        "latitude":     float(place["lat"]),
                        "longitude":    float(place["lon"]),
                        "display_name": place.get("display_name", clean_dest),
                        "country":      country,
                        "state":        state,
                        "boundingbox":  bbox,
                    }
                    _GEOCODE_CACHE[clean_dest] = res
                    logger.info(
                        f"[LocationService] [Nominatim OK] Geocoding request for '{clean_dest}' -> Lat: {res['latitude']}, Lng: {res['longitude']}"
                    )
                    return res
                else:
                    logger.warning(f"[LocationService] Nominatim returned empty results list for '{clean_dest}'. Response: {raw_body}")
            else:
                logger.warning(f"[LocationService] Nominatim returned HTTP status {status_code} for '{clean_dest}'")
    except Exception as e:
        logger.warning(f"[LocationService] Nominatim geocoding failed for '{clean_dest}': {e}")

    # ------------------------------------------------------------------
    # Layer 2: Photon Komoot API Fallback
    # ------------------------------------------------------------------
    photon_url = f"https://photon.komoot.io/api/?q={encoded}&limit=1"
    req_photon = urllib.request.Request(photon_url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req_photon, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                features = data.get("features", [])
                if features:
                    feat = features[0]
                    coords = feat.get("geometry", {}).get("coordinates", [])
                    props = feat.get("properties", {})
                    if len(coords) >= 2:
                        lon = float(coords[0])
                        lat = float(coords[1])
                        name = props.get("name") or props.get("city") or clean_dest
                        country = props.get("country", "")
                        state = props.get("state", "")

                        res = {
                            "destination":  clean_dest,
                            "latitude":     lat,
                            "longitude":    lon,
                            "display_name": f"{name}, {state}, {country}".strip(", "),
                            "country":      country,
                            "state":        state,
                        }
                        _GEOCODE_CACHE[clean_dest] = res
                        logger.info(
                            f"[LocationService] [Photon OK] Geocoding request for '{clean_dest}' -> Lat: {res['latitude']}, Lng: {res['longitude']}"
                        )
                        return res
    except Exception as e:
        logger.warning(f"[LocationService] Photon geocoding failed for '{clean_dest}': {e}")

    # ------------------------------------------------------------------
    # Layer 3: Open-Meteo Geocoding API Fallback
    # ------------------------------------------------------------------
    clean_name = clean_dest.split(",")[0].strip()
    encoded_clean = urllib.parse.quote(clean_name)
    openmeteo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_clean}&count=1&language=en&format=json"
    req_meteo = urllib.request.Request(openmeteo_url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req_meteo, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                results = data.get("results", [])
                if results:
                    r = results[0]
                    lat = float(r["latitude"])
                    lon = float(r["longitude"])
                    name = r.get("name", clean_dest)
                    country = r.get("country", "")
                    state = r.get("admin1", "")

                    res = {
                        "destination":  clean_dest,
                        "latitude":     lat,
                        "longitude":    lon,
                        "display_name": f"{name}, {state}, {country}".strip(", "),
                        "country":      country,
                        "state":        state,
                    }
                    _GEOCODE_CACHE[clean_dest] = res
                    logger.info(
                        f"[LocationService] [Open-Meteo OK] Geocoding request for '{clean_dest}' -> Lat: {res['latitude']}, Lng: {res['longitude']}"
                    )
                    return res
    except Exception as e:
        logger.warning(f"[LocationService] Open-Meteo geocoding failed for '{clean_dest}': {e}")

    # ------------------------------------------------------------------
    # Layer 4: Offline Curated Location Dictionary Fallback
    # ------------------------------------------------------------------
    dict_key = clean_name.lower()
    if dict_key in _OFFLINE_COORDINATES:
        offline_match = _OFFLINE_COORDINATES[dict_key]
        res = {
            "destination":  clean_dest,
            "latitude":     offline_match["lat"],
            "longitude":    offline_match["lng"],
            "display_name": offline_match["name"],
            "country":      offline_match["country"],
            "state":        offline_match["state"],
        }
        _GEOCODE_CACHE[clean_dest] = res
        logger.info(
            f"[LocationService] [Offline Database OK] Geocoding request for '{clean_dest}' -> Lat: {res['latitude']}, Lng: {res['longitude']}"
        )
        return res

    # If all 4 layers fail to resolve
    logger.error(
        f"[LocationService] Geocoding FAILED completely for '{clean_dest}'. All APIs and Offline fallbacks exhausted."
    )
    return None


def reverse_geocode(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Reverse geocode coordinates into a readable address using Nominatim.
    Retries once on failure. Caches results.
    """
    cache_key = (round(lat, 5), round(lon, 5))
    if cache_key in _REVERSE_CACHE:
        return _REVERSE_CACHE[cache_key]

    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    addr = data.get("address", {})
                    res = {
                        "display_name": data.get("display_name", f"{lat}, {lon}"),
                        "city":         addr.get("city") or addr.get("town") or addr.get("village") or "",
                        "state":        addr.get("state") or "",
                        "country":      addr.get("country") or "",
                    }
                    _REVERSE_CACHE[cache_key] = res
                    return res
        except Exception as e:
            logger.error(f"[LocationService] Reverse geocoding attempt {attempt + 1} failed for ({lat}, {lon}): {e}")
            if attempt == 0:
                time.sleep(0.5)

    return None
