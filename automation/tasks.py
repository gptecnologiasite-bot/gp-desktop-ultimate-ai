"""Tarefas agendadas, lembretes e gerenciamento de inicialização."""

from __future__ import annotations

import subprocess
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

try:
    import winreg  # type: ignore

    _HAS_WINREG = True
except Exception:  # pragma: no cover
    _HAS_WINREG = False
    winreg = None  # type: ignore

try:
    from PySide6.QtCore import QTimer  # type: ignore

    _HAS_QT = True
except Exception:  # pragma: no cover
    _HAS_QT = False
    QTimer = None  # type: ignore

_reminders: Dict[str, Dict[str, Any]] = {}
_reminder_counter = 0


def _next_id() -> str:
    global _reminder_counter
    _reminder_counter += 1
    return f"reminder_{_reminder_counter}"


def schedule_task(
    name: str,
    command: str,
    schedule: str = "daily",
    time: str = "09:00",
    days: Optional[str] = None,
) -> bool:
    """Agenda tarefa via schtasks. Retorna True em sucesso."""
    args = [
        "schtasks",
        "/Create",
        "/TN",
        name,
        "/TR",
        command,
        "/SC",
        schedule,
        "/ST",
        time,
        "/F",
    ]
    if days:
        args += ["/D", days]
    try:
        result = subprocess.run(args, capture_output=True, text=True, shell=False)
        return result.returncode == 0
    except Exception:
        return False


def delete_scheduled_task(name: str) -> bool:
    try:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", name, "/F"], capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def add_reminder(
    message: str, delay_ms: int, callback: Optional[Callable[[str], None]] = None
) -> str:
    """Adiciona lembrete in-memory com QTimer (ou threading)."""
    rid = _next_id()
    fired = {"done": False}

    def fire():
        fired["done"] = True
        if callback:
            try:
                callback(message)
            except Exception:
                pass

    if _HAS_QT:
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(fire)
        timer.start(delay_ms)
        _reminders[rid] = {
            "id": rid,
            "message": message,
            "delay_ms": delay_ms,
            "created": datetime.now().isoformat(),
            "timer": timer,
        }
    else:
        t = threading.Timer(delay_ms / 1000.0, fire)
        t.daemon = True
        t.start()
        _reminders[rid] = {
            "id": rid,
            "message": message,
            "delay_ms": delay_ms,
            "created": datetime.now().isoformat(),
            "timer": t,
        }
    return rid


def list_reminders() -> List[Dict[str, Any]]:
    return [
        {
            "id": r["id"],
            "message": r["message"],
            "delay_ms": r["delay_ms"],
            "created": r["created"],
        }
        for r in _reminders.values()
    ]


def cancel_reminder(rid: str) -> bool:
    r = _reminders.pop(rid, None)
    if not r:
        return False
    timer = r.get("timer")
    try:
        if hasattr(timer, "stop"):
            timer.stop()
    except Exception:
        pass
    return True


def clear_reminders() -> None:
    for rid in list(_reminders.keys()):
        cancel_reminder(rid)


def add_startup(name: str, command: str) -> bool:
    """Adiciona entrada na chave Run do registro."""
    if not _HAS_WINREG:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
        return True
    except Exception:
        return False


def remove_startup(name: str) -> bool:
    if not _HAS_WINREG:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.DeleteValue(key, name)
        return True
    except Exception:
        return False


def list_startup() -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    if not _HAS_WINREG:
        return result
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"
        ) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    result.append({"name": name, "command": value})
                    i += 1
                except OSError:
                    break
    except Exception:
        pass
    return result
