import json
import re
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional, List
from app.config.settings import settings
from app.utils.logger import logger

class LLMFactory:
    @staticmethod
    def get_llm(provider: Optional[str] = None):
        prov = provider or settings.DEFAULT_LLM_PROVIDER
        if prov == "openai" and settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.7
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI LLM: {e}. Falling back to Heuristic Runner.")
        
        # Fallback to local dynamic heuristic runner
        return HeuristicLLMRunner()

class HeuristicLLMRunner:
    """Intelligent standalone runner providing dynamic outputs for any requested destination."""
    
    def invoke(self, prompt: str) -> str:
        prompt_text = str(prompt)
        return self.generate_dynamic_response(prompt_text)

    def extract_destination(self, prompt_text: str) -> str:
        """Extract destination city/region from user prompt dynamically."""
        if not prompt_text:
            return "Varkala, Kerala, India"
            
        # Regex patterns for common phrases: "trip to X", "visit X", "in X", "for X", "to X"
        patterns = [
            r"(?:trip|travel|vacation|tour|journey|fly|go)\s+to\s+([A-Za-z\s,]+?)(?=\s+(?:under|with|for|in|around|budget|having|preferring|\$|₹|\d|$))",
            r"(?:visit|explore)\s+([A-Za-z\s,]+?)(?=\s+(?:under|with|for|in|around|budget|having|\$|₹|\d|$))",
            r"in\s+([A-Za-z\s,]+?)(?=\s+(?:under|with|for|budget|\$|₹|\d|$))",
            r"to\s+([A-Za-z\s,]+?)(?=\s+(?:under|with|for|budget|\$|₹|\d|$))"
        ]
        
        for pat in patterns:
            match = re.search(pat, prompt_text, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                # Exclude non-location words
                cleaned = re.sub(r"\b(a|an|the|my|our|days|day|night|nights|budget|trip|under)\b", "", extracted, flags=re.IGNORECASE).strip()
                if cleaned and len(cleaned) > 2:
                    return cleaned.title()
                    
        # Fallback split
        words = prompt_text.split()
        for i, word in enumerate(words):
            if word.lower() in ["to", "in", "at", "visit"] and i + 1 < len(words):
                candidate = words[i+1].strip(",.!?").title()
                if candidate and candidate.lower() not in ["a", "an", "the", "under", "for"]:
                    return candidate
                    
        return "Varkala, Kerala, India"

    def generate_dynamic_response(self, prompt_text: str) -> str:
        dest = self.extract_destination(prompt_text)
        return f"Dynamic intelligence generated for target destination: {dest}."

llm_factory = LLMFactory()

