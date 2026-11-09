"""Módulo assistant do GP Desktop Ultimate AI."""

from .chat import ChatManager
from .voice import VoiceManager
from .commands import WindowsCommandHandler, SAFE_COMMANDS, DESTRUCTIVE_COMMANDS
from .manager import AssistantManager

__all__ = [
    "ChatManager",
    "VoiceManager",
    "WindowsCommandHandler",
    "SAFE_COMMANDS",
    "DESTRUCTIVE_COMMANDS",
    "AssistantManager",
]
