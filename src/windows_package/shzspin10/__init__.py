"""
SHZSpin10 Ultima Apex — Unified Quantum ToE Engine
==================================================

Unified monolithic SHZSpin10 engine v14.5-ULTIMA COSMOS UNIFIED.

Laboratories:
  - Base Engine v13.6
  - Ultima Frontiers (BH, Yukawa, E8, TQEC)
  - Enterprise HPC / Quantum Bridge / SciML
  - Physics Apex (LQG Spin Foam EPRL, SM RGE Derivation)
  - Cloud SaaS API (6 microservices)
  - Cosmology (Big Bang, Inflation, FRW, CMB, Matter P(k))

Usage:
    >>> from shzspin10 import SHZSpin10UltimaApex
    >>> engine = SHZSpin10UltimaApex()
    >>> report = engine.run_ultima_simulation()
    >>> engine.display_ultima_dashboard(report)
"""

__version__ = "14.5.0"
__author__ = "SHZ Quantum Technologies Unified Kernel Team"

from .engine import SHZSpin10UltimaApex

__all__ = ["SHZSpin10UltimaApex"]

try:
    from .menu import main_menu
    from .cli import open_dashboard
    __all__ += ["main_menu", "open_dashboard"]
except ImportError:
    pass
