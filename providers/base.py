"""Base abstrata para provedores de IA."""

from __future__ import annotations

import abc
from typing import Any, Dict, Iterator, List, Optional


class ProviderError(Exception):
    """Erro genérico de provedor."""


class AuthenticationError(ProviderError):
    """Falha de autenticação (api key inválida)."""


class RateLimitError(ProviderError):
    """Limite de taxa excedido."""


class ProviderConnectionError(ProviderError):
    """Falha de conexão/rede."""


class ModelNotFoundError(ProviderError):
    """Modelo não encontrado."""


class AIProvider(abc.ABC):
    """Classe abstrata base para todos os provedores de IA."""

    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def configure(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        if api_key is not None:
            self.api_key = api_key
        if base_url is not None:
            self.base_url = base_url
        if model is not None:
            self.model = model
        if timeout is not None:
            self.timeout = timeout

    @abc.abstractmethod
    def test_connection(self) -> bool:
        """Testa a conexão com o provedor."""

    @abc.abstractmethod
    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        """Envia mensagens e retorna a resposta como string."""

    def chat_stream(
        self, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> Iterator[str]:
        """Streaming opcional de tokens."""
        raise NotImplementedError(f"{self.name} não suporta streaming")

    def _normalize_base_url(self) -> str:
        return (self.base_url or "").rstrip("/")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} model={self.model!r}>"
