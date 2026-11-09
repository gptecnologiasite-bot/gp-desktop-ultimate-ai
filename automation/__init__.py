"""Módulo de automação do GP Desktop Ultimate AI."""

from .programs import open_program, list_installed, create_shortcut
from .files import find_files, organize_folder, delete_file
from .tasks import (
    schedule_task,
    delete_scheduled_task,
    add_reminder,
    list_reminders,
    cancel_reminder,
    clear_reminders,
    add_startup,
    remove_startup,
    list_startup,
)
from .manager import AutomationManager

__all__ = [
    "open_program",
    "list_installed",
    "create_shortcut",
    "find_files",
    "organize_folder",
    "delete_file",
    "schedule_task",
    "delete_scheduled_task",
    "add_reminder",
    "list_reminders",
    "cancel_reminder",
    "clear_reminders",
    "add_startup",
    "remove_startup",
    "list_startup",
    "AutomationManager",
]
