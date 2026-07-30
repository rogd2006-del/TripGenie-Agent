"""
Intent Detection Module — LLM-first classifier with 40+ travel intents.
Falls back to rule-based regex when LLM is unavailable.
"""
import re
import json
from typing import Dict, Any, Tuple, Optional, List
from app.utils.logger import logger

# ── Canonical intent constants ─────────────────────────────────────────────────
class Intent:
    GREETING                = "GREETING"
    GENERAL_CONVERSATION    = "GENERAL_CONVERSATION"

    # Destination & information
    DESTINATION_INFO        = "DESTINATION_INFO"
    TOURIST_ATTRACTIONS     = "TOURIST_ATTRACTIONS"
    BEACHES                 = "BEACHES"
    WATERFALLS              = "WATERFALLS"
    MOUNTAINS               = "MOUNTAINS"
    TEMPLES                 = "TEMPLES"
    MUSEUMS                 = "MUSEUMS"
    PARKS                   = "PARKS"
    HISTORICAL_PLACES       = "HISTORICAL_PLACES"

    # Accommodation
    HOTELS                  = "HOTELS"
    RESORTS                 = "RESORTS"
    HOSTELS                 = "HOSTELS"

    # Food & drink
    RESTAURANTS             = "RESTAURANTS"
    CAFES                   = "CAFES"
    STREET_FOOD             = "STREET_FOOD"

    # Shopping & lifestyle
    SHOPPING                = "SHOPPING"

    # Weather
    WEATHER                 = "WEATHER"

    # Transport
    LOCAL_TRANSPORT         = "LOCAL_TRANSPORT"
    FLIGHTS                 = "FLIGHTS"
    TRAIN_INFORMATION       = "TRAIN_INFORMATION"
    BUS_INFORMATION         = "BUS_INFORMATION"
    TAXI                    = "TAXI"

    # Finance
    BUDGET_PLANNING         = "BUDGET_PLANNING"
    CURRENCY                = "CURRENCY"

    # Travel preparation
    TRAVEL_TIPS             = "TRAVEL_TIPS"
    PACKING_SUGGESTIONS     = "PACKING_SUGGESTIONS"
    SAFETY                  = "SAFETY"
    VISA_INFORMATION        = "VISA_INFORMATION"

    # Emergency
    EMERGENCY_SERVICES      = "EMERGENCY_SERVICES"
    HOSPITALS               = "HOSPITALS"
    PHARMACIES              = "PHARMACIES"

    # Activities & events
    LOCAL_EVENTS            = "LOCAL_EVENTS"
    NIGHTLIFE               = "NIGHTLIFE"
    ADVENTURE_ACTIVITIES    = "ADVENTURE_ACTIVITIES"
    FAMILY_ACTIVITIES       = "FAMILY_ACTIVITIES"
    COUPLE_ACTIVITIES       = "COUPLE_ACTIVITIES"
    KIDS_ACTIVITIES         = "KIDS_ACTIVITIES"
    ACCESSIBILITY           = "ACCESSIBILITY"

    # Itinerary
    ITINERARY_GENERATION    = "ITINERARY_GENERATION"
    ITINERARY_MODIFICATION  = "ITINERARY_MODIFICATION"

    # Booking
    BOOKING_ASSISTANCE      = "BOOKING_ASSISTANCE"

    # Fallback
    GENERAL_TRAVEL_QUESTION = "GENERAL_TRAVEL_QUESTION"


# ── LLM system prompt for intent classification ───────────────────────────────
_INTENT_SYSTEM_PROMPT = """You are a travel query intent classifier. Given a user message and optionally a current trip destination, classify the intent into EXACTLY ONE of these canonical labels:

GREETING, GENERAL_CONVERSATION, DESTINATION_INFO, TOURIST_ATTRACTIONS, BEACHES, WATERFALLS, MOUNTAINS, TEMPLES, MUSEUMS, PARKS, HISTORICAL_PLACES, HOTELS, RESORTS, HOSTELS, RESTAURANTS, CAFES, STREET_FOOD, SHOPPING, WEATHER, LOCAL_TRANSPORT, FLIGHTS, TRAIN_INFORMATION, BUS_INFORMATION, TAXI, BUDGET_PLANNING, CURRENCY, TRAVEL_TIPS, PACKING_SUGGESTIONS, SAFETY, VISA_INFORMATION, EMERGENCY_SERVICES, HOSPITALS, PHARMACIES, LOCAL_EVENTS, NIGHTLIFE, ADVENTURE_ACTIVITIES, FAMILY_ACTIVITIES, COUPLE_ACTIVITIES, KIDS_ACTIVITIES, ACCESSIBILITY, ITINERARY_GENERATION, ITINERARY_MODIFICATION, BOOKING_ASSISTANCE, GENERAL_TRAVEL_QUESTION

Also extract any mentioned destination (city/region name) and budget amount (as a number).

Respond ONLY with valid JSON — no markdown, no extra text:
{
  "intent": "<LABEL>",
  "destination": "<extracted destination or null>",
  "budget": <number or null>,
  "duration_days": <number or null>,
  "sub_type": "<optional sub-category like 'beach', 'temple' etc or null>"
}"""


