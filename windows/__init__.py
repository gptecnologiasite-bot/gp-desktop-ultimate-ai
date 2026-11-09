"""Módulo GP Windows - integração com o Windows."""

from . import startup
from . import registry
from . import shortcuts
from . import notifications
from . import display
from .manager import WindowsManager

__all__ = [
    "startup",
    "registry",
    "shortcuts",
    "notifications",
    "display",
    "WindowsManager",
]
