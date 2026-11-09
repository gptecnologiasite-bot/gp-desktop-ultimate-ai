"""Monitoramento de sistema baseado em psutil."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import psutil


class SystemMonitor:
    """Coleta métricas do sistema operacional."""

    def __init__(self, disk_path: str = "/"):
        self.disk_path = disk_path

    def get_cpu_percent(self, interval: Optional[float] = None) -> float:
        try:
            return float(psutil.cpu_percent(interval=interval))
        except Exception:
            return 0.0

    def get_ram(self) -> Dict[str, Any]:
        vm = psutil.virtual_memory()
        return {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent,
        }

    def get_disk(self, path: Optional[str] = None) -> Dict[str, Any]:
        target = path or self.disk_path
        # Windows: usar "C:\\" se "/" não existir
        if os.name == "nt" and target == "/":
            target = "C:\\"
        du = psutil.disk_usage(target)
        return {
            "path": target,
            "total": du.total,
            "used": du.used,
            "free": du.free,
            "percent": du.percent,
        }

    def get_network(self) -> Dict[str, Any]:
        io = psutil.net_io_counters()
        return {
            "bytes_sent": io.bytes_sent,
            "bytes_recv": io.bytes_recv,
            "packets_sent": io.packets_sent,
            "packets_recv": io.packets_recv,
            "errin": getattr(io, "errin", 0),
            "errout": getattr(io, "errout", 0),
        }

    def get_processes(
        self, top: int = 10, sort_by: str = "cpu"
    ) -> List[Dict[str, Any]]:
        procs: List[Dict[str, Any]] = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = p.info
                procs.append(
                    {
                        "pid": info.get("pid"),
                        "name": info.get("name"),
                        "cpu_percent": info.get("cpu_percent") or 0.0,
                        "memory_percent": info.get("memory_percent") or 0.0,
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
        procs.sort(key=lambda x: x.get(key, 0.0), reverse=True)
        return procs[:top]

    def get_temperatures(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        try:
            sensors = (
                psutil.sensors_temperatures()
                if hasattr(psutil, "sensors_temperatures")
                else None
            )
        except Exception:
            sensors = None
        if not sensors:
            return result
        for name, entries in sensors.items():
            result[name] = [
                {
                    "label": getattr(e, "label", "") or name,
                    "current": getattr(e, "current", None),
                    "high": getattr(e, "high", None),
                    "critical": getattr(e, "critical", None),
                }
                for e in (entries or [])
            ]
        return result

    def get_performance_summary(self) -> Dict[str, Any]:
        return {
            "cpu_percent": self.get_cpu_percent(),
            "ram": self.get_ram(),
            "disk": self.get_disk(),
            "network": self.get_network(),
            "temperatures": self.get_temperatures(),
            "top_processes": self.get_processes(top=5),
        }
