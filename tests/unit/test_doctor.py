"""Unit tests for the scope-aware health check behind `superclaude doctor`.

Regression target: four of the six checks read ~/.claude unconditionally. On a
local-scope install that made CLAUDE_SC.md and the CLAUDE.md import report a
correct install as broken, while the skills and hooks checks passed by
inspecting another tool's skills directory and another tool's hook
registrations — a 4/6 score in which no check had looked at SuperClaude.
"""

from __future__ import annotations

import json
from pathlib import Path

from superclaude.cli.doctor import (
    _check_claude_md_import,
    _check_claude_sc_md,
    _check_console_entry,
    _check_hooks_installed,
    run_doctor,
)
from superclaude.cli.install_inventory import _source_dir_names
from superclaude.cli.install_paths import _get_source_dir


SC_HOOK_EVENTS = ["SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"]


def _sc_hook_entry(script: str) -> dict:
    """A hook entry the marker check attributes to SuperClaude."""
    return {
        "matcher": "*",
        "hooks": [
            {
                "type": "command",
                "command": (
                    f"$CLAUDE_PROJECT_DIR/.claude/superclaude/scripts/{script}"
                ),
            }
        ],
    }


def _foreign_hook_entry() -> dict:
    """A hook entry belonging to some other tool."""
    return {
        "matcher": "*",
        "hooks": [{"type": "command", "command": "echo hello from another plugin"}],
    }


def _write_settings(path: Path, hooks: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"hooks": hooks}), encoding="utf-8")


class TestHooksCheck:
    """The hooks check reads this scope's settings file, SuperClaude entries only."""

    def test_local_scope_reads_settings_local_json(self, tmp_path: Path):
        _write_settings(
            tmp_path / "settings.local.json",
            {event: [_sc_hook_entry("session_init.py")] for event in SC_HOOK_EVENTS},
        )

        result = _check_hooks_installed(tmp_path, "local")

        assert result["passed"] is True
        assert result["name"] == "Hooks in settings.local.json"

    def test_local_scope_ignores_settings_json(self, tmp_path: Path):
        _write_settings(
            tmp_path / "settings.json",
            {event: [_sc_hook_entry("session_init.py")] for event in SC_HOOK_EVENTS},
        )

        result = _check_hooks_installed(tmp_path, "local")

        assert result["passed"] is False

    def test_user_scope_reads_settings_json(self, tmp_path: Path):
        _write_settings(
            tmp_path / "settings.json",
            {event: [_sc_hook_entry("session_init.py")] for event in SC_HOOK_EVENTS},
        )

        result = _check_hooks_installed(tmp_path, "user")

        assert result["passed"] is True
        assert result["name"] == "Hooks in settings.json"

    def test_foreign_hooks_do_not_certify_the_install(self, tmp_path: Path):
        _write_settings(
            tmp_path / "settings.json",
            {event: [_foreign_hook_entry()] for event in SC_HOOK_EVENTS},
        )

        result = _check_hooks_installed(tmp_path, "user")

        assert result["passed"] is False
        for event in SC_HOOK_EVENTS:
            assert event in result["details"][0]

    def test_missing_settings_file_fails(self, tmp_path: Path):
        result = _check_hooks_installed(tmp_path, "user")

        assert result["passed"] is False

    def test_invalid_json_fails_without_raising(self, tmp_path: Path):
        (tmp_path / "settings.json").write_text("{not json", encoding="utf-8")

        result = _check_hooks_installed(tmp_path, "user")

        assert result["passed"] is False


class TestClaudeScMdCheck:
    """CLAUDE_SC.md is looked for under the scope's own base path."""

    def test_found_in_scope(self, tmp_path: Path):
        sc_md = tmp_path / "superclaude" / "CLAUDE_SC.md"
        sc_md.parent.mkdir(parents=True)
        sc_md.write_text("@core/FLAGS.md\n", encoding="utf-8")

        assert _check_claude_sc_md(tmp_path, "local")["passed"] is True

    def test_missing_reports_the_path_it_checked(self, tmp_path: Path):
        result = _check_claude_sc_md(tmp_path, "local")

        assert result["passed"] is False
        assert str(tmp_path) in result["details"][0]


