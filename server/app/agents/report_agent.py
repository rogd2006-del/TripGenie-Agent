from typing import Dict, Any

class ReportAgent:
    def __init__(self):
        self.name = "Report Generator"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        dest = state.get("destination", "Goa, India")
        days = state.get("duration_days", 4)
        budget = state.get("budget", 20000)
        food = state.get("food_preference", "Vegetarian")
        
        summary = (
            f"A fully autonomous, multi-agent planned {days}-day trip to {dest} curated within a "
            f"budget of ₹{budget:,}. Features tailored {food} dining, beach activity schedules, "
            f"vetted hotel options, and full expense breakdown."
        )
        
        # Cover image mapping based on destination
        dest_lower = dest.lower()
        cover_image = "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80"
        if "bali" in dest_lower:
            cover_image = "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=80"
        elif "paris" in dest_lower:
            cover_image = "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80"
        elif "tokyo" in dest_lower:
            cover_image = "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80"

        return {
            "summary": summary,
            "cover_image": cover_image
        }

report_agent = ReportAgent()
