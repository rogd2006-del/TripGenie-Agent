from typing import Dict, Any

def search_transportation(destination: str, duration_days: int) -> Dict[str, Any]:
    """Calculate transport recommendations and estimated costs."""
    return {
        "recommended": "Self-drive Scooter / Rental Car & Airport Taxi",
        "estimated_cost": max(1500, duration_days * 600),
        "flight_train_note": f"Fly into primary airport near {destination}. Pre-booked prepaid taxis recommended from terminal."
    }