class TestClaudeMdImportCheck:
    """Local scope's import lives in <project>/CLAUDE.local.md, not CLAUDE.md."""

    def test_local_scope_reads_claude_local_md(self, tmp_path: Path):
        base_path = tmp_path / ".claude"
        base_path.mkdir()
        (tmp_path / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        result = _check_claude_md_import(base_path, "local")

        assert result["passed"] is True
        assert result["name"] == "CLAUDE.local.md import"

    def test_user_scope_reads_claude_md(self, tmp_path: Path):
        (tmp_path / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        result = _check_claude_md_import(tmp_path, "user")

        assert result["passed"] is True
        assert result["name"] == "CLAUDE.md import"

    def test_user_scope_import_does_not_satisfy_local_scope(self, tmp_path: Path):
        base_path = tmp_path / ".claude"
        base_path.mkdir()
        (base_path / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        assert _check_claude_md_import(base_path, "local")["passed"] is False


class TestRunDoctor:
    """run_doctor resolves the scope once and reports what it inspected."""

    def _make_local_install(self, project: Path) -> Path:
        base_path = project / ".claude"
        (base_path / "superclaude").mkdir(parents=True)
        (base_path / "superclaude" / "CLAUDE_SC.md").write_text(
            "@core/FLAGS.md\n", encoding="utf-8"
        )
        (project / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        _write_settings(
            base_path / "settings.local.json",
            {event: [_sc_hook_entry("session_init.py")] for event in SC_HOOK_EVENTS},
        )
        return base_path

    def _disk_checks(self, result: dict) -> list[dict]:
        """The three checks that read the install; the other two read the env."""
        environment = {"pytest plugin loaded", "Configuration", "superclaude on PATH"}
        return [c for c in result["checks"] if c["name"] not in environment]

    def test_detects_local_scope_from_the_working_directory(
        self, tmp_path: Path, monkeypatch
    ):
        self._make_local_install(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = run_doctor()

        assert result["scope"] == "local"
        assert result["base_path"] == str(tmp_path / ".claude")
        assert all(check["passed"] for check in self._disk_checks(result))

    def test_explicit_scope_overrides_detection(self, tmp_path: Path, monkeypatch):
        """The explicit scope must differ from what detection would return.

        Passing scope="local" into a fixture that already detects as local
        could not tell "the argument was honoured" from "the argument was
        dropped and detection agreed".
        """
        self._make_local_install(tmp_path)
        monkeypatch.chdir(tmp_path)
        assert run_doctor()["scope"] == "local"

        result = run_doctor(scope="user")

        assert result["scope"] == "user"
        assert result["base_path"] == str(Path.home() / ".claude")

    def test_reports_every_check(self, tmp_path: Path, monkeypatch):
        self._make_local_install(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = run_doctor()

        assert len(result["checks"]) == 6


class TestRepairCommandNamesWhereToRun:
    """doctor diagnoses by walking up; `install` writes to the CWD.

    A bare `superclaude install --scope local` printed from a subdirectory
    installed a second nested framework there and left the diagnosed install
    broken, after which doctor resolved to the stray copy and called it healthy.
    """

    def test_scoped_repair_names_the_project_directory(self, tmp_path: Path):
        from superclaude.cli.doctor import _repair_command

        base = tmp_path / "proj" / ".claude"

        hint = _repair_command("local", base)

        assert "--scope local" in hint
        assert str(tmp_path / "proj") in hint

    def test_user_scope_repair_needs_no_location(self, tmp_path: Path):
        from superclaude.cli.doctor import _repair_command

        hint = _repair_command("user", Path.home() / ".claude")

        assert "--scope user" in hint
        assert " from " not in hint

    def test_every_remediation_line_is_safe_to_follow(self, tmp_path: Path):
        """No check may print a bare `superclaude install` for a scoped install."""
        project = tmp_path / "proj"
        base = project / ".claude"
        (base / "superclaude").mkdir(parents=True)

        checks = [
            _check_claude_sc_md(base, "local"),
            _check_hooks_installed(base, "local"),
            _check_claude_md_import(base, "local"),
        ]

        for check in checks:
            for detail in check["details"]:
                if "superclaude install" not in detail:
                    continue
                assert "--scope local" in detail, detail
                assert str(project) in detail, detail


class TestConsoleEntryCheck:
    """Every hook command is `superclaude hook <name>`; a PATH that cannot
    resolve the console script makes all of them exit 127 in Claude Code."""

    def test_passes_and_names_the_script_it_found(self, monkeypatch):
        monkeypatch.setattr(
            "superclaude.cli.doctor.shutil.which",
            lambda name: "/home/x/.local/bin/superclaude",
        )

        result = _check_console_entry()

        assert result["passed"] is True
        assert "/home/x/.local/bin/superclaude" in result["details"][0]

    def test_fails_with_the_path_repair_when_missing(self, monkeypatch):
        monkeypatch.setattr("superclaude.cli.doctor.shutil.which", lambda name: None)

        result = _check_console_entry()

        assert result["passed"] is False
        assert any("127" in line for line in result["details"])
        assert any("PATH" in line for line in result["details"])
