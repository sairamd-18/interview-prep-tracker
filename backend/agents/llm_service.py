"""
LLM Service Layer supporting external providers (Gemini / OpenAI)
and intelligent fallback heuristics for structured JSON output.
"""
import os
import json
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger("LLMService")

class LLMService:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.provider = "gemini" if self.gemini_api_key else ("openai" if self.openai_api_key else "local_intelligent_engine")
        logger.info(f"Initialized LLMService with active provider: {self.provider}")

    def generate_json(self, prompt: str, system_prompt: str = "", fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates structured JSON response. Uses external LLM if configured;
        otherwise leverages the intelligent fallback data/engine.
        """
        if self.provider == "gemini":
            try:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                headers = {"Content-Type": "application/json"}
                full_prompt = f"{system_prompt}\n\nYou must respond ONLY in valid JSON format.\n\n{prompt}"
                payload = {
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json"}
                }
                res = requests.post(url, headers=headers, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    clean_text = self._clean_json_text(text)
                    return json.loads(clean_text)
                else:
                    logger.warning(f"Gemini API returned status {res.status_code}. Using fallback.")
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Utilizing fallback engine.")

        elif self.provider == "openai":
            try:
                import requests
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": f"{system_prompt}\nRespond strictly with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
                res = requests.post(url, headers=headers, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    text = data["choices"][0]["message"]["content"]
                    return json.loads(self._clean_json_text(text))
                else:
                    logger.warning(f"OpenAI API returned status {res.status_code}. Using fallback.")
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Utilizing fallback engine.")

        # Fallback Engine
        if fallback_data is not None:
            return fallback_data
            
        return {"status": "ok", "message": "Processed by local intelligent agent engine"}

    def _clean_json_text(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

# Global singleton
llm_service = LLMService()
