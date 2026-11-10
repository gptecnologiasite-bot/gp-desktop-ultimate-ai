"""Utilitários de criptografia baseados em DPAPI do Windows.

Fornece :func:`encrypt_bytes` e :func:`decrypt_bytes` usadas pelo
:mod:`security.credential_manager` para proteger segredos em disco quando o
Windows Credential Manager (``keyring``) não estiver disponível.

Estratégia:
* Se ``pywin32`` estiver instalado, usa ``win32crypt.CryptProtectData`` /
  ``CryptUnprotectData`` (DPAPI, ligado ao usuário/sessão do Windows).
* Caso contrário (ou em caso de falha), usa ``cryptography.Fernet`` com uma
  chave derivada via PBKDF2 de uma variável de ambiente (``GP_DESKTOP_SECRET_KEY``)
  e um salt fixo.
"""

from __future__ import annotations

import base64
import os
from typing import Optional

_SALT: bytes = b"gp-desktop-ultimate-ai-dpapi-salt-v1"
_ENV_VAR: str = "GP_DESKTOP_SECRET_KEY"
_ITERATIONS: int = 390_000


def _win32crypt_available() -> bool:
    try:
        import win32crypt  # noqa: F401

        return True
    except Exception:  # pragma: no cover - depende do ambiente
        return False


def _derive_fernet_key() -> bytes:
    """Deriva uma chave Fernet (32 bytes url-safe base64) a partir do ambiente."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    seed = os.environ.get(_ENV_VAR)
    if not seed:
        raise RuntimeError(
            f"Variável de ambiente {_ENV_VAR} não definida; não é possível "
            "derivar chave de criptografia fallback."
        )
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=_ITERATIONS,
    )
    raw = kdf.derive(seed.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)


def _fernet_encrypt(data: bytes) -> bytes:
    from cryptography.fernet import Fernet

    return Fernet(_derive_fernet_key()).encrypt(data)


def _fernet_decrypt(data: bytes) -> bytes:
    from cryptography.fernet import Fernet, InvalidToken

    try:
        return Fernet(_derive_fernet_key()).decrypt(data)
    except InvalidToken as exc:  # pragma: no cover - repassado como RuntimeError
        raise RuntimeError("Falha ao descriptografar dados (token inválido).") from exc


def encrypt_bytes(data: bytes) -> bytes:
    """Criptografa ``data`` e retorna os bytes cifrados.

    Prefere DPAPI do Windows quando disponível; caso contrário usa Fernet.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data deve ser bytes ou bytearray")

    if _win32crypt_available():
        try:
            import win32crypt

            return win32crypt.CryptProtectData(bytes(data))
        except Exception:
            # Fallback para Fernet se DPAPI falhar em tempo de execução.
            pass

    return _fernet_encrypt(bytes(data))


def decrypt_bytes(data: bytes) -> bytes:
    """Descriptografa bytes produzidos por :func:`encrypt_bytes`."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data deve ser bytes ou bytearray")

    data = bytes(data)

    # Tenta DPAPI primeiro (se disponível).
    if _win32crypt_available():
        try:
            import win32crypt

            _description, plaintext = win32crypt.CryptUnprotectData(data)
            return plaintext
        except Exception:
            pass

    # Fallback Fernet.
    return _fernet_decrypt(data)


__all__ = ["encrypt_bytes", "decrypt_bytes"]
