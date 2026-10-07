from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.config import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for model requests")
        self.model = settings.assistant_model
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    def complete(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
    ) -> str:
        request: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
        }
        if response_format is not None:
            request["response_format"] = response_format
        result = self.client.chat.completions.create(**request)
        return result.choices[0].message.content or ""

    def ping(self) -> None:
        self.client.models.retrieve(self.model)

    def complete_json(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        content = self.complete(messages, {"type": "json_object"})
        return json.loads(content)
