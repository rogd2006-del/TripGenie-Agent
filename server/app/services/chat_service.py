"""
Chat Service — coordinates message routing through the full agentic pipeline:
IntentClassifier → SupervisorAgent → Specialized Agents → LLM Response.
"""
from datetime import datetime
from typing import Dict, Any, Optional

from app.database.connection import db_manager
from app.services.conversation_memory import conversation_memory
from app.agents.chat_agent import chat_agent
from app.utils.logger import logger


class ChatService:
    """
    Entry point for all chat messages. Fetches trip context from DB/memory,
    delegates to ChatAgent (which runs the full intent→agent pipeline),
    and persists updated session state.
    """

    async def process_chat_message(
        self,
        message: str,
        trip_id: Optional[str] = None,
        user_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        session_id = trip_id or "default_session"
        user_id = str(user_info.get("_id") or user_info.get("id")) if user_info else "user-demo-1"

        logger.info(
            f"[ChatService] Session='{session_id}' | User='{user_id}' | Query='{message}'"
        )

        try:
            # ── 1. Record user message in memory ───────────────────────────
            conversation_memory.add_user_message(session_id, message)

            # ── 2. Fetch active trip context from DB or in-memory store ────
            trip_context: Dict[str, Any] = {}
            if trip_id:
                try:
                    if db_manager.use_fallback:
                        trips = db_manager.in_memory_store.get("trips", [])
                        trip_context = next(
                            (t for t in trips
                             if str(t.get("id")) == trip_id or str(t.get("_id")) == trip_id),
                            {}
                        )
                    else:
                        found = await db_manager.db["trips"].find_one({"_id": trip_id})
                        if not found:
                            found = await db_manager.db["trips"].find_one({"id": trip_id})
                        trip_context = found or {}
                except Exception as e:
                    logger.error(f"[ChatService] Error fetching trip {trip_id}: {e}", exc_info=True)

            # Fallback to the most recent trip
            if not trip_context:
                try:
                    if db_manager.use_fallback:
                        trips = db_manager.in_memory_store.get("trips", [])
                        trip_context = trips[0] if trips else {}
                    else:
                        trip_context = await db_manager.db["trips"].find_one(
                            {"user_id": user_id},
                            sort=[("created_at", -1)]
                        ) or {}
                except Exception as e:
                    logger.error(f"[ChatService] Error fetching fallback trip: {e}", exc_info=True)

            # ── 3. Merge memory state (destination/budget from prior messages) ─
            memory_state = conversation_memory.get_trip_state(session_id)
            active_context: Dict[str, Any] = {
                "destination":    memory_state.get("destination") or trip_context.get("destination") or "Varkala, Kerala, India",
                "budget":         memory_state.get("budget") or trip_context.get("budget") or 20000,
                "duration_days":  memory_state.get("duration_days") or trip_context.get("duration_days") or 4,
                "food_preference": trip_context.get("food_preference") or "Vegetarian",
                "luxury_level":   trip_context.get("luxury_level") or "Moderate",
                "itinerary":      trip_context.get("itinerary") or [],
                "hotels":         trip_context.get("hotels") or [],
                "restaurants":    trip_context.get("restaurants") or [],
            }

            # Include session state for follow-up resolution (last_intent, last_place_intent)
            session_state = dict(memory_state)

            # ── 4. History messages ─────────────────────────────────────────
            history_messages = conversation_memory.get_history(session_id, max_messages=8)

            # ── 5. Run ChatAgent (intent → routing → agents → LLM) ─────────
            chat_result = await chat_agent.execute_chat(
                user_message=message,
                trip_context=active_context,
                history_messages=history_messages,
                session_state=session_state,
            )

            reply_text  = chat_result.get("reply", "")
            agent_name  = chat_result.get("agent_name", "TripGenie AI")
            intent      = chat_result.get("intent", "GENERAL_CONVERSATION")
            agents_used = chat_result.get("agents_used", [])
            entities    = chat_result.get("entities", {})

            # ── 6. Update memory with intent + entities ─────────────────────
            conversation_memory.add_ai_message(session_id, reply_text)
            conversation_memory.update_intent_state(
                session_id=session_id,
                intent=intent,
                entities=entities,
                agents_used=agents_used,
            )

            logger.info(
                f"[ChatService] Response generated | Intent='{intent}' | "
                f"Agents={agents_used} | Reply length={len(reply_text)}"
            )

            return {
                "reply":       reply_text,
                "agent_name":  agent_name,
                "intent":      intent,
                "agents_used": agents_used,
                "timestamp":   datetime.utcnow().isoformat(),
                "trip_id":     trip_id,
            }

        except Exception as e:
            logger.error(f"[ChatService] Error processing message: {e}", exc_info=True)
            fallback_msg = (
                "Hello! I am **TripGenie**, your AI travel assistant. "
                "I encountered a temporary issue while fetching your request, but I'm ready to help you plan "
                "your hotels, weather, local attractions, and itinerary! Where would you like to explore?"
            )
            return {
                "reply":       fallback_msg,
                "agent_name":  "TripGenie AI",
                "intent":      "ERROR_FALLBACK",
                "agents_used": ["fallback"],
                "timestamp":   datetime.utcnow().isoformat(),
                "trip_id":     trip_id,
                "error":       str(e)
            }



chat_service = ChatService()
