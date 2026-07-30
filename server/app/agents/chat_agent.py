"""
Chat Agent — orchestrates parallel specialized agent execution and synthesizes
the final LLM response. Replaces keyword-matching with intent-driven routing.
"""
import asyncio
import json
from typing import Dict, Any, List, Optional

from app.utils.logger import logger
from app.services.llm_service import llm_service
from app.services.intent_classifier import intent_classifier, Intent
from app.agents.supervisor import supervisor_agent, INTENT_PLACES_TYPE_MAP

from langchain_core.messages import BaseMessage, HumanMessage


# ── Agent lazy imports (avoid circular) ────────────────────────────────────────
def _get_agents():
    from app.agents.hotel_agent import hotel_agent
    from app.agents.weather_agent import weather_agent
    from app.agents.restaurant_agent import restaurant_agent
    from app.agents.itinerary_agent import itinerary_agent
    from app.agents.budget_agent import budget_agent
    from app.agents.packing_agent import packing_agent
    from app.agents.attractions_agent import attractions_agent
    from app.agents.emergency_agent import emergency_agent
    from app.agents.transport_agent import transport_agent
    from app.agents.destination_agent import destination_agent
    return {
        "hotel":       hotel_agent,
        "weather":     weather_agent,
        "restaurant":  restaurant_agent,
        "itinerary":   itinerary_agent,
        "budget":      budget_agent,
        "packing":     packing_agent,
        "attractions": attractions_agent,
        "emergency":   emergency_agent,
        "transport":   transport_agent,
        "destination": destination_agent,
    }


# ── System prompt templates ────────────────────────────────────────────────────

_BASE_SYSTEM = """You are TripGenie, an expert AI travel assistant. You are helpful, warm, knowledgeable, and precise.

=== ACTIVE TRIP CONTEXT ===
Destination: {destination}
Budget: ₹{budget:,.0f}
Duration: {duration_days} days
Dietary Preference: {food_pref}
Luxury Level: {luxury_level}
Intent: {intent}
"""

_TOOL_SECTION = """
=== TOOL OUTPUTS ({agents}) ===
{tool_data}
"""

_INSTRUCTIONS = """
=== INSTRUCTIONS ===
1. Answer the user's question DIRECTLY, warmly, and conversationally based on the tool outputs above.
2. Format results clearly using **bold headers**, bullet points, and tables where appropriate.
3. Include place names, ratings, addresses, and Maps links from tool outputs.
4. NEVER say "I have synchronized your preferences" or "I've updated your trip" unless the user explicitly asked for an itinerary update.
5. NEVER produce generic placeholder responses.
6. For follow-up questions (e.g., "nearby cafes", "add to itinerary"), use the active destination from context.
7. If tool data is empty or sparse, generate a helpful, specific response using your knowledge — DO NOT apologize generically.
8. Keep the response concise but complete. Avoid unnecessary filler text.
"""


