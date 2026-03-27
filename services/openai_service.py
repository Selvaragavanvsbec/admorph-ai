import json
from typing import Any

from openai import OpenAI

from backend.config import settings


class OpenAIService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def generate_json(self, system_prompt: str, user_prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if not self.client:
            return fallback
        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                temperature=0,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            text = response.output_text
            return json.loads(text)
        except Exception:
            return fallback


openai_service = OpenAIService()
