"""IntegraÃ§Ã£o real com a Ã¡rea de trabalho do Windows para wallpapers.

Suporta imagem estÃ¡tica (JPG/PNG/WEBP) via ``SystemParametersInfoW`` e
wallpapers animados (GIF/vÃ­deo) via ``WorkerW``/``SetParent`` (best-effort).
"""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from typing import Any, Optional

SPI_GETDESKWALLPAPER = 0x0073
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

_CREATE_WORKERW_MSG = 0x052C

_original_wallpaper: Optional[str] = None
_animated_widget: Any = None
_animated_refs: dict = {}


def _user32():
    return ctypes.windll.user32


def get_current_wallpaper() -> str:
    """Retorna o caminho do wallpaper atual do Windows."""
    buf = ctypes.create_unicode_buffer(1024)
    try:
        _user32().SystemParametersInfoW(SPI_GETDESKWALLPAPER, len(buf), buf, 0)
    except Exception:
        return ""
    return buf.value or ""


def set_wallpaper_image(path: str) -> bool:
    """Define uma imagem como wallpaper do Windows."""
    global _original_wallpaper
    if _original_wallpaper is None:
        try:
            _original_wallpaper = get_current_wallpaper()
        except Exception:
            _original_wallpaper = ""
    try:
        full = os.path.abspath(path)
        res = _user32().SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, full, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        return bool(res)
    except Exception:
        return False


def restore_original() -> bool:
    """Restaura o wallpaper original capturado anteriormente."""
    global _original_wallpaper
    target = _original_wallpaper
    if not target:
        return False
    try:
        res = _user32().SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, target, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        _original_wallpaper = None
        return bool(res)
    except Exception:
        return False


def _find_workerw() -> int:
    """Tenta localizar a janela WorkerW do desktop (best-effort)."""
    user32 = _user32()
    progman = user32.FindWindowW("Progman", None)
    if not progman:
        return 0
    # Solicita criaÃ§Ã£o do WorkerW
    result = wintypes.LRESULT(0)
    try:
        user32.SendMessageTimeoutW(
            progman, _CREATE_WORKERW_MSG, 0, 0, 0, 1000, ctypes.byref(result)
        )
    except Exception:
        pass
    workerw = None

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def _enum(hwnd, lparam):
        nonlocal workerw
        try:
            def_view = user32.FindWindowExW(hwnd, None, "SHELLDLL_DefView", None)
            if def_view:
                w = user32.FindWindowExW(None, hwnd, "WorkerW", None)
                if w:
                    workerw = w
        except Exception:
            pass
        return True

    try:
        user32.EnumWindows(_enum, 0)
    except Exception:
        pass
    return workerw or progman


def _ensure_qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        try:
            app = QApplication([])
        except Exception:
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            app = QApplication([])
    return app


def set_animated_wallpaper(path: str, *, loop: bool = True, volume: int = 0) -> bool:
    """Aplica GIF/vÃ­deo como papel de parede animado (best-effort)."""
    global _animated_widget, _animated_refs
    stop_animated()
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".gif", ".mp4", ".webm", ".mov", ".avi", ".mkv"):
        return set_wallpaper_image(path)

    try:
        _ensure_qapp()
        from PySide6.QtCore import Qt, QUrl
        from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
        from PySide6.QtGui import QMovie

        widget = QWidget()
        widget.setWindowTitle("GP Wallpaper Animated")
        widget.setWindowFlags(Qt.FramelessWindowHint)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        refs: dict = {"widget": widget}

        if ext == ".gif":
            label = QLabel(widget)
            label.setScaledContents(True)
            movie = QMovie(path)
            try:
                movie.setLoopCount(-1 if loop else 1)
            except Exception:
                pass
            label.setMovie(movie)
            movie.start()
            layout.addWidget(label)
            refs.update({"label": label, "movie": movie})
        else:
            try:
                from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
                from PySide6.QtMultimediaWidgets import QVideoWidget
            except Exception:
                return set_wallpaper_image(path)
            video = QVideoWidget(widget)
            player = QMediaPlayer(widget)
            audio = QAudioOutput(widget)
            player.setAudioOutput(audio)
            player.setVideoOutput(video)
            try:
                audio.setVolume(max(0.0, min(1.0, volume / 100.0)))
            except Exception:
                pass
            try:
                player.setLoops(QMediaPlayer.Loops.Infinite if loop else 1)
            except Exception:
                pass
            player.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
            layout.addWidget(video)
            player.play()
            refs.update({"video": video, "player": player, "audio": audio})

        # redimensiona para a tela principal
        try:
            from PySide6.QtWidgets import QApplication

            screen = QApplication.primaryScreen()
            if screen is not None:
                geo = screen.geometry()
                widget.setGeometry(geo)
        except Exception:
            pass

        widget.show()

        # Reparent para a janela do desktop
        try:
            parent_hwnd = _find_workerw()
            if parent_hwnd:
                ctypes.windll.user32.SetParent(int(widget.winId()), parent_hwnd)
        except Exception:
            pass

        _animated_widget = widget
        _animated_refs.clear()
        _animated_refs.update(refs)
        return True
    except Exception:
        stop_animated()
        try:
            return set_wallpaper_image(path)
        except Exception:
            return False


def stop_animated() -> bool:
    """Para e remove o wallpaper animado, se ativo."""
    global _animated_widget, _animated_refs
    try:
        w = _animated_widget
        if w is not None:
            try:
                # para player/movie
                player = _animated_refs.get("player")
                if player is not None:
                    try:
                        player.stop()
                    except Exception:
                        pass
                movie = _animated_refs.get("movie")
                if movie is not None:
                    try:
                        movie.stop()
                    except Exception:
                        pass
                try:
                    w.hide()
                except Exception:
                    pass
                try:
                    w.deleteLater()
                except Exception:
                    pass
            finally:
                _animated_widget = None
                _animated_refs.clear()
        return True
    except Exception:
        _animated_widget = None
        _animated_refs.clear()
        return False
