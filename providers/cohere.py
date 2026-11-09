"""Provedor Cohere."""

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


class CohereProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
        name: str = "Cohere",
    ) -> None:
        if base_url is None:
            base_url = "https://api.cohere.com"
        if model is None:
            model = "command-r"
        super().__init__(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )

    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        if not self.model:
            raise ProviderError(f"{self.name}: modelo não configurado")
        payload: Dict[str, Any] = {"model": self.model, "messages": messages}
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        url = self._normalize_base_url() + "/v2/chat"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise ProviderConnectionError(
                f"{self.name}: falha de conexão: {exc}"
            ) from exc
        if response.status_code == 401:
            raise AuthenticationError(f"{self.name}: autenticação falhou")
        if response.status_code == 429:
            raise RateLimitError(f"{self.name}: limite de taxa excedido")
        if response.status_code >= 400:
            raise ProviderError(
                f"{self.name}: erro HTTP {response.status_code}: {response.text}"
            )
        data = response.json()
        try:
            msg = data.get("message", {})
            content = msg.get("content", "")
            if isinstance(content, list):
                return "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            if isinstance(content, dict):
                return content.get("text", str(content))
            return str(content) if content else data.get("text", "")
        except Exception as exc:
            raise ProviderError(f"{self.name}: resposta inesperada: {data}") from exc

    def test_connection(self) -> bool:
        try:
            self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False
