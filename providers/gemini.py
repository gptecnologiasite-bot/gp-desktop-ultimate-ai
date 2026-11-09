"""Provedor Google Gemini (generateContent)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .base import (
    AIProvider,
    AuthenticationError,
    ProviderConnectionError,
    ProviderError,
    RateLimitError,
)


class GeminiProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
        name: str = "Gemini",
    ) -> None:
        if base_url is None:
            base_url = "https://generativelanguage.googleapis.com"
        if model is None:
            model = "gemini-1.5-flash"
        super().__init__(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )

    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        if not self.model:
            raise ProviderError(f"{self.name}: modelo não configurado")
        contents = []
        system_instruction = None
        for m in messages:
            role = m.get("role", "user")
            text = m.get("content", "")
            if role == "system":
                system_instruction = {"parts": [{"text": text}]}
            else:
                gemini_role = "user" if role == "user" else "model"
                contents.append({"role": gemini_role, "parts": [{"text": text}]})
        payload: Dict[str, Any] = {"contents": contents}
        if system_instruction:
            payload["system_instruction"] = system_instruction
        gen_config: Dict[str, Any] = {}
        if "temperature" in kwargs and kwargs["temperature"] is not None:
            gen_config["temperature"] = kwargs.pop("temperature")
        if "max_tokens" in kwargs and kwargs["max_tokens"] is not None:
            gen_config["maxOutputTokens"] = kwargs.pop("max_tokens")
        if gen_config:
            payload["generationConfig"] = gen_config
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        url = (
            self._normalize_base_url()
            + f"/v1beta/models/{self.model}:generateContent?key={self.api_key or ''}"
        )
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise ProviderConnectionError(
                f"{self.name}: falha de conexão: {exc}"
            ) from exc
        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(f"{self.name}: autenticação falhou")
        if response.status_code == 429:
            raise RateLimitError(f"{self.name}: limite de taxa excedido")
        if response.status_code >= 400:
            raise ProviderError(
                f"{self.name}: erro HTTP {response.status_code}: {response.text}"
            )
        data = response.json()
        try:
            candidates = data["candidates"]
            parts = candidates[0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(f"{self.name}: resposta inesperada: {data}") from exc

    def test_connection(self) -> bool:
        try:
            self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False
