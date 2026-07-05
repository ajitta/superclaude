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

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch(
                "superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE",
                tracker_dir / "hook_executions.json",
            ),
            patch(
                "superclaude.hooks.hook_tracker.SESSION_FILE",
                tracker_dir / "current_session.txt",
            ),
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
        """Test frontmatter parsing with YAML lists in metadata."""
        from superclaude.hooks.inline_hooks import parse_frontmatter

        content = """---
name: test-skill
metadata:
  allowed-tools:
    - Read
    - Grep
    - WebFetch
---
"""
        fm = parse_frontmatter(content)
        assert fm["name"] == "test-skill"
        assert fm["metadata"]["allowed-tools"] == ["Read", "Grep", "WebFetch"]

    def test_parse_frontmatter_with_lists_root_compat(self):
        """Test frontmatter parsing with YAML lists at root (backward compat)."""
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
        """Test inline hooks parsing with nested format at top-level."""
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
                        "hooks": [{"type": "command", "command": "echo post"}],
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
                "PostToolUse": [{"type": "command", "command": "echo post"}],
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
                        "hooks": [{"type": "command", "command": "python cleanup.py"}],
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
        """Test fork context detection from top-level field."""
        from superclaude.hooks.inline_hooks import get_skill_context

        fm = {"name": "test", "context": "fork"}
        assert get_skill_context(fm) == "fork"

    def test_get_skill_context_invalid_falls_back(self):
        """Test invalid context value falls back to inline."""
        from superclaude.hooks.inline_hooks import get_skill_context

        fm = {"name": "test", "context": "unknown"}
        assert get_skill_context(fm) == "inline"

    def test_get_skill_agent(self):
        """Test agent field retrieval from top-level."""
        from superclaude.hooks.inline_hooks import get_skill_agent

        fm = {"name": "test", "agent": "backend-architect"}
        assert get_skill_agent(fm) == "backend-architect"

    def test_get_skill_agent_none(self):
        """Test agent returns None when not specified."""
        from superclaude.hooks.inline_hooks import get_skill_agent

        fm = {"name": "test"}
        assert get_skill_agent(fm) is None

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
