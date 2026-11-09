"""Perfis de personalização prontos (factory)."""

from __future__ import annotations

from .models import (
    CustomizationProfile,
    Theme,
    LayoutConfig,
    DesktopConfig,
    AppearanceProfile,
)


def gamer_profile() -> CustomizationProfile:
    return CustomizationProfile(
        name="Gamer",
        description="Visual neon, compacto e animado para jogos.",
        theme=Theme(
            name="Gamer",
            primary_color="#7c3aed",
            secondary_color="#ec4899",
            accent_color="#22d3ee",
            background_color="#0b0f1a",
            surface_color="#111827",
            text_color="#f9fafb",
            font_family="Rajdhani",
            font_size=13,
            transparency=0.88,
            border_radius=8,
            animations_enabled=True,
            animation_speed=1.4,
            blur_enabled=True,
            density="compact",
        ),
        layout=LayoutConfig(
            menu_position="left",
            sidebar_width=220,
            show_widgets=True,
            widgets=["fps", "cpu", "gpu"],
            compact_mode=True,
        ),
        desktop=DesktopConfig(dark_mode=True, icon_size=40),
        tags=["gamer", "dark", "neon"],
    )


def futurista_profile() -> CustomizationProfile:
    return CustomizationProfile(
        name="Futurista",
        description="Estética futurista com blur e arredondamento.",
        theme=Theme(
            name="Futurista",
            primary_color="#06b6d4",
            secondary_color="#8b5cf6",
            accent_color="#f472b6",
            background_color="#020617",
            surface_color="#0f172a",
            text_color="#e2e8f0",
            font_family="Orbitron",
            font_size=14,
            transparency=0.85,
            border_radius=18,
            animations_enabled=True,
            animation_speed=1.1,
            blur_enabled=True,
            shadow_enabled=True,
        ),
        layout=LayoutConfig(menu_position="left", sidebar_width=280, spacing=12),
        desktop=DesktopConfig(dark_mode=True, icon_size=52),
        tags=["futurista", "blur"],
    )


def minimalista_profile() -> CustomizationProfile:
    return CustomizationProfile(
        name="Minimalista",
        description="Limpo, claro e sem distrações.",
        theme=Theme(
            name="Minimalista",
            primary_color="#111827",
            secondary_color="#374151",
            accent_color="#2563eb",
            background_color="#f9fafb",
            surface_color="#ffffff",
            text_color="#111827",
            text_secondary_color="#6b7280",
            font_family="Inter",
            font_size=14,
            transparency=1.0,
            border_radius=6,
            animations_enabled=False,
            animation_speed=0.0,
            shadow_enabled=False,
            blur_enabled=False,
            density="spacious",
        ),
        layout=LayoutConfig(menu_position="top", compact_mode=False, spacing=16),
        desktop=DesktopConfig(dark_mode=False, icon_size=44),
        tags=["minimalista", "light"],
    )


def escritorio_profile() -> CustomizationProfile:
    return CustomizationProfile(
        name="Escritório",
        description="Profissional para ambiente corporativo.",
        theme=Theme(
            name="Escritório",
            primary_color="#1d4ed8",
            secondary_color="#1e40af",
            accent_color="#0ea5e9",
            background_color="#f1f5f9",
            surface_color="#ffffff",
            text_color="#0f172a",
            font_family="Calibri",
            font_size=14,
            transparency=1.0,
            border_radius=8,
            animations_enabled=True,
            animation_speed=0.8,
            density="comfortable",
        ),
        layout=LayoutConfig(menu_position="left", sidebar_width=250),
        desktop=DesktopConfig(dark_mode=False, icon_size=48),
        tags=["escritorio", "profissional"],
    )


def produtividade_profile() -> CustomizationProfile:
    return CustomizationProfile(
        name="Produtividade",
        description="Foco em tarefas e widgets de produtividade.",
        theme=Theme(
            name="Produtividade",
            primary_color="#059669",
            secondary_color="#10b981",
            accent_color="#f59e0b",
            background_color="#0b1220",
            surface_color="#111827",
            text_color="#f9fafb",
            font_family="Segoe UI",
            font_size=13,
            transparency=0.9,
            border_radius=10,
            animations_enabled=True,
            animation_speed=0.9,
            density="compact",
        ),
        layout=LayoutConfig(
            menu_position="left",
            show_widgets=True,
            widgets=["tasks", "calendar", "notes"],
            compact_mode=True,
        ),
        desktop=DesktopConfig(dark_mode=True, icon_size=42),
        tags=["produtividade", "tasks"],
    )


def personalizado_profile() -> CustomizationProfile:
    return CustomizationProfile(
        name="Personalizado",
        description="Perfil personalizável pelo usuário.",
        theme=Theme(name="Personalizado"),
        layout=LayoutConfig(),
        desktop=DesktopConfig(),
        is_default=True,
        tags=["personalizado"],
    )


PROFILE_FACTORIES = {
    "Gamer": gamer_profile,
    "Futurista": futurista_profile,
    "Minimalista": minimalista_profile,
    "Escritório": escritorio_profile,
    "Produtividade": produtividade_profile,
    "Personalizado": personalizado_profile,
}


def create_default_profiles() -> list[CustomizationProfile]:
    return [factory() for factory in PROFILE_FACTORIES.values()]


def get_profile_factory(name: str):
    return PROFILE_FACTORIES.get(name)


DEFAULT_PROFILES = create_default_profiles()
