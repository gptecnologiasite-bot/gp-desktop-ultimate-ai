"""Gerenciador de temas: aplicação, cores customizadas, persistência Supabase."""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, List, Optional

try:  # PySide6 opcional (ambientes de teste podem não tê-lo)
    from PySide6.QtCore import QObject, Signal  # type: ignore
    from PySide6.QtGui import QPalette, QColor  # type: ignore

    _QT = True
except Exception:  # pragma: no cover - depende do ambiente
    _QT = False
    QObject = object  # type: ignore
    Signal = None  # type: ignore
    QPalette = None  # type: ignore
    QColor = None  # type: ignore

from .theme_definitions import THEMES, get_theme, is_valid_theme
from .stylesheet import build_qss


class _Signal:
    """Sinal leve (fallback quando Qt não está disponível)."""

    def __init__(self) -> None:
        self._callbacks: List[Callable[..., None]] = []

    def connect(self, callback: Callable[..., None]) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def disconnect(self, callback: Callable[..., None]) -> None:
        try:
            self._callbacks.remove(callback)
        except ValueError:
            pass

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for cb in list(self._callbacks):
            try:
                cb(*args, **kwargs)
            except Exception:
                pass


class ThemeManager(QObject if _QT else object):  # type: ignore[misc]
    if _QT and Signal is not None:
        theme_changed = Signal(object)  # type: ignore[valid-type]

    def __init__(
        self,
        app: Any = None,
        db_manager: Any = None,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if _QT:
            super().__init__()
        self.app = app
        self.db_manager = db_manager
        self.user_id = user_id
        self._lock = threading.RLock()
        if not _QT:
            self.theme_changed = _Signal()  # type: ignore[assignment]
        self.current_theme: Dict[str, Any] = dict(THEMES["claro"])
        self.custom_colors: Dict[str, str] = {}
        self.current_name: str = "claro"

    # ------------------------------------------------------------------ #
    # Resolução
    # ------------------------------------------------------------------ #
    def _resolve(self, theme: Any) -> Dict[str, Any]:
        if theme is None:
            return dict(self.current_theme)
        if isinstance(theme, str):
            t = get_theme(theme)
            self.current_name = theme.strip().lower()
            return t
        if isinstance(theme, dict):
            if is_valid_theme(theme):
                merged = dict(self.current_theme)
                merged.update(
                    {k: theme[k] for k in theme if k in self.current_theme or True}
                )
                # mantém apenas chaves de cor conhecidas quando possível
                return merged
            return dict(theme)
        colors = getattr(theme, "colors", None) or getattr(theme, "palette", None)
        if isinstance(colors, dict):
            return self._resolve(colors)
        return dict(self.current_theme)

    def _merge_custom(self, base: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(base)
        result.update(self.custom_colors)
        return result

    # ------------------------------------------------------------------ #
    # Aplicação
    # ------------------------------------------------------------------ #
    def apply_theme(self, app: Any = None, theme: Any = None) -> Dict[str, Any]:
        target_app = app if app is not None else self.app
        resolved = (
            self._resolve(theme) if theme is not None else dict(self.current_theme)
        )
        resolved = self._merge_custom(resolved)
        self.current_theme = resolved
        qss = build_qss(resolved)
        if target_app is not None:
            try:
                if hasattr(target_app, "setStyleSheet"):
                    target_app.setStyleSheet(qss)
            except Exception:
                pass
            # (QPalette vazio removido - evita sobrescrever estilos)
        try:
            self.theme_changed.emit(resolved)
        except Exception:
            pass
        return resolved

    def set_custom_colors(self, colors: Any = None, **kwargs: Any) -> Dict[str, Any]:
        """Define cores personalizadas (dict ou kwargs)."""
        with self._lock:
            if isinstance(colors, dict):
                self.custom_colors.update(colors)
            self.custom_colors.update(
                {k: v for k, v in kwargs.items() if v is not None}
            )
            # aplica se houver app
            return self.apply_theme(self.app, None)

    def get_current_theme(self) -> Dict[str, Any]:
        return dict(self.current_theme)

    def get_colors(self) -> Dict[str, Any]:
        return dict(self.current_theme)

    # ------------------------------------------------------------------ #
    # Persistência Supabase
    # ------------------------------------------------------------------ #
    def _db(self, db_manager: Any = None) -> Any:
        if db_manager is not None:
            return db_manager
        if self.db_manager is not None:
            return self.db_manager
        try:
            from supabase.database import DatabaseManager

            return DatabaseManager()
        except Exception:
            return None

    def save_theme(
        self,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        theme: Any = None,
        db_manager: Any = None,
        **kwargs: Any,
    ) -> Any:
        uid = user_id if user_id is not None else self.user_id
        db = self._db(db_manager)
        data_theme = (
            self._resolve(theme) if theme is not None else dict(self.current_theme)
        )
        data_theme = self._merge_custom(data_theme)
        payload = {
            "user_id": uid,
            "name": name or self.current_name or "custom",
            "config": data_theme,
        }
        if db is None:
            return payload
        try:
            return db.upsert("themes", payload)
        except Exception:
            try:
                return db.insert("themes", payload)
            except Exception:
                return None

    # aliases
    def save(self, *a, **k):
        return self.save_theme(*a, **k)

    def save_to_supabase(self, *a, **k):
        return self.save_theme(*a, **k)

    def load_theme(
        self,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        db_manager: Any = None,
        theme_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        uid = user_id if user_id is not None else self.user_id
        db = self._db(db_manager)
        if db is None:
            return None
        filters = {}
        if uid is not None:
            filters["user_id"] = uid
        try:
            res = db.select("themes", filters=filters or None)
        except Exception:
            return None
        data = getattr(res, "data", None)
        if not data:
            try:
                data = res.get("data") if isinstance(res, dict) else None
            except Exception:
                data = None
        if not data:
            return None
        # escolhe por nome se fornecido
        target = theme_name or name or kwargs.get("name")
        chosen = None
        for row in data:
            if target and row.get("name") == target:
                chosen = row
                break
        if chosen is None:
            chosen = data[-1]
        config = chosen.get("config") if isinstance(chosen, dict) else None
        if isinstance(config, dict):
            self.current_name = chosen.get("name", self.current_name)
            self.current_theme = self._merge_custom(config)
            self.apply_theme(self.app, None)
        return chosen

    def load(self, *a, **k):
        return self.load_theme(*a, **k)

    def load_from_supabase(self, *a, **k):
        return self.load_theme(*a, **k)
