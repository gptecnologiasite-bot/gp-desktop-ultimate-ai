"""Pacote de provedores de IA."""

from .base import (
    AIProvider,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ProviderConnectionError,
    ModelNotFoundError,
)
from .openai_compatible import OpenAICompatibleProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from .ollama import OllamaProvider
from .lmstudio import LMStudioProvider
from .cohere import CohereProvider
from .huggingface import HuggingFaceProvider
from .registry import PROVIDERS, get_provider, list_providers

__all__ = [
    "AIProvider",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "ProviderConnectionError",
    "ModelNotFoundError",
    "OpenAICompatibleProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "OllamaProvider",
    "LMStudioProvider",
    "CohereProvider",
    "HuggingFaceProvider",
    "PROVIDERS",
    "get_provider",
    "list_providers",
]
