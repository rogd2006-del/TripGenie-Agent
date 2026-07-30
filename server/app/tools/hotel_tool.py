import random
from typing import List, Dict, Any

HOTEL_PREFIXES = ["The Grand", "Royal", "Heritage", "Sands", "Skyline", "Ocean View", "Boutique", "Palace & Spa", "Golden Oasis", "Paradise", "Serenity", "La Residency"]
HOTEL_SUFFIXES = ["Resort & Spa", "Suites", "Palace", "Boutique Stay", "Inn & Suites", "Grand Hotel", "Beach Villa", "Heights", "Retreat", "Lodge"]

ALL_AMENITIES = [
    "Free High-Speed WiFi", "Infinity Swimming Pool", "Rooftop Restaurant & Bar", 
    "Complimentary Breakfast", "Full-service Spa & Wellness", "24/7 Room Service", 
    "Airport Shuttle Service", "Fitness Center & Gym", "Panoramic City/Ocean View", 
    "Air Conditioned Rooms", "Valet Parking", "Concierge Service"
]

HOTEL_IMAGES = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80"
]

def search_hotels(destination: str, luxury_level: str = "Moderate", budget: float = 20000) -> List[Dict[str, Any]]:
    """Generate realistic, randomized fake hotels tailored to the target destination."""
    clean_dest = destination.split(",")[0].strip() if destination else "Destination"
    
    # Use destination + luxury level hash to seed random for reproducible yet distinct per destination results
    seed_val = hash(f"{clean_dest.lower()}_{luxury_level.lower()}") % (2**32)
    rng = random.Random(seed_val)

    lux = luxury_level.lower()
    if budget <= 5000 or lux == "budget":
        base_price = min(1800, max(900, int(budget * 0.25)))
        tier_label = "Budget"
    elif lux == "luxury" or budget >= 35000:
        base_price = max(4200, int(budget * 0.30))
        tier_label = "Luxury"
    else:
        base_price = max(2200, int(budget * 0.20))
        tier_label = "Moderate"

    hotels = []
    prefixes = rng.sample(HOTEL_PREFIXES, 3)
    suffixes = rng.sample(HOTEL_SUFFIXES, 3)

    for i in range(3):
        pfx = prefixes[i]
        sfx = suffixes[i]
        hotel_name = f"{pfx} {clean_dest} {sfx}"
        
        # Price variation: +/- 20%
        price_variation = rng.randint(-15, 25)
        price_per_night = max(800, int(base_price * (1 + price_variation / 100.0)))
        
        rating = round(rng.uniform(4.2, 4.9), 1)
        reviews_cnt = rng.randint(120, 950)
        
        # Select 4 random amenities
        amenities = rng.sample(ALL_AMENITIES, 4)
        
        img = HOTEL_IMAGES[i % len(HOTEL_IMAGES)]
        address = f"No. {rng.randint(12, 180)}, Main Boulevard, {clean_dest}, India"
        
        hotels.append({
            "hotel_id": f"HTL-{clean_dest[:3].upper()}-{rng.randint(100, 999)}",
            "name": hotel_name,
            "hotel_name": hotel_name,
            "rating": str(rating),
            "reviews": str(reviews_cnt),
            "price_per_night": price_per_night,
            "price": price_per_night,
            "amenities": amenities,
            "address": address,
            "image": img,
            "tier": tier_label,
            "maps_url": f"https://www.google.com/maps/search/?api=1&query={hotel_name.replace(' ', '+')}"
        })

    return hotels
