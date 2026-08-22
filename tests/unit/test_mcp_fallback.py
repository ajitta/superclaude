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

        with (
            patch(
                "superclaude.hooks.mcp_fallback.MCP_FALLBACK_FILE",
                tracker_dir / "mcp_fallbacks.json",
            ),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch(
                "superclaude.hooks.hook_tracker.SESSION_FILE",
                tracker_dir / "current_session.txt",
            ),
        ):
            yield tracker_dir

    def test_should_notify_fallback_first_time(self, temp_fallback_dir: Path):
        """Test first notification returns True."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        should_notify, fallback = should_notify_fallback("context7")
        assert should_notify is True
        assert fallback == "Tavily/WebSearch"

    def test_should_notify_fallback_second_time(self, temp_fallback_dir: Path):
        """Test second notification returns False."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        # First call
        should_notify_fallback("context7")

        # Second call - should not notify
        should_notify, fallback = should_notify_fallback("context7")
        assert should_notify is False
        assert fallback == "Tavily/WebSearch"

    def test_different_mcps_tracked_separately(self, temp_fallback_dir: Path):
        """Test that different MCPs are tracked independently."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        # Notify for context7
        should_notify_fallback("context7")

        # playwright should still notify (first time)
        should_notify, fallback = should_notify_fallback("playwright")
        assert should_notify is True
        assert "--devtools" in fallback

    def test_format_fallback_notification(self, temp_fallback_dir: Path):
        """Test notification message format."""
        from superclaude.hooks.mcp_fallback import format_fallback_notification

        msg = format_fallback_notification("Context7", "Tavily/WebSearch")
        # Conditional phrasing — the hook cannot check real availability,
        # so the hint must not assert the server is down.
        assert msg == "ℹ️ If Context7 MCP is unavailable, fall back to: Tavily/WebSearch"

    def test_check_mcp_and_notify_returns_message(self, temp_fallback_dir: Path):
        """Test combined check and notify function."""
        from superclaude.hooks.mcp_fallback import check_mcp_and_notify

        # First call - returns notification
        result = check_mcp_and_notify("playwright")
        assert result is not None
        assert "Playwright" in result or "playwright" in result
        assert "--devtools" in result

        # Second call - returns None
        result2 = check_mcp_and_notify("playwright")
        assert result2 is None

    def test_get_fallback_for_known_mcp(self, temp_fallback_dir: Path):
        """Test fallback lookup for known MCP."""
        from superclaude.hooks.mcp_fallback import get_fallback_for

        assert get_fallback_for("context7") == "Tavily/WebSearch"
        assert get_fallback_for("tavily") == "WebSearch (native)"
        assert (
            get_fallback_for("serena")
            == "Grep/Glob + Edit (no symbol ops or persistence)"
        )

    def test_get_fallback_for_unknown_mcp(self, temp_fallback_dir: Path):
        """Test fallback lookup for unknown MCP returns Native."""
        from superclaude.hooks.mcp_fallback import get_fallback_for

        assert get_fallback_for("unknown-mcp") == "Native"

    def test_session_id_passthrough_rotates_per_session(self, temp_fallback_dir: Path):
        """A new CC session id re-arms the hint; same session stays suppressed."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        first, _ = should_notify_fallback("serena", session_id="cc-session-1")
        assert first is True

        repeat, _ = should_notify_fallback("serena", session_id="cc-session-1")
        assert repeat is False

        next_session, _ = should_notify_fallback("serena", session_id="cc-session-2")
        assert next_session is True

    def test_check_mcp_and_notify_passes_session_id(self, temp_fallback_dir: Path):
        """check_mcp_and_notify keys the hint on the provided CC session id."""
        from superclaude.hooks.mcp_fallback import check_mcp_and_notify

        assert check_mcp_and_notify("tavily", session_id="cc-a") is not None
        assert check_mcp_and_notify("tavily", session_id="cc-a") is None
        assert check_mcp_and_notify("tavily", session_id="cc-b") is not None

    def test_case_insensitive_mcp_names(self, temp_fallback_dir: Path):
        """Test MCP names are handled case-insensitively."""
        from superclaude.hooks.mcp_fallback import should_notify_fallback

        # Use uppercase
        should_notify_fallback("CONTEXT7")

        # Lowercase should see as already notified
        should_notify, _ = should_notify_fallback("context7")
        assert should_notify is False

    def test_mcp_fallback_mapping_complete(self):
        """Test all expected MCPs have fallback mappings."""
        from superclaude.hooks.mcp_fallback import MCP_FALLBACKS

        expected_mcps = [
            "context7",
            "tavily",
            "serena",
            "playwright",
            "devtools",
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

        with (
            patch(
                "superclaude.hooks.mcp_fallback.MCP_FALLBACK_FILE",
                tracker_dir / "mcp_fallbacks.json",
            ),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch(
                "superclaude.hooks.hook_tracker.SESSION_FILE",
                tracker_dir / "current_session.txt",
            ),
        ):
            yield tracker_dir


class TestFallbackLedgerPruning:
    """The ledger gains one entry per session and never shed any.

    A real user-scope copy still held a key from the 16-hex scheme retired in
    April, and hints for `magic` and `morphllm` — MCP servers no longer in the
    roster at all (A8).
    """

    def _ledger(self, tmp_path, monkeypatch, data):
        import json

        from superclaude.utils import hook_state_dir

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        state = hook_state_dir()
        state.mkdir(parents=True, exist_ok=True)
        path = state / "mcp_fallbacks.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    @staticmethod
    def _stamp(days_ago: int) -> str:
        from datetime import datetime, timedelta

        return (datetime.now() - timedelta(days=days_ago)).isoformat()

    def test_aged_sessions_are_dropped(self, tmp_path, monkeypatch):
        import json

        from superclaude.utils import prune_fallback_ledger

        path = self._ledger(
            tmp_path,
            monkeypatch,
            {
                "old-session": {"serena": self._stamp(90)},
                "recent-session": {"serena": self._stamp(1)},
            },
        )

        prune_fallback_ledger()

        data = json.loads(path.read_text(encoding="utf-8"))
        assert "old-session" not in data
        assert "recent-session" in data

    def test_current_session_survives_regardless_of_age(self, tmp_path, monkeypatch):
        import json

        from superclaude.utils import prune_fallback_ledger

        path = self._ledger(
            tmp_path, monkeypatch, {"live": {"serena": self._stamp(90)}}
        )

        prune_fallback_ledger(session_id="live")

        assert "live" in json.loads(path.read_text(encoding="utf-8"))

    def test_retired_servers_are_dropped(self, tmp_path, monkeypatch):
        import json

        from superclaude.utils import prune_fallback_ledger

        path = self._ledger(
            tmp_path,
            monkeypatch,
            {
                "live": {
                    "serena": self._stamp(0),
                    "magic": self._stamp(0),
                    "morphllm": self._stamp(0),
                }
            },
        )

        prune_fallback_ledger(session_id="live")

        assert set(json.loads(path.read_text(encoding="utf-8"))["live"]) == {"serena"}

    def test_emptied_session_is_removed(self, tmp_path, monkeypatch):
        import json

        from superclaude.utils import prune_fallback_ledger

        path = self._ledger(tmp_path, monkeypatch, {"live": {"magic": self._stamp(0)}})

        prune_fallback_ledger(session_id="live")

        assert json.loads(path.read_text(encoding="utf-8")) == {}

    def test_roster_matches_the_fallback_table(self):
        """utils keeps its own copy to stay dependency-free — it must not drift.

        If the two disagree, the sweep either deletes hints for a live server or
        keeps hints for a dead one.
        """
        from superclaude.hooks.mcp_fallback import MCP_FALLBACKS
        from superclaude.utils import CURRENT_MCP_SERVERS

        assert set(MCP_FALLBACKS) == set(CURRENT_MCP_SERVERS)
