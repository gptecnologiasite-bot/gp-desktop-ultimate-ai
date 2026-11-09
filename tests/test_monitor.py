"""Testes do módulo monitor."""

import os
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from monitor import SystemMonitor, MonitorManager


class FakeVM:
    total = 16000
    available = 8000
    used = 8000
    percent = 50.0


class FakeDU:
    total = 1000
    used = 400
    free = 600
    percent = 40.0


class FakeIO:
    bytes_sent = 10
    bytes_recv = 20
    packets_sent = 1
    packets_recv = 2
    errin = 0
    errout = 0


def test_get_cpu_percent(monkeypatch):
    import monitor.system_monitor as sm

    monkeypatch.setattr(sm.psutil, "cpu_percent", lambda interval=None: 12.5)
    m = SystemMonitor()
    assert m.get_cpu_percent() == 12.5


def test_get_ram(monkeypatch):
    import monitor.system_monitor as sm

    monkeypatch.setattr(sm.psutil, "virtual_memory", lambda: FakeVM())
    m = SystemMonitor()
    r = m.get_ram()
    assert r["total"] == 16000
    assert r["percent"] == 50.0


def test_get_disk(monkeypatch):
    import monitor.system_monitor as sm

    monkeypatch.setattr(sm.psutil, "disk_usage", lambda path: FakeDU())
    m = SystemMonitor(disk_path="C:\\")
    d = m.get_disk()
    assert d["total"] == 1000
    assert d["percent"] == 40.0


def test_get_network(monkeypatch):
    import monitor.system_monitor as sm

    monkeypatch.setattr(sm.psutil, "net_io_counters", lambda: FakeIO())
    m = SystemMonitor()
    n = m.get_network()
    assert n["bytes_sent"] == 10
    assert n["bytes_recv"] == 20


def test_get_processes(monkeypatch):
    import monitor.system_monitor as sm

    class FakeProc:
        def __init__(self, info):
            self.info = info

    def fake_iter(attrs):
        return [
            FakeProc(
                {"pid": 1, "name": "a", "cpu_percent": 10.0, "memory_percent": 5.0}
            ),
            FakeProc(
                {"pid": 2, "name": "b", "cpu_percent": 2.0, "memory_percent": 1.0}
            ),
        ]

    monkeypatch.setattr(sm.psutil, "process_iter", fake_iter)
    m = SystemMonitor()
    procs = m.get_processes(top=1)
    assert len(procs) == 1
    assert procs[0]["pid"] == 1


def test_get_temperatures_empty(monkeypatch):
    import monitor.system_monitor as sm

    monkeypatch.setattr(sm.psutil, "sensors_temperatures", lambda: None, raising=False)
    m = SystemMonitor()
    assert m.get_temperatures() == {}


def test_get_temperatures_data(monkeypatch):
    import monitor.system_monitor as sm

    class E:
        label = "CPU"
        current = 50.0
        high = 80.0
        critical = 100.0

    monkeypatch.setattr(
        sm.psutil, "sensors_temperatures", lambda: {"cpu": [E()]}, raising=False
    )
    m = SystemMonitor()
    t = m.get_temperatures()
    assert "cpu" in t
    assert t["cpu"][0]["current"] == 50.0


def test_performance_summary(monkeypatch):
    import monitor.system_monitor as sm

    monkeypatch.setattr(sm.psutil, "cpu_percent", lambda interval=None: 1.0)
    monkeypatch.setattr(sm.psutil, "virtual_memory", lambda: FakeVM())
    monkeypatch.setattr(sm.psutil, "disk_usage", lambda path: FakeDU())
    monkeypatch.setattr(sm.psutil, "net_io_counters", lambda: FakeIO())
    monkeypatch.setattr(sm.psutil, "sensors_temperatures", lambda: None, raising=False)
    monkeypatch.setattr(sm.psutil, "process_iter", lambda attrs: [])
    m = SystemMonitor(disk_path="C:\\")
    s = m.get_performance_summary()
    assert "cpu_percent" in s
    assert "ram" in s
    assert "disk" in s


def test_monitor_manager_start_stop():
    mm = MonitorManager(interval_ms=10)
    assert not mm.is_running()
    # avoid real polling thread heavy: start then stop quickly
    mm.start()
    assert mm.is_running()
    mm.stop()
    assert not mm.is_running()


def test_monitor_manager_poll_once(monkeypatch):
    import monitor.system_monitor as sm

    monkeypatch.setattr(sm.psutil, "cpu_percent", lambda interval=None: 0.0)
    monkeypatch.setattr(sm.psutil, "virtual_memory", lambda: FakeVM())
    monkeypatch.setattr(sm.psutil, "disk_usage", lambda path: FakeDU())
    monkeypatch.setattr(sm.psutil, "net_io_counters", lambda: FakeIO())
    monkeypatch.setattr(sm.psutil, "sensors_temperatures", lambda: None, raising=False)
    monkeypatch.setattr(sm.psutil, "process_iter", lambda attrs: [])
    mm = MonitorManager(interval_ms=10)
    received = []
    mm.data_updated.connect(lambda d: received.append(d))
    mm.poll_once()
    assert len(received) == 1
