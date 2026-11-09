"""Testes do módulo widgets."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

import pytest

from widgets import BaseWidget, SystemWidget, WidgetManager


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


def test_base_widget_defaults():
    w = BaseWidget(title="T")
    assert w.title == "T"
    assert w.id
    cfg = w.to_config()
    assert cfg["title"] == "T"


def test_system_widget_refresh():
    sw = SystemWidget(title="Sistema")
    m = sw.refresh()
    assert "cpu_percent" in m
    assert "ram_percent" in m


def test_widget_manager_in_memory():
    wm = WidgetManager(db=None)
    w = wm.add(BaseWidget(title="W1"))
    assert w.id
    assert len(wm.list()) == 1

    wm.position(w.id, 10, 20)
    assert wm.list()[0].x == 10
    assert wm.list()[0].y == 20

    wm.size(w.id, 300, 150)
    assert wm.list()[0].width == 300
    assert wm.list()[0].height == 150

    wm.remove(w.id)
    assert len(wm.list()) == 0


def test_widget_manager_add_by_kwargs():
    wm = WidgetManager(db=None)
    w = wm.add(type="system", title="CPU")
    assert w.widget_type == "system"
    assert len(wm.list()) == 1


def test_widget_manager_persist_no_db():
    wm = WidgetManager(db=None)
    wm.add(BaseWidget(title="X"))
    assert wm.persist() is True
