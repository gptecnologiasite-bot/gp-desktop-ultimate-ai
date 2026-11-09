"""Gerenciador de relógios com persistência via Supabase."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

try:
    from PySide6.QtCore import QObject, Signal as _QtSignal  # type: ignore

    _HAS_QT = True
except Exception:  # pragma: no cover
    _HAS_QT = False

    class QObject:  # type: ignore
        pass

    class _SignalShim:
        def __init__(self):
            self._slots = []

        def connect(self, slot):
            self._slots.append(slot)

        def disconnect(self, slot=None):
            if slot is None:
                self._slots.clear()
            else:
                self._slots = [s for s in self._slots if s != slot]

        def emit(self, *a, **k):
            for s in list(self._slots):
                try:
                    s(*a, **k)
                except Exception:
                    pass

    class _SignalDescriptor:
        def __init__(self, *a, **k):
            pass

        def __set_name__(self, owner, name):
            self._name = name

        def __get__(self, obj, owner=None):
            if obj is None:
                return self
            store = obj.__dict__.setdefault("_signal_store", {})
            if self._name not in store:
                store[self._name] = _SignalShim()
            return store[self._name]

    def _QtSignal(*a, **k):  # type: ignore
        return _SignalDescriptor()

    pyqtSignal = _QtSignal

if _HAS_QT:
    from PySide6.QtCore import Signal as pyqtSignal  # type: ignore

from .models import ClockConfig


def _resolve_db(db):
    return db


class ClockManager(QObject):
    clocks_changed = pyqtSignal(list) if _HAS_QT else pyqtSignal(list)
    error_occurred = pyqtSignal(str) if _HAS_QT else pyqtSignal(str)

    def __init__(self, db=None, user_id: Optional[str] = None):
        if _HAS_QT:
            super().__init__()
        else:
            self._signal_store = {}
        self._db = _resolve_db(db)
        self._user_id = user_id
        self._clocks: Dict[str, ClockConfig] = {}
        try:
            self.load()
        except Exception as exc:
            self._emit_error(str(exc))

    def _emit_error(self, msg: str) -> None:
        try:
            self.error_occurred.emit(msg)
        except Exception:
            pass

    def _emit_changed(self) -> None:
        try:
            self.clocks_changed.emit(list(self._clocks.values()))
        except Exception:
            pass

    def _row_to_config(self, row: Any) -> Optional[ClockConfig]:
        try:
            if isinstance(row, dict):
                rid = row.get("id")
                data = row.get("config", row.get("data"))
            else:
                rid = getattr(row, "id", None)
                data = getattr(row, "config", None) or getattr(row, "data", None)
            if isinstance(data, str):
                obj = json.loads(data)
            elif isinstance(data, dict):
                obj = data
            else:
                obj = row if isinstance(row, dict) else None
            if obj is None:
                return None
            cfg = ClockConfig.from_dict(obj)
            if rid is not None:
                cfg.id = str(rid)
            return cfg
        except Exception:
            return None

    def load(self) -> List[ClockConfig]:
        configs: List[ClockConfig] = []
        if self._db is not None:
            try:
                res = self._db.select("clocks")
                rows = getattr(res, "data", res)
                if not isinstance(rows, list):
                    rows = list(rows) if rows is not None else []
                for row in rows:
                    cfg = self._row_to_config(row)
                    if cfg is not None:
                        self._clocks[cfg.id] = cfg
                        configs.append(cfg)
            except Exception as exc:
                self._emit_error(str(exc))
        self._emit_changed()
        return list(self._clocks.values())

    def save(self, config: Any) -> bool:
        return self.save_clock(config)

    def save_clock(self, config: Any) -> bool:
        if isinstance(config, dict):
            config = ClockConfig.from_dict(config)
        if not isinstance(config, ClockConfig):
            return False
        if not config.id:
            config.id = str(uuid.uuid4())
        self._clocks[config.id] = config
        if self._db is not None:
            try:
                payload = {
                    "id": config.id,
                    "name": config.name or "Relógio",
                    "config": json.dumps(config.to_dict(), ensure_ascii=False),
                }
                if self._user_id:
                    payload["user_id"] = self._user_id
                self._db.upsert("clocks", payload, on_conflict="id")
            except Exception as exc:
                self._emit_error(str(exc))
        self._emit_changed()
        return True

    def create(self, config: Any = None, **kwargs) -> ClockConfig:
        if config is None:
            config = ClockConfig(**kwargs)
        elif isinstance(config, dict):
            config = ClockConfig.from_dict(config)
            if kwargs:
                data = config.to_dict()
                data.update(kwargs)
                config = ClockConfig.from_dict(data)
        if not config.id:
            config.id = str(uuid.uuid4())
        self.save_clock(config)
        return config

    def update(self, clock_id: str, config: Any = None, **kwargs) -> ClockConfig:
        existing = self._clocks.get(str(clock_id))
        if config is None:
            data = existing.to_dict() if existing else {"id": clock_id}
            data.update(kwargs)
            data["id"] = str(clock_id)
            config = ClockConfig.from_dict(data)
        elif isinstance(config, dict):
            data = dict(config)
            data["id"] = str(clock_id)
            data.update(kwargs)
            config = ClockConfig.from_dict(data)
        else:
            config.id = str(clock_id)
            if kwargs:
                data = config.to_dict()
                data.update(kwargs)
                data["id"] = str(clock_id)
                config = ClockConfig.from_dict(data)
        self.save_clock(config)
        return config

    def remove(self, clock_id: Any) -> bool:
        cid = getattr(clock_id, "id", clock_id)
        cid = str(cid)
        existed = cid in self._clocks
        self._clocks.pop(cid, None)
        if self._db is not None:
            try:
                self._db.delete("clocks", filters={"id": cid})
            except Exception as exc:
                self._emit_error(str(exc))
        self._emit_changed()
        return existed or True

    def list(self) -> List[ClockConfig]:
        return list(self._clocks.values())

    list_clocks = list

    @property
    def clocks(self) -> Dict[str, ClockConfig]:
        return self._clocks
