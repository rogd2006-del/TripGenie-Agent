from typing import Dict, Any
import os
import re
from app.services.llm_factory import llm_factory, HeuristicLLMRunner

class PlannerAgent:
    def __init__(self):
        self.name = "Planner Agent"
        self.runner = HeuristicLLMRunner()

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        req = state.get("request", {})
        prompt = req.get("prompt", "")
        
        # Determine destination dynamically
        if req.get("destination"):
            destination = req.get("destination").strip().title()
        elif prompt:
            destination = self.runner.extract_destination(prompt)
        else:
            destination = state.get("destination", "Varkala, Kerala, India")
            
        # Determine budget dynamically
        budget = req.get("budget")
        if (budget is None or budget == "") and prompt:
            b_match = (
                re.search(r"(?:under|budget|cost|price|spend|for|with|of|₹|\$|inr|rs\.?)\s*(?:is|to|=)?\s*(?:₹|\$)?\s*([0-9,]+)", prompt, re.IGNORECASE) or
                re.search(r"([0-9,]+)\s*(?:inr|rs|rupees|budget)", prompt, re.IGNORECASE)
            )
            if b_match:
                try:
                    budget = float(b_match.group(1).replace(",", ""))
                except Exception:
                    budget = 20000.0
        if budget is None or budget == "":
            budget = 20000.0
            
        # Determine days dynamically
        days = req.get("duration_days")
        if not days and prompt:
            d_match = re.search(r"(\d+)\s*(?:-| )*(?:day|days)", prompt, re.IGNORECASE)
            if d_match:
                try:
                    days = int(d_match.group(1))
                except Exception:
                    days = 4
        if not days:
            days = 4
            
        food_pref = req.get("food_preference", "Vegetarian")
        if prompt and "vegan" in prompt.lower():
            food_pref = "Vegan"
        elif prompt and "non-veg" in prompt.lower():
            food_pref = "Non-Vegetarian"
        elif prompt and "halal" in prompt.lower():
            food_pref = "Halal"

        luxury_level = req.get("luxury_level", "Moderate")
        if prompt and ("luxury" in prompt.lower() or "5 star" in prompt.lower() or "resort" in prompt.lower()):
            luxury_level = "Luxury"
        elif prompt and ("budget" in prompt.lower() or "backpacker" in prompt.lower() or "hostel" in prompt.lower()):
            luxury_level = "Budget"

        adventure_level = req.get("adventure_level", "High")
        
        return {
            "destination": destination,
            "budget": float(budget),
            "duration_days": int(days),
            "travelers": req.get("travelers", 2),
            "food_preference": food_pref,
            "luxury_level": luxury_level,
            "adventure_level": adventure_level,
            "title": f"{days}-Day Unforgettable {destination} Trip"
        }

planner_agent = PlannerAgent()

