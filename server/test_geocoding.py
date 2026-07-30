import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.location_service import search_place
from app.agents.destination_agent import destination_agent
from app.utils.logger import logger

CITIES_TO_TEST = [
    "Mumbai",
    "Chennai",
    "Goa",
    "Varkala",
    "Delhi",
    "Ooty",
    "Mysore",
    "Kodaikanal",
    "Bangalore",
    "Hyderabad"
]

def test_all_destinations():
    print("=" * 60)
    print("Testing Geocoding & Destination Agent Resolution")
    print("=" * 60)
    
    passed = 0
    total = len(CITIES_TO_TEST)
    
    for city in CITIES_TO_TEST:
        state = {"destination": city}
        result = destination_agent.run(state)
        
        if not result.get("geocoding_failed") and result.get("latitude") and result.get("longitude"):
            print(f"[OK] {city:12} -> Lat: {result['latitude']:<9}, Lng: {result['longitude']:<9} | {result.get('display_name')}")
            passed += 1
        else:
            print(f"[FAIL] {city:12} -> Failed: {result.get('error')}")

    print("=" * 60)
    print(f"Results: {passed}/{total} cities resolved successfully!")
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = test_all_destinations()
    sys.exit(0 if success else 1)