class IntentClassifier:
    """
    LLM-first intent classifier. Falls back to rule-based regex when LLM unavailable.
    Supports 40+ canonical travel intents.
    """

    def classify_intent(
        self,
        message: str,
        trip_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Classify user message. Returns (intent, entities).
        Tries LLM first, then regex fallback.
        """
        # 1. Try LLM classification
        try:
            result = self._classify_with_llm(message, trip_context)
            if result:
                intent, entities = result
                logger.info(f"[IntentClassifier] LLM detected intent: {intent} | entities: {entities}")
                return intent, entities
        except Exception as e:
            logger.warning(f"[IntentClassifier] LLM classification failed, falling back to regex: {e}")

        # 2. Regex fallback
        intent, entities = self._classify_with_regex(message, trip_context)
        logger.info(f"[IntentClassifier] Regex detected intent: {intent} | entities: {entities}")
        return intent, entities

    def _classify_with_llm(
        self,
        message: str,
        trip_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Use the LLM to classify intent via a structured JSON prompt."""
        from app.services.llm_service import llm_service
        from langchain_core.messages import HumanMessage

        if not llm_service.openai_llm:
            return None

        ctx_note = ""
        if trip_context:
            dest = trip_context.get("destination", "")
            if dest:
                ctx_note = f"\nCurrent trip destination context: {dest}"

        user_content = f"User message: \"{message}\"{ctx_note}"
        raw = llm_service.invoke(
            messages=[HumanMessage(content=user_content)],
            system_prompt=_INTENT_SYSTEM_PROMPT
        )

        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)

        data = json.loads(cleaned)
        intent = str(data.get("intent", Intent.GENERAL_TRAVEL_QUESTION)).upper()

        entities: Dict[str, Any] = {}
        if data.get("destination"):
            entities["destination"] = str(data["destination"]).strip().title()
        if data.get("budget") is not None:
            try:
                entities["budget"] = float(data["budget"])
            except (ValueError, TypeError):
                pass
        if data.get("duration_days") is not None:
            try:
                entities["duration_days"] = int(data["duration_days"])
            except (ValueError, TypeError):
                pass
        if data.get("sub_type"):
            entities["sub_type"] = str(data["sub_type"])

        return intent, entities

    def _classify_with_regex(
        self,
        message: str,
        trip_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Rule-based regex classifier (fallback)."""
        msg = message.strip()
        low = msg.lower()
        entities: Dict[str, Any] = {}

        # ── Extract entities first ──────────────────────────────────────────
        # Budget
        bm = re.search(r"(?:budget|cost|price|spend|₹|\$)\s*(?:to|of|is|=|:)?\s*(?:₹|\$)?\s*([\d,]+)", low)
        if bm:
            try:
                entities["budget"] = float(bm.group(1).replace(",", ""))
            except ValueError:
                pass

        # Duration
        dm = re.search(r"(\d+)\s*(?:-\s*)?(?:day|days|night|nights)", low)
        if dm:
            entities["duration_days"] = int(dm.group(1))

        # Destination extraction
        dest_m = re.search(
            r"(?:trip\s+to|visit|explore|going\s+to|travel\s+to|go\s+to|reach|route\s+to|to|from|in|around|near)\s+([A-Z][a-zA-Z\s,]+?)(?=\s+(?:under|with|for|budget|₹|\$|\d|$)|[.!?]|$)",
            msg,
            re.IGNORECASE
        )
        if dest_m:
            raw_dest = dest_m.group(1).strip()
            cleaned = re.sub(r"^(in|to|at|around|for|the|reach|from)\s+", "", raw_dest, flags=re.IGNORECASE).strip()
            if len(cleaned) > 2 and cleaned.lower() not in ["a", "an", "the", "budget", "hotel", "food", "place", "day", "days"]:
                entities["destination"] = cleaned.title()

        # Fallback split-based destination extraction if not found by primary regex
        if "destination" not in entities:
            words = msg.split()
            for i, word in enumerate(words):
                if word.lower() in ["to", "in", "at", "visit", "reach", "explore", "near"] and i + 1 < len(words):
                    candidate = words[i+1].strip(",.!?").title()
                    # Check if next word is also capitalized (e.g. New Delhi)
                    if i + 2 < len(words) and words[i+2][0].isupper():
                        candidate += " " + words[i+2].strip(",.!?").title()
                    cleaned_cand = re.sub(r"^(in|to|at|around|for|the|reach|from)\s+", "", candidate, flags=re.IGNORECASE).strip()
                    if cleaned_cand and len(cleaned_cand) > 2 and cleaned_cand.lower() not in ["a", "an", "the", "under", "for", "budget", "hotel", "food", "place", "day", "days"]:
                        entities["destination"] = cleaned_cand
                        break

        # ── Intent matching ─────────────────────────────────────────────────

        # GREETING
        if re.search(r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|howdy|namaste)\b", low) and len(msg.split()) <= 5:
            return Intent.GREETING, entities

        # ITINERARY_GENERATION
        if re.search(r"\b(plan|create|make|generate|build|design)\b.*\b(trip|tour|travel|itinerary|schedule|vacation|holiday)\b", low):
            return Intent.ITINERARY_GENERATION, entities
        if re.search(r"\b(itinerary|day[-\s]by[-\s]day|day\s+plan|trip\s+plan)\b", low) and "modify" not in low and "change" not in low:
            return Intent.ITINERARY_GENERATION, entities

        # ITINERARY_MODIFICATION
        if re.search(r"\b(modify|update|change|edit|reschedule|replan|adjust)\s+(my\s+)?(itinerary|schedule|plan|trip)\b", low):
            return Intent.ITINERARY_MODIFICATION, entities
        if re.search(r"\b(add|remove|delete|swap)\s+(a\s+)?(day|activity|spot|visit|attraction)\b", low):
            return Intent.ITINERARY_MODIFICATION, entities

        # Accommodation types
        if re.search(r"\b(hostel|dorm|backpacker|budget\s+stay)\b", low):
            return Intent.HOSTELS, entities
        if re.search(r"\b(resort|luxury\s+resort|beachfront\s+resort|hill\s+resort)\b", low):
            return Intent.RESORTS, entities
        if re.search(r"\b(hotel|hotels|stay|lodging|accommodation|homestay)\b", low):
            return Intent.HOTELS, entities

        # Food & drink
        if re.search(r"\b(street\s+food|street\s+eats|local\s+food\s+stalls|chaat|pani\s+puri|bhel)\b", low):
            return Intent.STREET_FOOD, entities
        if re.search(r"\b(cafe|cafes|coffee\s+shop|bakery|patisserie)\b", low):
            return Intent.CAFES, entities
        if re.search(r"\b(restaurant|restaurants|dine|dining|eat|food|cuisine|thali|biryani|veg|vegetarian|vegan)\b", low):
            return Intent.RESTAURANTS, entities

        # Nature attractions
        if re.search(r"\b(waterfall|waterfalls|falls|cascade)\b", low):
            return Intent.WATERFALLS, entities
        if re.search(r"\b(mountain|mountains|hill\s+station|hills|peak|summit|trekking|trek)\b", low):
            return Intent.MOUNTAINS, entities
        if re.search(r"\b(beach|beaches|seashore|coastline|seafront|seaside|bay|cove)\b", low):
            return Intent.BEACHES, entities

        # Culture & heritage
        if re.search(r"\b(temple|temples|church|churches|mosque|shrine|mandir|kovil|dargah|gurudwara)\b", low):
            return Intent.TEMPLES, entities
        if re.search(r"\b(museum|museums|gallery|galleries|exhibition|artifact)\b", low):
            return Intent.MUSEUMS, entities
        if re.search(r"\b(park|garden|botanical|national\s+park|wildlife|sanctuary|reserve)\b", low):
            return Intent.PARKS, entities
        if re.search(r"\b(historical|historic|heritage|fort|palace|ruins|ancient|monument|old\s+city)\b", low):
            return Intent.HISTORICAL_PLACES, entities
        if re.search(r"\b(attraction|sightseeing|places\s+to\s+visit|things\s+to\s+do|tourist\s+spot|landmark)\b", low):
            return Intent.TOURIST_ATTRACTIONS, entities

        # Activities
        if re.search(r"\b(adventure|trekking|rafting|bungee|paragliding|scuba|skydiving|zip\s+line|rock\s+climbing)\b", low):
            return Intent.ADVENTURE_ACTIVITIES, entities
        if re.search(r"\b(couple|romantic|honeymoon|date|anniversary)\b", low):
            return Intent.COUPLE_ACTIVITIES, entities
        if re.search(r"\b(kids|children|child|family\s+with\s+kids|toddler)\b", low):
            return Intent.KIDS_ACTIVITIES, entities
        if re.search(r"\b(family|family\s+trip|family\s+vacation|family\s+friendly)\b", low):
            return Intent.FAMILY_ACTIVITIES, entities
        if re.search(r"\b(nightlife|clubs|bar|bars|pub|night\s+market|late\s+night)\b", low):
            return Intent.NIGHTLIFE, entities
        if re.search(r"\b(event|festival|fair|concert|show|cultural\s+event|celebration)\b", low):
            return Intent.LOCAL_EVENTS, entities
        if re.search(r"\b(shopping|market|mall|bazaar|souvenirs|handicraft|clothes|fashion)\b", low):
            return Intent.SHOPPING, entities
        if re.search(r"\b(wheelchair|accessible|accessibility|disabled|differently\s+abled|mobility)\b", low):
            return Intent.ACCESSIBILITY, entities

        # Transport
        if re.search(r"\b(flight|flights|fly|airline|airport|air\s+ticket)\b", low):
            return Intent.FLIGHTS, entities
        if re.search(r"\b(train|trains|railway|irctc|rail|rajdhani|shatabdi)\b", low):
            return Intent.TRAIN_INFORMATION, entities
        if re.search(r"\b(bus|buses|ksrtc|state\s+bus|volvo|coach)\b", low):
            return Intent.BUS_INFORMATION, entities
        if re.search(r"\b(taxi|cab|uber|ola|auto|rickshaw|tuk.?tuk)\b", low):
            return Intent.TAXI, entities
        if re.search(r"\b(local\s+transport|transport|how\s+to\s+reach|getting\s+to|commute|getting\s+around)\b", low):
            return Intent.LOCAL_TRANSPORT, entities

        # Weather
        if re.search(r"\b(weather|temperature|temp|rain|rainfall|forecast|climate|sunny|monsoon|humidity)\b", low):
            return Intent.WEATHER, entities

        # Finance & planning
        if re.search(r"\b(currency|exchange|forex|conversion|usd|eur|gbp|inr|dollar|euro|pound)\b", low):
            return Intent.CURRENCY, entities
        if re.search(r"\b(budget|cost|expense|price|spend|breakdown|₹|\$|affordable|cheap)\b", low):
            return Intent.BUDGET_PLANNING, entities

        # Travel prep
        if re.search(r"\b(visa|visa\s+required|visa\s+on\s+arrival|e.?visa|passport)\b", low):
            return Intent.VISA_INFORMATION, entities
        if re.search(r"\b(pack|packing|what\s+to\s+bring|luggage|suitcase|what\s+to\s+carry)\b", low):
            return Intent.PACKING_SUGGESTIONS, entities
        if re.search(r"\b(tip|tips|advice|recommendation|suggest|guide|best\s+time)\b", low):
            return Intent.TRAVEL_TIPS, entities

        # Safety & emergency
        if re.search(r"\b(hospital|clinic|doctor|medical|healthcare|emergency\s+room|urgent\s+care)\b", low):
            return Intent.HOSPITALS, entities
        if re.search(r"\b(pharmacy|chemist|drugstore|medicine\s+shop)\b", low):
            return Intent.PHARMACIES, entities
        if re.search(r"\b(emergency|ambulance|police|helpline|sos|distress|rescue)\b", low):
            return Intent.EMERGENCY_SERVICES, entities
        if re.search(r"\b(safe|safety|is\s+it\s+safe|dangerous|danger|crime|scam|precaution)\b", low):
            return Intent.SAFETY, entities

        # Booking
        if re.search(r"\b(book|booking|reserve|reservation|ticket|purchase|order)\b", low):
            return Intent.BOOKING_ASSISTANCE, entities

        # Destination info
        if re.search(r"\b(history|culture|language|famous\s+for|known\s+for|best\s+time|overview|about)\b", low):
            return Intent.DESTINATION_INFO, entities

        # General travel question
        if re.search(r"\b(is\s+there|are\s+there|can\s+i|where|how|why|what|distance|near|nearby|around)\b", low):
            return Intent.GENERAL_TRAVEL_QUESTION, entities

        return Intent.GENERAL_CONVERSATION, entities


intent_classifier = IntentClassifier()
