"""The `skills` directory component: SuperClaude's skills in Claude Code's shared
`.claude/skills/`.

That directory also holds the user's own skills and other tools' skills, so
install, uninstall, git-exclude and drift all touch only the directory names
SuperClaude ships. Tests that could reach past those names plant a
third-party skill next to ours and check it survives.
"""

import os
import sys
from pathlib import Path

import pytest

from superclaude.cli.install_components import install_component
from superclaude.cli.install_git_exclude import _collect_entries
from superclaude.cli.install_inventory import (
    _uninstall_shared_component,
    list_all_components,
    uninstall_all,
)
from superclaude.cli.install_paths import (
    COMPONENTS,
    DIRECTORY_COMPONENTS,
    SHARED_TARGET_COMPONENTS,
    _get_source_dir,
    shipped_md_names,
    shipped_names,
)
from superclaude.cli.verify_drift import DRIFTED, EXTRA, MISSING, verify_drift

_SOURCE = _get_source_dir("skills") / "sc-author"
_FIELDS = Path("references") / "fields.yaml"
_N = len(shipped_names("skills"))


def _plant_other(base: Path) -> Path:
    other = base / "skills" / "other" / "SKILL.md"
    other.parent.mkdir(parents=True)
    other.write_text("---\ndescription: Someone else's.\n---\n", encoding="utf-8")
    return other


def _install(base: Path, force: bool = False):
    return install_component("skills", base, force=force, scope="local")


class TestRegistry:
    def test_component_entry(self):
        assert COMPONENTS["skills"][:2] == ("skills", "skills")

    def test_shapes(self):
        assert DIRECTORY_COMPONENTS == ("templates", "skills")
        assert "skills" in SHARED_TARGET_COMPONENTS

    def test_shipped_names(self):
        assert shipped_names("skills") == {"sc-author", "sc-prompt"}
        assert shipped_names("agents") == shipped_md_names("agents")


class TestInstall:
    def test_copies_the_directory(self, tmp_path):
        installed, _, failed, names = _install(tmp_path)
        assert (installed, failed) == (_N, 0), names
        copy = tmp_path / "skills" / "sc-author" / _FIELDS
        assert copy.read_bytes() == (_SOURCE / _FIELDS).read_bytes()

    def test_leaves_other_skills_alone(self, tmp_path):
        other = _plant_other(tmp_path)
        before = other.read_bytes()
        _install(tmp_path, force=True)
        assert other.read_bytes() == before

    def test_existing_copy_needs_force(self, tmp_path):
        _install(tmp_path)
        copy = tmp_path / "skills" / "sc-author" / _FIELDS
        copy.write_text("edited", encoding="utf-8")

        _, skipped, _, _ = _install(tmp_path)
        assert skipped == _N
        assert copy.read_text(encoding="utf-8") == "edited"

        _install(tmp_path, force=True)
        assert copy.read_bytes() == (_SOURCE / _FIELDS).read_bytes()

    @pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges")
    def test_symlinked_target_outside_base_is_refused(self, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("keep", encoding="utf-8")
        base = tmp_path / "base"
        (base / "skills").mkdir(parents=True)
        os.symlink(outside, base / "skills" / "sc-author")

        _, _, failed, _ = _install(base, force=True)
        assert failed == 1
        assert (outside / "keep.txt").read_text(encoding="utf-8") == "keep"


class TestFileInTheWay:
    def test_file_named_like_the_skill_fails_loudly(self, tmp_path):
        blocker = tmp_path / "skills" / "sc-author"
        blocker.parent.mkdir(parents=True)
        blocker.write_text("not a directory", encoding="utf-8")
        for force in (False, True):
            installed, skipped, failed, names = _install(tmp_path, force=force)
            assert (installed, skipped, failed) == (_N - 1, 0, 1)
            assert "is not a directory" in names[0]
        assert blocker.read_text(encoding="utf-8") == "not a directory"


class TestUninstall:
    def test_removes_only_shipped_skills(self, tmp_path):
        other = _plant_other(tmp_path)
        _install(tmp_path)
        removed, _, failed, _ = _uninstall_shared_component("skills", tmp_path, False)
        assert (removed, failed) == (1, 0)
        assert not (tmp_path / "skills" / "sc-author").exists()
        assert other.exists()

    def test_empty_skills_dir_is_removed(self, tmp_path):
        _install(tmp_path)
        _uninstall_shared_component("skills", tmp_path, False)
        assert not (tmp_path / "skills").exists()

    def test_dry_run_removes_nothing(self, tmp_path):
        _install(tmp_path)
        _, _, _, messages = _uninstall_shared_component("skills", tmp_path, True)
        assert (tmp_path / "skills" / "sc-author").is_dir()
        assert any("Would remove" in m for m in messages)

    def test_uninstall_all_keeps_other_skills(self, tmp_path):
        other = _plant_other(tmp_path)
        _install(tmp_path)
        uninstall_all(base_path=tmp_path, scope="local")
        assert not (tmp_path / "skills" / "sc-author").exists()
        assert other.exists()

    @pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges")
    def test_symlinked_skill_dir_keeps_its_target(self, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("keep", encoding="utf-8")
        base = tmp_path / "base"
        (base / "skills").mkdir(parents=True)
        os.symlink(outside, base / "skills" / "sc-author")
        _uninstall_shared_component("skills", base, False)
        assert (outside / "keep.txt").read_text(encoding="utf-8") == "keep"


class TestGitExclude:
    def test_local_scope_lists_the_skill_directory(self):
        entries = _collect_entries("local")
        assert ".claude/skills/sc-author/" in entries
        assert ".claude/skills/" not in entries

    def test_project_scope_unchanged(self):
        assert not [e for e in _collect_entries("project") if "skills" in e]


class TestDrift:
    def _skills(self, base: Path) -> dict:
        return verify_drift(base, verbose=True)["components"]["skills"]

    def test_clean_after_install(self, tmp_path):
        _plant_other(tmp_path)
        _install(tmp_path)
        install_component("templates", tmp_path, scope="local")
        components = verify_drift(tmp_path, verbose=True)["components"]
        for name in ("skills", "templates"):
            data = components[name]
            assert data["ok"] > 0, name
            assert data["drifted"] == data["missing"] == data["extra"] == 0, data

    def test_nested_file_drift(self, tmp_path):
        _install(tmp_path)
        (tmp_path / "skills" / "sc-author" / _FIELDS).write_text("x", encoding="utf-8")
        files = self._skills(tmp_path)["files"]
        assert files["sc-author/references/fields.yaml"] == DRIFTED

    def test_extra_only_inside_shipped_skill(self, tmp_path):
        _plant_other(tmp_path)
        _install(tmp_path)
        (tmp_path / "skills" / "sc-author" / "extra.md").write_text(
            "x", encoding="utf-8"
        )
        files = self._skills(tmp_path)["files"]
        assert files["sc-author/extra.md"] == EXTRA
        assert not [k for k in files if k.startswith("other/")]

    def test_missing_skill(self, tmp_path):
        files = self._skills(tmp_path)["files"]
        assert files["sc-author/references/fields.yaml"] == MISSING


class TestInventory:
    def test_counts_shipped_directories_only(self, tmp_path):
        _plant_other(tmp_path)
        before = list_all_components(tmp_path, scope="local")["skills"]
        assert (before["available"], before["installed"]) == (_N, 0)
        _install(tmp_path)
        after = list_all_components(tmp_path, scope="local")["skills"]
        assert (after["available"], after["installed"]) == (_N, _N)
