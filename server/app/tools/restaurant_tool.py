from typing import List, Dict, Any

def search_restaurants(destination: str, food_preference: str = "Vegetarian") -> List[Dict[str, Any]]:
    """Find top dining spots based on destination and dietary preference."""
    pref_lower = food_preference.lower()
    clean_dest = destination.split(",")[0].strip() if destination else "Destination"
    
    if "veg" in pref_lower or "vegetarian" in pref_lower:
        return [
            {
                "name": f"The Green Garden Bistro {clean_dest}",
                "cuisine": "Global Organic & Pure Veg",
                "rating": 4.8,
                "avg_cost_two": 800,
                "specialty": f"Farm-Fresh Artisanal Bowls & Fresh Juices"
            },
            {
                "name": f"Grand Annapoorna Veg {clean_dest}",
                "cuisine": "Authentic North & South Indian Pure Veg",
                "rating": 4.7,
                "avg_cost_two": 550,
                "specialty": f"Special Local Veg Thali & Crisp Ghee Dosas"
            },
            {
                "name": f"Heritage Cafe & Bakery {clean_dest}",
                "cuisine": "Continental & Healthy Breakfast",
                "rating": 4.6,
                "avg_cost_two": 750,
                "specialty": "Avocado Toast, Artisan Coffee & Fresh Pastries"
            }
        ]
    elif "vegan" in pref_lower:
        return [
            {
                "name": f"Plant Power Cafe {clean_dest}",
                "cuisine": "100% Plant-Based Organic",
                "rating": 4.9,
                "avg_cost_two": 850,
                "specialty": "Tofu Smoothie Bowls & Vegan Cheesecakes"
            },
            {
                "name": f"Earthly Eats {clean_dest}",
                "cuisine": "Vegan Fusion & Smoothies",
                "rating": 4.7,
                "avg_cost_two": 650,
                "specialty": "Gluten-Free Buddha Bowls"
            }
        ]
    else:
        return [
            {
                "name": f"The Royal Harvest Restaurant {clean_dest}",
                "cuisine": f"Local Traditional & Multi-cuisine",
                "rating": 4.7,
                "avg_cost_two": 1200,
                "specialty": f"Traditional {clean_dest} Chef Specials & Live Music"
            },
            {
                "name": f"Central Bay Grill & Dining",
                "cuisine": "Grill & Local Delicacies",
                "rating": 4.6,
                "avg_cost_two": 1100,
                "specialty": "Signature Grilled Platters & Sunset Views"
            }
        ]

