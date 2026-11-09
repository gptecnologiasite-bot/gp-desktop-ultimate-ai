"""Modelos de personalização do GP Desktop Ultimate AI."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class Theme:
    name: str = "default"
    primary_color: str = "#6366f1"
    secondary_color: str = "#8b5cf6"
    accent_color: str = "#22d3ee"
    background_color: str = "#0f172a"
    surface_color: str = "#1e293b"
    text_color: str = "#f8fafc"
    text_secondary_color: str = "#94a3b8"
    font_family: str = "Segoe UI"
    font_size: int = 14
    transparency: float = 0.92
    border_radius: int = 12
    animations_enabled: bool = True
    animation_speed: float = 1.0
    shadow_enabled: bool = True
    blur_enabled: bool = True
    density: str = "comfortable"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Theme":
        if not data:
            return cls()
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class LayoutConfig:
    menu_position: str = "left"
    menu_collapsed: bool = False
    sidebar_width: int = 260
    show_widgets: bool = True
    widgets: List[str] = field(default_factory=list)
    grid_columns: int = 4
    spacing: int = 8
    compact_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None) -> "LayoutConfig":
        if not data:
            return cls()
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class DesktopConfig:
    wallpaper: str = ""
    icon_size: int = 48
    show_desktop_icons: bool = True
    shortcuts: List[Dict[str, Any]] = field(default_factory=list)
    snap_to_grid: bool = True
    grid_size: int = 20
    dark_mode: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None) -> "DesktopConfig":
        if not data:
            return cls()
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class AppearanceProfile:
    id: str = ""
    name: str = "Personalizado"
    description: str = ""
    theme: Theme = field(default_factory=Theme)
    ui_scale: float = 1.0
    cursor_size: int = 1
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["theme"] = self.theme.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None) -> "AppearanceProfile":
        if not data:
            return cls()
        data = dict(data)
        if "theme" in data and isinstance(data["theme"], dict):
            data["theme"] = Theme.from_dict(data["theme"])
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class CustomizationProfile:
    profile_id: str = ""
    name: str = "Personalizado"
    description: str = ""
    theme: Theme = field(default_factory=Theme)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    desktop: DesktopConfig = field(default_factory=DesktopConfig)
    appearance: Optional[AppearanceProfile] = None
    tags: List[str] = field(default_factory=list)
    is_default: bool = False
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.profile_id:
            self.profile_id = self.name.lower().replace(" ", "-")
        if self.appearance is not None and isinstance(self.appearance, dict):
            self.appearance = AppearanceProfile.from_dict(self.appearance)
        if isinstance(self.theme, dict):
            self.theme = Theme.from_dict(self.theme)
        if isinstance(self.layout, dict):
            self.layout = LayoutConfig.from_dict(self.layout)
        if isinstance(self.desktop, dict):
            self.desktop = DesktopConfig.from_dict(self.desktop)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "theme": self.theme.to_dict(),
            "layout": self.layout.to_dict(),
            "desktop": self.desktop.to_dict(),
            "appearance": self.appearance.to_dict() if self.appearance else None,
            "tags": list(self.tags),
            "is_default": self.is_default,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None) -> "CustomizationProfile":
        if not data:
            return cls()
        data = dict(data)
        if "theme" in data and isinstance(data["theme"], dict):
            data["theme"] = Theme.from_dict(data["theme"])
        if "layout" in data and isinstance(data["layout"], dict):
            data["layout"] = LayoutConfig.from_dict(data["layout"])
        if "desktop" in data and isinstance(data["desktop"], dict):
            data["desktop"] = DesktopConfig.from_dict(data["desktop"])
        if "appearance" in data and isinstance(data["appearance"], dict):
            data["appearance"] = AppearanceProfile.from_dict(data["appearance"])
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})
