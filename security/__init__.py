"""Pacote de segurança do GP Desktop Ultimate AI."""

from .credential_manager import CredentialManager, SERVICE_NAME
from .dpapi import decrypt_bytes, encrypt_bytes

__all__ = [
    "CredentialManager",
    "SERVICE_NAME",
    "encrypt_bytes",
    "decrypt_bytes",
]
