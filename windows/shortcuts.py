"""Criação de atalhos (.lnk) no Windows."""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Optional


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def create_shortcut(
    target: str,
    shortcut_path: str,
    icon: Optional[str] = None,
    args: Optional[str] = None,
    working_dir: Optional[str] = None,
    description: Optional[str] = None,
) -> bool:
    """Cria um atalho .lnk. Usa win32com e fallback VBScript."""
    _ensure_parent(shortcut_path)
    # Tenta win32com
    try:
        import win32com.client

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target
        if args:
            shortcut.Arguments = args
        if icon:
            shortcut.IconLocation = icon
        if working_dir:
            shortcut.WorkingDirectory = working_dir
        if description:
            shortcut.Description = description
        shortcut.Save()
        return True
    except Exception:
        pass

    # Fallback VBScript
    try:
        lines = [
            'Set sh = CreateObject("WScript.Shell")',
            f'Set lnk = sh.CreateShortcut("{shortcut_path}")',
            f'lnk.TargetPath = "{target}"',
        ]
        if args:
            lines.append(f'lnk.Arguments = "{args}"')
        if icon:
            lines.append(f'lnk.IconLocation = "{icon}"')
        if working_dir:
            lines.append(f'lnk.WorkingDirectory = "{working_dir}"')
        if description:
            lines.append(f'lnk.Description = "{description}"')
        lines.append("lnk.Save")
        vbs_content = "\n".join(lines)

        fd, vbs_path = tempfile.mkstemp(suffix=".vbs")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(vbs_content)
            result = subprocess.run(
                ["cscript", "//nologo", vbs_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        finally:
            try:
                os.remove(vbs_path)
            except OSError:
                pass
    except Exception:
        return False


def remove_shortcut(shortcut_path: str) -> bool:
    try:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        return True
    except Exception:
        return False


__all__ = ["create_shortcut", "remove_shortcut"]
