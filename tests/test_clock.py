"""Testes do módulo clock."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

import pytest

from clock import ClockConfig, ClockManager, FloatingClock


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


def test_clock_config_defaults_and_roundtrip():
    cfg = ClockConfig()
    assert cfg.style in ("digital", "futuristic")
    d = cfg.to_dict()
    cfg2 = ClockConfig.from_dict(d)
    assert cfg2.id == cfg.id
    assert cfg2.font_size == cfg.font_size


def test_clock_config_invalid_style():
    cfg = ClockConfig(style="foo")
    assert cfg.style == "digital"


def test_manager_in_memory():
    mgr = ClockManager(db=None)
    assert mgr is not None
    cfg = mgr.create(name="Relógio Teste", font_size=24)
    assert cfg.id
    assert cfg.font_size == 24
    assert len(mgr.list()) == 1

    updated = mgr.update(cfg.id, font_size=32)
    assert updated.font_size == 32
    assert mgr.list()[0].font_size == 32

    assert mgr.remove(cfg.id) is not False
    assert len(mgr.list()) == 0


def test_manager_save_load():
    mgr = ClockManager(db=None)
    cfg = ClockConfig(name="X")
    assert mgr.save(cfg) is True
    assert cfg.id in {c.id for c in mgr.list()}


def test_floating_clock_instantiation():
    fc = FloatingClock({"font_size": 20})
    assert fc is not None
    assert fc.config.font_size == 20
    fc.apply_config({"font_size": 30})
    assert fc.config.font_size == 30
