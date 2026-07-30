"""
Supervisor Agent — Dynamic intent-to-agents router.
Selects one or more specialized agents based on detected intent.
"""
from typing import Dict, Any, List
from app.utils.logger import logger
from app.services.intent_classifier import Intent


# ── Intent → Agent plan mapping ─────────────────────────────────────────────
# Each plan is a list of agent identifiers to run in parallel.
# The Chat Agent always synthesizes the final response using tool outputs.

_INTENT_AGENT_MAP: Dict[str, List[str]] = {
    # Conversational
    Intent.GREETING:               ["chat"],
    Intent.GENERAL_CONVERSATION:   ["chat"],
    Intent.GENERAL_TRAVEL_QUESTION:["destination", "chat"],

    # Destination info
    Intent.DESTINATION_INFO:       ["destination"],
    Intent.TOURIST_ATTRACTIONS:    ["attractions", "destination"],

    # Nature
    Intent.BEACHES:                ["attractions"],
    Intent.WATERFALLS:             ["attractions"],
    Intent.MOUNTAINS:              ["attractions"],
    Intent.PARKS:                  ["attractions"],
    Intent.HISTORICAL_PLACES:      ["attractions", "destination"],

    # Culture
    Intent.TEMPLES:                ["attractions"],
    Intent.MUSEUMS:                ["attractions"],

    # Accommodation
    Intent.HOTELS:                 ["hotel"],
    Intent.RESORTS:                ["hotel"],
    Intent.HOSTELS:                ["hotel"],

    # Food
    Intent.RESTAURANTS:            ["restaurant"],
    Intent.CAFES:                  ["restaurant"],
    Intent.STREET_FOOD:            ["restaurant"],

    # Shopping & lifestyle
    Intent.SHOPPING:               ["attractions"],
    Intent.NIGHTLIFE:              ["attractions"],
    Intent.LOCAL_EVENTS:           ["attractions"],

    # Activities
    Intent.ADVENTURE_ACTIVITIES:   ["attractions"],
    Intent.FAMILY_ACTIVITIES:      ["attractions"],
    Intent.COUPLE_ACTIVITIES:      ["attractions"],
    Intent.KIDS_ACTIVITIES:        ["attractions"],
    Intent.ACCESSIBILITY:          ["destination", "chat"],

    # Weather
    Intent.WEATHER:                ["weather"],

    # Transport
    Intent.LOCAL_TRANSPORT:        ["transport"],
    Intent.TAXI:                   ["transport"],
    Intent.FLIGHTS:                ["transport"],
    Intent.TRAIN_INFORMATION:      ["transport"],
    Intent.BUS_INFORMATION:        ["transport"],

    # Finance
    Intent.BUDGET_PLANNING:        ["budget"],
    Intent.CURRENCY:               ["budget"],

    # Travel prep
    Intent.TRAVEL_TIPS:            ["destination", "chat"],
    Intent.PACKING_SUGGESTIONS:    ["packing"],
    Intent.VISA_INFORMATION:       ["destination", "chat"],

    # Safety & emergency
    Intent.SAFETY:                 ["emergency"],
    Intent.EMERGENCY_SERVICES:     ["emergency"],
    Intent.HOSPITALS:              ["emergency"],
    Intent.PHARMACIES:             ["emergency"],

    # Itinerary (multi-agent)
    Intent.ITINERARY_GENERATION:   ["destination", "weather", "hotel", "restaurant", "itinerary"],
    Intent.ITINERARY_MODIFICATION: ["itinerary"],

    # Booking
    Intent.BOOKING_ASSISTANCE:     ["hotel", "transport"],
}

# Sub-type → attractions search keyword mapping
SUBTYPE_KEYWORD_MAP: Dict[str, str] = {
    "beach":        "beach",
    "waterfall":    "waterfall",
    "mountain":     "mountain trekking",
    "temple":       "temple hindu",
    "museum":       "museum",
    "park":         "park garden",
    "historical":   "historical heritage monument",
    "shopping":     "shopping market",
    "nightlife":    "nightclub bar",
    "adventure":    "adventure sports",
    "family":       "family park",
    "kids":         "kids play area",
    "romantic":     "romantic viewpoint",
    "event":        "festival event",
    "hospital":     "hospital",
    "pharmacy":     "pharmacy",
    "emergency":    "emergency services",
}

# Intent → Google Places type keyword
INTENT_PLACES_TYPE_MAP: Dict[str, str] = {
    Intent.BEACHES:             "beach",
    Intent.WATERFALLS:          "waterfall",
    Intent.MOUNTAINS:           "mountain",
    Intent.TEMPLES:             "temple",
    Intent.MUSEUMS:             "museum",
    Intent.PARKS:               "park",
    Intent.HISTORICAL_PLACES:   "historical monument",
    Intent.TOURIST_ATTRACTIONS: "tourist attraction",
    Intent.SHOPPING:            "shopping mall market",
    Intent.NIGHTLIFE:           "bar nightclub",
    Intent.LOCAL_EVENTS:        "event festival",
    Intent.ADVENTURE_ACTIVITIES:"adventure sports",
    Intent.FAMILY_ACTIVITIES:   "family park",
    Intent.KIDS_ACTIVITIES:     "kids park amusement",
    Intent.COUPLE_ACTIVITIES:   "romantic viewpoint",
    Intent.HOSPITALS:           "hospital",
    Intent.PHARMACIES:          "pharmacy chemist",
    Intent.EMERGENCY_SERVICES:  "emergency services police",
}


class SupervisorAgent:
    """
    Supervisor Agent — classifies user intent and returns an ordered agent execution plan.
    Multiple agents may be selected for complex queries (e.g., itinerary generation).
    """

    def __init__(self):
        self.name = "Supervisor Agent"

    def route(
        self,
        intent: str,
        entities: Dict[str, Any],
        trip_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Given detected intent + entities, return an execution plan:
        {
            "agents":       [list of agent keys to run],
            "places_type":  <google places type keyword or None>,
            "intent":       <canonical intent>,
            "entities":     <extracted entities>,
        }
        """
        agents = _INTENT_AGENT_MAP.get(intent, ["chat"])

        # Determine Google Places type for attractions queries
        places_type: str = ""
        if "attractions" in agents:
            # Sub_type from LLM entity extraction takes priority
            sub = entities.get("sub_type", "")
            if sub:
                places_type = SUBTYPE_KEYWORD_MAP.get(sub.lower(), sub)
            else:
                places_type = INTENT_PLACES_TYPE_MAP.get(intent, "tourist attraction")

        logger.info(
            f"[SupervisorAgent] Intent: {intent} → Agents: {agents} | "
            f"Places type: '{places_type}' | Entities: {entities}"
        )

        return {
            "agents":      agents,
            "places_type": places_type,
            "intent":      intent,
            "entities":    entities,
        }

    # Legacy method — retained for LangGraph workflow compatibility
    def plan_next_step(self, current_state: Dict[str, Any]) -> str:
        completed = current_state.get("completed_nodes", [])
        sequence = ["planner", "destination", "weather", "hotel",
                    "restaurant", "budget", "itinerary", "transport",
                    "packing", "report"]
        for node in sequence:
            if node not in completed:
                return node
        return "FINISH"



supervisor_agent = SupervisorAgent()
