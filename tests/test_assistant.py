"""Testes do módulo assistant."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

from assistant import ChatManager, WindowsCommandHandler, AssistantManager, VoiceManager


def test_chat_history():
    provider = MagicMock()
    provider.chat.return_value = "resposta"
    cm = ChatManager(provider=provider)
    r = cm.send_message("oi")
    assert r == "resposta"
    assert len(cm.history) == 2
    assert cm.history[0] == {"role": "user", "content": "oi"}
    assert cm.history[1] == {"role": "assistant", "content": "resposta"}


def test_chat_clear_history():
    provider = MagicMock()
    provider.chat.return_value = "x"
    cm = ChatManager(provider=provider)
    cm.send_message("oi")
    cm.clear_history()
    assert cm.history == []


def test_command_handler_confirm_false():
    handler = WindowsCommandHandler(confirm=lambda msg: False)
    # destructive should be cancelled
    import tempfile
    from pathlib import Path as P

    d = P(tempfile.mkdtemp())
    f = d / "x.txt"
    f.write_text("x")
    res = handler.execute_command("delete_file", path=str(f))
    assert res is False
    assert f.exists()


def test_command_handler_confirm_true():
    handler = WindowsCommandHandler(confirm=lambda msg: True)
    import tempfile
    from pathlib import Path as P

    d = P(tempfile.mkdtemp())
    f = d / "x.txt"
    f.write_text("x")
    res = handler.execute_command("delete_file", path=str(f))
    assert res is True
    assert not f.exists()


def test_command_handler_safe_no_confirm():
    handler = WindowsCommandHandler(confirm=lambda msg: False)
    # safe command should execute regardless of confirm
    res = handler.execute_command("find_files", root=".", pattern="*.py")
    assert isinstance(res, list)


def test_command_handler_dict():
    handler = WindowsCommandHandler(confirm=lambda msg: True)
    import tempfile
    from pathlib import Path as P

    d = P(tempfile.mkdtemp())
    f = d / "y.txt"
    f.write_text("y")
    res = handler.execute_command({"command": "delete_file", "path": str(f)})
    assert res is True


def test_voice_manager_instantiation():
    vm = VoiceManager()
    assert vm is not None
    assert isinstance(vm.list_voices(), list)


def test_assistant_manager():
    provider = MagicMock()
    provider.chat.return_value = "ok"
    am = AssistantManager(provider=provider)
    assert am.send_message("hi") == "ok"
    assert (
        am.execute_command("list_installed") is not None
        or am.execute_command("list_installed") is False
    )
    # list_installed returns list (possibly empty)
    assert isinstance(am.execute_command("list_installed"), list)
