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

        Only the filename is asserted; the directory is covered by
        TestHookStateDir.
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

    def test_cache_file_carries_the_session(self, tmp_path: Path, monkeypatch):
        """A session id in the payload names a file of its own."""
        from superclaude.scripts.context_reset import get_cache_file

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        scoped = get_cache_file("sess-A")
        assert scoped != get_cache_file()
        assert scoped.name.endswith("_sess-A.txt")

    def test_reset_spares_a_concurrent_session(self, tmp_path: Path, monkeypatch):
        """/clear in one window must not starve another window of context.

        Deleting every cache file for the project would force the sibling
        session to re-inject contexts it already holds — the same starvation,
        pointed the other way.
        """
        from superclaude.scripts.context_reset import (
            get_cache_file,
            reset_context_cache,
        )

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        mine = get_cache_file("sess-A")
        theirs = get_cache_file("sess-B")
        legacy = get_cache_file()
        for path in (mine, theirs, legacy):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("modes/MODE_Brainstorming.md", encoding="utf-8")

        assert reset_context_cache("sess-A") is True

        assert not mine.exists(), "the resetting session kept its stale cache"
        assert not legacy.exists(), "the pre-session-keying cache was left behind"
        assert theirs.exists(), "reset clobbered a concurrent session's cache"

    def test_reset_reports_nothing_to_do(self, tmp_path: Path, monkeypatch):
        """No cache, no claim that one was reset."""
        from superclaude.scripts.context_reset import reset_context_cache

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        assert reset_context_cache("sess-A") is False


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


class TestHookStatePruning:
    """Runtime state must not grow without bound.

    loop_guard prunes entries *inside* a state file; nothing pruned the files.
    A real user-scope state directory had accumulated 25 context caches and 25
    loop-guard files, the oldest from a project key that no longer resolves (A8).
    """

    @staticmethod
    def _age(path: Path, days: float) -> Path:
        import os
        import time

        old = time.time() - days * 86400
        os.utime(path, (old, old))
        return path

    def test_aged_state_is_removed(self, tmp_path: Path, monkeypatch):
        from superclaude.utils import hook_state_dir, prune_hook_state

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        state = hook_state_dir()
        state.mkdir(parents=True, exist_ok=True)

        stale = state / "claude_context_deadbeef.txt"
        stale.write_text("modes/MODE_Brainstorming.md", encoding="utf-8")
        self._age(stale, days=30)
        fresh = state / "claude_context_cafebabe.txt"
        fresh.write_text("modes/MODE_Brainstorming.md", encoding="utf-8")

        removed = prune_hook_state()

        assert not stale.exists(), "aged state file survived the sweep"
        assert fresh.exists(), "live state was collected"
        assert removed == 1

    def test_unknown_files_are_left_alone(self, tmp_path: Path, monkeypatch):
        """The sweep deletes state it recognises, not whatever shares the dir."""
        from superclaude.utils import hook_state_dir, prune_hook_state

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        state = hook_state_dir()
        state.mkdir(parents=True, exist_ok=True)

        stranger = state / "someone_elses_notes.md"
        stranger.write_text("keep me", encoding="utf-8")
        self._age(stranger, days=90)

        prune_hook_state()

        assert stranger.exists()

    def test_fallback_ledger_is_never_deleted_wholesale(
        self, tmp_path: Path, monkeypatch
    ):
        """mcp_fallbacks.json is pruned by entry, so the file itself stays."""
        from superclaude.utils import hook_state_dir, prune_hook_state

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        state = hook_state_dir()
        state.mkdir(parents=True, exist_ok=True)

        ledger = state / "mcp_fallbacks.json"
        ledger.write_text("{}", encoding="utf-8")
        self._age(ledger, days=90)

        prune_hook_state()

        assert ledger.exists()

    def test_session_start_sweeps(self, tmp_path: Path, monkeypatch):
        """The sweep is wired to the hook that already runs at session start."""
        from superclaude.scripts.context_reset import reset_context_cache
        from superclaude.utils import hook_state_dir

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        state = hook_state_dir()
        state.mkdir(parents=True, exist_ok=True)
        stale = state / "loop_guard_deadbeef.json"
        stale.write_text('{"entries": []}', encoding="utf-8")
        self._age(stale, days=30)

        reset_context_cache("sess-A")

        assert not stale.exists()


class TestStateHygiene:
    """The sweep and the session-start reset both named the wrong thing.

    `_PRUNABLE_PREFIXES` claimed a `hook_tracker` file that has never existed —
    the tracker writes `hook_executions.json` — so the one file the sweep was
    written for was the one it never collected. And `session_init` reset the
    context cache with no session id at all, deleting the project-only fallback
    a concurrent session without an id is using, while `context_reset` on the
    same SessionStart event already did it correctly with the id from stdin.
    """

    def test_the_sweep_collects_the_tracker_file(self, tmp_path, monkeypatch):
        import time

        from superclaude.utils import STATE_MAX_AGE_DAYS, prune_hook_state

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        state = tmp_path / ".claude" / ".superclaude_hooks"
        state.mkdir(parents=True)
        (tmp_path / ".claude" / "superclaude").mkdir()
        aged = state / "hook_executions.json"
        aged.write_text("{}", encoding="utf-8")
        old = time.time() - (STATE_MAX_AGE_DAYS + 1) * 86400
        import os

        os.utime(aged, (old, old))

        prune_hook_state()

        assert not aged.exists(), "the sweep left the file it was written to collect"

    def test_session_init_does_not_reset_blind(self):
        """One reset per SessionStart, by the hook that knows the session."""
        from pathlib import Path as _Path

        source = (
            _Path(__file__).parent.parent.parent
            / "src"
            / "superclaude"
            / "scripts"
            / "session_init.py"
        ).read_text(encoding="utf-8")

        assert "reset_context_cache()" not in source, (
            "session_init still resets the cache without a session id"
        )


class TestImportingAHookWritesNothing:
    """Importing a hook module must not touch the filesystem.

    `context_loader` resolved its cache directory at module import and created
    it there. Under pytest that happens during collection, before any fixture
    has redirected HOME, so every run left a directory in the developer's real
    home — the same class of leak the sandbox fixture was written to stop, one
    layer earlier than the fixture can reach.
    """

    def test_context_loader_creates_nothing_on_import(self, tmp_path):
        import os
        import subprocess
        import sys
        from pathlib import Path as _Path

        home = tmp_path / "home"
        home.mkdir()
        src = _Path(__file__).parent.parent.parent / "src"

        result = subprocess.run(
            [sys.executable, "-c", "import superclaude.scripts.context_loader"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=60,
            env={
                "PATH": os.environ.get("PATH", ""),
                "HOME": str(home),
                "USERPROFILE": str(home),
                "PYTHONPATH": str(src),
            },
        )

        assert result.returncode == 0, result.stderr
        assert not (home / ".claude").exists(), (
            "importing the loader created state in the home directory"
        )
