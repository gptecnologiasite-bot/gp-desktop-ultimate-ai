"""Testes do módulo automation."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from automation import (
    find_files,
    organize_folder,
    delete_file,
    add_reminder,
    list_reminders,
    cancel_reminder,
    clear_reminders,
    AutomationManager,
)


def test_find_files(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "b.py").write_text("y")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("z")
    files = find_files(str(tmp_path), "*.txt", recursive=True)
    assert len(files) == 2
    files2 = find_files(str(tmp_path), "*.txt", recursive=False)
    assert len(files2) == 1


def test_organize_folder(tmp_path):
    (tmp_path / "img.png").write_text("x")
    (tmp_path / "doc.pdf").write_text("y")
    (tmp_path / "other.xyz").write_text("z")
    summary = organize_folder(str(tmp_path), dry_run=False)
    assert summary["moved"] == 3
    assert (tmp_path / "Imagens" / "img.png").exists()
    assert (tmp_path / "Documentos" / "doc.pdf").exists()
    assert (tmp_path / "Outros" / "other.xyz").exists()


def test_organize_dry_run(tmp_path):
    (tmp_path / "img.png").write_text("x")
    summary = organize_folder(str(tmp_path), dry_run=True)
    assert summary["moved"] == 1
    assert (tmp_path / "img.png").exists()
    assert not (tmp_path / "Imagens").exists()


def test_delete_file_confirm(tmp_path):
    f = tmp_path / "del.txt"
    f.write_text("x")
    # confirm false
    assert delete_file(str(f), confirm=lambda p: False) is False
    assert f.exists()
    # confirm true
    assert delete_file(str(f), confirm=lambda p: True) is True
    assert not f.exists()


def test_delete_file_missing():
    assert delete_file("/nao/existe/arquivo.txt") is False


def test_reminders():
    clear_reminders()
    rid = add_reminder("ola", 1000)
    assert rid in [r["id"] for r in list_reminders()]
    assert cancel_reminder(rid) is True
    assert rid not in [r["id"] for r in list_reminders()]


def test_automation_manager_delete_requires_confirm(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("x")
    mgr = AutomationManager(confirm=lambda msg: False)
    assert mgr.delete_file(str(f)) is False
    assert f.exists()
    mgr2 = AutomationManager(confirm=lambda msg: True)
    assert mgr2.delete_file(str(f)) is True
    assert not f.exists()


def test_automation_manager_find():
    mgr = AutomationManager(confirm=lambda m: True)
    with tempfile.TemporaryDirectory() as d:
        Path(d, "a.txt").write_text("x")
        res = mgr.find_files(d, "*.txt")
        assert len(res) == 1


def test_automation_manager_organize_cancel():
    mgr = AutomationManager(confirm=lambda m: False)
    r = mgr.organize_folder("/tmp/qualquer")
    assert r.get("cancelled") is True
