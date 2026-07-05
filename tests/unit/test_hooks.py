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
