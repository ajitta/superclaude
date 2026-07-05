"""SuperClaude Hooks Module

v2.1.0 Features:
- inline_hooks: Parse inline hooks from frontmatter
- hook_tracker: Fallback session identity + stale-session cleanup
  (once-per-session hook gating is CC-native `once: true`)
"""

from superclaude.hooks.hook_tracker import (
    cleanup_old_sessions,
    get_session_id,
)
from superclaude.hooks.inline_hooks import (
    InlineHook,
    InlineHooks,
    get_skill_agent,
    get_skill_context,
    parse_frontmatter,
    parse_inline_hooks,
    parse_skill_frontmatter,
)

__all__ = [
    # hook_tracker
    "get_session_id",
    "cleanup_old_sessions",
    # inline_hooks
    "InlineHook",
    "InlineHooks",
    "parse_frontmatter",
    "parse_inline_hooks",
    "parse_skill_frontmatter",
    "get_skill_context",
    "get_skill_agent",
]
