"""Smoke tests para o modulo windows."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

import winreg

from windows import registry, startup, display, WindowsManager


def _cleanup_key(subkey):
    # remove valores e chave
    try:
        vals = registry.list_values("HKCU", subkey)
        for name in vals:
            registry.delete_value("HKCU", subkey, name)
    except Exception:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, subkey)
    except Exception:
        pass


def test_registry_roundtrip():
    subkey = r"Software\GPDesktopTest"
    _cleanup_key(subkey)
    try:
        assert registry.write_value("HKCU", subkey, "foo", "bar") is True
        assert registry.read_value("HKCU", subkey, "foo") == "bar"
        assert registry.read_value("HKCU", subkey, "missing", default="x") == "x"
        assert registry.value_exists("HKCU", subkey, "foo") is True
        assert registry.value_exists("HKCU", subkey, "missing") is False

        # inteiro
        assert registry.write_value("HKCU", subkey, "num", 42) is True
        assert registry.read_value("HKCU", subkey, "num") == 42

        # listagem
        vals = registry.list_values("HKCU", subkey)
        assert "foo" in vals and "num" in vals

        # delete
        assert registry.delete_value("HKCU", subkey, "foo") is True
        assert registry.read_value("HKCU", subkey, "foo") is None
        assert registry.delete_value("HKCU", subkey, "foo") is True  # idempotente
    finally:
        _cleanup_key(subkey)


def test_registry_default_root():
    subkey = r"Software\GPDesktopTest2"
    _cleanup_key(subkey)
    try:
        assert registry.write_value(subkey=subkey, name="k", value="v") is True
        assert registry.read_value(subkey=subkey, name="k") == "v"
    finally:
        _cleanup_key(subkey)


def test_startup_flag():
    app_name = "GPDesktopTestStartup"
    exe = r"C:\Windows\System32\notepad.exe"
    # cleanup inicial
    startup.remove_from_startup(app_name)
    try:
        assert startup.add_to_startup(app_name, exe) is True
        assert startup.is_in_startup(app_name) is True
        assert startup.remove_from_startup(app_name) is True
        assert startup.is_in_startup(app_name) is False
    finally:
        startup.remove_from_startup(app_name)


def test_monitor_enumeration_mock(monkeypatch):
    class FakeScreen:
        pass

    class FakeApp:
        @staticmethod
        def instance():
            return FakeApp()

        def screens(self):
            return [FakeScreen(), FakeScreen()]

    monkeypatch.setattr(display, "QApplication", FakeApp)
    monkeypatch.setattr(display, "QGuiApplication", None)
    screens = display.get_monitors()
    assert len(screens) == 2


def test_is_fullscreen_active_returns_bool():
    result = display.is_fullscreen_active()
    assert isinstance(result, bool)


def test_manager_instantiation():
    m = WindowsManager()
    assert m is not None
    assert m.is_in_startup("nope") is False


def test_shortcut_creation_tmp(tmp_path):
    from windows import shortcuts

    target = r"C:\Windows\System32\notepad.exe"
    lnk = tmp_path / "test.lnk"
    # win32com pode falhar em ambiente headless; apenas não quebrar
    result = shortcuts.create_shortcut(target, str(lnk))
    # Se criou, arquivo existe
    if result:
        assert lnk.exists()


