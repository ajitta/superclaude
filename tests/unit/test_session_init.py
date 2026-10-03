"""
Unit tests for session_init script.

Tests session initialization, git status formatting and PR status checking.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.scripts.session_init import (
    get_git_status,
    get_pr_status,
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
# TestGetGitStatus
# ---------------------------------------------------------------------------


class TestGetGitStatus:
    """Test get_git_status formatting for various repository states."""

    def test_clean_repo(self):
        """Clean repository returns 'Git: clean' message."""
        fake = FakeCompletedProcess(returncode=0, stdout="")
        with patch(
            "superclaude.scripts.session_init.subprocess.run", return_value=fake
        ):
            result = get_git_status()

        assert result == "\U0001f4ca Git: clean"

    def test_dirty_repo_single_file(self):
        """Single modified file reports '1 files'."""
        fake = FakeCompletedProcess(returncode=0, stdout=" M src/main.py\n")
        with patch(
            "superclaude.scripts.session_init.subprocess.run", return_value=fake
        ):
            result = get_git_status()

        assert result == "\U0001f4ca Git: 1 files"

    def test_dirty_repo_multiple_files(self):
        """Multiple modified files reports correct count."""
        porcelain = " M src/main.py\n?? new_file.txt\nA  added.py\n"
        fake = FakeCompletedProcess(returncode=0, stdout=porcelain)
        with patch(
            "superclaude.scripts.session_init.subprocess.run", return_value=fake
        ):
            result = get_git_status()

        assert result == "\U0001f4ca Git: 3 files"

    def test_not_a_repo(self):
        """Non-zero return code yields 'not a repo'."""
        fake = FakeCompletedProcess(
            returncode=128, stdout="", stderr="fatal: not a git repo"
        )
        with patch(
            "superclaude.scripts.session_init.subprocess.run", return_value=fake
        ):
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
        with patch(
            "superclaude.scripts.session_init.subprocess.run", return_value=fake
        ) as mock_run:
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

    @pytest.fixture(autouse=True)
    def _isolated_pr_cache(self, tmp_path: Path, monkeypatch):
        """Give every test its own PR-status cache.

        ``get_pr_status`` caches the rendered line per branch to skip the 552ms
        ``gh pr view`` round-trip. Without this fixture the cache resolves to the
        real ``hook_state_dir()``: tests sharing a branch name read each other's
        writes (a "no PR" test poisons the draft-PR test with an empty string),
        and the suite leaves state files in the developer's real project. Pinning
        ``CLAUDE_PROJECT_DIR`` is what anchors the resolver — ``chdir`` alone does
        not, because ``project_root()`` reads the env first.
        """
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        (tmp_path / ".claude" / "superclaude").mkdir(parents=True, exist_ok=True)

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
        pr = FakeCompletedProcess(
            returncode=1, stdout="", stderr="no pull requests found"
        )
        with self._mock_subprocess(branch, pr):
            assert get_pr_status() == ""

    def test_draft_pr(self):
        """Draft PR shows white circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/foo\n")
        pr_data = {
            "isDraft": True,
            "state": "OPEN",
            "reviewDecision": "",
            "url": "https://github.com/org/repo/pull/1",
        }
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "draft" in result
        assert "https://github.com/org/repo/pull/1" in result

    def test_approved_pr(self):
        """Approved PR shows green circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/bar\n")
        pr_data = {
            "isDraft": False,
            "state": "OPEN",
            "reviewDecision": "APPROVED",
            "url": "https://github.com/org/repo/pull/2",
        }
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "approved" in result
        assert "https://github.com/org/repo/pull/2" in result

    def test_changes_requested_pr(self):
        """Changes-requested PR shows red circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="fix/bug\n")
        pr_data = {
            "isDraft": False,
            "state": "OPEN",
            "reviewDecision": "CHANGES_REQUESTED",
            "url": "https://github.com/org/repo/pull/3",
        }
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "changes requested" in result

    def test_pending_review_pr(self):
        """Pending-review PR shows yellow circle indicator."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/baz\n")
        pr_data = {
            "isDraft": False,
            "state": "OPEN",
            "reviewDecision": "",
            "url": "https://github.com/org/repo/pull/4",
        }
        pr = FakeCompletedProcess(returncode=0, stdout=json.dumps(pr_data))
        with self._mock_subprocess(branch, pr):
            result = get_pr_status()

        assert "pending review" in result

    def test_pr_without_url(self):
        """PR status with no URL omits parenthetical."""
        branch = FakeCompletedProcess(returncode=0, stdout="feature/x\n")
        pr_data = {
            "isDraft": False,
            "state": "OPEN",
            "reviewDecision": "APPROVED",
            "url": "",
        }
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
# TestMain
# ---------------------------------------------------------------------------


class TestMain:
    """Test main() orchestration and output."""

    def test_main_prints_git_status(self, capsys):
        """main() includes git status in output."""
        with (
            patch(
                "superclaude.scripts.session_init.get_git_status",
                return_value="\U0001f4ca Git: clean",
            ),
            patch("superclaude.scripts.session_init.get_pr_status", return_value=""),
        ):
            main()

        out = capsys.readouterr().out
        assert "Git: clean" in out

    def test_main_prints_pr_status_when_present(self, capsys):
        """main() includes PR status when non-empty."""
        with (
            patch(
                "superclaude.scripts.session_init.get_git_status",
                return_value="\U0001f4ca Git: clean",
            ),
            patch(
                "superclaude.scripts.session_init.get_pr_status",
                return_value="\U0001f7e2 PR: approved (url)",
            ),
        ):
            main()

        out = capsys.readouterr().out
        assert "PR: approved" in out

    def test_main_omits_pr_status_when_empty(self, capsys):
        """main() does not print PR line when get_pr_status returns empty."""
        with (
            patch(
                "superclaude.scripts.session_init.get_git_status",
                return_value="\U0001f4ca Git: clean",
            ),
            patch("superclaude.scripts.session_init.get_pr_status", return_value=""),
        ):
            main()

        out = capsys.readouterr().out
        assert "PR:" not in out

    def test_main_prints_install_status(self, capsys):
        """main() closes with a line derived from the install, not a fixed block.

        Superseding an assertion on five hardcoded checkmarks, which passed
        whether or not anything they named was installed.
        """
        with (
            patch(
                "superclaude.scripts.session_init.get_git_status",
                return_value="\U0001f4ca Git: clean",
            ),
            patch("superclaude.scripts.session_init.get_pr_status", return_value=""),
        ):
            main()

        out = capsys.readouterr().out
        assert "SuperClaude:" in out
        assert "Core Services Available" not in out


class TestInstallStatusLine:
    """Session start may only claim what it actually checked.

    Five checkmarks were printed unconditionally on every startup — roughly
    40-60 tokens saying the same thing whether or not any of it was installed.
    The framework was in fact absent from user scope for months while this block
    reported it ready (A2, A10).
    """

    FIXED_CLAIMS = (
        "Core Services Available",
        "Confidence Check (pre-implementation validation)",
        "Deep Research (web/MCP integration)",
        "Repository Index (token-efficient exploration)",
        "PR Status Check (Claude Code 2.1.20+)",
        "Task Auto-Cleanup (stale task removal)",
    )

    def test_no_unverified_capability_claims_remain(self):
        source = (
            Path(__file__).parent.parent.parent
            / "src"
            / "superclaude"
            / "scripts"
            / "session_init.py"
        ).read_text(encoding="utf-8")
        for claim in self.FIXED_CLAIMS:
            assert claim not in source, (
                f"session start still hardcodes {claim!r}, which nothing checks"
            )

    def test_reports_what_is_installed(self, tmp_path: Path, monkeypatch):
        from superclaude.scripts.session_init import get_install_status

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        base = tmp_path / ".claude"
        (base / "superclaude").mkdir(parents=True)
        (base / "commands" / "sc").mkdir(parents=True)
        for name in ("analyze", "review", "help"):
            (base / "commands" / "sc" / f"{name}.md").write_text("x", encoding="utf-8")
        (base / "agents").mkdir()
        (base / "agents" / "self-review.md").write_text("x", encoding="utf-8")

        line = get_install_status()

        assert "3 commands" in line
        assert "1 agent" in line
        assert "project" in line

    def test_local_scope_is_not_labelled_project(self, tmp_path: Path, monkeypatch):
        """Local and project share <project>/.claude, so a two-way test lied.

        The banner read `(project scope)` on every local install, which is the
        scope name the user has to pass back to `superclaude install`.
        """
        from superclaude.scripts.session_init import get_install_status

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        base = tmp_path / ".claude"
        (base / "superclaude").mkdir(parents=True)
        (base / "commands" / "sc").mkdir(parents=True)
        (base / "commands" / "sc" / "analyze.md").write_text("x", encoding="utf-8")
        (tmp_path / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        line = get_install_status()

        assert "local scope" in line
        assert "project scope" not in line

    def test_absent_install_says_so(self, tmp_path: Path, monkeypatch):
        """The line that would have caught `0 installed` the first day."""
        from superclaude.scripts.session_init import get_install_status

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        line = get_install_status()

        assert "no commands installed" in line.lower()
