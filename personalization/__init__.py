"""Módulo de personalização do GP Desktop Ultimate AI."""

from .models import (
    Theme,
    AppearanceProfile,
    LayoutConfig,
    DesktopConfig,
    CustomizationProfile,
)
from .manager import PersonalizationManager
from .profiles import (
    create_default_profiles,
    get_profile_factory,
    DEFAULT_PROFILES,
    PROFILE_FACTORIES,
    gamer_profile,
    futurista_profile,
    minimalista_profile,
    escritorio_profile,
    produtividade_profile,
    personalizado_profile,
)

__all__ = [
    "Theme",
    "AppearanceProfile",
    "LayoutConfig",
    "DesktopConfig",
    "CustomizationProfile",
    "PersonalizationManager",
    "create_default_profiles",
    "get_profile_factory",
    "DEFAULT_PROFILES",
    "PROFILE_FACTORIES",
    "gamer_profile",
    "futurista_profile",
    "minimalista_profile",
    "escritorio_profile",
    "produtividade_profile",
    "personalizado_profile",
]
