"""Widget base do GP Desktop Ultimate AI."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

try:
    from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout  # type: ignore
    from PySide6.QtCore import Qt, QTimer  # type: ignore

    _HAS_QT = True
except Exception:  # pragma: no cover
    _HAS_QT = False

    class QApplication:  # type: ignore
        @staticmethod
        def instance():
            return None

    class QWidget:  # type: ignore
        def __init__(self, *a, **k):
            pass

        def setWindowTitle(self, *a, **k):
            pass

        def resize(self, *a, **k):
            pass

        def move(self, *a, **k):
            pass

    class QLabel:  # type: ignore
        def __init__(self, *a, **k):
            pass

        def setText(self, *a, **k):
            pass

    class QVBoxLayout:  # type: ignore
        def __init__(self, *a, **k):
            pass

        def addWidget(self, *a, **k):
            pass

        def setContentsMargins(self, *a, **k):
            pass

    class Qt:  # type: ignore
        AlignCenter = 0

    class QTimer:  # type: ignore
        def __init__(self, *a, **k):
            pass


class BaseWidget(QWidget if _HAS_QT else object):
    widget_type = "base"

    def __init__(
        self,
        id: str = "",
        title: str = "Widget",
        config: Optional[Dict[str, Any]] = None,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 120,
        parent=None,
        **kwargs,
    ):
        if _HAS_QT:
            if QApplication.instance() is None:
                try:
                    QApplication([])
                except Exception:
                    pass
            super().__init__(parent)
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.config = dict(config or {})
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        # aceita kwargs extras
        for k, v in kwargs.items():
            setattr(self, k, v)
        if _HAS_QT:
            self.setWindowTitle(self.title)
            self.resize(self.width, self.height)
            self.move(self.x, self.y)

    def refresh(self) -> None:
        """Atualiza o conteúdo do widget. Subclasses sobrescrevem."""
        return None

    def to_config(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.widget_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "config": dict(self.config),
        }

    @classmethod
    def from_config(cls, data: Optional[Dict[str, Any]] = None) -> "BaseWidget":
        if not data:
            return cls()
        data = dict(data)
        cfg = data.pop("config", {}) if isinstance(data.get("config"), dict) else {}
        if "config" in data and not isinstance(data["config"], dict):
            cfg = {}
        return cls(
            id=data.get("id", ""),
            title=data.get("title", "Widget"),
            config=cfg,
            x=data.get("x", 0),
            y=data.get("y", 0),
            width=data.get("width", 200),
            height=data.get("height", 120),
        )
