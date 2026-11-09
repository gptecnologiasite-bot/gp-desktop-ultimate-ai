"""Smoke tests para o modulo wallpaper."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

from wallpaper import WallpaperLibrary, WallpaperPlayer, WallpaperManager


def test_library_add_list():
    lib = WallpaperLibrary()
    item = lib.add("C:/tmp/wall.jpg")
    assert item is not None
    assert item["path"].endswith("wall.jpg")
    assert len(lib.list()) == 1
    assert lib.list()[0]["type"] == "image"


def test_library_favorites_filter():
    lib = WallpaperLibrary()
    lib.add("C:/tmp/a.jpg", favorite=True)
    lib.add("C:/tmp/b.mp4")
    favs = lib.favorites()
    assert len(favs) == 1
    assert lib.list(favorites_only=True) == favs
    assert lib.toggle_favorite(path="C:/tmp/b.mp4") is True
    assert len(lib.favorites()) == 2


def test_player_instantiation_without_video():
    p = WallpaperPlayer()
    assert p is not None
    assert p.current_path() is None
    assert p.mode() is None


def test_manager_instantiation():
    m = WallpaperManager()
    assert m is not None
    assert m.current is None
