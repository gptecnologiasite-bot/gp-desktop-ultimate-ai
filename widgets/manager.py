"""Gerenciador de widgets com persistência via Supabase."""

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

from .base import BaseWidget
from .system_widget import SystemWidget


def _resolve_db(db):
    return db


class WidgetManager(QObject):
    widgets_changed = pyqtSignal(list) if _HAS_QT else pyqtSignal(list)
    error_occurred = pyqtSignal(str) if _HAS_QT else pyqtSignal(str)

    def __init__(self, db=None, user_id: Optional[str] = None):
        if _HAS_QT:
            super().__init__()
        else:
            self._signal_store = {}
        self._db = _resolve_db(db)
        self._user_id = user_id
        self._widgets: Dict[str, Any] = {}
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
            self.widgets_changed.emit(list(self._widgets.values()))
        except Exception:
            pass

    def _row_to_widget(self, row: Any) -> Optional[Any]:
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
            if not isinstance(obj, dict):
                return None
            wtype = obj.get("type", "base")
            cls = SystemWidget if wtype == "system" else BaseWidget
            w = cls.from_config(obj)
            if rid is not None:
                w.id = str(rid)
            return w
        except Exception:
            return None

    def load(self) -> List[Any]:
        widgets: List[Any] = []
        if self._db is not None:
            try:
                res = self._db.select("widgets")
                rows = getattr(res, "data", res)
                if not isinstance(rows, list):
                    rows = list(rows) if rows is not None else []
                for row in rows:
                    w = self._row_to_widget(row)
                    if w is not None:
                        self._widgets[w.id] = w
                        widgets.append(w)
            except Exception as exc:
                self._emit_error(str(exc))
        self._emit_changed()
        return list(self._widgets.values())

    def add(self, widget: Any = None, **kwargs) -> Any:
        if widget is None:
            wtype = kwargs.pop("type", kwargs.pop("widget_type", "base"))
            if wtype == "system":
                w = SystemWidget(**kwargs)
            else:
                w = BaseWidget(**kwargs)
        elif isinstance(widget, dict):
            wtype = widget.get("type", "base")
            cls = SystemWidget if wtype == "system" else BaseWidget
            w = cls.from_config(widget)
        else:
            w = widget
        if not getattr(w, "id", None):
            w.id = str(uuid.uuid4())
        # garante atributos de geometria
        for attr, default in (("x", 0), ("y", 0), ("width", 200), ("height", 120)):
            if not hasattr(w, attr):
                setattr(w, attr, default)
        self._widgets[w.id] = w
        self._emit_changed()
        return w

    def remove(self, widget_or_id: Any) -> bool:
        wid = getattr(widget_or_id, "id", widget_or_id)
        wid = str(wid)
        existed = wid in self._widgets
        self._widgets.pop(wid, None)
        if self._db is not None:
            try:
                self._db.delete("widgets", filters={"id": wid})
            except Exception as exc:
                self._emit_error(str(exc))
        self._emit_changed()
        return existed or True

    def list(self) -> List[Any]:
        return list(self._widgets.values())

    def position(self, widget_or_id: Any, x: int, y: int) -> Any:
        w = self._resolve(widget_or_id)
        if w is None:
            return None
        w.x = int(x)
        w.y = int(y)
        if hasattr(w, "move"):
            try:
                w.move(w.x, w.y)
            except Exception:
                pass
        self._emit_changed()
        return w

    def size(self, widget_or_id: Any, width: int, height: int) -> Any:
        w = self._resolve(widget_or_id)
        if w is None:
            return None
        w.width = int(width)
        w.height = int(height)
        if hasattr(w, "resize"):
            try:
                w.resize(w.width, w.height)
            except Exception:
                pass
        self._emit_changed()
        return w

    def persist(self) -> bool:
        if self._db is None:
            return True
        ok = True
        for w in list(self._widgets.values()):
            try:
                payload = {
                    "id": w.id,
                    "name": getattr(w, "title", "Widget") or "Widget",
                    "config": json.dumps(w.to_config(), ensure_ascii=False),
                }
                if self._user_id:
                    payload["user_id"] = self._user_id
                self._db.upsert("widgets", payload, on_conflict="id")
            except Exception as exc:
                ok = False
                self._emit_error(str(exc))
        return ok

    def save(self, widget: Any = None) -> bool:
        if widget is not None:
            self.add(widget)
        return self.persist()

    def _resolve(self, widget_or_id: Any) -> Optional[Any]:
        if isinstance(widget_or_id, str):
            return self._widgets.get(widget_or_id)
        wid = getattr(widget_or_id, "id", None)
        if wid is not None:
            if wid in self._widgets:
                return self._widgets[wid]
            return widget_or_id
        # busca por identidade
        for w in self._widgets.values():
            if w is widget_or_id:
                return w
        return widget_or_id if hasattr(widget_or_id, "id") else None

    @property
    def widgets(self) -> Dict[str, Any]:
        return self._widgets
