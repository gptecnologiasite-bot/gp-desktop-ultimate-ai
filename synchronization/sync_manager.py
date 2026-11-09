"""Gerenciador de sincronização (push/pull) via Supabase.

Sincroniza personalizações, temas e configs. Mantém fila offline em memória
que é drenada ao reconectar. Sem banco local.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional


def _resolve_db(db=None, database=None, client=None):
    if db is not None:
        return db
    if database is not None:
        return database
    try:
        from supabase import DatabaseManager

        return DatabaseManager(client)
    except Exception:
        return None


def _resolve_realtime(realtime=None, client=None):
    if realtime is not None:
        return realtime
    try:
        from supabase import RealtimeManager

        return RealtimeManager(client)
    except Exception:
        return None


_CATEGORY_ALIASES = {
    "personalization": "personalizations",
    "personalizations": "personalizations",
    "customization": "personalizations",
    "customizations": "personalizations",
    "theme": "themes",
    "themes": "themes",
    "config": "settings",
    "configs": "settings",
    "configuration": "settings",
    "configurations": "settings",
    "setting": "settings",
    "settings": "settings",
}

_TABLE_MAP = {
    "personalizations": "personalizations",
    "themes": "themes",
    "settings": "settings",
}


class SyncManager:
    def __init__(
        self,
        client=None,
        db=None,
        database=None,
        realtime=None,
        user_id: Optional[str] = None,
        online: bool = True,
    ):
        self._client = client
        self._db = _resolve_db(db, database, client)
        self._realtime = _resolve_realtime(realtime, client)
        self._user_id = user_id
        self._online = bool(online)
        self._status = "online" if self._online else "offline"
        self._queue: List[Dict[str, Any]] = []
        self._channel = None
        self._callbacks: List[Callable[[Any], None]] = []

    # ---------- status ----------
    @property
    def status(self) -> str:
        return self._status

    @property
    def online(self) -> bool:
        return self._online

    @property
    def is_online(self) -> bool:
        return self._online

    @property
    def queue(self) -> List[Dict[str, Any]]:
        return list(self._queue)

    @property
    def pending(self) -> List[Dict[str, Any]]:
        return list(self._queue)

    def set_online(self, value: bool) -> None:
        self._online = bool(value)
        self._status = "online" if self._online else "offline"
        if self._online:
            self.drain_queue()

    def set_status(self, value: str) -> None:
        self._status = value

    # ---------- helpers ----------
    def _normalize(self, category: Any) -> str:
        key = str(category).strip().lower()
        return _CATEGORY_ALIASES.get(key, key)

    def _table(self, category: str) -> str:
        cat = self._normalize(category)
        return _TABLE_MAP.get(cat, cat)

    def _user_filter(self) -> Optional[Dict[str, Any]]:
        if self._user_id:
            return {"user_id": self._user_id}
        return None

    def _merge(
        self, extra: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        f = self._user_filter()
        if extra:
            f = dict(f or {})
            f.update(extra)
        return f

    def _push_now(self, category: str, data: Any, **kwargs: Any) -> Any:
        cat = self._normalize(category)
        table = _TABLE_MAP.get(cat, cat)
        if self._db is None:
            return True

        if cat == "personalizations":
            name = kwargs.get("name")
            if isinstance(data, dict):
                name = name or data.get("name")
            payload: Dict[str, Any] = {
                "name": name,
                "data": json.dumps(data, ensure_ascii=False, default=str),
            }
            if self._user_id:
                payload["user_id"] = self._user_id
            return self._db.upsert(
                table,
                payload,
                on_conflict="name" if not self._user_id else "user_id,name",
            )

        if cat == "themes":
            name = kwargs.get("name")
            if isinstance(data, dict):
                name = name or data.get("name") or data.get("theme_name")
            payload = {
                "name": name,
                "data": json.dumps(data, ensure_ascii=False, default=str),
            }
            if self._user_id:
                payload["user_id"] = self._user_id
            # themes table may have columns; store in data jsonb if possible
            try:
                return self._db.upsert(
                    table,
                    payload,
                    on_conflict="name" if not self._user_id else "user_id,name",
                )
            except Exception:
                return self._db.insert(table, payload)

        # settings/configs: data pode ser dict key->value ou {"key":..., "value":...}
        if cat == "settings":
            if isinstance(data, dict) and "key" in data and "value" in data:
                items = [(data["key"], data["value"])]
            elif isinstance(data, dict):
                items = list(data.items())
            else:
                items = [(kwargs.get("key", "config"), data)]
            results = []
            for key, value in items:
                payload = {"key": str(key), "value": value}
                if self._user_id:
                    payload["user_id"] = self._user_id
                try:
                    r = self._db.upsert(
                        table,
                        payload,
                        on_conflict="user_id,key" if self._user_id else "key",
                    )
                except Exception:
                    r = self._db.upsert(table, payload)
                results.append(r)
            return results if len(results) > 1 else (results[0] if results else True)

        # genérico
        payload = data if isinstance(data, dict) else {"data": data}
        if self._user_id and isinstance(payload, dict):
            payload.setdefault("user_id", self._user_id)
        try:
            return self._db.upsert(table, payload)
        except Exception:
            return self._db.insert(table, payload)

    def _pull_now(self, category: str, **kwargs: Any) -> Any:
        cat = self._normalize(category)
        table = _TABLE_MAP.get(cat, cat)
        if self._db is None:
            return []
        filters = self._merge(kwargs.get("filters"))
        # por chave
        if kwargs.get("key") is not None:
            filters = self._merge({"key": kwargs["key"]})
        res = self._db.select(table, filters=filters)
        rows = getattr(res, "data", res)
        if not isinstance(rows, list):
            rows = list(rows) if rows is not None else []
        return rows

    # ---------- API pública ----------
    def push(self, category: Any, data: Any = None, **kwargs: Any) -> Any:
        cat = self._normalize(category)
        if not self._online:
            self._queue.append(
                {"op": "push", "category": cat, "data": data, "kwargs": kwargs}
            )
            return False
        self._status = "syncing"
        try:
            result = self._push_now(cat, data, **kwargs)
            self._status = "online"
            return result
        except Exception:
            self._queue.append(
                {"op": "push", "category": cat, "data": data, "kwargs": kwargs}
            )
            self._online = False
            self._status = "offline"
            return False

    # aliases específicos
    def push_personalization(self, data: Any, **kwargs: Any) -> Any:
        return self.push("personalizations", data, **kwargs)

    def push_personalizations(self, data: Any, **kwargs: Any) -> Any:
        return self.push("personalizations", data, **kwargs)

    def push_theme(self, data: Any, **kwargs: Any) -> Any:
        return self.push("themes", data, **kwargs)

    def push_themes(self, data: Any, **kwargs: Any) -> Any:
        return self.push("themes", data, **kwargs)

    def push_config(self, data: Any, **kwargs: Any) -> Any:
        return self.push("settings", data, **kwargs)

    def push_configs(self, data: Any, **kwargs: Any) -> Any:
        return self.push("settings", data, **kwargs)

    def push_settings(self, data: Any, **kwargs: Any) -> Any:
        return self.push("settings", data, **kwargs)

    def pull(self, category: Any, **kwargs: Any) -> Any:
        cat = self._normalize(category)
        if not self._online:
            self._queue.append({"op": "pull", "category": cat, "kwargs": kwargs})
            return None
        self._status = "syncing"
        try:
            result = self._pull_now(cat, **kwargs)
            self._status = "online"
            return result
        except Exception:
            self._online = False
            self._status = "offline"
            return None

    def pull_personalizations(self, **kwargs: Any) -> Any:
        return self.pull("personalizations", **kwargs)

    def pull_themes(self, **kwargs: Any) -> Any:
        return self.pull("themes", **kwargs)

    def pull_configs(self, **kwargs: Any) -> Any:
        return self.pull("settings", **kwargs)

    def pull_settings(self, **kwargs: Any) -> Any:
        return self.pull("settings", **kwargs)

    def drain_queue(self) -> None:
        if not self._online:
            return
        pending = list(self._queue)
        self._queue.clear()
        for op in pending:
            try:
                self._status = "syncing"
                if op.get("op") == "push":
                    self._push_now(
                        op["category"], op.get("data"), **op.get("kwargs", {})
                    )
                elif op.get("op") == "pull":
                    self._pull_now(op["category"], **op.get("kwargs", {}))
                self._status = "online"
            except Exception:
                self._queue.append(op)
                self._online = False
                self._status = "offline"
                break

    def sync_all(self) -> Dict[str, Any]:
        self.drain_queue()
        result: Dict[str, Any] = {}
        for cat in ("personalizations", "themes", "settings"):
            try:
                result[cat] = self.pull(cat)
            except Exception:
                result[cat] = None
        return result

    # ---------- realtime ----------
    def subscribe(
        self,
        callback: Optional[Callable[[Any], None]] = None,
        channel: str = "sync",
        table: Optional[str] = None,
        event: str = "*",
    ) -> Any:
        cb = callback if callback is not None else self._on_remote_change
        if cb not in self._callbacks:
            self._callbacks.append(cb)
        ch = None
        if self._realtime is not None:
            try:
                ch = self._realtime.subscribe(channel, cb, table=table, event=event)
            except Exception:
                try:
                    ch = self._realtime.subscribe(channel, cb)
                except Exception:
                    ch = None
        self._channel = ch
        return ch

    def subscribe_realtime(self, *args: Any, **kwargs: Any) -> Any:
        return self.subscribe(*args, **kwargs)

    def unsubscribe(self, channel: Optional[str] = None) -> bool:
        if self._realtime is not None and self._channel is not None:
            try:
                self._realtime.unsubscribe(channel or "sync")
            except Exception:
                pass
        self._channel = None
        return True

    def _on_remote_change(self, payload: Any) -> None:
        for cb in list(self._callbacks):
            if cb is not self._on_remote_change:
                try:
                    cb(payload)
                except Exception:
                    pass
        # drena notificações: pull best-effort
        try:
            self.pull("personalizations")
        except Exception:
            pass
