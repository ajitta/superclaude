"""Unit tests for MCP fallback notification module.

Tests mcp_fallback.py functionality for first-time-only notifications.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


class TestMcpFallback:
    """Tests for mcp_fallback.py functionality."""

    @pytest.fixture
    def temp_fallback_dir(self, tmp_path: Path):
        """Create temporary fallback tracking directory."""
        tracker_dir = tmp_path / ".superclaude_hooks"
        tracker_dir.mkdir(parents=True)

        with patch(
            "superclaude.hooks.mcp_fallback.MCP_FALLBACK_FILE",
            tracker_dir / "mcp_fallbacks.json",
        ), patch(
            "superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir
        ), patch(
            "superclaude.hooks.hook_tracker.SESSION_FILE",
            tracker_dir / "current_session.txt",
        ):
            yield tracker_dir

    def test_should_notify_fallback_first_time(self, temp_fallback_dir: Path):
        """Test first notification returns True."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        should_notify, fallback = should_notify_fallback("morphllm")
        assert should_notify is True
        assert fallback == "Edit (native)"

    def test_should_notify_fallback_second_time(self, temp_fallback_dir: Path):
        """Test second notification returns False."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        # First call
        should_notify_fallback("morphllm")

        # Second call - should not notify
        should_notify, fallback = should_notify_fallback("morphllm")
        assert should_notify is False
        assert fallback == "Edit (native)"

    def test_different_mcps_tracked_separately(self, temp_fallback_dir: Path):
        """Test that different MCPs are tracked independently."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        # Notify for morphllm
        should_notify_fallback("morphllm")

        # magic should still notify (first time)
        should_notify, fallback = should_notify_fallback("magic")
        assert should_notify is True
        assert fallback == "Write (native)"

    def test_format_fallback_notification(self, temp_fallback_dir: Path):
        """Test notification message format."""
        from superclaude.hooks.mcp_fallback import format_fallback_notification

        msg = format_fallback_notification("Morphllm", "Edit (native)")
        assert msg == "⚠️ Morphllm unavailable → using Edit (native)"

    def test_check_mcp_and_notify_returns_message(self, temp_fallback_dir: Path):
        """Test combined check and notify function."""
        from superclaude.hooks.mcp_fallback import check_mcp_and_notify

        # First call - returns notification
        result = check_mcp_and_notify("playwright")
        assert result is not None
        assert "Playwright" in result or "playwright" in result
        assert "--chrome (native)" in result

        # Second call - returns None
        result2 = check_mcp_and_notify("playwright")
        assert result2 is None

    def test_get_fallback_for_known_mcp(self, temp_fallback_dir: Path):
        """Test fallback lookup for known MCP."""
        from superclaude.hooks.mcp_fallback import get_fallback_for

        assert get_fallback_for("context7") == "Tavily/WebSearch"
        assert get_fallback_for("tavily") == "WebSearch (native)"
        assert get_fallback_for("sequential") == "Native reasoning"
        assert get_fallback_for("serena") == "Native search"

    def test_get_fallback_for_unknown_mcp(self, temp_fallback_dir: Path):
        """Test fallback lookup for unknown MCP returns Native."""
        from superclaude.hooks.mcp_fallback import get_fallback_for

        assert get_fallback_for("unknown-mcp") == "Native"

    def test_case_insensitive_mcp_names(self, temp_fallback_dir: Path):
        """Test MCP names are handled case-insensitively."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        # Use uppercase
        should_notify_fallback("MORPHLLM")

        # Lowercase should see as already notified
        should_notify, _ = should_notify_fallback("morphllm")
        assert should_notify is False

    def test_mcp_fallback_mapping_complete(self):
        """Test all expected MCPs have fallback mappings."""
        from superclaude.hooks.mcp_fallback import MCP_FALLBACKS

        expected_mcps = [
            "context7", "tavily", "sequential", "serena",
            "morphllm", "magic", "playwright", "devtools",
        ]

        for mcp in expected_mcps:
            assert mcp in MCP_FALLBACKS, f"Missing fallback for {mcp}"


class TestMcpFallbackCleanup:
    """Tests for session cleanup functionality."""

    @pytest.fixture
    def temp_fallback_dir(self, tmp_path: Path):
        """Create temporary fallback tracking directory."""
        tracker_dir = tmp_path / ".superclaude_hooks"
        tracker_dir.mkdir(parents=True)

        with patch(
            "superclaude.hooks.mcp_fallback.MCP_FALLBACK_FILE",
            tracker_dir / "mcp_fallbacks.json",
        ), patch(
            "superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir
        ), patch(
            "superclaude.hooks.hook_tracker.SESSION_FILE",
            tracker_dir / "current_session.txt",
        ):
            yield tracker_dir

    def test_cleanup_removes_old_sessions(self, temp_fallback_dir: Path):
        """Test that cleanup removes sessions older than TTL."""
        import json
        from datetime import datetime, timedelta

        from superclaude.hooks.mcp_fallback import (
            cleanup_old_fallback_sessions,
        )

        # Manually create old session data
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        old_data = {
            "old-session-123": {"morphllm": old_time},
        }

        fallback_file = temp_fallback_dir / "mcp_fallbacks.json"
        fallback_file.write_text(json.dumps(old_data))

        # Run cleanup with 24h TTL
        cleaned = cleanup_old_fallback_sessions(ttl_seconds=24 * 60 * 60)
        assert cleaned == 1

        # Verify file is now empty or has no sessions
        data = json.loads(fallback_file.read_text())
        assert len(data) == 0
