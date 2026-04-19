"""
Unit tests for session_init script.

Tests session initialization, git status formatting, PR status checking,
and multi-directory CLAUDE.md detection.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.scripts.session_init import (
    get_additional_dirs_status,
    get_git_status,
    get_pr_status,
    init_hook_tracker,
    main,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@dataclass
class FakeCompletedProcess:
    """Minimal stand-in for subprocess.CompletedProcess."""

    returncode: int
    stdout: str = ""
    stderr: str = ""


# ---------------------------------------------------------------------------
# TestInitHookTracker
# ---------------------------------------------------------------------------


class TestInitHookTracker:
    """Test init_hook_tracker session initialization and cleanup."""

    def test_returns_session_id_on_success(self):
        """init_hook_tracker returns a session ID when hook_tracker is available."""
        with (
            patch(
                "superclaude.scripts.session_init.cleanup_old_sessions",
                create=True,
            ) as mock_cleanup,
            patch(
                "superclaude.scripts.session_init.get_session_id",
                create=True,
            ) as mock_get_id,
        ):
            # Mock the lazy imports inside init_hook_tracker
            mock_cleanup_fn = MagicMock(return_value=0)
            mock_get_id_fn = MagicMock(return_value="abc123def456")

            # We need to patch the actual import mechanism
            import superclaude.hooks.hook_tracker as ht_mod

            with (
                patch.object(ht_mod, "cleanup_old_sessions", mock_cleanup_fn),
                patch.object(ht_mod, "get_session_id", mock_get_id_fn),
            ):
                result = init_hook_tracker()

            assert result == "abc123def456"
            mock_cleanup_fn.assert_called_once()
            mock_get_id_fn.assert_called_once()

    def test_returns_none_on_import_error(self):
        """init_hook_tracker returns None when hook_tracker is not importable."""
        with patch.dict(
            "sys.modules",
            {"superclaude.hooks.hook_tracker": None},
        ):
            result = init_hook_tracker()
            assert result is None

    def test_prints_cleanup_count_when_sessions_cleaned(self, capsys):
        """init_hook_tracker prints cleanup message when old sessions are removed."""
        import superclaude.hooks.hook_tracker as ht_mod

        with (
            patch.object(ht_mod, "cleanup_old_sessions", return_value=3),
            patch.object(ht_mod, "get_session_id", return_value="sess-id"),
        ):
            init_hook_tracker()

        captured = capsys.readouterr()
        assert "Cleaned 3 old hook session(s)" in captured.err

    def test_no_cleanup_message_when_zero_sessions(self, capsys):
        """init_hook_tracker is silent when no sessions are cleaned."""
        import superclaude.hooks.hook_tracker as ht_mod

        with (
            patch.object(ht_mod, "cleanup_old_sessions", return_value=0),
            patch.object(ht_mod, "get_session_id", return_value="sess-id"),
        ):
            init_hook_tracker()

        captured = capsys.readouterr()
        assert "Cleaned" not in captured.err


# ---------------------------------------------------------------------------
# TestGetGitStatus
# ---------------------------------------------------------------------------


class TestGetGitStatus:
    """Test get_git_status formatting for various repository states."""

    def test_clean_repo(self):
        """Clean repository returns 'Git: clean' message."""
        fake = FakeCompletedProcess(returncode=0, stdout="")
        with patch("superclaude.scripts.session_init.subprocess.run", return_value=fake):
            result = get_git_status()

        assert result == "\U0001f4ca Git: clean"

    def test_dirty_repo_single_file(self):
        """Single modified file reports '1 files'."""
        fake = FakeCompletedProcess(returncode=0, stdout=" M src/main.py\n")
        with patch("superclaude.scripts.session_init.subprocess.run", return_value=fake):
            result = get_git_status()

        assert result == "\U0001f4ca Git: 1 files"

    def test_dirty_repo_multiple_files(self):
        """Multiple modified files reports correct count."""
        porcelain = " M src/main.py\n?? new_file.txt\nA  added.py\n"
        fake = FakeCompletedProcess(returncode=0, stdout=porcelain)
        with patch("superclaude.scripts.session_init.subprocess.run", return_value=fake):
            result = get_git_status()

        assert result == "\U0001f4ca Git: 3 files"

    def test_not_a_repo(self):
        """Non-zero return code yields 'not a repo'."""
        fake = FakeCompletedProcess(returncode=128, stdout="", stderr="fatal: not a git repo")
        with patch("superclaude.scripts.session_init.subprocess.run", return_value=fake):
            result = get_git_status()

        assert result == "\U0001f4ca Git: not a repo"

    def test_timeout_returns_not_a_repo(self):
        """Subprocess timeout is handled gracefully."""
        with patch(
            "superclaude.scripts.session_init.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5),
        ):
            result = get_git_status()

        assert result == "\U0001f4ca Git: not a repo"

    def test_oserror_returns_not_a_repo(self):
        """OSError (git not installed) is handled gracefully."""
        with patch(
            "superclaude.scripts.session_init.subprocess.run",
            side_effect=OSError("git not found"),
        ):
            result = get_git_status()

        assert result == "\U0001f4ca Git: not a repo"

    def test_subprocess_called_with_correct_args(self):
        """Verifies subprocess.run is called with --porcelain and timeout."""
        fake = FakeCompletedProcess(returncode=0, stdout="")
        with patch("superclaude.scripts.session_init.subprocess.run", return_value=fake) as mock_run:
            get_git_status()

        mock_run.assert_called_once_with(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
        )


# ---------------------------------------------------------------------------
# TestGetPrStatus
# ---------------------------------------------------------------------------


class TestGetPrStatus:
    """Test get_pr_status for various PR states and error conditions."""

    def _mock_subprocess(self, branch_result, pr_result=None):
        """Helper to mock two sequential subprocess.run calls (branch + gh pr)."""
        side_effects = [branch_result]
        if pr_result is not None:
            side_effects.append(pr_result)
        return patch(
            "superclaude.scripts.session_init.subprocess.run",
            side_effect=side_effects,
        )

    def test_no_git_repo_returns_empty(self):
        """Returns empty string when not in a git repository."""
        branch = FakeCompletedProcess(returncode=128, stdout="")
        with self._mock_subprocess(branch):
            assert get_pr_status() == ""

    def test_main_branch_returns_empty(self):
        """Returns empty string on main branch (no PR expected)."""
        branch = FakeCompletedProcess(returncode=0, stdout="main\n")
        with self._mock_subprocess(branch):
            assert get_pr_status() == ""

    def test_master_branch_returns_empty(self):
        """Returns empty string on master branch (no PR expected)."""
        branch = FakeCompletedProcess(returncode=0, stdout="master\n")
        with self._mock_subprocess(branch):
            assert get_pr_status() == ""

    def test_no_pr_for_branch_returns_empty(self):
        """Returns empty string when gh pr view fails (no PR exists)."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/foo\n")
        pr = FakeCompletedProcess(returncode=1, stdout="", stderr="no pull requests found")
        with self._mock_subprocess(branch, pr):
            assert get_pr_status() == ""

    def test_draft_pr(self):
        """Draft PR shows white circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/foo\n")
        pr_data = {"isDraft": True, "state": "OPEN", "reviewDecision": "", "url": "https://github.com/org/repo/pull/1"}
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "draft" in result
        assert "https://github.com/org/repo/pull/1" in result

    def test_approved_pr(self):
        """Approved PR shows green circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/bar\n")
        pr_data = {"isDraft": False, "state": "OPEN", "reviewDecision": "APPROVED", "url": "https://github.com/org/repo/pull/2"}
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "approved" in result
        assert "https://github.com/org/repo/pull/2" in result

    def test_changes_requested_pr(self):
        """Changes-requested PR shows red circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="fix/bug\n")
        pr_data = {"isDraft": False, "state": "OPEN", "reviewDecision": "CHANGES_REQUESTED", "url": "https://github.com/org/repo/pull/3"}
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "changes requested" in result

    def test_pending_review_pr(self):
        """Pending-review PR shows yellow circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/baz\n")
        pr_data = {"isDraft": False, "state": "OPEN", "reviewDecision": "", "url": "https://github.com/org/repo/pull/4"}
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "pending review" in result

    def test_pr_without_url(self):
        """PR status with no URL omits parenthetical."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/x\n")
        pr_data = {"isDraft": False, "state": "OPEN", "reviewDecision": "APPROVED", "url": ""}
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "approved" in result
        assert "(" not in result

    def test_gh_cli_not_installed(self):
        """Returns empty string when gh CLI is not installed."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/x\n")
        effects = [branch, FileNotFoundError("gh not found")]
        with patch(
            "superclaude.scripts.session_init.subprocess.run",
            side_effect=effects,
        ):
            assert get_pr_status() == ""

    def test_invalid_json_from_gh(self):
        """Returns empty string when gh returns invalid JSON."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/x\n")
        pr = FakeCompletedProcess(returncode=0, stdout="not json at all")
        with self._mock_subprocess(branch, pr):
            assert get_pr_status() == ""

    def test_timeout_returns_empty(self):
        """Returns empty string on subprocess timeout."""
        with patch(
            "superclaude.scripts.session_init.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5),
        ):
            assert get_pr_status() == ""


# ---------------------------------------------------------------------------
# TestGetAdditionalDirsStatus
# ---------------------------------------------------------------------------


class TestGetAdditionalDirsStatus:
    """Test get_additional_dirs_status monorepo detection."""

    def test_disabled_by_default(self, monkeypatch):
        """Returns empty when env var is not set."""
        monkeypatch.delenv("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", raising=False)
        assert get_additional_dirs_status() == ""

    def test_disabled_when_env_zero(self, monkeypatch):
        """Returns empty when env var is '0'."""
        monkeypatch.setenv("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "0")
        assert get_additional_dirs_status() == ""

    def test_no_additional_dirs(self, tmp_path, monkeypatch):
        """Returns empty when no subdirectories contain CLAUDE.md."""
        monkeypatch.setenv("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "1")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "packages").mkdir()
        (tmp_path / "packages" / "core").mkdir()
        # No CLAUDE.md inside
        assert get_additional_dirs_status() == ""

    def test_detects_packages_claude_md(self, tmp_path, monkeypatch):
        """Detects CLAUDE.md files in packages/ subdirectories."""
        monkeypatch.setenv("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "1")
        monkeypatch.chdir(tmp_path)

        pkg = tmp_path / "packages" / "core"
        pkg.mkdir(parents=True)
        (pkg / "CLAUDE.md").write_text("# Core")

        result = get_additional_dirs_status()
        assert "1 additional CLAUDE.md" in result

    def test_detects_multiple_patterns(self, tmp_path, monkeypatch):
        """Detects CLAUDE.md across packages/, apps/, libs/, services/."""
        monkeypatch.setenv("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "1")
        monkeypatch.chdir(tmp_path)

        for parent, child in [("packages", "ui"), ("apps", "web"), ("libs", "utils")]:
            d = tmp_path / parent / child
            d.mkdir(parents=True)
            (d / "CLAUDE.md").write_text(f"# {child}")

        result = get_additional_dirs_status()
        assert "3 additional CLAUDE.md" in result

    def test_ignores_files_not_directories(self, tmp_path, monkeypatch):
        """Only counts directories, not files matching the glob."""
        monkeypatch.setenv("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "1")
        monkeypatch.chdir(tmp_path)

        (tmp_path / "packages").mkdir()
        # Create a file (not directory) that matches the glob
        (tmp_path / "packages" / "not-a-dir").write_text("file")

        assert get_additional_dirs_status() == ""


# ---------------------------------------------------------------------------
# TestMain
# ---------------------------------------------------------------------------


class TestMain:
    """Test main() orchestration and output."""

    def test_main_prints_git_status(self, capsys):
        """main() includes git status in output."""
        with (
            patch("superclaude.scripts.session_init.init_hook_tracker", return_value=None),
            patch("superclaude.scripts.session_init.get_git_status", return_value="\U0001f4ca Git: clean"),
            patch("superclaude.scripts.session_init.get_pr_status", return_value=""),
            patch("superclaude.scripts.session_init.get_additional_dirs_status", return_value=""),
        ):
            main()

        out = capsys.readouterr().out
        assert "Git: clean" in out

    def test_main_prints_pr_status_when_present(self, capsys):
        """main() includes PR status when non-empty."""
        with (
            patch("superclaude.scripts.session_init.init_hook_tracker", return_value=None),
            patch("superclaude.scripts.session_init.get_git_status", return_value="\U0001f4ca Git: clean"),
            patch("superclaude.scripts.session_init.get_pr_status", return_value="\U0001f7e2 PR: approved (url)"),
            patch("superclaude.scripts.session_init.get_additional_dirs_status", return_value=""),
        ):
            main()

        out = capsys.readouterr().out
        assert "PR: approved" in out

    def test_main_omits_pr_status_when_empty(self, capsys):
        """main() does not print PR line when get_pr_status returns empty."""
        with (
            patch("superclaude.scripts.session_init.init_hook_tracker", return_value=None),
            patch("superclaude.scripts.session_init.get_git_status", return_value="\U0001f4ca Git: clean"),
            patch("superclaude.scripts.session_init.get_pr_status", return_value=""),
            patch("superclaude.scripts.session_init.get_additional_dirs_status", return_value=""),
        ):
            main()

        out = capsys.readouterr().out
        assert "PR:" not in out

    def test_main_prints_core_services(self, capsys):
        """main() prints the core services block."""
        with (
            patch("superclaude.scripts.session_init.init_hook_tracker", return_value=None),
            patch("superclaude.scripts.session_init.get_git_status", return_value="\U0001f4ca Git: clean"),
            patch("superclaude.scripts.session_init.get_pr_status", return_value=""),
            patch("superclaude.scripts.session_init.get_additional_dirs_status", return_value=""),
        ):
            main()

        out = capsys.readouterr().out
        assert "Core Services Available" in out
        assert "Confidence Check" in out
        assert "SC Agent ready" in out

    def test_main_prints_additional_dirs_when_present(self, capsys):
        """main() includes additional dirs status when non-empty."""
        with (
            patch("superclaude.scripts.session_init.init_hook_tracker", return_value=None),
            patch("superclaude.scripts.session_init.get_git_status", return_value="\U0001f4ca Git: clean"),
            patch("superclaude.scripts.session_init.get_pr_status", return_value=""),
            patch("superclaude.scripts.session_init.get_additional_dirs_status", return_value="\U0001f4c1 Multi-dir: 2 additional CLAUDE.md found"),
        ):
            main()

        out = capsys.readouterr().out
        assert "Multi-dir: 2 additional CLAUDE.md" in out
