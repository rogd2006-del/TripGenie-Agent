import urllib.parse
import urllib.request
import json
from typing import Dict, Any

USER_AGENT = "TripGenieApp/1.0 (contact@tripgenie.ai)"

def search_destination_coordinates(destination: str) -> Dict[str, Any]:
    """Provide destination coordinates and map bounding box dynamically for ANY destination."""
    clean_dest = destination.strip() if destination else ""
    if not clean_dest:
        return {"error": "Unable to locate the destination."}

    encoded_dest = urllib.parse.quote(clean_dest)
    try:
        req_url = f"https://nominatim.openstreetmap.org/search?q={encoded_dest}&format=json&limit=1"
        req = urllib.request.Request(req_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lng = float(data[0]["lon"])
                zoom = 12
                embed_url = f"https://maps.google.com/maps?q={encoded_dest}&z={zoom}&output=embed"
                return {
                    "destination": clean_dest,
                    "latitude": lat,
                    "longitude": lng,
                    "zoom": zoom,
                    "map_embed_url": embed_url
                }
    except Exception as e:
        pass

    return {"destination": clean_dest, "error": "Unable to locate the destination."}

