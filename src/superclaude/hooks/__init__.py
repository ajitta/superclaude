"""SuperClaude Hooks Module

v2.1.0 Features:
- inline_hooks: Parse inline hooks from frontmatter
- hook_tracker: Session-based hook execution tracking (once: true support)
"""

from superclaude.hooks.hook_tracker import (
    check_and_mark,
    cleanup_old_sessions,
    get_session_id,
    get_session_stats,
    has_executed_once,
    mark_executed,
    reset_session,
    should_execute_hook,
)
from superclaude.hooks.inline_hooks import (
    InlineHook,
    InlineHooks,
    get_allowed_tools,
    get_skill_agent,
    get_skill_context,
    is_tool_allowed,
    is_user_invocable,
    parse_frontmatter,
    parse_inline_hooks,
    parse_skill_frontmatter,
)

__all__ = [
    # hook_tracker
    "get_session_id",
    "has_executed_once",
    "mark_executed",
    "should_execute_hook",
    "check_and_mark",
    "cleanup_old_sessions",
    "reset_session",
    "get_session_stats",
    # inline_hooks
    "InlineHook",
    "InlineHooks",
    "parse_frontmatter",
    "parse_inline_hooks",
    "parse_skill_frontmatter",
    "get_skill_context",
    "get_skill_agent",
    "is_user_invocable",
    "get_allowed_tools",
    "is_tool_allowed",
]
