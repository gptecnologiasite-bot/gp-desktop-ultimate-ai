"""WindowsManager - agregador de funcionalidades Windows."""

from __future__ import annotations

from typing import Any, Optional

from . import startup
from . import registry
from . import shortcuts
from . import notifications
from . import display


class WindowsManager:
    def __init__(self):
        self.startup = startup
        self.registry = registry
        self.shortcuts = shortcuts
        self.notifications = notifications
        self.display = display

    # startup
    def add_to_startup(self, app_name: str, exe_path: str, args: str = "") -> bool:
        return startup.add_to_startup(app_name, exe_path, args)

    def remove_from_startup(self, app_name: str) -> bool:
        return startup.remove_from_startup(app_name)

    def is_in_startup(self, app_name: str) -> bool:
        return startup.is_in_startup(app_name)

    # registry
    def read_registry(self, root=None, subkey="", name="", default=None):
        return registry.read_value(root, subkey, name, default)

    def write_registry(self, root=None, subkey="", name="", value="", value_type=None):
        return registry.write_value(root, subkey, name, value, value_type)

    def delete_registry(self, root=None, subkey="", name=""):
        return registry.delete_value(root, subkey, name)

    # shortcuts
    def create_shortcut(
        self, target, shortcut_path, icon=None, args=None, working_dir=None
    ):
        return shortcuts.create_shortcut(
            target, shortcut_path, icon=icon, args=args, working_dir=working_dir
        )

    # notifications
    def show_toast(self, title, message, duration=5, threaded=True):
        return notifications.show_toast(
            title, message, duration=duration, threaded=threaded
        )

    # display
    def get_monitors(self, app=None):
        return display.get_monitors(app)

    def is_fullscreen_active(self):
        return display.is_fullscreen_active()


__all__ = ["WindowsManager"]
