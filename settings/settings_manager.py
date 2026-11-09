"""Gerenciador de configurações (settings) com persistência no Supabase.

Persiste na tabela ``settings`` (key/value jsonb), mantém cache em memória
e permite reset. Sem banco local.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


def _resolve_db(db=None, client=None):
    if db is not None:
        return db
    try:
        from supabase import DatabaseManager

        return DatabaseManager(client)
    except Exception:
        return None


class SettingsManager:
    """Gerencia configurações do aplicativo.

    Parâmetros:
        db: instância de DatabaseManager (opcional)
        client: client Supabase (opcional)
        user_id: id do usuário (opcional, para filtrar linhas)
        defaults: valores padrão iniciais
    """

    def __init__(
        self,
        db=None,
        client=None,
        user_id: Optional[str] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ):
        self._db = _resolve_db(db, client)
        self._client = client
        self._user_id = user_id
        self._cache: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = dict(defaults or {})
        # aplica defaults no cache
        for k, v in self._defaults.items():
            self._cache.setdefault(k, v)
        try:
            self.load()
        except Exception:
            pass

    # ---------- helpers ----------
    def _user_filter(self) -> Optional[Dict[str, Any]]:
        if self._user_id:
            return {"user_id": self._user_id}
        return None

    def _merge_filters(
        self, extra: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        f = self._user_filter()
        if extra:
            f = dict(f or {})
            f.update(extra)
        return f

    def _parse_value(self, value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value

    # ---------- persistência ----------
    def load(self) -> Dict[str, Any]:
        """Carrega todas as settings do Supabase para o cache."""
        if self._db is None:
            return dict(self._cache)
        try:
            res = self._db.select("settings", filters=self._user_filter())
            rows = getattr(res, "data", res)
            if not isinstance(rows, list):
                rows = list(rows) if rows is not None else []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                key = row.get("key")
                if key is None:
                    continue
                self._cache[key] = self._parse_value(row.get("value"))
        except Exception:
            pass
        return dict(self._cache)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._cache:
            return self._cache[key]
        # tenta recarregar (best-effort)
        if self._db is not None:
            try:
                res = self._db.select(
                    "settings", filters=self._merge_filters({"key": key})
                )
                rows = getattr(res, "data", res)
                if isinstance(rows, list) and rows:
                    val = rows[0].get("value") if isinstance(rows[0], dict) else None
                    val = self._parse_value(val)
                    self._cache[key] = val
                    return val
            except Exception:
                pass
        if default is None and key in self._defaults:
            return self._defaults[key]
        return default

    def set(self, key: str, value: Any) -> bool:
        self._cache[key] = value
        if self._db is None:
            return True
        try:
            payload: Dict[str, Any] = {"key": key, "value": value}
            if self._user_id:
                payload["user_id"] = self._user_id
            on_conflict = "user_id,key" if self._user_id else "key"
            self._db.upsert("settings", payload, on_conflict=on_conflict)
            return True
        except Exception:
            return False

    # alias
    set_value = set
    put = set

    def get_all(self) -> Dict[str, Any]:
        return dict(self._cache)

    def all(self) -> Dict[str, Any]:
        return self.get_all()

    def delete(self, key: str) -> bool:
        self._cache.pop(key, None)
        if self._db is None:
            return True
        try:
            self._db.delete("settings", filters=self._merge_filters({"key": key}))
            return True
        except Exception:
            return False

    def reset(self, key: Optional[str] = None) -> bool:
        """Reseta uma chave ou todas as settings."""
        if key is None:
            # limpa cache (mantém defaults)
            self._cache.clear()
            for k, v in self._defaults.items():
                self._cache[k] = v
            if self._db is not None:
                try:
                    self._db.delete("settings", filters=self._user_filter())
                except Exception:
                    pass
            return True
        # reset de chave única
        if key in self._defaults:
            self._cache[key] = self._defaults[key]
        else:
            self._cache.pop(key, None)
        if self._db is not None:
            try:
                self._db.delete("settings", filters=self._merge_filters({"key": key}))
            except Exception:
                pass
            if key in self._cache:
                # re-persiste default
                self.set(key, self._cache[key])
        return True

    def reset_all(self) -> bool:
        return self.reset(None)

    # helpers de conveniência para settings comuns
    def get_language(self, default: str = "pt-BR") -> str:
        return self.get("language", default)

    def set_language(self, value: str) -> bool:
        return self.set("language", value)

    def get_startup(self, default: bool = False) -> bool:
        return self.get("startup", default)

    def set_startup(self, value: bool) -> bool:
        return self.set("startup", value)

    def get_notifications(self, default: bool = True) -> bool:
        return self.get("notifications", default)

    def set_notifications(self, value: bool) -> bool:
        return self.set("notifications", value)

    @property
    def cache(self) -> Dict[str, Any]:
        return self._cache
