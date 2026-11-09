"""Registro de provedores disponíveis."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from .anthropic import AnthropicProvider
from .base import AIProvider
from .cohere import CohereProvider
from .gemini import GeminiProvider
from .huggingface import HuggingFaceProvider
from .lmstudio import LMStudioProvider
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider

# IDs canônicos e aliases -> classe
PROVIDERS: Dict[str, Type[AIProvider]] = {
    "openai": OpenAICompatibleProvider,
    "anthropic": AnthropicProvider,
    "claude": AnthropicProvider,
    "gemini": GeminiProvider,
    "google": GeminiProvider,
    "grok": OpenAICompatibleProvider,
    "xai": OpenAICompatibleProvider,
    "deepseek": OpenAICompatibleProvider,
    "mistral": OpenAICompatibleProvider,
    "groq": OpenAICompatibleProvider,
    "openrouter": OpenAICompatibleProvider,
    "cohere": CohereProvider,
    "perplexity": OpenAICompatibleProvider,
    "together": OpenAICompatibleProvider,
    "fireworks": OpenAICompatibleProvider,
    "cerebras": OpenAICompatibleProvider,
    "huggingface": HuggingFaceProvider,
    "ollama": OllamaProvider,
    "lmstudio": LMStudioProvider,
    "custom": OpenAICompatibleProvider,
    "openai-compatible": OpenAICompatibleProvider,
}

DEFAULT_BASE_URLS: Dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "grok": "https://api.x.ai/v1",
    "xai": "https://api.x.ai/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "mistral": "https://api.mistral.ai/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "perplexity": "https://api.perplexity.ai",
    "together": "https://api.together.xyz/v1",
    "fireworks": "https://api.fireworks.ai/inference/v1",
    "cerebras": "https://api.cerebras.ai/v1",
}

DEFAULT_MODELS: Dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-latest",
    "claude": "claude-3-5-sonnet-latest",
    "gemini": "gemini-1.5-flash",
    "google": "gemini-1.5-flash",
    "grok": "grok-2-latest",
    "deepseek": "deepseek-chat",
    "mistral": "mistral-small-latest",
    "groq": "llama-3.3-70b-versatile",
    "openrouter": "openai/gpt-4o-mini",
    "cohere": "command-r",
    "perplexity": "llama-3.1-sonar-small-128k-online",
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "fireworks": "accounts/fireworks/models/llama-v3p1-8b-instruct",
    "cerebras": "llama3.1-8b",
    "ollama": "llama3",
    "lmstudio": "local-model",
    "huggingface": "meta-llama/Llama-3.1-8B-Instruct",
}


def list_providers() -> List[str]:
    """Lista os ids de provedores disponíveis."""
    return sorted(PROVIDERS.keys())


def get_provider(
    provider_id: str, config: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> AIProvider:
    """Factory: cria instância do provedor a partir do id e config."""
    pid = (provider_id or "").strip().lower()
    if pid not in PROVIDERS:
        raise ValueError(f"Provedor desconhecido: {provider_id}")
    cls = PROVIDERS[pid]
    cfg = dict(config or {})
    cfg.update(kwargs)
    api_key = cfg.get("api_key")
    base_url = cfg.get("base_url", DEFAULT_BASE_URLS.get(pid))
    model = cfg.get("model", DEFAULT_MODELS.get(pid))
    timeout = cfg.get("timeout", 30.0)
    name = cfg.get("name", pid)
    if cls is OpenAICompatibleProvider:
        return cls(
            name=name, api_key=api_key, base_url=base_url, model=model, timeout=timeout
        )
    # providers com nome fixo
    try:
        return cls(
            api_key=api_key, base_url=base_url, model=model, timeout=timeout, name=name
        )
    except TypeError:
        return cls(api_key=api_key, base_url=base_url, model=model, timeout=timeout)
