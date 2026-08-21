"""Unit tests for the interactive install wizard."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from superclaude.cli import install_interactive
from superclaude.cli.main import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()



@pytest.fixture
def mock_install_all():
    """Patch install_all in both bind sites so neither path touches the FS.

    The wizard imports from install_components; the non-interactive path
    imports from install_commands (which re-exports). Patch both.
    """
    ret = (True, "📊 Summary: 0 installed, 0 skipped, 0 failed")
    with (
        patch("superclaude.cli.install_components.install_all", return_value=ret) as m1,
        patch("superclaude.cli.install_commands.install_all", return_value=ret) as m2,
    ):
        # Expose a unified mock that records calls from either site.
        class _Either:
            @property
            def call_count(self):
                return m1.call_count + m2.call_count

            @property
            def call_args(self):
                return m1.call_args or m2.call_args

            def assert_called_once(self):
                assert self.call_count == 1, f"expected 1 call, got {self.call_count}"

            def assert_not_called(self):
                assert self.call_count == 0

        yield _Either()


def _isolated_cwd(runner: CliRunner, tmp_path: Path):
    """Run inside an isolated cwd that monkey-patches Path.cwd via chdir."""
    return runner.isolated_filesystem(temp_dir=tmp_path)


class TestNoFlagsTriggersWizard:
    def test_no_flags_enters_interactive(
        self, runner, tmp_path, mock_install_all
    ):
        # Choose user scope (1), no force, confirm proceed.
        # Inputs map to: scope choice, force confirm, proceed confirm.
        with _isolated_cwd(runner, tmp_path):
            result = runner.invoke(main, ["install"], input="1\nn\ny\n")

        assert result.exit_code == 0, result.output
        assert "interactive installer" in result.output
        assert "Step 1/5: Installation scope" in result.output
        mock_install_all.assert_called_once()
        kwargs = mock_install_all.call_args.kwargs
        assert kwargs["scope"] == "user"
        assert kwargs["force"] is False

    def test_explicit_flag_enters_interactive(
        self, runner, tmp_path, mock_install_all
    ):
        with _isolated_cwd(runner, tmp_path):
            result = runner.invoke(main, ["install", "-i"], input="1\nn\ny\n")
        assert result.exit_code == 0, result.output
        assert "Step 1/5" in result.output

    def test_any_flag_skips_wizard(self, runner, tmp_path, mock_install_all):
        # Passing --force should bypass interactive and run install_all directly.
        with _isolated_cwd(runner, tmp_path):
            result = runner.invoke(main, ["install", "--force"])
        assert result.exit_code == 0, result.output
        # Wizard banner must not appear.
        assert "interactive installer" not in result.output
        mock_install_all.assert_called_once()


class TestGitInitPrompt:
    def test_local_scope_offers_git_init_when_missing(
        self, runner, tmp_path, mock_install_all
    ):
        # Scope=3 (local), git init=y, force=n, proceed=y
        with _isolated_cwd(runner, tmp_path):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = runner.invoke(main, ["install"], input="3\ny\nn\ny\n")
                assert result.exit_code == 0, result.output
                assert "Git check" in result.output
                assert "Initialize a git repo" in result.output
                # subprocess.run called for git init
                assert mock_run.called
                cmd = mock_run.call_args.args[0]
                assert cmd[:2] == ["git", "init"]

    def test_local_scope_skips_git_init_when_declined(
        self, runner, tmp_path, mock_install_all
    ):
        with _isolated_cwd(runner, tmp_path):
            with patch("subprocess.run") as mock_run:
                # decline git init (n), force n, proceed y
                result = runner.invoke(main, ["install"], input="3\nn\nn\ny\n")
                assert result.exit_code == 0, result.output
                assert "Skipped git init" in result.output
                assert not mock_run.called
        # Install still proceeded.
        mock_install_all.assert_called_once()

    def test_user_scope_does_not_prompt_for_git(
        self, runner, tmp_path, mock_install_all
    ):
        with _isolated_cwd(runner, tmp_path):
            result = runner.invoke(main, ["install"], input="1\nn\ny\n")
        assert "Git check" not in result.output
        mock_install_all.assert_called_once()


class TestAbortPath:
    def test_abort_at_final_confirm(
        self, runner, tmp_path, mock_install_all
    ):
        # scope=1, force=n, proceed=n
        with _isolated_cwd(runner, tmp_path):
            result = runner.invoke(main, ["install"], input="1\nn\nn\n")
        assert result.exit_code == 1
        assert "Aborted" in result.output
        mock_install_all.assert_not_called()


class TestHelpers:
    def test_has_git_detects_parent_dir(self, tmp_path: Path):
        (tmp_path / ".git").mkdir()
        sub = tmp_path / "a" / "b"
        sub.mkdir(parents=True)
        assert install_interactive._has_git(sub) is True

    def test_has_git_returns_false_when_absent(self, tmp_path: Path):
        sub = tmp_path / "a"
        sub.mkdir()
        assert install_interactive._has_git(sub) is False


class TestUnattendedInstall:
    """`superclaude install` with no flags must work where there is no terminal.

    The bare form is the one every doc shows, and it routed straight into a
    five-step wizard. With no TTY the wizard reads EOF and aborts with exit 2,
    installing nothing — in CI, in a script, in `claude -p`, or behind a pipe.
    That is the command the audit says never successfully ran at user scope (A2).
    """

    def test_bare_install_completes_without_a_terminal(self):
        from click.testing import CliRunner

        from superclaude.cli.main import install

        # No input at all: every prompt reads EOF, exactly as in CI.
        result = CliRunner().invoke(install, [], input="")

        assert result.exit_code == 0, result.output
        assert "No input available for the wizard" in result.output, (
            "the wizard died on EOF instead of falling back"
        )
        assert "Installing SuperClaude components" in result.output, (
            "the command exited without reaching the install"
        )

    def test_explicit_flag_still_opens_the_wizard(self, sandbox_home):
        from click.testing import CliRunner

        from superclaude.cli.main import install

        answers = "\n" * 4 + "n\n"
        result = CliRunner().invoke(install, ["-i"], input=answers)

        assert "Step 1/5" in result.output


class TestScopeHintWording:
    """The hint has to read as a note, not as an instruction to start over."""

    def test_hint_leads_with_the_action_taken(self):
        from pathlib import Path as _Path

        source = (
            _Path(__file__).parent.parent.parent
            / "src"
            / "superclaude"
            / "cli"
            / "main.py"
        ).read_text(encoding="utf-8")
        assert "Detected git repo at CWD." not in source, (
            "the hint still opens on the detection rather than on what it is doing"
        )

    def test_declining_the_wizard_still_aborts(self, runner, tmp_path, mock_install_all):
        """A user who says no must not be overridden by the fallback.

        The wizard reports its two outcomes differently on purpose: declining
        returns, and an unreadable prompt raises. Only the second falls through.
        """
        with _isolated_cwd(runner, tmp_path):
            result = runner.invoke(main, ["install"], input="1" + chr(10) + "n" + chr(10) + "n" + chr(10))

        assert result.exit_code == 1
        assert "Installing SuperClaude components" not in result.output
        mock_install_all.assert_not_called()

