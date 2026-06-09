"""Small wrapper around an OpenAI-compatible chat completion API."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from src.config import Settings


class AIServiceError(RuntimeError):
    """Raised when the configured AI service cannot return usable JSON."""


class AIClient:
    """Send prompts to an OpenAI-compatible provider."""

    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise ValueError("An API key is required to create the AI client.")
        self.model = settings.model
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Return a chat completion parsed as a JSON object."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            parsed = json.loads(_remove_markdown_fence(content))
        except Exception as exc:
            raise AIServiceError(f"The AI provider returned an error: {exc}") from exc

        if not isinstance(parsed, dict):
            raise AIServiceError("The AI provider did not return a JSON object.")
        return parsed


def _remove_markdown_fence(content: str) -> str:
    """Remove an optional JSON Markdown fence used by some providers."""

    match = re.fullmatch(r"\s*```(?:json)?\s*(.*?)\s*```\s*", content, re.DOTALL)
    return match.group(1) if match else content.strip()

