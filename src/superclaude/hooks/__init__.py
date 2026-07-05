"""SuperClaude Hooks Module

v2.1.0 Features:
- inline_hooks: Frontmatter parsing (parse_frontmatter)
- hook_tracker: Fallback session identity + stale-session cleanup
  (once-per-session hook gating is CC-native `once: true`)
"""

from superclaude.hooks.hook_tracker import (
    cleanup_old_sessions,
    get_session_id,
)
from superclaude.hooks.inline_hooks import parse_frontmatter

__all__ = [
    # hook_tracker
    "get_session_id",
    "cleanup_old_sessions",
    # inline_hooks
    "parse_frontmatter",
]
