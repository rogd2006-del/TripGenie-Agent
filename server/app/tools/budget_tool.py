from typing import Dict, Any

def calculate_budget_breakdown(budget: float, duration_days: int) -> Dict[str, float]:
    """Categorize and calculate precise budget allocation."""
    stay = round(budget * 0.45, 2)
    food = round(budget * 0.25, 2)
    activities = round(budget * 0.15, 2)
    transport = round(budget * 0.10, 2)
    contingency = round(budget * 0.05, 2)
    total = round(stay + food + activities + transport + contingency, 2)
    
    return {
        "stay": stay,
        "food": food,
        "activities": activities,
        "transport": transport,
        "contingency": contingency,
        "total": total
    }
