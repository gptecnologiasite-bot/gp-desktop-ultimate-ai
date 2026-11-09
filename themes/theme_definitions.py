"""Definições de temas predefinidos do GP Desktop Ultimate AI.

Cada tema é um dicionário de cores com as chaves:
background, surface, text, accent, menu, button, border.
"""

from __future__ import annotations

from typing import Any, Dict, List

THEMES: Dict[str, Dict[str, str]] = {
    "claro": {
        "background": "#ffffff",
        "surface": "#f3f4f6",
        "text": "#111827",
        "accent": "#2563eb",
        "menu": "#e5e7eb",
        "button": "#2563eb",
        "border": "#d1d5db",
    },
    "escuro": {
        "background": "#0f172a",
        "surface": "#1e293b",
        "text": "#e2e8f0",
        "accent": "#38bdf8",
        "menu": "#1e293b",
        "button": "#0ea5e9",
        "border": "#334155",
    },
    "futurista": {
        "background": "#0a0014",
        "surface": "#1a0b2e",
        "text": "#e0e7ff",
        "accent": "#a855f7",
        "menu": "#2d1b4e",
        "button": "#7c3aed",
        "border": "#6d28d9",
    },
    "gamer": {
        "background": "#0d0d0d",
        "surface": "#1a1a1a",
        "text": "#00ff88",
        "accent": "#ff0055",
        "menu": "#111111",
        "button": "#ff0055",
        "border": "#333333",
    },
    "minimalista": {
        "background": "#fafafa",
        "surface": "#ffffff",
        "text": "#262626",
        "accent": "#000000",
        "menu": "#f5f5f5",
        "button": "#000000",
        "border": "#e5e5e5",
    },
    "profissional": {
        "background": "#f8fafc",
        "surface": "#ffffff",
        "text": "#0f172a",
        "accent": "#1d4ed8",
        "menu": "#e2e8f0",
        "button": "#1d4ed8",
        "border": "#cbd5e1",
    },
}

# Alias histórico/alternativo
THEME_DEFINITIONS = THEMES

PREDEFINED_THEMES: List[str] = list(THEMES.keys())

REQUIRED_COLOR_KEYS = (
    "background",
    "surface",
    "text",
    "accent",
    "menu",
    "button",
    "border",
)


def get_theme(name: str) -> Dict[str, str]:
    """Retorna a definição de um tema pelo nome (case-insensitive)."""
    if not isinstance(name, str):
        if isinstance(name, dict):
            return dict(name)
        raise ValueError("Nome de tema inválido")
    key = name.strip().lower()
    if key in THEMES:
        return dict(THEMES[key])
    # aliases em inglês
    aliases = {
        "light": "claro",
        "dark": "escuro",
        "futuristic": "futurista",
        "minimalist": "minimalista",
        "professional": "profissional",
    }
    if key in aliases and aliases[key] in THEMES:
        return dict(THEMES[aliases[key]])
    raise KeyError(f"Tema desconhecido: {name}")


def list_themes() -> List[str]:
    return list(THEMES.keys())


def is_valid_theme(theme: Any) -> bool:
    if isinstance(theme, str):
        try:
            get_theme(theme)
            return True
        except Exception:
            return False
    if isinstance(theme, dict):
        return all(k in theme for k in REQUIRED_COLOR_KEYS)
    return False
