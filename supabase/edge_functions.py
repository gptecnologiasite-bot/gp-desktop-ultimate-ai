"""Gerenciador de Edge Functions."""

from __future__ import annotations

from typing import Any, Optional

from .client import get_supabase_client


class EdgeFunctionsManager:
    def __init__(self, client=None):
        self._client = client if client is not None else get_supabase_client()

    def invoke(self, function_name: str, payload: Optional[Any] = None):
        options = {"body": payload} if payload is not None else None
        if options is None:
            return self._client.functions.invoke(function_name)
        return self._client.functions.invoke(function_name, invoke_options=options)
