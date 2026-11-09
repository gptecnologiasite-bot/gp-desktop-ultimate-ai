"""Provedor compatível com o protocolo OpenAI (chat/completions)."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Optional

import httpx

from .base import (
    AIProvider,
    AuthenticationError,
    ModelNotFoundError,
    ProviderConnectionError,
    ProviderError,
    RateLimitError,
)


class OpenAICompatibleProvider(AIProvider):
    def __init__(
        self,
        name: str = "OpenAI-compatible",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        if base_url is None:
            base_url = "https://api.openai.com/v1"
        super().__init__(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _handle_error(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise AuthenticationError(
                f"{self.name}: autenticação falhou ({response.text})"
            )
        if response.status_code == 404:
            raise ModelNotFoundError(
                f"{self.name}: recurso/modelo não encontrado ({response.text})"
            )
        if response.status_code == 429:
            raise RateLimitError(
                f"{self.name}: limite de taxa excedido ({response.text})"
            )
        if response.status_code >= 400:
            raise ProviderError(
                f"{self.name}: erro HTTP {response.status_code}: {response.text}"
            )

    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        if not self.model:
            raise ProviderError(f"{self.name}: modelo não configurado")
        payload: Dict[str, Any] = {"model": self.model, "messages": messages}
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        url = self._normalize_base_url() + "/chat/completions"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._headers(), json=payload)
        except httpx.HTTPError as exc:
            raise ProviderConnectionError(
                f"{self.name}: falha de conexão: {exc}"
            ) from exc
        self._handle_error(response)
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(f"{self.name}: resposta inesperada: {data}") from exc

    def chat_stream(
        self, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> Iterator[str]:
        if not self.model:
            raise ProviderError(f"{self.name}: modelo não configurado")
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        url = self._normalize_base_url() + "/chat/completions"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream(
                    "POST", url, headers=self._headers(), json=payload
                ) as response:
                    if response.status_code >= 400:
                        response.read()
                        self._handle_error(response)
                        return
                    for line in response.iter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data:"):
                            continue
                        chunk = line[len("data:") :].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                        except json.JSONDecodeError:
                            continue
                        try:
                            delta = data["choices"][0]["delta"].get("content")
                        except (KeyError, IndexError, TypeError):
                            delta = None
                        if delta:
                            yield delta
        except httpx.HTTPError as exc:
            raise ProviderConnectionError(
                f"{self.name}: falha de conexão: {exc}"
            ) from exc

    def test_connection(self) -> bool:
        try:
            self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False
