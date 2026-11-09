"""Automação de programas (abrir, listar instalados, atalhos)."""

from __future__ import annotations

import os
import subprocess
from typing import Any, Dict, List, Optional

try:
    import winreg  # type: ignore

    _HAS_WINREG = True
except Exception:  # pragma: no cover
    _HAS_WINREG = False
    winreg = None  # type: ignore

try:
    import win32com.client  # type: ignore

    _HAS_WIN32COM = True
except Exception:  # pragma: no cover
    _HAS_WIN32COM = False


def open_program(
    path: str, args: Optional[List[str]] = None, wait: bool = False
) -> bool:
    """Abre um programa/caminho. Retorna True em sucesso."""
    try:
        if os.name == "nt":
            if path.lower().endswith((".bat", ".cmd")):
                subprocess.Popen([path] + (args or []), shell=True)
            else:
                os.startfile(path)  # type: ignore[attr-defined]
            return True
        else:
            subprocess.Popen([path] + (args or []))
            return True
    except Exception:
        try:
            subprocess.Popen([path] + (args or []))
            return True
        except Exception:
            return False


def list_installed() -> List[Dict[str, Any]]:
    """Lista programas instalados via registro Windows (best-effort)."""
    result: List[Dict[str, Any]] = []
    if not _HAS_WINREG:
        return result
    roots = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
    ]
    seen = set()
    for hive, key_path in roots:
        try:
            with winreg.OpenKey(hive, key_path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_name) as sub:

                            def get(val):
                                try:
                                    return winreg.QueryValueEx(sub, val)[0]
                                except Exception:
                                    return None

                            name = get("DisplayName")
                            if not name:
                                continue
                            entry = {
                                "name": name,
                                "version": get("DisplayVersion"),
                                "publisher": get("Publisher"),
                                "install_location": get("InstallLocation"),
                                "uninstall_string": get("UninstallString"),
                            }
                            ident = (entry["name"], entry["version"])
                            if ident in seen:
                                continue
                            seen.add(ident)
                            result.append(entry)
                    except Exception:
                        continue
        except Exception:
            continue
    result.sort(key=lambda x: (x.get("name") or "").lower())
    return result


def create_shortcut(
    target: str,
    shortcut_path: str,
    working_dir: Optional[str] = None,
    icon: Optional[str] = None,
    description: Optional[str] = None,
) -> bool:
    """Cria atalho .lnk via win32com (best-effort)."""
    if not _HAS_WIN32COM:
        return False
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target
        if working_dir:
            shortcut.WorkingDirectory = working_dir
        if icon:
            shortcut.IconLocation = icon
        if description:
            shortcut.Description = description
        shortcut.save()
        return True
    except Exception:
        return False
