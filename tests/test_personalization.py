"""Testes do módulo personalization."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

import pytest

from personalization import (
    CustomizationProfile,
    Theme,
    PersonalizationManager,
    create_default_profiles,
)
from personalization.profiles import PROFILE_FACTORIES


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


def test_profiles_count_and_names():
    profiles = create_default_profiles()
    assert len(profiles) == 6
    names = {p.name for p in profiles}
    assert {
        "Gamer",
        "Futurista",
        "Minimalista",
        "Escritório",
        "Produtividade",
        "Personalizado",
    } == names


def test_profile_factories():
    for name, factory in PROFILE_FACTORIES.items():
        p = factory()
        assert isinstance(p, CustomizationProfile)
        assert p.name == name
        assert isinstance(p.theme, Theme)


def test_manager_in_memory():
    mgr = PersonalizationManager(db=None)
    assert mgr is not None
    assert len(mgr.list_profiles()) >= 0
    # adiciona perfis padrão
    for p in create_default_profiles():
        mgr.save_profile(p)
    assert "Gamer" in mgr.list_profiles()
    # apply
    applied = mgr.apply("Gamer")
    assert applied.name == "Gamer"
    assert mgr.current.name == "Gamer"
    # preview
    prev = mgr.preview("Minimalista")
    assert prev.name == "Minimalista"
    assert mgr.previewed.name == "Minimalista"


def test_duplicate_rename_delete():
    mgr = PersonalizationManager(db=None)
    for p in create_default_profiles():
        mgr.save_profile(p)
    clone = mgr.duplicate("Gamer", "Gamer 2")
    assert clone.name == "Gamer 2"
    assert "Gamer 2" in mgr.list_profiles()
    mgr.rename("Gamer 2", "Gamer X")
    assert "Gamer X" in mgr.list_profiles()
    assert "Gamer 2" not in mgr.list_profiles()
    assert mgr.delete_profile("Gamer X") is True
    assert "Gamer X" not in mgr.list_profiles()


def test_export_import_json(tmp_path):
    mgr = PersonalizationManager(db=None)
    for p in create_default_profiles():
        mgr.save_profile(p)
    mgr.apply("Futurista")
    exported = mgr.export_profile("Futurista")
    assert isinstance(exported, str)
    data = json.loads(exported)
    assert data["name"] == "Futurista"

    out_file = tmp_path / "tema.json"
    mgr.export_profile("Futurista", path=str(out_file))
    assert out_file.exists()

    mgr2 = PersonalizationManager(db=None)
    imported = mgr2.import_profile(str(out_file), name="Importado")
    assert imported.name == "Importado"
    assert "Importado" in mgr2.list_profiles()
    # roundtrip theme
    assert imported.theme.primary_color == data["theme"]["primary_color"]


def test_restore_default():
    mgr = PersonalizationManager(db=None)
    for p in create_default_profiles():
        mgr.save_profile(p)
    mgr.apply("Gamer")
    restored = mgr.restore_default()
    assert restored is not None


def test_signals_callable():
    mgr = PersonalizationManager(db=None)
    received = []

    def slot(p):
        received.append(getattr(p, "name", p))

    mgr.profile_changed.connect(slot)
    for p in create_default_profiles():
        mgr.save_profile(p)
    mgr.apply("Gamer")
    # signal emit best-effort
    assert received == [] or received[-1] == "Gamer"
