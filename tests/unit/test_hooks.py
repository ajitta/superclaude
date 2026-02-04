"""Unit tests for SuperClaude hooks module.

Tests hook_tracker.py and inline_hooks.py functionality.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


class TestHookTracker:
    """Tests for hook_tracker.py functionality."""

    @pytest.fixture
    def temp_tracker_dir(self, tmp_path: Path):
        """Create temporary tracker directory for testing."""
        tracker_dir = tmp_path / ".superclaude_hooks"
        tracker_dir.mkdir(parents=True)

        with patch(
            "superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir
        ), patch(
            "superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE",
            tracker_dir / "hook_executions.json",
        ), patch(
            "superclaude.hooks.hook_tracker.SESSION_FILE",
            tracker_dir / "current_session.txt",
        ):
            yield tracker_dir

    def test_get_session_id_generates_id(self, temp_tracker_dir: Path):
        """Test that session ID is generated when none exists."""
        from superclaude.hooks.hook_tracker import get_session_id

        session_id = get_session_id()
        assert session_id is not None
        assert len(session_id) == 16  # SHA256 truncated to 16 chars

    def test_session_id_is_cached(self, temp_tracker_dir: Path):
        """Test that session ID remains consistent within session."""
        from superclaude.hooks.hook_tracker import get_session_id

        session1 = get_session_id()
        session2 = get_session_id()
        assert session1 == session2

    def test_has_executed_once_returns_false_initially(
        self, temp_tracker_dir: Path
    ):
        """Test that hook shows as not executed initially."""
        from superclaude.hooks.hook_tracker import has_executed_once

        result = has_executed_once(
            hook_type="PreToolUse",
            command="echo test",
            source="test-skill",
        )
        assert result is False

    def test_mark_executed_records_execution(self, temp_tracker_dir: Path):
        """Test that marking execution is recorded."""
        from superclaude.hooks.hook_tracker import (
            has_executed_once,
            mark_executed,
        )

        mark_executed(
            hook_type="PreToolUse",
            command="echo test",
            source="test-skill",
        )

        result = has_executed_once(
            hook_type="PreToolUse",
            command="echo test",
            source="test-skill",
        )
        assert result is True

    def test_should_execute_hook_with_once_false(self, temp_tracker_dir: Path):
        """Test that hooks without once=true always execute."""
        from superclaude.hooks.hook_tracker import (
            mark_executed,
            should_execute_hook,
        )

        # Mark as executed
        mark_executed(
            hook_type="PostToolUse",
            command="echo cleanup",
            source="cleanup-skill",
        )

        # Should still return True when once=False
        result = should_execute_hook(
            hook_type="PostToolUse",
            command="echo cleanup",
            source="cleanup-skill",
            once=False,
        )
        assert result is True

    def test_should_execute_hook_with_once_true(self, temp_tracker_dir: Path):
        """Test that once=true hooks only execute once."""
        from superclaude.hooks.hook_tracker import (
            mark_executed,
            should_execute_hook,
        )

        # First check - should execute
        result1 = should_execute_hook(
            hook_type="SessionStart",
            command="python init.py",
            source="hooks.json",
            once=True,
        )
        assert result1 is True

        # Mark as executed
        mark_executed(
            hook_type="SessionStart",
            command="python init.py",
            source="hooks.json",
        )

        # Second check - should NOT execute
        result2 = should_execute_hook(
            hook_type="SessionStart",
            command="python init.py",
            source="hooks.json",
            once=True,
        )
        assert result2 is False

    def test_check_and_mark_atomic(self, temp_tracker_dir: Path):
        """Test check_and_mark performs atomic check-and-mark."""
        from superclaude.hooks.hook_tracker import check_and_mark

        # First call - should return True and mark
        result1 = check_and_mark(
            hook_type="PreToolUse",
            command="validate.py",
            source="confidence-check",
            once=True,
        )
        assert result1 is True

        # Second call - should return False (already marked)
        result2 = check_and_mark(
            hook_type="PreToolUse",
            command="validate.py",
            source="confidence-check",
            once=True,
        )
        assert result2 is False

    def test_get_session_stats(self, temp_tracker_dir: Path):
        """Test session statistics retrieval."""
        from superclaude.hooks.hook_tracker import (
            get_session_stats,
            mark_executed,
        )

        # Mark some executions
        mark_executed("PreToolUse", "cmd1", "skill1")
        mark_executed("PreToolUse", "cmd2", "skill2")
        mark_executed("PostToolUse", "cmd3", "skill3")

        stats = get_session_stats()
        assert stats["hooks_executed"] == 3
        assert stats["hook_types"]["PreToolUse"] == 2
        assert stats["hook_types"]["PostToolUse"] == 1

    def test_reset_session(self, temp_tracker_dir: Path):
        """Test session reset generates new ID."""
        from superclaude.hooks.hook_tracker import get_session_id, reset_session

        _ = get_session_id()  # Initialize session first
        new_session = reset_session()

        # New session should be generated
        assert new_session is not None
        assert len(new_session) == 16

    def test_different_matchers_tracked_separately(
        self, temp_tracker_dir: Path
    ):
        """Test that hooks with different matchers are tracked separately."""
        from superclaude.hooks.hook_tracker import (
            has_executed_once,
            mark_executed,
        )

        # Mark with one matcher
        mark_executed(
            hook_type="PreToolUse",
            command="echo test",
            source="test-skill",
            matcher="WebFetch",
        )

        # Should show as executed with same matcher
        assert (
            has_executed_once(
                hook_type="PreToolUse",
                command="echo test",
                source="test-skill",
                matcher="WebFetch",
            )
            is True
        )

        # Should NOT show as executed with different matcher
        assert (
            has_executed_once(
                hook_type="PreToolUse",
                command="echo test",
                source="test-skill",
                matcher="WebSearch",
            )
            is False
        )


class TestMcpFallback:
    """Tests for mcp_fallback.py functionality."""

    def test_cleanup_old_fallback_sessions_uses_latest_timestamp(self, tmp_path: Path):
        """Test that cleanup uses the latest timestamp across all MCPs in a session."""
        import json
        from datetime import datetime, timedelta
        from unittest.mock import patch

        fallback_file = tmp_path / "mcp_fallbacks.json"
        tracker_dir = tmp_path

        old_time = (datetime.now() - timedelta(hours=48)).isoformat()
        recent_time = datetime.now().isoformat()

        # Session has one old and one recent MCP timestamp
        data = {
            "session-old": {
                "context7": old_time,
                "tavily": old_time,
            },
            "session-mixed": {
                "context7": old_time,
                "tavily": recent_time,  # This is recent — session should survive
            },
        }
        fallback_file.write_text(json.dumps(data))

        with patch(
            "superclaude.hooks.mcp_fallback.MCP_FALLBACK_FILE", fallback_file
        ), patch(
            "superclaude.hooks.mcp_fallback._ensure_tracker_dir",
            lambda: None,
        ):
            from superclaude.hooks.mcp_fallback import cleanup_old_fallback_sessions

            cleaned = cleanup_old_fallback_sessions(ttl_seconds=24 * 60 * 60)

        # Only session-old should be cleaned; session-mixed has a recent timestamp
        assert cleaned == 1
        remaining = json.loads(fallback_file.read_text())
        assert "session-old" not in remaining
        assert "session-mixed" in remaining


class TestInlineHooks:
    """Tests for inline_hooks.py functionality."""

    def test_parse_frontmatter_basic(self):
        """Test basic frontmatter parsing."""
        from superclaude.hooks.inline_hooks import parse_frontmatter

        content = """---
