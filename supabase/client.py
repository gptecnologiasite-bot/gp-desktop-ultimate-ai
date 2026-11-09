"""Cliente Supabase (singleton com reset)."""

from __future__ import annotations

import os
import sys
import threading
from typing import Optional

# Carrega o pacote supabase instalado (supabase-py) evitando colisão com este módulo.
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_saved_path = sys.path[:]
sys.path = [p for p in sys.path if p not in ("", _root, os.getcwd())]
_stashed = {}
for k in list(sys.modules):
    if k == "supabase" or k.startswith("supabase."):
        _stashed[k] = sys.modules.pop(k)
try:
    from supabase import Client, create_client
finally:
    sys.path = _saved_path
    sys.modules.update(_stashed)

_client: Optional[Client] = None
_client_url: Optional[str] = None
_client_key: Optional[str] = None
_lock = threading.Lock()


def get_supabase_client(
    url: Optional[str] = None, anon_key: Optional[str] = None
) -> Client:
    """Retorna o client Supabase (singleton). Lê SUPABASE_URL/SUPABASE_ANON_KEY do env."""
    global _client, _client_url, _client_key
    with _lock:
        url = url or os.getenv("SUPABASE_URL")
        anon_key = anon_key or os.getenv("SUPABASE_ANON_KEY")
        if not url or not anon_key:
            raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórios")
        if _client is None or url != _client_url or anon_key != _client_key:
            _client = create_client(url, anon_key)
            _client_url = url
            _client_key = anon_key
        return _client


def reset_client() -> None:
    """Reseta o singleton (útil para testes)."""
    global _client, _client_url, _client_key
    with _lock:
        _client = None
        _client_url = None
        _client_key = None
