"""Gerenciador de Realtime (channels)."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .client import get_supabase_client


class RealtimeManager:
    def __init__(self, client=None):
        self._client = client if client is not None else get_supabase_client()
        self._channels: Dict[str, Any] = {}

    def subscribe(
        self,
        channel: str,
        callback: Callable[[Any], None],
        table: Optional[str] = None,
        event: str = "*",
    ):
        ch = self._client.channel(channel)
        filter_cfg = {"event": event, "schema": "public"}
        if table:
            filter_cfg["table"] = table
        try:
            ch.on("postgres_changes", filter_cfg, callback)
        except Exception:
            ch.on_postgres_changes(filter_cfg, callback)
        ch.subscribe()
        self._channels[channel] = ch
        return ch

    def unsubscribe(self, channel: str):
        ch = self._channels.pop(channel, None)
        if ch is not None:
            try:
                self._client.remove_channel(ch)
            except Exception:
                pass
        return True