name: test-skill
description: A test skill
---
Content here
"""
        fm = parse_frontmatter(content)
        assert fm["name"] == "test-skill"
        assert fm["description"] == "A test skill"

    def test_parse_frontmatter_with_lists(self):
        """Test frontmatter parsing with YAML lists."""
        from superclaude.hooks.inline_hooks import parse_frontmatter

        content = """---
name: test-skill
allowed-tools:
  - Read
  - Grep
  - WebFetch
---
"""
        fm = parse_frontmatter(content)
        assert fm["name"] == "test-skill"
        assert fm["allowed-tools"] == ["Read", "Grep", "WebFetch"]

    def test_parse_inline_hooks(self):
        """Test inline hooks parsing with nested (Claude Code native) format."""
        from superclaude.hooks.inline_hooks import parse_inline_hooks

        fm = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "WebFetch|WebSearch",
                        "hooks": [
                            {"type": "command", "command": "echo pre", "once": True}
                        ],
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "Write",
                        "hooks": [
                            {"type": "command", "command": "echo post"}
                        ],
                    }
                ],
            }
        }

        hooks = parse_inline_hooks(fm)
        assert hooks.has_hooks() is True
        assert len(hooks.pre_tool_use) == 1
        assert len(hooks.post_tool_use) == 1
        assert hooks.pre_tool_use[0].once is True
        assert hooks.pre_tool_use[0].matcher == "WebFetch|WebSearch"
        assert hooks.post_tool_use[0].once is False
        assert hooks.post_tool_use[0].matcher == "Write"

    def test_parse_inline_hooks_flat_format_legacy(self):
        """Test inline hooks parsing with flat (legacy) format for backward compat."""
        from superclaude.hooks.inline_hooks import parse_inline_hooks

        fm = {
            "hooks": {
                "PreToolUse": [
                    {
                        "type": "command",
                        "command": "echo pre",
                        "matcher": "Bash",
                        "once": True,
                    }
                ],
                "PostToolUse": [
                    {"type": "command", "command": "echo post"}
                ],
            }
        }

        hooks = parse_inline_hooks(fm)
        assert hooks.has_hooks() is True
        assert len(hooks.pre_tool_use) == 1
        assert hooks.pre_tool_use[0].matcher == "Bash"
        assert hooks.pre_tool_use[0].once is True
        assert len(hooks.post_tool_use) == 1
        assert hooks.post_tool_use[0].once is False

    def test_parse_inline_hooks_nested_no_matcher(self):
        """Test nested format without matcher (e.g. Stop hooks)."""
        from superclaude.hooks.inline_hooks import parse_inline_hooks

        fm = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {"type": "command", "command": "python cleanup.py"}
                        ],
                    }
                ],
            }
        }

        hooks = parse_inline_hooks(fm)
        assert hooks.has_hooks() is True
        assert len(hooks.stop) == 1
        assert hooks.stop[0].command == "python cleanup.py"
        assert hooks.stop[0].matcher is None

    def test_to_claude_code_format(self):
        """Test conversion to Claude Code's native nested format."""
        from superclaude.hooks.inline_hooks import InlineHook, InlineHooks

        hooks = InlineHooks(
            pre_tool_use=[
                InlineHook(
                    type="command",
                    command="python validate.py",
                    matcher="WebFetch|WebSearch",
                    timeout=30,
                    once=True,
                )
            ],
            stop=[
                InlineHook(
                    type="command",
                    command="python cleanup.py",
                    matcher=None,
                )
            ],
        )

        fmt = hooks.to_claude_code_format()
        assert "PreToolUse" in fmt
        assert "Stop" in fmt
        assert "PostToolUse" not in fmt

        pre = fmt["PreToolUse"]
        assert len(pre) == 1
        assert pre[0]["matcher"] == "WebFetch|WebSearch"
        assert len(pre[0]["hooks"]) == 1
        assert pre[0]["hooks"][0]["command"] == "python validate.py"
        assert pre[0]["hooks"][0]["once"] is True
        # matcher should not be in the inner hook dict
        assert "matcher" not in pre[0]["hooks"][0]

        stop = fmt["Stop"]
        assert len(stop) == 1
        assert "matcher" not in stop[0]
        assert stop[0]["hooks"][0]["command"] == "python cleanup.py"

    def test_get_skill_context_default(self):
        """Test default context is inline."""
        from superclaude.hooks.inline_hooks import get_skill_context

        fm = {"name": "test"}
        assert get_skill_context(fm) == "inline"

    def test_get_skill_context_fork(self):
        """Test fork context detection."""
        from superclaude.hooks.inline_hooks import get_skill_context

        fm = {"name": "test", "context": "fork"}
        assert get_skill_context(fm) == "fork"

    def test_get_skill_agent(self):
        """Test agent field retrieval."""
        from superclaude.hooks.inline_hooks import get_skill_agent

        fm = {"name": "test", "agent": "backend-architect"}
        assert get_skill_agent(fm) == "backend-architect"

        fm_no_agent = {"name": "test"}
        assert get_skill_agent(fm_no_agent) is None

    def test_is_user_invocable_default(self):
        """Test default user-invocable is True."""
        from superclaude.hooks.inline_hooks import is_user_invocable

        fm = {"name": "test"}
        assert is_user_invocable(fm) is True

    def test_is_user_invocable_false(self):
        """Test user-invocable can be set to False."""
        from superclaude.hooks.inline_hooks import is_user_invocable

        fm = {"name": "test", "user-invocable": False}
        assert is_user_invocable(fm) is False

    def test_get_allowed_tools(self):
        """Test allowed-tools retrieval."""
        from superclaude.hooks.inline_hooks import get_allowed_tools

        fm = {"allowed-tools": ["Read", "Grep", "mcp__serena__*"]}
        assert get_allowed_tools(fm) == ["Read", "Grep", "mcp__serena__*"]

        fm_empty = {}
        assert get_allowed_tools(fm_empty) == []

    def test_is_tool_allowed_exact_match(self):
        """Test exact tool matching."""
        from superclaude.hooks.inline_hooks import is_tool_allowed

        allowed = ["Read", "Grep"]
        assert is_tool_allowed("Read", allowed) is True
        assert is_tool_allowed("Write", allowed) is False

    def test_is_tool_allowed_wildcard(self):
        """Test wildcard tool matching."""
        from superclaude.hooks.inline_hooks import is_tool_allowed

        allowed = ["mcp__serena__*"]
        assert is_tool_allowed("mcp__serena__find_symbol", allowed) is True
        assert is_tool_allowed("mcp__serena__search", allowed) is True
        assert is_tool_allowed("mcp__context7__query", allowed) is False

    def test_is_tool_allowed_agent_pattern(self):
        """Test Task(agent-name) pattern matching."""
        from superclaude.hooks.inline_hooks import is_tool_allowed

        allowed = ["Task(backend-architect)"]
        assert is_tool_allowed("Task", allowed) is True
        assert is_tool_allowed("Read", allowed) is False
        assert is_tool_allowed("Bash", allowed) is False

    def test_is_tool_allowed_empty_list(self):
        """Test that empty allowed list means all tools allowed."""
        from superclaude.hooks.inline_hooks import is_tool_allowed

        assert is_tool_allowed("AnyTool", []) is True

    def test_inline_hook_to_dict(self):
        """Test InlineHook serialization."""
        from superclaude.hooks.inline_hooks import InlineHook

        hook = InlineHook(
            type="command",
            command="echo test",
            matcher="WebFetch",
            timeout=60,
            once=True,
        )

        d = hook.to_dict()
        assert d["type"] == "command"
        assert d["command"] == "echo test"
        assert d["matcher"] == "WebFetch"
        assert d["timeout"] == 60
        assert d["once"] is True
