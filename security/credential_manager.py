"""Gerenciador de credenciais/secrets para o GP Desktop Ultimate AI.

Armazena chaves de API de provedores de IA de forma segura:

* Por padrão usa o Windows Credential Manager via ``keyring``.
* Se ``keyring`` não estiver disponível (ou o backend falhar), cai para um
  arquivo local cifrado com :mod:`security.dpapi`.

Nunca armazena segredos em texto aberto no Supabase ou em arquivos de config.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import List, Optional

try:  # keyring é opcional em tempo de importação
    import keyring as _keyring

    _KEYRING_IMPORTED = True
except Exception:  # pragma: no cover - depende do ambiente
    _keyring = None  # type: ignore[assignment]
    _KEYRING_IMPORTED = False

from .dpapi import decrypt_bytes, encrypt_bytes

SERVICE_NAME = "gp-desktop-ultimate-ai"
VAULT_FILENAME = "secrets.vault"
INDEX_FILENAME = "secrets.index.json"


class CredentialManager:
    """Gerencia segredos nomeados.

    Parameters
    ----------
    storage_dir:
        Diretório usado para o cofre local (fallback) e para o índice de nomes.
        Se ``None``, usa ``%APPDATA%/GPDesktopUltimateAI`` (ou ``~``).
    service_name:
        Nome do serviço usado no Windows Credential Manager.
    prefer_keyring:
        Se ``False``, força o uso do cofre local cifrado (útil para testes).
    """

    def __init__(
        self,
        storage_dir: Optional[str | Path] = None,
        service_name: str = SERVICE_NAME,
        prefer_keyring: bool = True,
    ) -> None:
        self.service_name = service_name
        base = (
            storage_dir
            if storage_dir is not None
            else os.environ.get("APPDATA", os.path.expanduser("~"))
        )
        self.storage_dir = (
            Path(base) / "GPDesktopUltimateAI" if storage_dir is None else Path(base)
        )
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._prefer_keyring = prefer_keyring
        self._use_keyring = (
            prefer_keyring and _KEYRING_IMPORTED and self._keyring_usable()
        )
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    # Internos
    # ------------------------------------------------------------------ #
    def _keyring_usable(self) -> bool:
        if not _KEYRING_IMPORTED or _keyring is None:
            return False
        try:
            _keyring.get_keyring()
            return True
        except Exception:
            return False

    @property
    def backend(self) -> str:
        """Nome do backend ativo ('keyring' ou 'vault')."""
        return "keyring" if self._use_keyring else "vault"

    def _vault_path(self) -> Path:
        return self.storage_dir / VAULT_FILENAME

    def _index_path(self) -> Path:
        return self.storage_dir / INDEX_FILENAME

    def _load_vault(self) -> dict:
        path = self._vault_path()
        if not path.exists():
            return {}
        try:
            plaintext = decrypt_bytes(path.read_bytes())
            data = json.loads(plaintext.decode("utf-8"))
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    def _save_vault(self, vault: dict) -> None:
        payload = json.dumps(vault, ensure_ascii=False).encode("utf-8")
        self._vault_path().write_bytes(encrypt_bytes(payload))

    def _load_index(self) -> List[str]:
        path = self._index_path()
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [str(x) for x in data]
            return []
        except Exception:
            return []

    def _save_index(self, names: List[str]) -> None:
        unique = sorted(set(names))
        self._index_path().write_text(
            json.dumps(unique, ensure_ascii=False), encoding="utf-8"
        )

    # ------------------------------------------------------------------ #
    # API pública
    # ------------------------------------------------------------------ #
    def save_secret(self, name: str, value: str) -> None:
        """Salva (ou sobrescreve) o segredo ``name`` com ``value``."""
        if not name:
            raise ValueError("name não pode ser vazio")
        if value is None:
            raise ValueError("value não pode ser None")

        with self._lock:
            if self._use_keyring:
                _keyring.set_password(self.service_name, name, value)
                index = self._load_index()
                if name not in index:
                    index.append(name)
                    self._save_index(index)
            else:
                vault = self._load_vault()
                vault[name] = value
                self._save_vault(vault)

    def get_secret(self, name: str) -> Optional[str]:
        """Retorna o valor do segredo ou ``None`` se não existir."""
        if not name:
            return None

        with self._lock:
            if self._use_keyring:
                try:
                    return _keyring.get_password(self.service_name, name)
                except Exception:
                    return None
            else:
                return self._load_vault().get(name)

    def delete_secret(self, name: str) -> None:
        """Remove o segredo ``name`` (idempotente)."""
        if not name:
            return

        with self._lock:
            if self._use_keyring:
                try:
                    _keyring.delete_password(self.service_name, name)
                except Exception:
                    # Pode não existir; ignorar.
                    pass
                index = [n for n in self._load_index() if n != name]
                self._save_index(index)
            else:
                vault = self._load_vault()
                if name in vault:
                    del vault[name]
                    self._save_vault(vault)

    def list_secrets(self, prefix: str = "") -> List[str]:
        """Lista nomes de segredos que começam com ``prefix``."""
        with self._lock:
            if self._use_keyring:
                names = self._load_index()
            else:
                names = list(self._load_vault().keys())
            return sorted(n for n in names if n.startswith(prefix))


__all__ = ["CredentialManager", "SERVICE_NAME"]
