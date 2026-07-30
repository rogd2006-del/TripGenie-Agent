import math
import json
import urllib.parse
import urllib.request
import asyncio
from typing import List, Dict, Any, Tuple
from app.config.settings import settings
from app.utils.logger import logger

try:
    import httpx
except ImportError:
    httpx = None

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two lat/lon coordinates."""
    R = 6371.0  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class GooglePlacesTool:
    """Tool to search real physical hotels via Google Places API or Nominatim Places API."""

    DEFAULT_HOTEL_IMAGE = "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80"
    USER_AGENT = "TripGenieApp/1.0 (contact@tripgenie.ai)"

    async def geocode_destination(self, destination: str) -> Tuple[float, float, str]:
        """Convert destination name to (latitude, longitude, formatted_address)."""
        encoded_dest = urllib.parse.quote(destination)

        # 1. Try Google Geocoding API if key available
        if settings.GOOGLE_MAPS_API_KEY and httpx:
            try:
                async with httpx.AsyncClient() as client:
                    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_dest}&key={settings.GOOGLE_MAPS_API_KEY}"
                    res = await client.get(url, timeout=6.0)
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("results"):
                            loc = data["results"][0]["geometry"]["location"]
                            addr = data["results"][0]["formatted_address"]
                            return (loc["lat"], loc["lng"], addr)
            except Exception as e:
                logger.warning(f"Google Geocoding error: {e}")

        # 2. Fallback to OpenStreetMap Nominatim Geocoding API
        try:
            req_url = f"https://nominatim.openstreetmap.org/search?q={encoded_dest}&format=json&limit=1"
            req = urllib.request.Request(req_url, headers={"User-Agent": self.USER_AGENT})
            loop = asyncio.get_event_loop()
            res_bytes = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=5).read())
            data = json.loads(res_bytes.decode('utf-8'))
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                addr = data[0].get("display_name", destination)
                return (lat, lon, addr)
        except Exception as e:
            logger.warning(f"Nominatim geocoding error: {e}")

        h = abs(hash(destination))
        lat = round(9.0 + (h % 1800) / 100.0, 4)
        lng = round(73.0 + ((h >> 8) % 1200) / 100.0, 4)
        return (lat, lng, destination)

    async def search_nearby_hotels(
        self,
        lat: float,
        lng: float,
        radius_meters: int = 5000,
        destination_name: str = "Destination"
    ) -> List[Dict[str, Any]]:
        """Fetch real physical hotels within radius_meters using Google Places API or Nominatim Places API."""
        hotels = []

        # Option 1: Google Places API (Nearby Search + Place Details)
        if settings.GOOGLE_MAPS_API_KEY and httpx:
            try:
                async with httpx.AsyncClient() as client:
                    nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius_meters}&type=lodging&key={settings.GOOGLE_MAPS_API_KEY}"
                    res = await client.get(nearby_url, timeout=8.0)
                    if res.status_code == 200:
                        data = res.json()
                        results = data.get("results", [])
                        
                        for place in results[:6]:
                            place_id = place.get("place_id")
                            p_lat = place["geometry"]["location"]["lat"]
                            p_lng = place["geometry"]["location"]["lng"]
                            dist_km = haversine_distance(lat, lng, p_lat, p_lng)

                            phone, website, photo_url = "", "", self.DEFAULT_HOTEL_IMAGE
                            if place_id:
                                try:
                                    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number,website,photos&key={settings.GOOGLE_MAPS_API_KEY}"
                                    det_res = await client.get(details_url, timeout=5.0)
                                    if det_res.status_code == 200:
                                        det_data = det_res.json().get("result", {})
                                        phone = det_data.get("formatted_phone_number", "")
                                        website = det_data.get("website", "")
                                        if det_data.get("photos"):
                                            ref = det_data["photos"][0]["photo_reference"]
                                            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={ref}&key={settings.GOOGLE_MAPS_API_KEY}"
                                except Exception:
                                    pass

                            rating = place.get("rating", 4.5)
                            price_level = place.get("price_level", 2)
                            price_est = 2500 + (price_level * 1200)

                            hotel_obj = {
                                "hotel_name": place.get("name", "Boutique Hotel"),
                                "address": place.get("vicinity", destination_name),
                                "latitude": str(p_lat),
                                "longitude": str(p_lng),
                                "rating": str(rating),
                                "reviews": str(place.get("user_ratings_total", 120)),
                                "price": price_est,
                                "distance": f"{dist_km} km",
                                "amenities": ["Free WiFi", "Air Conditioning", "Room Service", "Swimming Pool"],
                                "phone": phone,
                                "website": website,
                                "image": photo_url,
                                "maps_url": f"https://www.google.com/maps/search/?api=1&query={p_lat},{p_lng}"
                            }
                            hotels.append(hotel_obj)

                        if hotels:
                            return hotels
            except Exception as e:
                logger.warning(f"Google Places API search failed: {e}")

        # Option 2: Real Physical Hotels via OpenStreetMap Nominatim Places API
        try:
            city_name = destination_name.split(",")[0].strip()
            query_str = urllib.parse.quote(f"hotels in {city_name}")
            req_url = f"https://nominatim.openstreetmap.org/search?q={query_str}&format=json&limit=10"
            req = urllib.request.Request(req_url, headers={"User-Agent": self.USER_AGENT})
            
            loop = asyncio.get_event_loop()
            res_bytes = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=6).read())
            data = json.loads(res_bytes.decode('utf-8'))
            
            for place in data:
                name = place.get("display_name", "").split(",")[0].strip()
                if not name or len(name) < 3:
                    continue
                
                p_lat = float(place.get("lat"))
                p_lng = float(place.get("lon"))
                dist_km = haversine_distance(lat, lng, p_lat, p_lng)

                full_addr = ", ".join(place.get("display_name", "").split(",")[1:4]).strip()
                if not full_addr:
                    full_addr = destination_name

                hotels.append({
                    "hotel_name": name,
                    "address": full_addr,
                    "latitude": str(p_lat),
                    "longitude": str(p_lng),
                    "rating": "4.6",
                    "reviews": "184",
                    "price": 3500,
                    "distance": f"{dist_km} km",
                    "amenities": ["Free WiFi", "Air Conditioning", "24/7 Front Desk", "Breakfast Included"],
                    "phone": "",
                    "website": "",
                    "image": self.DEFAULT_HOTEL_IMAGE,
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={p_lat},{p_lng}"
                })

            if hotels:
                return hotels[:6]
        except Exception as e:
            logger.warning(f"Nominatim real hotel search error: {e}")

        return hotels

    async def search_places_by_type(
        self,
        destination: str,
        place_type: str,
        limit: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        Search for any type of place (beach, temple, museum, hospital, etc.)
        at a given destination using Google Places Text Search → OSM Overpass fallback.
        Returns a list of place dicts with name, rating, address, coordinates, maps_url.
        """
        places: List[Dict[str, Any]] = []
        lat, lng, addr = await self.geocode_destination(destination)

        # ── 1. Google Places Text Search ────────────────────────────────────
        if settings.GOOGLE_MAPS_API_KEY and httpx:
            try:
                query = urllib.parse.quote(f"{place_type} in {destination}")
                url = (
                    f"https://maps.googleapis.com/maps/api/place/textsearch/json"
                    f"?query={query}&key={settings.GOOGLE_MAPS_API_KEY}"
                )
                async with httpx.AsyncClient() as client:
                    res = await client.get(url, timeout=8.0)
                    if res.status_code == 200:
                        results = res.json().get("results", [])
                        for place in results[:limit]:
                            p_lat = place["geometry"]["location"]["lat"]
                            p_lng = place["geometry"]["location"]["lng"]
                            photo_url = ""
                            if settings.GOOGLE_MAPS_API_KEY and place.get("photos"):
                                ref = place["photos"][0]["photo_reference"]
                                photo_url = (
                                    f"https://maps.googleapis.com/maps/api/place/photo"
                                    f"?maxwidth=800&photo_reference={ref}&key={settings.GOOGLE_MAPS_API_KEY}"
                                )
                            places.append({
                                "name":         place.get("name", "Unknown Place"),
                                "address":      place.get("formatted_address", destination),
                                "rating":       str(place.get("rating", "N/A")),
                                "reviews":      str(place.get("user_ratings_total", 0)),
                                "latitude":     str(p_lat),
                                "longitude":    str(p_lng),
                                "maps_url":     f"https://www.google.com/maps/search/?api=1&query={p_lat},{p_lng}",
                                "photo":        photo_url,
                                "place_type":   place_type,
                            })
                        if places:
                            return places
            except Exception as e:
                logger.warning(f"Google Places Text Search error for '{place_type}' in '{destination}': {e}")

        # ── 2. OSM Overpass API fallback ────────────────────────────────────
        # Map common human keywords → OSM tag key/value pairs
        osm_tag_map = {
            "beach":                ("natural", "beach"),
            "waterfall":            ("waterway", "waterfall"),
            "mountain":             ("natural", "peak"),
            "temple":               ("amenity", "place_of_worship"),
            "museum":               ("tourism", "museum"),
            "park":                 ("leisure", "park"),
            "historical":           ("historic", "monument"),
            "monument":             ("historic", "monument"),
            "shopping":             ("shop", "mall"),
            "market":               ("amenity", "marketplace"),
            "hospital":             ("amenity", "hospital"),
            "pharmacy":             ("amenity", "pharmacy"),
            "police":               ("amenity", "police"),
            "bar":                  ("amenity", "bar"),
            "nightclub":            ("amenity", "nightclub"),
            "tourist attraction":   ("tourism", "attraction"),
            "viewpoint":            ("tourism", "viewpoint"),
            "adventure":            ("sport", "climbing"),
        }

        # Find best matching OSM tag
        osm_tag = None
        place_type_lower = place_type.lower()
        for keyword, tag in osm_tag_map.items():
            if keyword in place_type_lower:
                osm_tag = tag
                break
        if not osm_tag:
            osm_tag = ("tourism", "attraction")  # default

        radius_m = 30000  # 30 km search radius
        overpass_query = (
            f'[out:json][timeout:10];'
            f'(node["{osm_tag[0]}"="{osm_tag[1]}"](around:{radius_m},{lat},{lng});'
            f' way["{osm_tag[0]}"="{osm_tag[1]}"](around:{radius_m},{lat},{lng}););'
            f'out center {limit};'
        )

        try:
            req_url = "https://overpass-api.de/api/interpreter"
            req = urllib.request.Request(
                req_url,
                data=urllib.parse.urlencode({"data": overpass_query}).encode("utf-8"),
                headers={"User-Agent": self.USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"},
                method="POST"
            )
            loop = __import__("asyncio").get_event_loop()
            res_bytes = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=10).read())
            data = json.loads(res_bytes.decode("utf-8"))

            for elem in data.get("elements", [])[:limit]:
                tags = elem.get("tags", {})
                name = tags.get("name") or tags.get("name:en", "")
                if not name or len(name) < 2:
                    continue
                p_lat = elem.get("lat") or elem.get("center", {}).get("lat", lat)
                p_lng = elem.get("lon") or elem.get("center", {}).get("lon", lng)
                places.append({
                    "name":       name,
                    "address":    tags.get("addr:full") or tags.get("addr:city") or destination,
                    "rating":     "N/A",
                    "reviews":    "0",
                    "latitude":   str(p_lat),
                    "longitude":  str(p_lng),
                    "maps_url":   f"https://www.google.com/maps/search/?api=1&query={p_lat},{p_lng}",
                    "photo":      "",
                    "place_type": place_type,
                })
        except Exception as e:
            logger.warning(f"Overpass API search error for '{place_type}' in '{destination}': {e}")

        return places


google_places_tool = GooglePlacesTool()
