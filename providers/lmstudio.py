"""Provedor LM Studio (OpenAI-compatible local)."""

from __future__ import annotations

from typing import Optional

from .openai_compatible import OpenAICompatibleProvider


class LMStudioProvider(OpenAICompatibleProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
        name: str = "LM Studio",
    ) -> None:
        if base_url is None:
            base_url = "http://localhost:1234/v1"
        super().__init__(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )
