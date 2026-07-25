"""Unit tests for scope-aware path resolution in superclaude.utils.

Covers the four helpers that decide which install a running hook belongs to and
which project it is acting on: project_root, claude_base, hook_state_dir,
project_key. Regression target: hook state and context lookups used to hardcode
~/.claude (or Path.cwd()), so a local-scope install wrote runtime state into
user scope and a subdirectory CWD silently loaded user-scope content.
"""

from __future__ import annotations

from pathlib import Path

from superclaude.utils import (
    claude_base,
    get_skill_directories,
    hook_state_dir,
    project_key,
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


class TestProjectKey:
    """project_key names per-project state inside a possibly shared state dir."""

    def test_stable_from_subdirectory(self, tmp_path: Path, monkeypatch):
        """Regression: keying on os.getcwd() gave a subdir its own state file.

        The dedup cache and the loop_guard counters both hang off this key, so a
        drifting key silently re-injects contexts and resets the circuit breaker.
        """
        subdir = tmp_path / "src" / "deep"
        subdir.mkdir(parents=True)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        monkeypatch.chdir(tmp_path)
        from_root = project_key()
        monkeypatch.chdir(subdir)

        assert project_key() == from_root

    def test_differs_across_projects(self, tmp_path: Path, monkeypatch):
        """A user-scope install shares one state dir across every project."""
        other = tmp_path / "other"
        other.mkdir()

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        first = project_key()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(other))

        assert project_key() != first

    def test_is_filename_safe(self, tmp_path: Path, monkeypatch):
        """The key goes straight into a filename, so it must carry no separators."""
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path / "a b" / "c-d.e"))

        key = project_key()
        assert key.isalnum()
        assert len(key) == 8


class TestContextCacheKeying:
    """context_reset must delete the file context_loader actually wrote."""

    def test_cache_file_stable_from_subdirectory(self, tmp_path: Path, monkeypatch):
        """Regression D2: both sides keyed on os.getcwd(), so a hook firing from
        a subdirectory read a different cache file and dedup silently failed.

        Only the filename is asserted. context_reset.CACHE_DIR resolves
        hook_state_dir() once at import, which is correct for a one-shot hook
        subprocess (the env is set before Python starts) but means the directory
        cannot follow monkeypatched env inside a single test session.
        """
        from superclaude.scripts.context_reset import get_cache_file

        subdir = tmp_path / "src" / "deep"
        subdir.mkdir(parents=True)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        monkeypatch.chdir(tmp_path)
        from_root = get_cache_file()
        monkeypatch.chdir(subdir)

        assert get_cache_file() == from_root
        assert from_root.name == f"claude_context_{project_key()}.txt"

    def test_cache_file_follows_project_not_cwd(self, tmp_path: Path, monkeypatch):
        """Two projects must not share one dedup cache file."""
        from superclaude.scripts.context_reset import get_cache_file

        other = tmp_path / "other"
        other.mkdir()

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        first = get_cache_file()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(other))

        assert get_cache_file() != first


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
