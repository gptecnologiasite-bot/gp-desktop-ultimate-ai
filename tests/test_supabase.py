import os
import pathlib

import pytest

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon-key")

from supabase import (
    get_supabase_client,
    reset_client,
    AuthManager,
    DatabaseManager,
    StorageManager,
    RealtimeManager,
    EdgeFunctionsManager,
    TABLES,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_client()
    yield
    reset_client()


def test_get_client_singleton():
    c1 = get_supabase_client()
    c2 = get_supabase_client()
    assert c1 is c2


def test_reset_client():
    c1 = get_supabase_client()
    reset_client()
    c2 = get_supabase_client()
    assert c1 is not c2


def test_auth_manager_instantiation():
    am = AuthManager()
    assert am.auth is not None


def test_database_manager_tables():
    dm = DatabaseManager()
    assert dm is not None
    assert "users" in TABLES
    assert "devices" in TABLES
    assert len(TABLES) == 13


def test_database_select_invalid_table():
    dm = DatabaseManager()
    with pytest.raises(ValueError):
        dm.select("nope")


def test_storage_manager_instantiation():
    sm = StorageManager()
    assert sm is not None


def test_realtime_manager_instantiation():
    rm = RealtimeManager()
    assert rm is not None


def test_edge_functions_manager_instantiation():
    em = EdgeFunctionsManager()
    assert em is not None


def test_sql_migration_non_empty():
    base = pathlib.Path(__file__).resolve().parents[1]
    sql_path = base / "migrations" / "0001_init.sql"
    assert sql_path.exists()
    content = sql_path.read_text(encoding="utf-8")
    assert len(content.strip()) > 0
    assert "create table" in content.lower()
    assert "enable row level security" in content.lower()
