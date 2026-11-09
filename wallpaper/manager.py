"""Gerenciador de wallpapers (aplicar, restaurar, rotaÃ§Ã£o, configuraÃ§Ã£o por monitor)."""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Optional

from .library import WallpaperLibrary
from .player import WallpaperPlayer
from . import windows_wallpaper as ww


class WallpaperManager:
    def __init__(
        self,
        library: Optional[WallpaperLibrary] = None,
        player: Optional[WallpaperPlayer] = None,
    ):
        self.library = library if library is not None else WallpaperLibrary()
        self.player = player if player is not None else WallpaperPlayer()
        self._current: Optional[str] = None
        self._original: Optional[str] = None
        self._monitor_config: dict[Any, str] = {}
        self._auto_thread: Optional[threading.Thread] = None
        self._auto_stop = threading.Event()
        self._auto_interval = 300
        self._auto_favorites_only = False
        self._pause_on_fullscreen = False
        self._paused = False

    # ---------- aplicaÃ§Ã£o ----------

    def _capture_original(self) -> None:
        if self._original is None:
            try:
                self._original = ww.get_current_wallpaper()
            except Exception:
                self._original = ""

    def apply(self, path_or_item: Any, monitor: Any = None, animated: Optional[bool] = None) -> bool:
        self._capture_original()
        path = path_or_item
        if not isinstance(path, str):
            path = getattr(path_or_item, "path", None) or (
                path_or_item.get("path") if isinstance(path_or_item, dict) else None
            )
        if not path:
            return False
        ext = os.path.splitext(path)[1].lower()
        is_anim = ext in (".gif", ".mp4", ".webm", ".mov", ".avi", ".mkv")
        if animated is None:
            animated = is_anim

        try:
            if animated and is_anim:
                ww.set_animated_wallpaper(path)
                self.player.set_source(path)
                self.player.play()
            elif ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
                ww.set_wallpaper_image(path)
                try:
                    self.player.stop()
                except Exception:
                    pass
            else:
                # fallback imagem
                ww.set_wallpaper_image(path)
            self._current = path
            if monitor is not None:
                self._monitor_config[monitor] = path
            return True
        except Exception:
            return False

    def apply_to_monitor(self, monitor: Any, path: Any) -> bool:
        return self.apply(path, monitor=monitor)

    def restore(self) -> bool:
        try:
            ww.stop_animated()
        except Exception:
            pass
        try:
            self.player.stop()
        except Exception:
            pass
        try:
            if self._original:
                ww.set_wallpaper_image(self._original)
            else:
                ww.restore_original()
            return True
        except Exception:
            try:
                return ww.restore_original()
            except Exception:
                return False
        finally:
            self._current = None

    # ---------- auto rotaÃ§Ã£o ----------

    def start_auto_rotate(
        self,
        interval_seconds: int = 300,
        favorites_only: bool = False,
    ) -> None:
        self.stop_auto_rotate()
        self._auto_interval = max(5, int(interval_seconds))
        self._auto_favorites_only = bool(favorites_only)
        self._auto_stop.clear()
        self._auto_thread = threading.Thread(target=self._auto_loop, daemon=True)
        self._auto_thread.start()

    def auto_rotate(self, interval_seconds: int = 300, favorites_only: bool = False) -> None:
        self.start_auto_rotate(interval_seconds, favorites_only)

    def stop_auto_rotate(self) -> None:
        self._auto_stop.set()
        t = self._auto_thread
        if t is not None and t.is_alive():
            t.join(timeout=2)
        self._auto_thread = None

    def _auto_loop(self) -> None:
        while not self._auto_stop.wait(self._auto_interval):
            try:
                items = self.library.favorites() if self._auto_favorites_only else list(self.library)
                if not items:
                    items = list(self.library)
                if not items:
                    continue
                # escolhe prÃ³ximo
                idx = 0
                if self._current:
                    paths = [i.get("path") for i in items]
                    if self._current in paths:
                        idx = (paths.index(self._current) + 1) % len(paths)
                target = items[idx]
                self.apply(target)
            except Exception:
                continue

    # ---------- monitor config ----------

    def set_monitor_wallpaper(self, monitor: Any, path: Any) -> bool:
        self._monitor_config[monitor] = path if isinstance(path, str) else getattr(path, "path", str(path))
        return self.apply(path, monitor=monitor)

    def monitor_config(self) -> dict:
        return dict(self._monitor_config)

    def get_monitor_wallpaper(self, monitor: Any) -> Optional[str]:
        return self._monitor_config.get(monitor)

    # ---------- fullscreen pause ----------

    def enable_pause_on_fullscreen(self, enabled: bool = True) -> None:
        self._pause_on_fullscreen = bool(enabled)

    def check_fullscreen(self) -> bool:
        """Detecta (best-effort) se hÃ¡ janela em tela cheia e pausa/retoma."""
        if not self._pause_on_fullscreen:
            return False
        is_fs = False
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                # tela primÃ¡ria
                sw = user32.GetSystemMetrics(0)
                sh = user32.GetSystemMetrics(1)
                if (rect.right - rect.left) >= sw and (rect.bottom - rect.top) >= sh:
                    is_fs = True
        except Exception:
            is_fs = False

        if is_fs and not self._paused:
            try:
                self.player.pause()
            except Exception:
                pass
            self._paused = True
        elif (not is_fs) and self._paused:
            try:
                self.player.play()
            except Exception:
                pass
            self._paused = False
        return is_fs

    @property
    def current(self) -> Optional[str]:
        return self._current
