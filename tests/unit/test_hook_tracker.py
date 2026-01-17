"""
Unit tests for Hook Tracker

Tests session tracking and hook execution management.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.hooks.hook_tracker import (
    HOOK_TRACKER_DIR,
    HOOK_TRACKER_FILE,
    SESSION_FILE,
    HookExecution,
    SessionData,
    _ensure_tracker_dir,
    _generate_hook_id,
    _load_tracker_data,
    _save_tracker_data,
    check_and_mark,
    cleanup_old_sessions,
    get_session_id,
    get_session_stats,
    has_executed_once,
    mark_executed,
    reset_session,
    should_execute_hook,
)


class TestHookExecution:
    """Test HookExecution dataclass"""

    def test_creation(self):
        """Test HookExecution creation"""
        execution = HookExecution(
            hook_id="abc123",
            hook_type="PreToolUse",
            executed_at="2024-01-01T12:00:00",
            source="test_skill",
        )

        assert execution.hook_id == "abc123"
        assert execution.hook_type == "PreToolUse"
        assert execution.executed_at == "2024-01-01T12:00:00"
        assert execution.source == "test_skill"


class TestSessionData:
    """Test SessionData dataclass"""

    def test_creation_empty(self):
        """Test SessionData with no executions"""
        session = SessionData(
            session_id="sess123",
            started_at="2024-01-01T12:00:00",
        )

        assert session.session_id == "sess123"
        assert session.executions == {}

    def test_creation_with_executions(self):
        """Test SessionData with executions"""
        execution = HookExecution(
            hook_id="hook1",
            hook_type="SessionStart",
            executed_at="2024-01-01T12:00:00",
            source="skill.md",
        )

        session = SessionData(
            session_id="sess123",
            started_at="2024-01-01T12:00:00",
            executions={"hook1": execution},
        )

        assert len(session.executions) == 1
        assert "hook1" in session.executions


class TestGetSessionId:
    """Test get_session_id function"""

    def test_from_environment(self, monkeypatch):
        """Test session ID from environment variable"""
        monkeypatch.setenv("CLAUDE_SESSION_ID", "env-session-123")

        session_id = get_session_id()
        assert session_id == "env-session-123"

    def test_from_cache_file(self, tmp_path, monkeypatch):
        """Test session ID from cache file"""
        monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)

        # Create temp session file
        session_file = tmp_path / "current_session.txt"
        session_file.write_text("cached-session-456")

        with patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file):
            session_id = get_session_id()
            assert session_id == "cached-session-456"

    def test_generates_new(self, tmp_path, monkeypatch):
        """Test new session ID generation"""
        monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)

        # Use temp directory
        tracker_dir = tmp_path / ".superclaude_hooks"
        session_file = tmp_path / ".superclaude_hooks" / "current_session.txt"

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            session_id = get_session_id()

            # Should be a 16-char hex string
            assert len(session_id) == 16
            assert all(c in "0123456789abcdef" for c in session_id)

            # Should be cached
            assert session_file.read_text() == session_id


class TestGenerateHookId:
    """Test _generate_hook_id function"""

    def test_basic_generation(self):
        """Test basic hook ID generation"""
        hook_id = _generate_hook_id("PreToolUse", "echo test", "skill.md")

        assert len(hook_id) == 12
        assert all(c in "0123456789abcdef" for c in hook_id)

    def test_with_matcher(self):
        """Test hook ID with matcher"""
        hook_id1 = _generate_hook_id("PreToolUse", "echo test", "skill.md", None)
        hook_id2 = _generate_hook_id("PreToolUse", "echo test", "skill.md", "Write")

        # Different matchers should produce different IDs
        assert hook_id1 != hook_id2

    def test_deterministic(self):
        """Test hook ID is deterministic"""
        id1 = _generate_hook_id("PostToolUse", "cmd", "source")
        id2 = _generate_hook_id("PostToolUse", "cmd", "source")

        assert id1 == id2


class TestTrackerDataPersistence:
    """Test _load_tracker_data and _save_tracker_data"""

    def test_load_empty(self, tmp_path):
        """Test loading from non-existent file"""
        tracker_file = tmp_path / "hook_executions.json"

        with patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file):
            data = _load_tracker_data()
            assert data == {}

    def test_save_and_load(self, tmp_path):
        """Test saving and loading data"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
        ):
            # Create data
            execution = HookExecution(
                hook_id="test123",
                hook_type="SessionStart",
                executed_at="2024-01-01T12:00:00",
                source="test.md",
            )
            session = SessionData(
                session_id="sess1",
                started_at="2024-01-01T11:00:00",
                executions={"test123": execution},
            )
            data = {"sess1": session}

            # Save
            _save_tracker_data(data)

            # Load
            loaded = _load_tracker_data()

            assert "sess1" in loaded
            assert loaded["sess1"].session_id == "sess1"
            assert "test123" in loaded["sess1"].executions

    def test_load_invalid_json(self, tmp_path):
        """Test loading handles invalid JSON"""
        tracker_file = tmp_path / "hook_executions.json"
        tracker_file.write_text("invalid json {")

        with patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file):
            data = _load_tracker_data()
            assert data == {}


class TestHasExecutedOnce:
    """Test has_executed_once function"""

    def test_not_executed(self, tmp_path, monkeypatch):
        """Test returns False when not executed"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            result = has_executed_once("PreToolUse", "cmd", "source")
            assert result is False

    def test_executed(self, tmp_path, monkeypatch):
        """Test returns True when already executed"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            # Mark as executed
            mark_executed("PreToolUse", "cmd", "source")

            # Check
            result = has_executed_once("PreToolUse", "cmd", "source")
            assert result is True


