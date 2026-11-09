"""Testes básicos do módulo security."""

from __future__ import annotations

import os
import tempfile

import pytest

from security import CredentialManager, decrypt_bytes, encrypt_bytes


def test_dpapi_roundtrip():
    data = b"segredo-super-secreto-123"
    enc = encrypt_bytes(data)
    assert enc != data
    dec = decrypt_bytes(enc)
    assert dec == data


def test_dpapi_roundtrip_with_env_key(monkeypatch):
    monkeypatch.setenv("GP_DESKTOP_SECRET_KEY", "chave-de-teste-42")
    data = b"outro-segredo"
    enc = encrypt_bytes(data)
    dec = decrypt_bytes(enc)
    assert dec == data


def test_credential_manager_vault_save_get_delete(tmp_path):
    cm = CredentialManager(storage_dir=tmp_path, prefer_keyring=False)
    assert cm.backend == "vault"

    cm.save_secret("openai_api_key", "sk-test-123")
    assert cm.get_secret("openai_api_key") == "sk-test-123"

    cm.save_secret("anthropic_api_key", "ant-456")
    names = cm.list_secrets("openai")
    assert names == ["openai_api_key"]
    assert sorted(cm.list_secrets()) == ["anthropic_api_key", "openai_api_key"]

    cm.delete_secret("openai_api_key")
    assert cm.get_secret("openai_api_key") is None
    assert "openai_api_key" not in cm.list_secrets()


def test_credential_manager_missing_returns_none(tmp_path):
    cm = CredentialManager(storage_dir=tmp_path, prefer_keyring=False)
    assert cm.get_secret("inexistente") is None


def test_credential_manager_empty_name_raises(tmp_path):
    cm = CredentialManager(storage_dir=tmp_path, prefer_keyring=False)
    with pytest.raises(ValueError):
        cm.save_secret("", "valor")


def test_credential_manager_persistence(tmp_path):
    cm1 = CredentialManager(storage_dir=tmp_path, prefer_keyring=False)
    cm1.save_secret("k", "v")
    cm2 = CredentialManager(storage_dir=tmp_path, prefer_keyring=False)
    assert cm2.get_secret("k") == "v"
    assert cm2.list_secrets() == ["k"]


def test_credential_manager_prefix_filter(tmp_path):
    cm = CredentialManager(storage_dir=tmp_path, prefer_keyring=False)
    cm.save_secret("prov.openai", "a")
    cm.save_secret("prov.anthropic", "b")
    cm.save_secret("other", "c")
    assert sorted(cm.list_secrets("prov.")) == ["prov.anthropic", "prov.openai"]
