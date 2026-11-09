"""Modelos do módulo clock do GP Desktop Ultimate AI."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional


def _now() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class ClockConfig:
    id: str = ""
    name: str = "Relógio"
    format_12_24: bool = False
    show_seconds: bool = True
    show_date: bool = True
    font_family: str = "Segoe UI"
    font_size: int = 28
    color: str = "#ffffff"
    transparency: float = 0.85
    width: int = 260
    height: int = 100
    x: int = 100
    y: int = 100
    always_on_top: bool = True
    style: str = "digital"

    def __post_init__(self):
        if self.style not in ("digital", "futuristic"):
            self.style = "digital"
        if not self.id:
            import uuid

            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None) -> "ClockConfig":
        if not data:
            return cls()
        data = dict(data)
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})
