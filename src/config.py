"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Settings used to connect to an OpenAI-compatible API."""

    api_key: str | None
    base_url: str
    model: str

    @property
    def ai_enabled(self) -> bool:
        """Return whether an API key is available."""

        return bool(self.api_key and self.api_key != "your_api_key_here")


def get_settings() -> Settings:
    """Read application settings from the current environment."""

    return Settings(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )

