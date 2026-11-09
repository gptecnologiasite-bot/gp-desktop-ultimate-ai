"""AutomationManager orquestrando automação com confirmação para destrutivas."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

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


class AutomationManager:
    def __init__(self, confirm: Optional[Callable[[str], bool]] = None):
        self.confirm = confirm or (lambda msg: True)

    # Programs
    def open_program(self, path, args=None):
        return open_program(path, args=args)

    def list_installed(self):
        return list_installed()

    def create_shortcut(self, target, shortcut_path, **kwargs):
        return create_shortcut(target, shortcut_path, **kwargs)

    # Files
    def find_files(self, root, pattern="*", recursive=True, max_results=10000):
        return find_files(
            root, pattern=pattern, recursive=recursive, max_results=max_results
        )

    def organize_folder(
        self, folder, mapping=None, dry_run=False, require_confirm=True
    ):
        if require_confirm and not self.confirm(f"Organizar pasta {folder}?"):
            return {"cancelled": True}
        return organize_folder(folder, mapping=mapping, dry_run=dry_run)

    def delete_file(self, path, require_confirm=True):
        def cb(p):
            if not require_confirm:
                return True
            return bool(self.confirm(f"Excluir {p}?"))

        return delete_file(path, confirm=cb)

    # Tasks
    def schedule_task(self, name, command, schedule="daily", time="09:00", days=None):
        if not self.confirm(f"Agendar tarefa '{name}'?"):
            return False
        return schedule_task(name, command, schedule=schedule, time=time, days=days)

    def delete_scheduled_task(self, name):
        if not self.confirm(f"Remover tarefa '{name}'?"):
            return False
        return delete_scheduled_task(name)

    def add_reminder(self, message, delay_ms, callback=None):
        return add_reminder(message, delay_ms, callback=callback)

    def list_reminders(self):
        return list_reminders()

    def cancel_reminder(self, rid):
        return cancel_reminder(rid)

    def clear_reminders(self):
        clear_reminders()

    # Startup
    def add_startup(self, name, command):
        if not self.confirm(f"Adicionar '{name}' à inicialização?"):
            return False
        return add_startup(name, command)

    def remove_startup(self, name):
        if not self.confirm(f"Remover '{name}' da inicialização?"):
            return False
        return remove_startup(name)

    def list_startup(self):
        return list_startup()
