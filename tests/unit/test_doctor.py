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
    _check_hooks_installed,
    _check_skills_installed,
    run_doctor,
)
from superclaude.cli.install_inventory import _source_dir_names
from superclaude.cli.install_paths import _get_source_dir

SHIPPED_SKILLS = sorted(_source_dir_names(_get_source_dir("skills")))

SC_HOOK_EVENTS = ["SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"]


def _install_skills(base_path: Path, names: list[str]) -> None:
    """Lay down SKILL.md manifests the way install does."""
    for name in names:
        skill_dir = base_path / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")


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


class TestSkillsCheck:
    """The skills check counts what SuperClaude ships, not what shares the dir."""

    def test_passes_when_every_shipped_skill_is_present(self, tmp_path: Path):
        _install_skills(tmp_path, SHIPPED_SKILLS)

        result = _check_skills_installed(tmp_path)

        assert result["passed"] is True

    def test_foreign_skills_do_not_stand_in_for_missing_ones(self, tmp_path: Path):
        _install_skills(tmp_path, [f"someone-elses-skill-{i}" for i in range(30)])

        result = _check_skills_installed(tmp_path)

        assert result["passed"] is False
        assert "0/" in result["details"][0]

    def test_foreign_skills_do_not_break_a_complete_install(self, tmp_path: Path):
        _install_skills(tmp_path, SHIPPED_SKILLS + ["someone-elses-skill"])

        result = _check_skills_installed(tmp_path)

        assert result["passed"] is True
        assert "someone-elses-skill" not in result["details"][0]

    def test_reports_the_scope_directory_it_looked_in(self, tmp_path: Path):
        result = _check_skills_installed(tmp_path)

        assert result["passed"] is False
        assert str(tmp_path / "skills") in " ".join(result["details"])


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

        assert _check_claude_sc_md(tmp_path)["passed"] is True

    def test_missing_reports_the_path_it_checked(self, tmp_path: Path):
        result = _check_claude_sc_md(tmp_path)

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
        _install_skills(base_path, SHIPPED_SKILLS)
        _write_settings(
            base_path / "settings.local.json",
            {event: [_sc_hook_entry("session_init.py")] for event in SC_HOOK_EVENTS},
        )
        return base_path

    def _disk_checks(self, result: dict) -> list[dict]:
        """The four checks that read the install; the other two read the env."""
        environment = {"pytest plugin loaded", "Configuration"}
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
        self._make_local_install(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = run_doctor(scope="local")

        assert result["scope"] == "local"

    def test_reports_every_check(self, tmp_path: Path, monkeypatch):
        self._make_local_install(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = run_doctor()

        assert len(result["checks"]) == 6
