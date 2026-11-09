"""Módulo de temas do GP Desktop Ultimate AI."""

from .theme_definitions import (
    THEMES,
    THEME_DEFINITIONS,
    PREDEFINED_THEMES,
    REQUIRED_COLOR_KEYS,
    get_theme,
    list_themes,
    is_valid_theme,
)
from .stylesheet import build_qss
from .manager import ThemeManager

__all__ = [
    "THEMES",
    "THEME_DEFINITIONS",
    "PREDEFINED_THEMES",
    "REQUIRED_COLOR_KEYS",
    "get_theme",
    "list_themes",
    "is_valid_theme",
    "build_qss",
    "ThemeManager",
]
