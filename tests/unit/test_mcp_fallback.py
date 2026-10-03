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
        ):
            yield tracker_dir

    def test_different_mcps_tracked_separately(self, temp_fallback_dir: Path):
        """Test that different MCPs are tracked independently."""
        from superclaude.hooks.mcp_fallback import check_mcp_and_notify

        # Notify for context7. Conditional phrasing — the hook cannot check real
        # availability, so the hint must not assert the server is down.
        msg = check_mcp_and_notify("context7")
        assert msg == "ℹ️ If context7 MCP is unavailable, fall back to: Tavily/WebSearch"

        # playwright should still notify (first time)
        msg = check_mcp_and_notify("playwright")
        assert msg is not None
        assert "--devtools" in msg

        # an MCP with no fallback entry still gets a hint, naming Native
        msg = check_mcp_and_notify("unknown-mcp")
        assert msg is not None
        assert msg.endswith("fall back to: Native")

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

    def test_check_mcp_and_notify_passes_session_id(self, temp_fallback_dir: Path):
        """check_mcp_and_notify keys the hint on the provided CC session id."""
        from superclaude.hooks.mcp_fallback import check_mcp_and_notify

        assert check_mcp_and_notify("tavily", session_id="cc-a") is not None
        assert check_mcp_and_notify("tavily", session_id="cc-a") is None
        assert check_mcp_and_notify("tavily", session_id="cc-b") is not None

    def test_case_insensitive_mcp_names(self, temp_fallback_dir: Path):
        """Test MCP names are handled case-insensitively."""
        from superclaude.hooks.mcp_fallback import check_mcp_and_notify

        # Use uppercase
        check_mcp_and_notify("CONTEXT7")

        # Lowercase should see as already notified
        assert check_mcp_and_notify("context7") is None

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
