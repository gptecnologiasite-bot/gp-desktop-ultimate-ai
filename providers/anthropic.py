"""Provedor Anthropic (Claude)."""

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


class AnthropicProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
        name: str = "Anthropic",
    ) -> None:
        if base_url is None:
            base_url = "https://api.anthropic.com"
        super().__init__(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
        }

    def _split_messages(self, messages: List[Dict[str, Any]]):
        system_parts = []
        chat = []
        for m in messages:
            if m.get("role") == "system":
                system_parts.append(m.get("content", ""))
            else:
                chat.append(
                    {"role": m.get("role", "user"), "content": m.get("content", "")}
                )
        system = "\n".join(system_parts) if system_parts else None
        return system, chat

    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        if not self.model:
            raise ProviderError(f"{self.name}: modelo não configurado")
        system, chat_messages = self._split_messages(messages)
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": kwargs.pop("max_tokens", 1024),
        }
        if system:
            payload["system"] = system
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        url = self._normalize_base_url() + "/v1/messages"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._headers(), json=payload)
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
            content = data["content"]
            if isinstance(content, list):
                return "".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict)
                )
            return str(content)
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"{self.name}: resposta inesperada: {data}") from exc

    def test_connection(self) -> bool:
        try:
            self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False
