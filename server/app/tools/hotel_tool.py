from typing import List, Dict, Any

def search_hotels(destination: str, luxury_level: str = "Moderate", budget: float = 20000) -> List[Dict[str, Any]]:
    """Search lodging options tailored to target destination, luxury level, and budget."""
    clean_dest = destination.split(",")[0].strip() if destination else "Destination"
    
    # If budget is low (e.g. <= 5000 or 3000), default luxury level to budget
    if budget <= 5000 or luxury_level.lower() == "budget":
        return [
            {
                "name": f"The Backpackers Sanctuary {clean_dest}",
                "rating": 4.4,
                "price_per_night": min(1200, max(800, int(budget * 0.4))),
                "amenities": ["Free WiFi", "Social Lounge", "Lockers", "Coffee Bar"],
                "address": f"Central Heritage Street, {destination}",
                "image": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": f"{clean_dest} Cliffside Budget Homestay",
                "rating": 4.5,
                "price_per_night": min(2200, max(1500, int(budget * 0.7))),
                "amenities": ["Free WiFi", "Kitchenette", "Garden Terrace", "Breakfast"],
                "address": f"Cliff Promenade, {destination}",
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": f"{clean_dest} Beach Breeze Inn",
                "rating": 4.3,
                "price_per_night": min(2800, max(1800, int(budget * 0.85))),
                "amenities": ["Sea View", "Free WiFi", "AC Rooms", "24/7 Desk"],
                "address": f"Papanasam Beach Road, {destination}",
                "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=500&q=80"
            }
        ]
    elif luxury_level.lower() == "luxury":
        return [
            {
                "name": f"The Royal Grand Palace & Spa {clean_dest}",
                "rating": 4.9,
                "price_per_night": max(4500, int(budget * 0.35)),
                "amenities": ["Infinity Pool", "Panoramic Spa & Wellness", "Fine Dining", "Concierge"],
                "address": f"Prime Avenue, {destination}",
                "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": f"Heritage Grand Hotel {clean_dest}",
                "rating": 4.8,
                "price_per_night": max(3800, int(budget * 0.28)),
                "amenities": ["Rooftop Lounge", "Valet Parking", "Butler Service", "Gourmet Breakfast"],
                "address": f"Downtown Boulevard, {destination}",
                "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=500&q=80"
            }
        ]
    else:  # Moderate
        return [
            {
                "name": f"{clean_dest} Residency & Suites",
                "rating": 4.6,
                "price_per_night": max(2200, int(budget * 0.18)),
                "amenities": ["Swimming Pool", "Free Hot Breakfast", "Scenic Views", "High-speed WiFi"],
                "address": f"Main Boulevard, {destination}",
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": f"Green Promenade Hotel {clean_dest}",
                "rating": 4.5,
                "price_per_night": max(1800, int(budget * 0.15)),
                "amenities": ["Balcony Views", "Breakfast Included", "24/7 Front Desk"],
                "address": f"Park Road, {destination}",
                "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=500&q=80"
            }
        ]

