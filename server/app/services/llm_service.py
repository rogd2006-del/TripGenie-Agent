"""
LLM Service — OpenAI ChatGPT via LangChain with async support and intent-aware fallback.
"""
import os
import re
import json
import asyncio
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.utils.logger import logger
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage


class LLMService:
    """
    OpenAI API service wrapper utilizing LangChain ChatOpenAI.
    Provides both synchronous invoke() and async invoke_async().
    Falls back to intent-aware dynamic generator when no API key is configured.
    """

    def __init__(self):
        self.openai_llm = None
        self.model_name = settings.OPENAI_MODEL or "gpt-4o"
        self.reload_llm()

    def reload_llm(self):
        """(Re)initialize ChatOpenAI client if API key is configured."""
        key = (settings.OPENAI_API_KEY or "").strip()
        if key and key not in ("your_openai_api_key_here", ""):
            try:
                from langchain_openai import ChatOpenAI
                self.openai_llm = ChatOpenAI(
                    model=settings.OPENAI_MODEL or "gpt-4o",
                    api_key=key,
                    temperature=0.7
                )
                self.model_name = settings.OPENAI_MODEL or "gpt-4o"
                logger.info(f"LangChain ChatOpenAI active with model: {self.model_name}")
            except Exception as e:
                logger.error(f"[Exceptions] Could not initialize ChatOpenAI: {e}", exc_info=True)
                self.openai_llm = None
        else:
            self.openai_llm = None
            logger.warning("[Exceptions] OpenAI API Key not set or set to default placeholder in .env!")

    # ── Synchronous invoke ──────────────────────────────────────────────────

    def invoke(
        self,
        messages: List[BaseMessage],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Execute ChatOpenAI via LangChain (synchronous).
        Falls back to intent-aware dynamic generation if OpenAI unavailable.
        """
        if not self.openai_llm:
            self.reload_llm()

        logger.info(
            f"[LLM Request] Provider: {'OpenAI (' + self.model_name + ')' if self.openai_llm else 'Fallback Generator'} | "
            f"Messages: {len(messages)} | SysPrompt chars: {len(system_prompt or '')}"
        )

        if self.openai_llm:
            try:
                full_messages = []
                if system_prompt:
                    full_messages.append(SystemMessage(content=system_prompt))
                full_messages.extend(messages)
                response = self.openai_llm.invoke(full_messages)
                res_str = str(response.content) if hasattr(response, "content") else str(response)
                logger.info(f"[LLM Response] OpenAI ({len(res_str)} chars): {res_str[:120]}...")
                return res_str
            except Exception as e:
                logger.error(f"[Exceptions] OpenAI API error: {e}", exc_info=True)

        logger.info("[LLM Request] Running dynamic fallback generator.")
        res = self._generate_dynamic_fallback(messages, system_prompt)
        logger.info(f"[LLM Response] Fallback ({len(res)} chars): {res[:120]}...")
        return res

    # ── Async invoke ────────────────────────────────────────────────────────

    async def invoke_async(
        self,
        messages: List[BaseMessage],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Async wrapper — runs invoke() in a thread pool to avoid blocking the event loop.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.invoke(messages, system_prompt)
        )

    # ── Intent-aware fallback generator ────────────────────────────────────

    def _generate_dynamic_fallback(
        self,
        messages: List[BaseMessage],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generates a meaningful contextual response when OpenAI is unavailable.
        Uses system prompt context (destination, intent, tool outputs) to craft replies.
        """
        # Extract latest user query
        user_query = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                user_query = m.content
                break
        if not user_query and messages:
            user_query = str(messages[-1].content)

        query_lower = user_query.lower()
        sys_str = system_prompt or ""

        # Extract destination from system prompt
        dest_match = re.search(r"Destination:\s*([^\n,|]+)", sys_str, re.IGNORECASE)
        dest = dest_match.group(1).strip() if dest_match else "your destination"

        # Extract intent from system prompt
        intent_match = re.search(r"Intent:\s*([A-Z_]+)", sys_str)
        intent = intent_match.group(1).upper() if intent_match else ""

        # Extract tool data if present
        has_tool_data = "=== TOOL OUTPUTS ===" in sys_str or "=== AGENT TOOL OUTPUTS" in sys_str

        # ── Intent-driven responses ─────────────────────────────────────────

        if intent == "GREETING" or query_lower in ("hi", "hello", "hey", "namaste", "greetings"):
            return (
                f"Hello! 👋 I'm **TripGenie**, your AI travel assistant.\n\n"
                f"I can help you with:\n"
                f"- 🏖️ Finding beaches, temples, waterfalls, and attractions\n"
                f"- 🏨 Hotel and accommodation recommendations\n"
                f"- 🌤️ Real-time weather information\n"
                f"- 🚌 Transport options (flights, trains, buses, taxis)\n"
                f"- 💰 Budget planning and currency exchange\n"
                f"- 🗓️ Complete itinerary generation\n"
                f"- 🏥 Safety tips and emergency contacts\n\n"
                f"Where would you like to travel? Just ask me anything! ✈️"
            )

        if intent == "WEATHER":
            # Tool data will be in system prompt if available — LLM synthesizes it
            return (
                f"🌤️ **Weather in {dest}**\n\n"
                f"Current conditions are pleasant for travel. The temperature typically ranges "
                f"between 20–30°C depending on the season.\n\n"
                f"> **Tip:** Always check the 7-day forecast before packing. "
                f"Carry a light jacket for evenings and an umbrella during monsoon season."
            )

        if intent in ("BEACHES",):
            return (
                f"🏖️ **Beaches near {dest}**\n\n"
                f"Here are some top beach spots in the area:\n\n"
                f"• **Main Beach** — Popular, well-maintained, good for swimming\n"
                f"• **Secluded Cove** — Quiet beach, ideal for relaxation and photography\n"
                f"• **Fishing Village Beach** — Authentic local experience with fresh seafood stalls\n\n"
                f"> ℹ️ Add your **Google Maps API key** to `.env` for real-time place listings with ratings and directions."
            )

        if intent in ("HOTELS", "RESORTS", "HOSTELS"):
            kind = "resort" if intent == "RESORTS" else ("hostel" if intent == "HOSTELS" else "hotel")
            return (
                f"🏨 **{kind.title()} options in {dest}**\n\n"
                f"Here are recommended stays:\n\n"
                f"• **Premium Option** — 4-star property with pool, breakfast included (₹3,500–6,000/night)\n"
                f"• **Mid-Range Option** — Comfortable rooms with amenities (₹1,500–3,000/night)\n"
                f"• **Budget Option** — Clean, well-located, great value (₹600–1,500/night)\n\n"
                f"> 💡 Add your **Google Maps API key** for live hotel listings with real ratings and photos."
            )

        if intent in ("RESTAURANTS", "CAFES", "STREET_FOOD"):
            cat = "cafés" if intent == "CAFES" else ("street food stalls" if intent == "STREET_FOOD" else "restaurants")
            return (
                f"🍽️ **Top {cat} in {dest}**\n\n"
                f"• **Local Specialty Place** — Must-try regional cuisine (₹200–500/person)\n"
                f"• **Popular Café** — Great ambiance, artisan coffee, breakfast options\n"
                f"• **Street Food Corner** — Authentic local bites; try the street-side chaats and snacks\n\n"
                f"> 🌶️ Ask me for specific dietary preferences (vegetarian, vegan, seafood) for tailored picks!"
            )

        if intent == "WEATHER":
            return (
                f"🌤️ **Weather for {dest}**\n\n"
                f"Current conditions are pleasant. Typical temperature: 22–30°C.\n"
                f"Check a live weather app for real-time updates.\n\n"
                f"> Add your **OpenWeather API key** to `.env` for real-time forecasts."
            )

        if intent in ("SAFETY", "EMERGENCY_SERVICES", "HOSPITALS", "PHARMACIES"):
            return (
                f"🛡️ **Safety Information for {dest}**\n\n"
                f"**Emergency Numbers (India):**\n"
                f"- 🚔 Police: **100**\n"
                f"- 🚑 Ambulance: **108**\n"
                f"- 🚒 Fire: **101**\n"
                f"- 📞 Tourist Helpline: **1800-111-363**\n\n"
                f"**Safety Tips:**\n"
                f"- Keep photocopies of your ID and passport\n"
                f"- Share your itinerary with someone you trust\n"
                f"- Avoid isolated areas at night\n"
                f"- Use registered taxis or app-based cabs\n"
                f"- Keep emergency contacts saved on your phone\n\n"
                f"For nearby hospitals and pharmacies, I need your **Google Maps API key** configured."
            )

        if intent in ("LOCAL_TRANSPORT", "TAXI", "FLIGHTS", "TRAIN_INFORMATION", "BUS_INFORMATION"):
            return (
                f"🚗 **Transport Options for {dest}**\n\n"
                f"**Local:**\n"
                f"- Auto-rickshaws / Tuk-tuks: ₹20–80 for short distances\n"
                f"- Ola/Uber: Available in most cities, transparent pricing\n"
                f"- Local buses: ₹10–30, economical option\n\n"
                f"**Intercity:**\n"
                f"- Trains: Book via [IRCTC](https://www.irctc.co.in/)\n"
                f"- Buses: Book via [RedBus](https://www.redbus.in/)\n"
                f"- Flights: Compare on [MakeMyTrip](https://www.makemytrip.com/)\n\n"
                f"> 💡 Share your origin city for specific route and price estimates!"
            )

        if intent == "BUDGET_PLANNING":
            return (
                f"💰 **Budget Breakdown for {dest}**\n\n"
                f"Typical daily budget estimates:\n\n"
                f"| Category | Budget | Mid-range | Luxury |\n"
                f"|---|---|---|---|\n"
                f"| Accommodation | ₹600–1,200 | ₹1,500–3,000 | ₹4,000+ |\n"
                f"| Food | ₹300–500 | ₹600–1,200 | ₹1,500+ |\n"
                f"| Local transport | ₹100–200 | ₹300–500 | ₹800+ |\n"
                f"| Activities | ₹200–500 | ₹500–1,500 | ₹2,000+ |\n\n"
                f"Tell me your total budget and trip duration for a personalized breakdown!"
            )

        if intent in ("PACKING_SUGGESTIONS", "TRAVEL_TIPS"):
            return (
                f"🎒 **Packing & Travel Tips for {dest}**\n\n"
                f"**Essential Documents:**\n"
                f"- ID proof (Aadhaar/Passport)\n"
                f"- Travel insurance documents\n"
                f"- Hotel booking confirmations\n\n"
                f"**Clothing:**\n"
                f"- Light cottons for warm weather; layered clothing for hill stations\n"
                f"- Comfortable walking shoes\n"
                f"- Rain jacket/umbrella (monsoon season)\n\n"
                f"**Health:**\n"
                f"- Personal medications\n"
                f"- Sunscreen, insect repellent\n"
                f"- Oral rehydration salts for tropical climates\n\n"
                f"**Tech:**\n"
                f"- Power bank\n"
                f"- Universal adapter\n"
                f"- Offline maps downloaded"
            )

        if intent == "ITINERARY_GENERATION":
            return (
                f"🗓️ **Generating itinerary for {dest}**\n\n"
                f"I'm putting together a complete travel plan for you! Here's a sample structure:\n\n"
                f"**Day 1:** Arrival & Orientation → Hotel check-in → Local dinner\n"
                f"**Day 2:** Top Attractions & Sightseeing → Cultural experiences\n"
                f"**Day 3:** Nature & Adventure → Local markets & shopping\n"
                f"**Day 4 (if applicable):** Leisure + Departure\n\n"
                f"> 💡 Add your **OpenAI API key** to `.env` for a fully personalized, hour-by-hour AI-generated itinerary!"
            )

        if intent == "VISA_INFORMATION":
            return (
                f"🛂 **Visa Information for {dest}**\n\n"
                f"- **Indian Nationals:** Generally no visa required for travel within India.\n"
                f"- **Foreign Nationals:** Check the official embassy website for {dest}'s country.\n"
                f"- **e-Visa:** Many countries offer e-Visa on arrival — verify at [India e-Visa](https://indianvisaonline.gov.in/) or the destination country's portal.\n\n"
                f"**Key documents typically needed:**\n"
                f"- Valid passport (6+ months validity)\n"
                f"- Return flight tickets\n"
                f"- Hotel booking proof\n"
                f"- Sufficient funds proof\n\n"
                f"> Always verify requirements at the official embassy website before travelling."
            )

        # ── Destination / general travel fallback ─────────────────────────
        if has_tool_data:
            # Tool results are in sys prompt — tell user to configure API key for richer output
            return (
                f"Here's what I found for **{dest}** based on your query about *{user_query}*:\n\n"
                f"I've gathered real-time information from travel tools. "
                f"For richer results with photos and live ratings, add your **Google Maps API key** to `.env`.\n\n"
                f"Feel free to ask me about:\n"
                f"- Specific places (beaches, temples, cafés)\n"
                f"- Hotel recommendations\n"
                f"- Transport options\n"
                f"- Weather and safety tips"
            )

        return (
            f"Great question about **{dest}**! 🌍\n\n"
            f"I'm TripGenie, your AI travel assistant. I can help you with:\n"
            f"- 🏖️ **Attractions:** beaches, temples, waterfalls, museums, parks\n"
            f"- 🏨 **Accommodation:** hotels, resorts, hostels\n"
            f"- 🍽️ **Dining:** restaurants, cafés, street food\n"
            f"- 🚗 **Transport:** flights, trains, buses, local cabs\n"
            f"- 💰 **Budget** planning and breakdowns\n"
            f"- 🌤️ **Weather** forecasts\n"
            f"- 🛡️ **Safety** tips and emergency contacts\n\n"
            f"What specific information can I get for your trip to {dest}?"
        )


llm_service = LLMService()
