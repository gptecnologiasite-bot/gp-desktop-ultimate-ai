"""MÃ³dulo GP Wallpaper AI."""

from .windows_wallpaper import (
    set_wallpaper_image,
    get_current_wallpaper,
    restore_original,
    set_animated_wallpaper,
    stop_animated,
)
from .library import WallpaperLibrary
from .player import WallpaperPlayer
from .manager import WallpaperManager

__all__ = [
    "set_wallpaper_image",
    "get_current_wallpaper",
    "restore_original",
    "set_animated_wallpaper",
    "stop_animated",
    "WallpaperLibrary",
    "WallpaperPlayer",
    "WallpaperManager",
]
