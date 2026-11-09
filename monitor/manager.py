"""Gerenciador de monitoramento com polling (QTimer)."""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, List, Optional

try:
    from PySide6.QtCore import QObject, QTimer, Signal as _QtSignal  # type: ignore

    _HAS_QT = True
except Exception:  # pragma: no cover - fallback
    _HAS_QT = False

    class QObject:  # type: ignore
        pass

    class QTimer:  # type: ignore
        def __init__(self, parent=None):
            self._interval = 1000
            self._callback = None
            self._running = False

        def setInterval(self, ms):
            self._interval = ms

        def timeout(self):
            class _Sig:
                def __init__(self, owner):
                    self._owner = owner

                def connect(self, cb):
                    self._cb = cb
                    self._owner._callback = cb

                def emit(self, *a, **k):
                    pass

            return _Sig(self)

        def start(self):
            self._running = True

        def stop(self):
            self._running = False

        def isActive(self):
            return self._running

    class _SignalShim:
        def __init__(self):
            self._slots: List[Callable] = []

        def connect(self, slot):
            self._slots.append(slot)

        def disconnect(self, slot=None):
            if slot is None:
                self._slots.clear()
            else:
                self._slots = [s for s in self._slots if s != slot]

        def emit(self, *args, **kwargs):
            for slot in list(self._slots):
                try:
                    slot(*args, **kwargs)
                except Exception:
                    pass

    class _SignalDescriptor:
        def __init__(self, *args, **kwargs):
            self._args = args
            self._kwargs = kwargs

        def __set_name__(self, owner, name):
            self._name = name

        def __get__(self, obj, owner=None):
            if obj is None:
                return self
            store = obj.__dict__.setdefault("_signal_store", {})
            if self._name not in store:
                store[self._name] = _SignalShim()
            return store[self._name]

    def _QtSignal(*args, **kwargs):  # type: ignore
        return _SignalDescriptor(*args, **kwargs)

    pyqtSignal = _QtSignal

if _HAS_QT:
    from PySide6.QtCore import Signal as pyqtSignal  # type: ignore


from .system_monitor import SystemMonitor


class MonitorManager(QObject):
    if _HAS_QT:
        data_updated = pyqtSignal(object)  # type: ignore
    else:
        data_updated = _SignalDescriptor(object)  # type: ignore

    def __init__(
        self,
        monitor: Optional[SystemMonitor] = None,
        interval_ms: int = 2000,
        parent=None,
    ):
        if _HAS_QT:
            super().__init__(parent)
        else:
            self._signal_store = {}
        self.monitor = monitor or SystemMonitor()
        self.interval_ms = interval_ms
        self._timer = None
        self._running = False
        self._thread = None
        self._callback = None

    def _emit(self, data):
        try:
            self.data_updated.emit(data)
        except Exception:
            pass

    def _poll(self):
        try:
            data = self.monitor.get_performance_summary()
        except Exception:
            data = {}
        self._emit(data)

    def start(self):
        if self._running:
            return
        self._running = True
        if _HAS_QT:
            self._timer = QTimer(self)
            self._timer.setInterval(self.interval_ms)
            self._timer.timeout.connect(self._poll)
            self._timer.start()
        else:

            def loop():
                while self._running:
                    self._poll()
                    time.sleep(self.interval_ms / 1000.0)

            self._thread = threading.Thread(target=loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if _HAS_QT and self._timer is not None:
            try:
                self._timer.stop()
            except Exception:
                pass
            self._timer = None
        self._thread = None

    def is_running(self) -> bool:
        return self._running

    def poll_once(self):
        self._poll()
