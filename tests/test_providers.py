"""Smoke tests para o módulo providers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unittest.mock import MagicMock, patch

import pytest

from providers import (
    AIProvider,
    AnthropicProvider,
    CohereProvider,
    GeminiProvider,
    HuggingFaceProvider,
    LMStudioProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    get_provider,
    list_providers,
    PROVIDERS,
)


def test_list_providers():
    providers = list_providers()
    assert isinstance(providers, list)
    assert len(providers) >= 17
    assert "openai" in providers


def test_factory_all():
    for pid in list_providers():
        p = get_provider(pid, api_key="test-key", model="test-model")
        assert isinstance(p, AIProvider)


def test_instantiation_no_network():
    p = OpenAICompatibleProvider(name="X", api_key="k", model="m")
    assert p.name == "X"
    a = AnthropicProvider(api_key="k", model="m")
    assert a.name == "Anthropic"
    g = GeminiProvider(api_key="k", model="m")
    assert g.name == "Gemini"
    o = OllamaProvider(model="m")
    assert o.name == "Ollama"
    l = LMStudioProvider(model="m")
    assert l.name == "LM Studio"
    c = CohereProvider(api_key="k", model="m")
    assert c.name == "Cohere"
    h = HuggingFaceProvider(api_key="k", model="m")
    assert h.name == "Hugging Face"


def test_configure():
    p = get_provider("openai", api_key="old", model="old-model")
    p.configure(api_key="new", model="new-model", timeout=10.0)
    assert p.api_key == "new"
    assert p.model == "new-model"
    assert p.timeout == 10.0


def test_chat_mock_openai():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"choices": [{"message": {"content": "olá"}}]}
    fake_client = MagicMock()
    fake_client.__enter__.return_value = fake_client
    fake_client.post.return_value = fake_response

    with patch("providers.openai_compatible.httpx.Client", return_value=fake_client):
        p = get_provider("openai", api_key="k", model="gpt-4o-mini")
        result = p.chat([{"role": "user", "content": "oi"}])
    assert result == "olá"


def test_test_connection_false_on_error():
    with patch(
        "providers.openai_compatible.httpx.Client", side_effect=Exception("boom")
    ):
        p = get_provider("openai", api_key="k", model="gpt-4o-mini")
        assert p.test_connection() is False


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        get_provider("nao-existe")


def test_providers_dict():
    assert isinstance(PROVIDERS, dict)
    assert "anthropic" in PROVIDERS
    assert "claude" in PROVIDERS
