import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

import pytest

from synchronization import SyncManager


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


def test_status_online_default():
    sm = SyncManager(db=None, online=True)
    assert sm.status == "online"
    assert sm.online is True


def test_status_offline():
    sm = SyncManager(db=None, online=False)
    assert sm.status == "offline"
    assert sm.online is False


def test_push_pull_offline_queue():
    db = MagicMock()
    db.upsert.return_value = MagicMock(data=[{"ok": True}])
    db.select.return_value = MagicMock(data=[{"id": 1}])
    sm = SyncManager(db=db, online=False)
    assert sm.push("themes", {"name": "t1", "color": "#fff"}) is False
    assert len(sm.queue) == 1
    # reconectar drena
    sm.set_online(True)
    assert sm.status == "online"
    assert len(sm.queue) == 0
    assert db.upsert.called


def test_push_online_calls_db():
    db = MagicMock()
    db.upsert.return_value = MagicMock(data=[{"ok": True}])
    sm = SyncManager(db=db, online=True)
    res = sm.push("personalizations", {"name": "p1"})
    assert db.upsert.called
    assert sm.status == "online"


def test_pull_online():
    db = MagicMock()
    db.select.return_value = MagicMock(data=[{"id": 1, "name": "x"}])
    sm = SyncManager(db=db, online=True)
    rows = sm.pull("themes")
    assert isinstance(rows, list)
    assert rows[0]["name"] == "x"


def test_realtime_subscribe():
    rt = MagicMock()
    rt.subscribe.return_value = MagicMock()
    sm = SyncManager(db=None, realtime=rt, online=True)
    ch = sm.subscribe(callback=lambda p: None, table="themes")
    assert rt.subscribe.called
    assert ch is not None


def test_drain_failure_sets_offline():
    db = MagicMock()
    db.upsert.side_effect = Exception("boom")
    sm = SyncManager(db=db, online=False)
    sm.push("settings", {"key": "k", "value": 1})  # queued, no db call
    # make db still fail on drain
    sm.set_online(True)
    # drain attempted; failure => offline
    assert sm.status == "offline"
    assert len(sm.queue) >= 1


def test_sync_all():
    db = MagicMock()
    db.select.return_value = MagicMock(data=[])
    sm = SyncManager(db=db, online=True)
    out = sm.sync_all()
    assert isinstance(out, dict)
    assert "themes" in out
