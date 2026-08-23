"""SuperClaude Hooks Module

v2.1.0 Features:
- inline_hooks: Frontmatter parsing (parse_frontmatter)
- hook_tracker: Fallback session identity + stale-session cleanup
  (once-per-session hook gating is CC-native `once: true`)

Re-exports resolve lazily (PEP 562). Importing any submodule of this package
runs this file first, so eager re-exports made every consumer pay for both
submodules: `context_loader.py` reaches `mcp_fallback` on every prompt and was
loading `inline_hooks` -> `yaml` (7.8ms) for a `parse_frontmatter` it never
calls. No caller imports these names from the package -- every one of them
imports the submodule directly -- so the names are kept only to preserve the
documented API.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superclaude.hooks.hook_tracker import cleanup_old_sessions, get_session_id
    from superclaude.hooks.inline_hooks import parse_frontmatter

__all__ = [
    # hook_tracker
    "get_session_id",
    "cleanup_old_sessions",
    # inline_hooks
    "parse_frontmatter",
]

_LAZY = {
    "get_session_id": "superclaude.hooks.hook_tracker",
    "cleanup_old_sessions": "superclaude.hooks.hook_tracker",
    "parse_frontmatter": "superclaude.hooks.inline_hooks",
}


def __getattr__(name: str):
    """Import the owning submodule on first attribute access."""
    module_name = _LAZY.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    return getattr(importlib.import_module(module_name), name)


def __dir__() -> list[str]:
    return sorted(__all__)
