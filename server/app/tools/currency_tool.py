from typing import Dict, Any

FX_RATES = {
    "INR": 1.0,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0095,
    "AED": 0.044
}

def convert_currency(amount: float, from_curr: str = "INR", to_curr: str = "USD") -> float:
    """Convert amount across supported currencies."""
    if from_curr not in FX_RATES or to_curr not in FX_RATES:
        return amount
    in_inr = amount / FX_RATES[from_curr]
    return round(in_inr * FX_RATES[to_curr], 2)
