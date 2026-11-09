"""Gerenciamento de inicialização automática com o Windows."""

from __future__ import annotations

from . import registry

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def add_to_startup(app_name: str, exe_path: str, args: str = "") -> bool:
    """Adiciona o aplicativo à inicialização do Windows (HKCU Run)."""
    try:
        value = f'"{exe_path}"'
        if args:
            value = f"{value} {args}"
        return registry.write_value("HKCU", RUN_KEY, app_name, value)
    except Exception:
        return False


def remove_from_startup(app_name: str) -> bool:
    """Remove o aplicativo da inicialização do Windows."""
    try:
        return registry.delete_value("HKCU", RUN_KEY, app_name)
    except Exception:
        return False


def is_in_startup(app_name: str) -> bool:
    """Verifica se o aplicativo está configurado para iniciar com o Windows."""
    try:
        return registry.value_exists("HKCU", RUN_KEY, app_name)
    except Exception:
        return False


def list_startup() -> dict:
    return registry.list_values("HKCU", RUN_KEY)


__all__ = [
    "add_to_startup",
    "remove_from_startup",
    "is_in_startup",
    "list_startup",
    "RUN_KEY",
]
