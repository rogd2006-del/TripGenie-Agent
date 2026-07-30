from typing import Dict, Any

def calculate_budget_breakdown(budget: float, duration_days: int) -> Dict[str, Any]:
    """Categorize and calculate precise budget allocation guaranteed not to exceed max budget."""
    if budget < 1000:
        return {
            "error": "No itinerary could be generated within your selected budget.",
            "hotel_cost": 0,
            "transport_cost": 0,
            "food_cost": 0,
            "sightseeing_cost": 0,
            "miscellaneous": 0,
            "taxes": 0,
            "grand_total": 0,
            "total": 0
        }

    # Allocate initial budget buckets ensuring room for 5% taxes
    net_budget = budget * 0.95
    taxes = round(budget * 0.05, 2)
    
    hotel_cost = round(net_budget * 0.42, 2)
    food_cost = round(net_budget * 0.25, 2)
    transport_cost = round(net_budget * 0.15, 2)
    sightseeing_cost = round(net_budget * 0.12, 2)
    miscellaneous = round(net_budget * 0.06, 2)

    total = round(hotel_cost + transport_cost + food_cost + sightseeing_cost + miscellaneous + taxes, 2)

    # Hard cap check: if total exceeds max budget by rounding, trim miscellaneous
    if total > budget:
        diff = round(total - budget, 2)
        miscellaneous = round(max(0, miscellaneous - diff), 2)
        total = round(hotel_cost + transport_cost + food_cost + sightseeing_cost + miscellaneous + taxes, 2)

    return {
        "stay": hotel_cost,
        "hotel_cost": hotel_cost,
        "food": food_cost,
        "food_cost": food_cost,
        "activities": sightseeing_cost,
        "sightseeing_cost": sightseeing_cost,
        "transport": transport_cost,
        "transport_cost": transport_cost,
        "contingency": miscellaneous,
        "miscellaneous": miscellaneous,
        "taxes": taxes,
        "total": total,
        "grand_total": total,
        "max_budget": budget,
        "remaining_budget": round(max(0, budget - total), 2)
    }


