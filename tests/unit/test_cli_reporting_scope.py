"""CLI-level tests for the commands that report on an install.

Every other test for this behaviour stops at `resolve_reporting_target()` or
`run_doctor()`. That left the call sites unguarded: reverting all three in
main.py to the pre-fix `get_base_path(scope or "user")` reproduced the original
user-visible bug — a healthy local install reported as broken — with the full
suite green. These drive the commands the way a user does.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from superclaude.cli.main import main

SC_HOOKS = {
    "hooks": {
        event: [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": (
                            "$CLAUDE_PROJECT_DIR/.claude/superclaude/scripts/"
                            "session_init.py"
                        ),
                    }
                ],
            }
        ]
        for event in ("SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse")
    }
}


@pytest.fixture
def local_install(tmp_path, monkeypatch):
    """A real local-scope install, with the CWD parked in a subdirectory of it.

    The subdirectory is the point: walking up from it is the behaviour these
    commands gained, and running from the project root would pass even with the
    fix reverted on a machine whose home happens to have no install.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)

    project = home / "project"
    project.mkdir()
    # chdir first: a local-scope install writes to the CWD, and running it
    # before the chdir installed into whatever directory pytest started in,
    # which for a developer is the real repo's dev-tree .claude/.
    monkeypatch.chdir(project)
    result = CliRunner().invoke(main, ["install", "--scope", "local", "--force"])
    assert result.exit_code == 0, result.output
    (project / ".claude" / "settings.local.json").write_text(
        json.dumps(SC_HOOKS), encoding="utf-8"
    )

    deep = project / "src" / "pkg"
    deep.mkdir(parents=True)
    monkeypatch.chdir(deep)
    return project


def _run(args):
    return CliRunner().invoke(main, args)


class TestDoctorResolvesTheInstall:
    def test_reports_the_local_install_from_a_subdirectory(self, local_install):
        result = _run(["doctor"])

        assert "scope: local" in result.output
        assert str(local_install / ".claude") in result.output

    def test_is_healthy_on_a_correct_install(self, local_install):
        result = _run(["doctor"])

        assert "❌" not in result.output, result.output
        assert result.exit_code == 0

    def test_explicit_user_scope_still_reaches_home(self, local_install):
        result = _run(["doctor", "--scope", "user"])

        assert "scope: user" in result.output

    def test_repair_advice_is_safe_to_follow_from_here(self, local_install):
        """A bare `superclaude install` here would build a nested install."""
        settings = local_install / ".claude" / "settings.local.json"
        settings.write_text("{}", encoding="utf-8")

        result = _run(["doctor", "--verbose"])

        assert "❌" in result.output
        for line in result.output.splitlines():
            if "superclaude install" in line:
                assert "--scope local" in line, line
                assert str(local_install) in line, line


class TestVerifyDriftResolvesTheInstall:
    def test_reports_the_local_install_from_a_subdirectory(self, local_install):
        result = _run(["verify-drift"])

        assert "scope: local" in result.output

    def test_clean_install_has_no_drift(self, local_install):
        result = _run(["verify-drift"])

        assert "No drift detected" in result.output
        assert result.exit_code == 0

    def test_explicit_user_scope_still_reaches_home(self, local_install):
        result = _run(["verify-drift", "--scope", "user"])

        assert "scope: user" in result.output


class TestAuditResolvesTheInstall:
    def test_reports_the_local_install_from_a_subdirectory(self, local_install):
        result = _run(["audit"])

        assert "scope: local" in result.output

    def test_clean_install_passes(self, local_install):
        result = _run(["audit"])

        assert "All checks passed" in result.output
        assert result.exit_code == 0


class TestInventoryCommandsResolveTheInstall:
    """agents and skills never write, so they follow the same rule."""

    def test_agents_lists_the_local_install(self, local_install):
        result = _run(["agents", "--list"])

        assert "(scope: local)" in result.output
        assert "No agents installed" not in result.output

    def test_list_all_reports_the_local_install(self, local_install):
        result = _run(["install", "--list-all"])

        assert "(scope: local)" in result.output
        assert "[0/" not in result.output


class TestWritingStillFollowsTheShell:
    def test_install_defaults_to_user_scope_inside_a_project(self, local_install):
        """The listing rebinding must not reach the install path."""
        result = _run(["install", "--force"])

        assert "(scope: user)" in result.output
        assert (Path.home() / ".claude" / "superclaude" / "CLAUDE_SC.md").exists()
