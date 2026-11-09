import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

import pytest

from settings import SettingsManager


@pytest.fixture(autouse=True)
def _reset_supabase():
    try:
        from supabase import reset_client

        reset_client()
    except Exception:
        pass
    yield
    try:
        from supabase import reset_client

        reset_client()
    except Exception:
        pass


def test_settings_in_memory():
    mgr = SettingsManager(db=None, defaults={"language": "pt-BR"})
    assert mgr.get("language") == "pt-BR"
    mgr.set("notifications", True)
    assert mgr.get("notifications") is True
    assert mgr.get_all()["notifications"] is True


def test_settings_persist_supabase():
    db = MagicMock()
    db.select.return_value = MagicMock(data=[])
    db.upsert.return_value = MagicMock(data=[{"key": "language", "value": "en"}])
    mgr = SettingsManager(db=db, user_id="u1")
    mgr.set("language", "en")
    assert db.upsert.called
    # cache updated
    assert mgr.get("language") == "en"


def test_settings_load_from_db():
    db = MagicMock()
    db.select.return_value = MagicMock(
        data=[{"key": "theme", "value": {"accent": "#fff"}}]
    )
    mgr = SettingsManager(db=db)
    assert mgr.get("theme") == {"accent": "#fff"}


def test_settings_reset_single():
    db = MagicMock()
    db.select.return_value = MagicMock(data=[])
    mgr = SettingsManager(db=db, defaults={"language": "pt-BR"})
    mgr.set("language", "en")
    mgr.reset("language")
    assert mgr.get("language") == "pt-BR"


def test_settings_reset_all():
    db = MagicMock()
    db.select.return_value = MagicMock(data=[])
    mgr = SettingsManager(db=db)
    mgr.set("a", 1)
    mgr.set("b", 2)
    mgr.reset()
    assert mgr.get("a") is None
    assert db.delete.called


def test_settings_convenience():
    mgr = SettingsManager(db=None)
    mgr.set_language("es")
    mgr.set_startup(True)
    mgr.set_notifications(False)
    assert mgr.get_language() == "es"
    assert mgr.get_startup() is True
    assert mgr.get_notifications() is False
