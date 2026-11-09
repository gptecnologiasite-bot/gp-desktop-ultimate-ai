"""Handler de comandos Windows do assistente, com autorização."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from automation.programs import open_program, list_installed, create_shortcut
from automation.files import find_files, organize_folder, delete_file
from automation.tasks import (
    schedule_task,
    delete_scheduled_task,
    add_startup,
    remove_startup,
)


SAFE_COMMANDS = {
    "open_program",
    "list_installed",
    "create_shortcut",
    "find_files",
}

DESTRUCTIVE_COMMANDS = {
    "delete_file",
    "organize_folder",
    "schedule_task",
    "delete_scheduled_task",
    "add_startup",
    "remove_startup",
}


class WindowsCommandHandler:
    """Executa comandos Windows, exigindo confirmação para operações destrutivas."""

    def __init__(self, confirm: Optional[Callable[[str], bool]] = None) -> None:
        self.confirm = confirm if confirm is not None else (lambda msg: False)

    def is_safe(self, command: str) -> bool:
        return str(command).strip().lower() in SAFE_COMMANDS

    def is_destructive(self, command: str) -> bool:
        return str(command).strip().lower() in DESTRUCTIVE_COMMANDS

    def list_commands(self) -> Dict[str, List[str]]:
        return {
            "safe": sorted(SAFE_COMMANDS),
            "destructive": sorted(DESTRUCTIVE_COMMANDS),
        }

    def _resolve(
        self, command: Any, kwargs: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        if isinstance(command, dict):
            cmd = (
                command.get("command")
                or command.get("action")
                or command.get("name")
                or command.get("cmd")
            )
            params = {
                k: v
                for k, v in command.items()
                if k not in {"command", "action", "name", "cmd"}
            }
            params.update(kwargs)
            return str(cmd), params
        if isinstance(command, str):
            # suporta "comando chave=valor" simples? não; tratar como nome
            return command.strip(), kwargs
        return str(command), kwargs

    def execute_command(self, command: Any, **kwargs: Any) -> Any:
        """Executa um comando. Operações destrutivas exigem confirmação."""
        cmd, params = self._resolve(command, kwargs)
        key = cmd.strip().lower()

        if key in DESTRUCTIVE_COMMANDS:
            msg = (
                params.get("message")
                or params.get("confirm_message")
                or f"Executar '{key}'?"
            )
            if not bool(self.confirm(msg)):
                return False

        try:
            if key == "open_program":
                path = (
                    params.get("path") or params.get("program") or params.get("target")
                )
                return open_program(path, args=params.get("args"))
            if key == "list_installed":
                return list_installed()
            if key == "create_shortcut":
                return create_shortcut(
                    params.get("target"),
                    params.get("shortcut_path") or params.get("path"),
                    working_dir=params.get("working_dir"),
                    icon=params.get("icon"),
                    description=params.get("description"),
                )
            if key == "find_files":
                return find_files(
                    params.get("root")
                    or params.get("folder")
                    or params.get("path", "."),
                    pattern=params.get("pattern", "*"),
                    recursive=params.get("recursive", True),
                    max_results=params.get("max_results", 10000),
                )
            if key == "delete_file":
                path = params.get("path") or params.get("file")
                return delete_file(path)
            if key == "organize_folder":
                folder = params.get("folder") or params.get("path")
                return organize_folder(
                    folder,
                    mapping=params.get("mapping"),
                    dry_run=params.get("dry_run", False),
                )
            if key == "schedule_task":
                return schedule_task(
                    params.get("name"),
                    params.get("command"),
                    schedule=params.get("schedule", "daily"),
                    time=params.get("time", "09:00"),
                    days=params.get("days"),
                )
            if key == "delete_scheduled_task":
                return delete_scheduled_task(params.get("name"))
            if key == "add_startup":
                return add_startup(params.get("name"), params.get("command"))
            if key == "remove_startup":
                return remove_startup(params.get("name"))
        except Exception:
            return False

        return False
