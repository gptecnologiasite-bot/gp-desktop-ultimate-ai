"""Provedor Hugging Face (Inference API)."""

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


class HuggingFaceProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
        name: str = "Hugging Face",
    ) -> None:
        if base_url is None:
            base_url = "https://api-inference.huggingface.co"
        if model is None:
            model = "meta-llama/Llama-3.1-8B-Instruct"
        super().__init__(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )

    def _build_prompt(self, messages: List[Dict[str, Any]]) -> str:
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"{role}: {content}")
        return "\n".join(parts)

    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        if not self.model:
            raise ProviderError(f"{self.name}: modelo não configurado")
        prompt = self._build_prompt(messages)
        payload: Dict[str, Any] = {"inputs": prompt, "parameters": {}}
        if kwargs.get("max_tokens") is not None:
            payload["parameters"]["max_new_tokens"] = kwargs.pop("max_tokens")
        if kwargs.get("temperature") is not None:
            payload["parameters"]["temperature"] = kwargs.pop("temperature")
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        url = self._normalize_base_url() + f"/models/{self.model}"
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
            if isinstance(data, list) and data:
                item = data[0]
                if isinstance(item, dict):
                    text = item.get("generated_text", "")
                    if text.startswith(prompt):
                        text = text[len(prompt) :]
                    return text.strip()
            if isinstance(data, dict):
                if "generated_text" in data:
                    text = data["generated_text"]
                    if text.startswith(prompt):
                        text = text[len(prompt) :]
                    return text.strip()
                return str(data)
            return str(data)
        except Exception as exc:
            raise ProviderError(f"{self.name}: resposta inesperada: {data}") from exc

    def test_connection(self) -> bool:
        try:
            self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False