class ChatAgent:
    """
    Orchestrates intent detection → supervisor routing → parallel agent execution
    → LLM response synthesis.
    """

    def __init__(self):
        self.name = "Chat Agent"

    async def execute_chat(
        self,
        user_message: str,
        trip_context: Dict[str, Any],
        history_messages: List[BaseMessage],
        session_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Full chat pipeline:
        1. Classify intent (LLM-first, regex fallback)
        2. Supervisor routes to agents
        3. Run agents in parallel
        4. Synthesize LLM response
        """
        destination = trip_context.get("destination") or "Varkala, Kerala, India"
        budget      = float(trip_context.get("budget") or 20000)
        duration    = int(trip_context.get("duration_days") or 4)
        food_pref   = trip_context.get("food_preference") or "Vegetarian"
        luxury      = trip_context.get("luxury_level") or "Moderate"

        # ── 1. Intent classification ───────────────────────────────────────
        intent, entities = intent_classifier.classify_intent(
            message=user_message,
            trip_context=trip_context,
        )

        # Update destination/budget from entities if extracted
        if entities.get("destination"):
            destination = entities["destination"]
        if entities.get("budget"):
            budget = entities["budget"]
        if entities.get("duration_days"):
            duration = entities["duration_days"]

        # Geocode destination coordinates to store in shared trip_context
        from app.services.location_service import search_place
        geo = search_place(destination)
        if geo:
            trip_context["destination_lat"] = geo["latitude"]
            trip_context["destination_lng"] = geo["longitude"]
            trip_context["destination_country"] = geo["country"]
            trip_context["destination_state"] = geo["state"]
            trip_context["display_name"] = geo["display_name"]
            destination = geo["display_name"]

        logger.info(f"[ChatAgent] Intent='{intent}' | Destination='{destination}' | Entities={entities}")

        # ── 2. Supervisor routing ──────────────────────────────────────────
        plan = supervisor_agent.route(intent, entities, trip_context)
        agent_keys  = plan["agents"]
        places_type = plan["places_type"]
        active_agents_label = " + ".join(a.replace("_", " ").title() + " Agent" for a in agent_keys)

        # ── 3. Parallel agent execution ────────────────────────────────────
        agents_map = _get_agents()
        tool_results: Dict[str, Any] = {}

        async def run_agent(key: str):
            try:
                agent = agents_map.get(key)
                if not agent:
                    logger.warning(f"[ChatAgent] No agent registered for key '{key}'")
                    return key, {}

                if key == "hotel":
                    # Use async method directly to avoid blocking
                    result = await agent.run_async({
                        "destination": destination,
                        "destination_lat": trip_context.get("destination_lat"),
                        "destination_lng": trip_context.get("destination_lng"),
                        "luxury_level": luxury,
                        "budget": budget,
                        "request": {
                            "destination": destination,
                            "luxury_level": luxury,
                            "budget": budget,
                        }
                    })
                    return key, result

                elif key == "weather":
                    from app.tools.weather_tool import fetch_weather_forecast
                    result = await fetch_weather_forecast(destination, duration)
                    return key, result

                elif key == "restaurant":
                    # Execute restaurant agent passing the coordinates
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: agent.run({
                            "destination": destination,
                            "destination_lat": trip_context.get("destination_lat"),
                            "destination_lng": trip_context.get("destination_lng"),
                            "food_preference": food_pref,
                        })
                    )
                    return key, result

                elif key == "budget":
                    from app.tools.budget_tool import calculate_budget_breakdown
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: calculate_budget_breakdown(budget, duration)
                    )
                    return key, result

                elif key == "packing":
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: agent.run({
                            "destination": destination,
                            "duration_days": duration,
                            "luxury_level": luxury,
                        })
                    )
                    return key, result

                elif key == "attractions":
                    ptype = places_type or "tourist attraction"
                    res = agent.run(
                        destination=destination,
                        place_type=ptype,
                        state=trip_context
                    )
                    result = await res if asyncio.iscoroutine(res) else res
                    return key, result

                elif key == "emergency":
                    q_type = "hospital" if intent == Intent.HOSPITALS else \
                             "pharmacy" if intent == Intent.PHARMACIES else \
                             "emergency" if intent == Intent.EMERGENCY_SERVICES else "safety"
                    res = agent.run(
                        destination=destination,
                        query_type=q_type,
                        state=trip_context
                    )
                    result = await res if asyncio.iscoroutine(res) else res
                    return key, result

                elif key == "transport":
                    t_type_map = {
                        Intent.FLIGHTS:           "flights",
                        Intent.TRAIN_INFORMATION: "train",
                        Intent.BUS_INFORMATION:   "bus",
                        Intent.TAXI:              "taxi",
                    }
                    t_type = t_type_map.get(intent, "local_transport")
                    origin = entities.get("origin") or (session_state.get("origin") if session_state else None)
                    if hasattr(agent, "run_async"):
                        result = await agent.run_async(
                            state_or_dest=destination,
                            transport_type=t_type,
                            origin=origin,
                            budget=budget,
                            state=trip_context,
                        )
                    else:
                        res = agent.run(
                            destination_or_state=destination,
                            transport_type=t_type,
                            origin=origin,
                            budget=budget,
                            state=trip_context,
                        )
                        result = await res if asyncio.iscoroutine(res) else res
                    return key, result

                elif key == "destination":
                    if hasattr(agent, "run_async"):
                        result = await agent.run_async({
                            "destination": destination,
                            "request": {"destination": destination}
                        })
                    else:
                        res = agent.run({
                            "destination": destination,
                            "request": {"destination": destination}
                        })
                        result = await res if asyncio.iscoroutine(res) else res
                    return key, result

                elif key == "itinerary":
                    state = {
                        "destination":    destination,
                        "destination_lat": trip_context.get("destination_lat"),
                        "destination_lng": trip_context.get("destination_lng"),
                        "duration_days":  duration,
                        "food_preference": food_pref,
                        "luxury_level":   luxury,
                        "budget":         budget,
                        "weather":        tool_results.get("weather", {}),
                    }
                    if hasattr(agent, "run_async"):
                        result = await agent.run_async(state)
                    else:
                        res = agent.run(state)
                        result = await res if asyncio.iscoroutine(res) else res
                    return key, result


                elif key == "chat":
                    return key, {}  # LLM handles pure chat directly

                return key, {}

            except Exception as e:
                logger.error(f"[ChatAgent] Agent '{key}' failed: {e}", exc_info=True)
                return key, {}

        # Run non-itinerary agents first (itinerary may need weather result)
        primary_keys   = [k for k in agent_keys if k != "itinerary" and k != "chat"]
        secondary_keys = [k for k in agent_keys if k == "itinerary"]

        if primary_keys:
            primary_results = await asyncio.gather(*[run_agent(k) for k in primary_keys])
            for k, v in primary_results:
                if v:
                    tool_results[k] = v

        if secondary_keys:
            secondary_results = await asyncio.gather(*[run_agent(k) for k in secondary_keys])
            for k, v in secondary_results:
                if v:
                    tool_results[k] = v

        logger.info(f"[ChatAgent] Tool results collected from: {list(tool_results.keys())}")

        # ── 4. Build system prompt and invoke LLM ─────────────────────────
        system_prompt = _BASE_SYSTEM.format(
            destination=destination,
            budget=budget,
            duration_days=duration,
            food_pref=food_pref,
            luxury_level=luxury,
            intent=intent,
        )

        if tool_results:
            # Serialize tool outputs compactly
            tool_data_lines = []
            for agent_key, data in tool_results.items():
                serialized = json.dumps(data, default=str, ensure_ascii=False)
                if len(serialized) > 3000:
                    serialized = serialized[:3000] + "...[truncated]"
                tool_data_lines.append(f"[{agent_key.upper()}]: {serialized}")

            system_prompt += _TOOL_SECTION.format(
                agents=active_agents_label,
                tool_data="\n".join(tool_data_lines)
            )

        system_prompt += _INSTRUCTIONS

        # Build message chain
        message_chain = list(history_messages[-8:])  # last 8 messages for context
        message_chain.append(HumanMessage(content=user_message))

        response_text = await llm_service.invoke_async(message_chain, system_prompt=system_prompt)

        # Determine displayed agent name
        if len(agent_keys) > 1:
            display_agent = "Supervisor Agent → " + " + ".join(
                k.replace("_", " ").title() + " Agent" for k in agent_keys if k != "chat"
            )
        elif agent_keys and agent_keys[0] != "chat":
            display_agent = agent_keys[0].replace("_", " ").title() + " Agent"
        else:
            display_agent = "TripGenie AI"

        return {
            "reply":        response_text,
            "agent_name":   display_agent,
            "intent":       intent,
            "agents_used":  agent_keys,
            "entities":     entities,
            "tool_results": tool_results,
        }


chat_agent = ChatAgent()
