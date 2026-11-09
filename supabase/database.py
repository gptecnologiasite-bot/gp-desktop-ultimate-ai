"""Gerenciador genérico de banco de dados (PostgREST)."""

from __future__ import annotations

from typing import Any, Iterable, Optional

from .client import get_supabase_client

TABLES = [
    "users",
    "profiles",
    "settings",
    "themes",
    "personalizations",
    "appearance_profiles",
    "clocks",
    "widgets",
    "wallpapers",
    "favorites",
    "ai_history",
    "preferences",
    "devices",
]


class DatabaseManager:
    def __init__(self, client=None):
        self._client = client if client is not None else get_supabase_client()

    def _validate_table(self, table: str) -> None:
        if table not in TABLES:
            raise ValueError(f"Tabela não permitida: {table}")

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[dict] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        self._validate_table(table)
        q = self._client.table(table).select(columns)
        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)
        if order:
            q = q.order(order)
        if limit is not None:
            q = q.limit(limit)
        if offset is not None:
            q = q.offset(offset)
        return q.execute()

    def insert(self, table: str, data: Any):
        self._validate_table(table)
        return self._client.table(table).insert(data).execute()

    def update(self, table: str, data: dict, filters: Optional[dict] = None):
        self._validate_table(table)
        q = self._client.table(table).update(data)
        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)
        return q.execute()

    def delete(self, table: str, filters: Optional[dict] = None):
        self._validate_table(table)
        q = self._client.table(table).delete()
        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)
        return q.execute()

    def upsert(self, table: str, data: Any, on_conflict: Optional[str] = None):
        self._validate_table(table)
        opts = {}
        if on_conflict:
            opts["on_conflict"] = on_conflict
        return self._client.table(table).upsert(data, **opts).execute()
