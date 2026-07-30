"""
Conversation Memory Manager — LangChain-compatible buffer memory with trip state.
Tracks message history, destination, budget, last intent, and last place type
for seamless follow-up query handling.
"""
import re
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


class ConversationMemoryManager:
    """
    Maintains message history and trip context per session/trip.
    Extended to track intent + place_type for follow-up query context.
    """

    def __init__(self):
        # session_id → list of BaseMessage
        self.memory_store: Dict[str, List[BaseMessage]] = {}
        # session_id → dict of extracted state
        self.trip_state_store: Dict[str, Dict[str, Any]] = {}

    # ── Message history ─────────────────────────────────────────────────────

    def add_user_message(self, session_id: str, message: str):
        if session_id not in self.memory_store:
            self.memory_store[session_id] = []
        self.memory_store[session_id].append(HumanMessage(content=message))
        self._extract_and_update_state(session_id, message)

    def add_ai_message(self, session_id: str, message: str):
        if session_id not in self.memory_store:
            self.memory_store[session_id] = []
        self.memory_store[session_id].append(AIMessage(content=message))

    def get_history(self, session_id: str, max_messages: int = 12) -> List[BaseMessage]:
        return self.memory_store.get(session_id, [])[-max_messages:]

    def get_history_as_string(self, session_id: str, max_messages: int = 10) -> str:
        messages = self.get_history(session_id, max_messages)
        if not messages:
            return "No previous conversation history."
        formatted = []
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

    # ── Trip state ──────────────────────────────────────────────────────────

    def update_trip_state(self, session_id: str, updates: Dict[str, Any]):
        if session_id not in self.trip_state_store:
            self.trip_state_store[session_id] = {}
        for k, v in updates.items():
            if v is not None and v != "":
                self.trip_state_store[session_id][k] = v

    def get_trip_state(self, session_id: str) -> Dict[str, Any]:
        return self.trip_state_store.get(session_id, {})

    def update_intent_state(
        self,
        session_id: str,
        intent: str,
        entities: Dict[str, Any],
        agents_used: Optional[List[str]] = None,
    ):
        """
        Record the latest intent and key entities for follow-up query resolution.
        E.g., if user asked for beaches and then says "show me cafes nearby" —
        the destination is already known from state.
        """
        updates: Dict[str, Any] = {"last_intent": intent}

        if entities.get("destination"):
            updates["destination"] = entities["destination"]
        if entities.get("budget"):
            updates["budget"] = entities["budget"]
        if entities.get("duration_days"):
            updates["duration_days"] = entities["duration_days"]
        if agents_used:
            updates["last_agents_used"] = agents_used

        # Track place type for "show me more" or "nearby X" follow-ups
        place_intent_types = {
            "BEACHES", "WATERFALLS", "MOUNTAINS", "TEMPLES", "MUSEUMS",
            "PARKS", "HISTORICAL_PLACES", "TOURIST_ATTRACTIONS", "SHOPPING",
            "NIGHTLIFE", "ADVENTURE_ACTIVITIES", "FAMILY_ACTIVITIES",
            "KIDS_ACTIVITIES", "COUPLE_ACTIVITIES", "LOCAL_EVENTS",
        }
        if intent in place_intent_types:
            updates["last_place_intent"] = intent

        self.update_trip_state(session_id, updates)

    def clear(self, session_id: str):
        self.memory_store.pop(session_id, None)
        self.trip_state_store.pop(session_id, None)

    # ── Auto-extract state from user messages ───────────────────────────────

    def _extract_and_update_state(self, session_id: str, message: str):
        """Extract destination or budget updates from user chat message into memory."""
        if session_id not in self.trip_state_store:
            self.trip_state_store[session_id] = {}

        state = self.trip_state_store[session_id]

        # Extract destination
        dest_match = re.search(
            r"(?:trip\s+to|visit|explore|going\s+to|travel\s+to|go\s+to|reach|route\s+to|to|from|in|around|near)\s+"
            r"([A-Z][a-zA-Z\s,]+?)(?=\s+(?:under|with|for|budget|₹|\$|\d)|[.!?]|$)",
            message,
            re.IGNORECASE
        )
        if dest_match:
            extracted_dest = dest_match.group(1).strip()
            cleaned_dest = re.sub(
                r"^(in|to|at|around|for|the|reach|from)\s+", "", extracted_dest, flags=re.IGNORECASE
            ).strip()
            if (
                len(cleaned_dest) > 2
                and cleaned_dest.lower() not in
                ["a", "an", "the", "budget", "hotel", "food", "place", "best place", "day", "days"]
            ):
                state["destination"] = cleaned_dest.title()
        else:
            # Fallback split extraction
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ["to", "in", "at", "visit", "reach", "explore", "near"] and i + 1 < len(words):
                    candidate = words[i+1].strip(",.!?").title()
                    if i + 2 < len(words) and words[i+2][0].isupper():
                        candidate += " " + words[i+2].strip(",.!?").title()
                    cleaned_cand = re.sub(r"^(in|to|at|around|for|the|reach|from)\s+", "", candidate, flags=re.IGNORECASE).strip()
                    if cleaned_cand and len(cleaned_cand) > 2 and cleaned_cand.lower() not in ["a", "an", "the", "under", "for", "budget", "hotel", "food", "place", "day", "days"]:
                        state["destination"] = cleaned_cand
                        break

        # Extract budget
        budget_match = re.search(
            r"(?:budget|cost|price|spend|₹|\$)\s*(?:to|of|is|=|:)?\s*(?:₹|\$)?\s*([\d,]+)",
            message,
            re.IGNORECASE
        )
        if budget_match:
            try:
                num_str = budget_match.group(1).replace(",", "")
                budget_val = float(num_str)
                if budget_val > 100:
                    state["budget"] = budget_val
            except ValueError:
                pass

        # Extract duration
        dur_match = re.search(r"(\d+)\s*(?:-\s*)?(?:day|days|night|nights)\b", message, re.IGNORECASE)
        if dur_match:
            state["duration_days"] = int(dur_match.group(1))


conversation_memory = ConversationMemoryManager()
