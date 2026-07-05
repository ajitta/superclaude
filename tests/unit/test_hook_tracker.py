"""
Unit tests for Hook Tracker

Tests session tracking and hook execution management.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from superclaude.hooks.hook_tracker import (
    HookExecution,
    SessionData,
    _ensure_tracker_dir,
    _load_tracker_data,
    _save_tracker_data,
    cleanup_old_sessions,
    get_session_id,
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
