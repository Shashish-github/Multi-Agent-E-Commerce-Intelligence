"""
LLM Service for Dynamic Natural Language Processing using Groq / Gemini / OpenAI.
Provides robust fallback to deterministic algorithms if the external API is unreachable or rate-limited.
"""
import json
import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("commerce_intelligence.llm")


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.groq_api_key = settings.GROQ_API_KEY
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        self.timeout = 5.0  # fast 5s timeout to guarantee high responsiveness

    async def call_groq(self, prompt: str, system_prompt: str = "You are an expert e-commerce product analyst.", response_json: bool = False) -> Optional[str]:
        """Calls Groq Cloud API with ultra-low latency."""
        if not self.groq_api_key:
            return None

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload: Dict[str, Any] = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 512
        }

        if response_json:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content.strip()
                else:
                    logger.warning(f"Groq API returned status {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.warning(f"Failed to connect to Groq API: {e}")
            return None

    async def parse_user_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Extracts structured shopping constraints using LLM if available."""
        if self.provider != "groq" or not self.groq_api_key:
            return None

        system_prompt = (
            "You are a strict shopping query parsing engine. Extract structured constraints from user shopping queries. "
            "Output strictly valid JSON with keys: category (one of 'laptop', 'smartphone', 'monitor', 'audio'), "
            "budget_max (number or null in INR), hard_constraints (array of objects {field, operator, value, unit}), "
            "soft_preferences (array of objects {aspect, weight, value}), exclusions (array of strings)."
        )
        
        prompt = f"Extract structured constraints from this shopping request: \"{query}\""
        raw_result = await self.call_groq(prompt, system_prompt=system_prompt, response_json=True)
        
        if raw_result:
            try:
                parsed = json.loads(raw_result)
                return parsed
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON response: {e}")
                return None
        return None

    async def generate_recommendation_thesis(self, product_name: str, score: float, rank: int, highlights: list, price: float) -> Optional[str]:
        """Generates dynamic human-like recommendation thesis using LLM."""
        if self.provider != "groq" or not self.groq_api_key:
            return None

        system_prompt = (
            "You are an executive shopping advisor. Write an authoritative, concise 2-sentence thesis explaining "
            "why a specific product was ranked for the user based on provided score, price, and highlights."
        )
        
        prompt = (
            f"Product: {product_name}\n"
            f"Rank: #{rank}\n"
            f"Overall Score: {score:.2f}/1.0\n"
            f"Price: ₹{price:,.0f}\n"
            f"Key Highlights: {', '.join(highlights)}\n"
            f"Write a 2-sentence crisp recommendation verdict."
        )
        
        return await self.call_groq(prompt, system_prompt=system_prompt, response_json=False)


llm_service = LLMService()
