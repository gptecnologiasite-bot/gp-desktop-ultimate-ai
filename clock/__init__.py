"""Módulo de relógio do GP Desktop Ultimate AI."""

from .models import ClockConfig
from .floating_clock import FloatingClock
from .manager import ClockManager

__all__ = ["ClockConfig", "FloatingClock", "ClockManager"]