class TestMarkExecuted:
    """Test mark_executed function"""

    def test_marks_execution(self, tmp_path, monkeypatch):
        """Test marking execution"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            mark_executed("PostToolUse", "echo done", "skill.md", "Write")

            data = _load_tracker_data()
            assert "test-session" in data
            assert len(data["test-session"].executions) == 1


class TestShouldExecuteHook:
    """Test should_execute_hook function"""

    def test_always_executes_when_not_once(self, tmp_path, monkeypatch):
        """Test hooks without once=true always execute"""
        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        result = should_execute_hook("PreToolUse", "cmd", "source", once=False)
        assert result is True

    def test_checks_once_flag(self, tmp_path, monkeypatch):
        """Test once=true checks execution history"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            # First time should execute
            result1 = should_execute_hook("PreToolUse", "cmd", "source", once=True)
            assert result1 is True

            # Mark as executed
            mark_executed("PreToolUse", "cmd", "source")

            # Second time should not execute
            result2 = should_execute_hook("PreToolUse", "cmd", "source", once=True)
            assert result2 is False


class TestCheckAndMark:
    """Test check_and_mark atomic function"""

    def test_first_execution_returns_true(self, tmp_path, monkeypatch):
        """Test first execution returns True and marks"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            result = check_and_mark("PreToolUse", "cmd", "source", once=True)

            assert result is True
            # Should be marked now
            assert has_executed_once("PreToolUse", "cmd", "source") is True

    def test_second_execution_returns_false(self, tmp_path, monkeypatch):
        """Test second execution returns False"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            # First call
            check_and_mark("PreToolUse", "cmd", "source", once=True)

            # Second call
            result = check_and_mark("PreToolUse", "cmd", "source", once=True)
            assert result is False

    def test_once_false_always_returns_true(self):
        """Test once=False always returns True without any I/O"""
        result = check_and_mark("PreToolUse", "cmd", "source", once=False)
        assert result is True


class TestCleanupOldSessions:
    """Test cleanup_old_sessions function"""

    def test_cleanup_old_sessions(self, tmp_path, monkeypatch):
        """Test cleaning up old sessions"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "current-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            # Create old session
            old_time = (datetime.now() - timedelta(days=2)).isoformat()
            old_session = SessionData(
                session_id="old-session",
                started_at=old_time,
            )

            # Create current session
            current_time = datetime.now().isoformat()
            current_session = SessionData(
                session_id="current-session",
                started_at=current_time,
            )

            data = {
                "old-session": old_session,
                "current-session": current_session,
            }
            _save_tracker_data(data)

            # Cleanup with 24-hour TTL
            cleaned = cleanup_old_sessions(ttl_seconds=24 * 60 * 60)

            assert cleaned == 1

            # Verify old session removed
            data = _load_tracker_data()
            assert "old-session" not in data
            assert "current-session" in data

    def test_cleanup_empty_data(self, tmp_path):
        """Test cleanup with no data"""
        tracker_file = tmp_path / "hook_executions.json"

        with patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file):
            cleaned = cleanup_old_sessions()
            assert cleaned == 0


class TestResetSession:
    """Test reset_session function"""

    def test_reset_clears_cached(self, tmp_path, monkeypatch):
        """Test reset clears cached session"""
        tracker_dir = tmp_path / "hooks"
        session_file = tmp_path / "session.txt"
        session_file.write_text("old-session-id")

        monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            new_id = reset_session()

            # Should get a new ID
            assert new_id != "old-session-id"
            assert len(new_id) == 16

    def test_reset_clears_env(self, tmp_path, monkeypatch):
        """Test reset clears environment variable"""
        tracker_dir = tmp_path / "hooks"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "env-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            reset_session()

            # Environment should be cleared
            assert "CLAUDE_SESSION_ID" not in os.environ


class TestGetSessionStats:
    """Test get_session_stats function"""

    def test_stats_no_session(self, tmp_path, monkeypatch):
        """Test stats for new session"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "new-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            stats = get_session_stats()

            assert stats["session_id"] == "new-session"
            assert stats["started_at"] is None
            assert stats["hooks_executed"] == 0
            assert stats["hook_types"] == {}

    def test_stats_with_executions(self, tmp_path, monkeypatch):
        """Test stats with hook executions"""
        tracker_dir = tmp_path / "hooks"
        tracker_file = tracker_dir / "hook_executions.json"
        session_file = tmp_path / "session.txt"

        monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session")

        with (
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir),
            patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_FILE", tracker_file),
            patch("superclaude.hooks.hook_tracker.SESSION_FILE", session_file),
        ):
            # Mark some executions
            mark_executed("PreToolUse", "cmd1", "source1")
            mark_executed("PreToolUse", "cmd2", "source2")
            mark_executed("PostToolUse", "cmd3", "source3")

            stats = get_session_stats()

            assert stats["session_id"] == "test-session"
            assert stats["hooks_executed"] == 3
            assert stats["hook_types"]["PreToolUse"] == 2
            assert stats["hook_types"]["PostToolUse"] == 1


class TestEnsureTrackerDir:
    """Test _ensure_tracker_dir function"""

    def test_creates_directory(self, tmp_path):
        """Test directory creation"""
        tracker_dir = tmp_path / "new_hooks_dir"

        with patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir):
            _ensure_tracker_dir()
            assert tracker_dir.exists()

    def test_handles_existing(self, tmp_path):
        """Test handles existing directory"""
        tracker_dir = tmp_path / "existing_dir"
        tracker_dir.mkdir()

        with patch("superclaude.hooks.hook_tracker.HOOK_TRACKER_DIR", tracker_dir):
            # Should not raise
            _ensure_tracker_dir()
            assert tracker_dir.exists()
