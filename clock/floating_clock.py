"""Relógio flutuante (frameless, always on top, arrastável)."""

from __future__ import annotations

import datetime as _dt
from typing import Any, Optional

try:
    from PySide6.QtCore import Qt, QTimer, QPoint  # type: ignore
    from PySide6.QtGui import QFont, QColor  # type: ignore
    from PySide6.QtWidgets import (  # type: ignore
        QApplication,
        QWidget,
        QLabel,
        QVBoxLayout,
        QHBoxLayout,
    )

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

    class QLabel:  # type: ignore
        def __init__(self, *a, **k):
            pass

    class QVBoxLayout:  # type: ignore
        def __init__(self, *a, **k):
            pass

        def addWidget(self, *a, **k):
            pass

        def setContentsMargins(self, *a, **k):
            pass

        def setSpacing(self, *a, **k):
            pass

    class QHBoxLayout:  # type: ignore
        pass

    class QTimer:  # type: ignore
        def __init__(self, *a, **k):
            self._cb = None

        def setInterval(self, ms):
            pass

        def timeout(self):
            class S:
                def connect(self, cb):
                    self._cb = cb

            return S()

        def start(self):
            pass

        def stop(self):
            pass

    class QPoint:  # type: ignore
        def __init__(self, *a, **k):
            pass

    class QFont:  # type: ignore
        pass

    class QColor:  # type: ignore
        pass

    class Qt:  # type: ignore
        FramelessWindowHint = 0
        WindowStaysOnTopHint = 0
        Tool = 0
        WA_TranslucentBackground = 0
        LeftButton = 1


from .models import ClockConfig


class FloatingClock(QWidget if _HAS_QT else object):
    def __init__(self, config: Any = None, parent=None):
        if _HAS_QT:
            if QApplication.instance() is None:
                try:
                    QApplication([])
                except Exception:
                    pass
            super().__init__(parent)
        self.config = (
            config
            if isinstance(config, ClockConfig)
            else ClockConfig.from_dict(config or {})
        )
        self._drag_offset = None
        if _HAS_QT:
            self._build_ui()
            self.apply_config(self.config)
            self._timer = QTimer(self)
            self._timer.setInterval(1000 if not self.config.show_seconds else 1000)
            self._timer.timeout.connect(self._tick)
            self._timer.start()
            self._tick()

    def _build_ui(self):
        if not _HAS_QT:
            return
        self.setWindowTitle("FloatingClock")
        self.label_time = QLabel(self)
        self.label_date = QLabel(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        layout.addWidget(self.label_time)
        layout.addWidget(self.label_date)
        self.label_date.setAlignment(Qt.AlignCenter)
        self.label_time.setAlignment(Qt.AlignCenter)

    def apply_config(self, config: Any = None):
        if config is not None:
            self.config = (
                config
                if isinstance(config, ClockConfig)
                else ClockConfig.from_dict(config or {})
            )
        cfg = self.config
        if not _HAS_QT:
            return
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(cfg.width, cfg.height)
        self.move(cfg.x, cfg.y)
        font = QFont(cfg.font_family, cfg.font_size)
        self.label_time.setFont(font)
        self.label_time.setStyleSheet(f"color: {cfg.color};")
        date_font = QFont(cfg.font_family, max(8, cfg.font_size // 2))
        self.label_date.setFont(date_font)
        self.label_date.setStyleSheet(f"color: {cfg.color};")
        self.label_date.setVisible(cfg.show_date)
        self.setWindowOpacity(cfg.transparency)
        if cfg.always_on_top:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.update()

    def _tick(self):
        if not _HAS_QT:
            return
        cfg = self.config
        now = _dt.datetime.now()
        if getattr(cfg, "format_12_24", False):
            fmt = "%I:%M" + (":%S" if cfg.show_seconds else "") + " %p"
        else:
            fmt = "%H:%M" + (":%S" if cfg.show_seconds else "")
        self.label_time.setText(now.strftime(fmt))
        if cfg.show_date:
            self.label_date.setText(now.strftime("%d/%m/%Y"))

    def mousePressEvent(self, event):
        if _HAS_QT and event.button() == Qt.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if _HAS_QT and self._drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            self.config.x = self.x()
            self.config.y = self.y()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)
