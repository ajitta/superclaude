"""Unit tests for scope-aware path resolution in superclaude.utils.

Covers the three helpers that decide which install a running hook belongs to:
project_root, claude_base, hook_state_dir. Regression target: hook state and
context lookups used to hardcode ~/.claude (or Path.cwd()), so a local-scope
install wrote runtime state into user scope and a subdirectory CWD silently
loaded user-scope content.
"""

from __future__ import annotations

from pathlib import Path

from superclaude.utils import (
    claude_base,
    get_skill_directories,
    hook_state_dir,
    project_root,
)


def _make_scoped_install(root: Path) -> Path:
    """Create the marker a project/local scope install leaves behind."""
    content_dir = root / ".claude" / "superclaude"
    content_dir.mkdir(parents=True)
    return content_dir


class TestProjectRoot:
    """project_root anchors on $CLAUDE_PROJECT_DIR, not the CWD."""

    def test_prefers_claude_project_dir(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        monkeypatch.chdir(tmp_path.parent)

        assert project_root() == tmp_path

    def test_falls_back_to_cwd(self, tmp_path: Path, monkeypatch):
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        monkeypatch.chdir(tmp_path)

        assert project_root() == Path.cwd()


class TestClaudeBase:
    """claude_base identifies the scope by the presence of .claude/superclaude."""

    def test_project_scope_when_content_present(self, tmp_path: Path, monkeypatch):
        _make_scoped_install(tmp_path)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert claude_base() == tmp_path / ".claude"

    def test_user_scope_when_no_project_install(self, tmp_path: Path, monkeypatch):
        # A .claude exists but carries no framework content — not a scoped install.
        (tmp_path / ".claude").mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert claude_base() == Path.home() / ".claude"

    def test_resolves_from_subdirectory(self, tmp_path: Path, monkeypatch):
        """Regression: CWD-based resolution broke when CC started in a subdir."""
        _make_scoped_install(tmp_path)
        subdir = tmp_path / "src" / "deep"
        subdir.mkdir(parents=True)

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        monkeypatch.chdir(subdir)

        assert claude_base() == tmp_path / ".claude"


class TestHookStateDir:
    """hook_state_dir keeps runtime state inside the active scope."""

    def test_project_scope_leaves_no_user_footprint(self, tmp_path: Path, monkeypatch):
        _make_scoped_install(tmp_path)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        state = hook_state_dir()
        assert state == tmp_path / ".claude" / ".superclaude_hooks"
        assert Path.home() not in state.parents

    def test_user_scope_state_dir(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert hook_state_dir() == Path.home() / ".claude" / ".superclaude_hooks"

    def test_sibling_of_content_dir(self, tmp_path: Path, monkeypatch):
        """State and content resolve under the same .claude, so uninstall gets both."""
        content = _make_scoped_install(tmp_path)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert hook_state_dir().parent == content.parent


class TestSkillDirectories:
    """get_skill_directories finds project skills from any CWD."""

    def test_project_dir_from_subdirectory(self, tmp_path: Path, monkeypatch):
        """Regression: a subdir CWD reported only user-scope skills."""
        (tmp_path / ".claude" / "skills").mkdir(parents=True)
        subdir = tmp_path / "src" / "deep"
        subdir.mkdir(parents=True)

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        monkeypatch.chdir(subdir)

        assert tmp_path / ".claude" / "skills" in get_skill_directories()

    def test_user_scope_always_included(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert Path.home() / ".claude" / "skills" in get_skill_directories()


class TestContextLoaderBasePath:
    """context_loader._get_base_path composes the same resolution."""

    def test_superclaude_path_env_wins(self, tmp_path: Path, monkeypatch):
        from superclaude.scripts.context_loader import _get_base_path

        override = tmp_path / "custom-content"
        override.mkdir()
        monkeypatch.setenv("SUPERCLAUDE_PATH", str(override))

        assert _get_base_path() == override

    def test_project_scope_content(self, tmp_path: Path, monkeypatch):
        from superclaude.scripts.context_loader import _get_base_path

        content = _make_scoped_install(tmp_path)
        monkeypatch.delenv("SUPERCLAUDE_PATH", raising=False)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert _get_base_path() == content

    def test_project_scope_content_from_subdirectory(self, tmp_path: Path, monkeypatch):
        """Regression: subdir CWD used to fall through to user-scope content."""
        from superclaude.scripts.context_loader import _get_base_path

        content = _make_scoped_install(tmp_path)
        subdir = tmp_path / "nested"
        subdir.mkdir()

        monkeypatch.delenv("SUPERCLAUDE_PATH", raising=False)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        monkeypatch.chdir(subdir)

        assert _get_base_path() == content
