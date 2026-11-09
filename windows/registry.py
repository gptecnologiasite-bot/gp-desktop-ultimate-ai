"""Acesso seguro ao registro do Windows (winreg)."""

from __future__ import annotations

import winreg
from typing import Any, Optional

ROOT_ALIASES = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKU": winreg.HKEY_USERS,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
}

DEFAULT_ROOT = winreg.HKEY_CURRENT_USER


def _resolve_root(root: Any) -> int:
    if root is None:
        return DEFAULT_ROOT
    if isinstance(root, int):
        return root
    key = str(root).strip().upper()
    if key in ROOT_ALIASES:
        return ROOT_ALIASES[key]
    attr = getattr(winreg, key, None)
    if isinstance(attr, int):
        return attr
    raise ValueError(f"Raiz de registro desconhecida: {root!r}")


def _value_type(value: Any, value_type: Optional[int]) -> int:
    if value_type is not None:
        return value_type
    if isinstance(value, bool):
        return winreg.REG_DWORD
    if isinstance(value, int):
        return winreg.REG_DWORD
    if isinstance(value, bytes):
        return winreg.REG_BINARY
    if isinstance(value, (list, tuple)):
        return winreg.REG_MULTI_SZ
    return winreg.REG_SZ


def read_value(
    root: Any = None,
    subkey: str = "",
    name: str = "",
    default: Any = None,
) -> Any:
    try:
        with winreg.OpenKey(_resolve_root(root), subkey or "") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except (FileNotFoundError, OSError):
        return default
    except Exception:
        return default


def write_value(
    root: Any = None,
    subkey: str = "",
    name: str = "",
    value: Any = "",
    value_type: Optional[int] = None,
) -> bool:
    try:
        vt = _value_type(value, value_type)
        with winreg.CreateKey(_resolve_root(root), subkey or "") as key:
            winreg.SetValueEx(key, name, 0, vt, value)
        return True
    except Exception:
        return False


def delete_value(
    root: Any = None,
    subkey: str = "",
    name: str = "",
) -> bool:
    try:
        with winreg.OpenKey(
            _resolve_root(root), subkey or "", 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, name)
        return True
    except FileNotFoundError:
        return True
    except OSError:
        try:
            with winreg.OpenKey(_resolve_root(root), subkey or "") as key:
                winreg.DeleteValue(key, name)
            return True
        except FileNotFoundError:
            return True
        except Exception:
            return False
    except Exception:
        return False


def value_exists(root: Any = None, subkey: str = "", name: str = "") -> bool:
    try:
        with winreg.OpenKey(_resolve_root(root), subkey or "") as key:
            winreg.QueryValueEx(key, name)
        return True
    except Exception:
        return False


def list_values(root: Any = None, subkey: str = "") -> dict:
    result: dict = {}
    try:
        with winreg.OpenKey(_resolve_root(root), subkey or "") as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    result[name] = value
                    i += 1
                except OSError:
                    break
    except Exception:
        pass
    return result


def create_key(root: Any = None, subkey: str = "") -> bool:
    try:
        with winreg.CreateKey(_resolve_root(root), subkey or ""):
            pass
        return True
    except Exception:
        return False


def delete_key(root: Any = None, subkey: str = "") -> bool:
    try:
        winreg.DeleteKey(_resolve_root(root), subkey or "")
        return True
    except FileNotFoundError:
        return True
    except Exception:
        return False


__all__ = [
    "read_value",
    "write_value",
    "delete_value",
    "value_exists",
    "list_values",
    "create_key",
    "delete_key",
    "ROOT_ALIASES",
]
