"""Detecção de monitores e tela cheia."""

from __future__ import annotations

from typing import Any, List, Optional

# Importações opcionais (permitem mock em testes)
try:
    from PySide6.QtWidgets import QApplication
except Exception:  # pragma: no cover
    QApplication = None  # type: ignore

try:
    from PySide6.QtGui import QGuiApplication
except Exception:  # pragma: no cover
    QGuiApplication = None  # type: ignore

try:
    import win32gui
except Exception:  # pragma: no cover
    win32gui = None  # type: ignore

try:
    import win32con
except Exception:  # pragma: no cover
    win32con = None  # type: ignore


def get_monitors(app: Any = None) -> List[Any]:
    """Retorna lista de QScreen (monitores). Best-effort, nunca lança."""
    if app is None:
        if QApplication is not None:
            try:
                app = QApplication.instance()
            except Exception:
                app = None
        if app is None and QGuiApplication is not None:
            try:
                app = QGuiApplication.instance()
            except Exception:
                app = None
    if app is None:
        return []
    try:
        screens = app.screens()
        return list(screens) if screens is not None else []
    except Exception:
        try:
            return list(app.screens())
        except Exception:
            return []


def _primary_screen_size() -> tuple[int, int]:
    try:
        import ctypes

        user32 = ctypes.windll.user32
        return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))
    except Exception:
        return 0, 0


def is_fullscreen_active() -> bool:
    """Best-effort: detecta se a janela em primeiro plano está em tela cheia."""
    if win32gui is None:
        # fallback ctypes
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            sw = user32.GetSystemMetrics(0)
            sh = user32.GetSystemMetrics(1)
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            # também considera posição (0,0)
            if rect.left <= 0 and rect.top <= 0 and width >= sw and height >= sh:
                return True
            return False
        except Exception:
            return False
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return False
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        sw, sh = _primary_screen_size()
        # janela maximizada/tela cheia
        if sw > 0 and sh > 0 and width >= sw and height >= sh:
            # excluir desktop/shell
            try:
                if win32gui.GetClassName(hwnd) in (
                    "Progman",
                    "WorkerW",
                    "Shell_TrayWnd",
                ):
                    return False
            except Exception:
                pass
            return True
        return False
    except Exception:
        return False


def monitor_count() -> int:
    return len(get_monitors())


__all__ = [
    "get_monitors",
    "is_fullscreen_active",
    "monitor_count",
    "QApplication",
    "QGuiApplication",
]
