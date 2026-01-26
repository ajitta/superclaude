"""
SuperClaude Installation — Re-export Facade

This module re-exports all public symbols from the focused submodules
so that existing imports (main.py, tests) continue to work unchanged.

Submodules:
- install_paths: Path resolution (COMPONENTS, get_base_path, etc.)
- install_settings: Settings, hooks & CLAUDE.md management
- install_components: Component installation & orchestration
- install_inventory: Listing & uninstallation
"""

# Path resolution
# Component installation & orchestration
from .install_components import install_all, install_commands  # noqa: F401

# Listing & uninstallation
from .install_inventory import (  # noqa: F401
    list_all_components,
    list_available_commands,
    list_installed_commands,
    uninstall_all,
)
from .install_paths import COMPONENTS, get_base_path  # noqa: F401

# Settings, hooks & CLAUDE.md
from .install_settings import CLAUDE_SC_IMPORT, SUPERCLAUDE_HOOK_MARKERS  # noqa: F401

__all__ = [
    # Path resolution
    "COMPONENTS",
    "get_base_path",
    # Settings & hooks
    "CLAUDE_SC_IMPORT",
    "SUPERCLAUDE_HOOK_MARKERS",
    # Installation
    "install_all",
    "install_commands",
    # Listing & uninstallation
    "list_all_components",
    "list_available_commands",
    "list_installed_commands",
    "uninstall_all",
]
