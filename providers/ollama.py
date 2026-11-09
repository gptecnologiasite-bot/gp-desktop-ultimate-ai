"""Provedor Ollama (local)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .base import (
    AIProvider,
    ProviderConnectionError,
    ProviderError,
)


class OllamaProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
        name: str = "Ollama",
    ) -> None:
        if base_url is None:
            base_url = "http://localhost:11434"
        if model is None:
            model = "llama3"
        super().__init__(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )

    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        if not self.model:
            raise ProviderError(f"{self.name}: modelo não configurado")
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        url = self._normalize_base_url() + "/api/chat"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise ProviderConnectionError(
                f"{self.name}: falha de conexão: {exc}"
            ) from exc
        if response.status_code >= 400:
            raise ProviderError(
                f"{self.name}: erro HTTP {response.status_code}: {response.text}"
            )
        data = response.json()
        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"{self.name}: resposta inesperada: {data}") from exc

    def test_connection(self) -> bool:
        try:
            self.chat([{"role": "user", "content": "ping"}])
            return True
        except Exception:
            return False
