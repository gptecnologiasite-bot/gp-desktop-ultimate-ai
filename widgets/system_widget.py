"""Widget de sistema (CPU/RAM)."""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout  # type: ignore
    from PySide6.QtCore import Qt  # type: ignore

    _HAS_QT = True
except Exception:  # pragma: no cover
    _HAS_QT = False

    class QLabel:  # type: ignore
        def __init__(self, *a, **k):
            pass

        def setText(self, *a, **k):
            pass

        def setAlignment(self, *a, **k):
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


try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None

from .base import BaseWidget


class SystemWidget(BaseWidget):
    widget_type = "system"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = self.title or "Sistema"
        if _HAS_QT:
            self._label = QLabel(self)
            self._label.setAlignment(Qt.AlignCenter)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.addWidget(self._label)
        else:
            self._label = None
        self.refresh()

    def _metrics(self) -> Dict[str, Any]:
        cpu = 0.0
        ram_percent = 0.0
        ram_used = 0
        ram_total = 0
        try:
            if psutil is not None:
                cpu = float(psutil.cpu_percent(interval=None))
                vm = psutil.virtual_memory()
                ram_percent = float(vm.percent)
                ram_used = int(vm.used)
                ram_total = int(vm.total)
        except Exception:
            pass
        return {
            "cpu_percent": cpu,
            "ram_percent": ram_percent,
            "ram_used": ram_used,
            "ram_total": ram_total,
        }

    def refresh(self) -> None:
        m = self._metrics()
        text = (
            f"CPU: {m['cpu_percent']:.1f}%\n"
            f"RAM: {m['ram_percent']:.1f}% "
            f"({m['ram_used']}/{m['ram_total']})"
        )
        self.config.update(m)
        if _HAS_QT and self._label is not None:
            try:
                self._label.setText(text)
            except Exception:
                pass
        return m
