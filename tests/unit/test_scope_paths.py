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
    detect_scope,
    get_skill_directories,
    hook_state_dir,
    main_worktree_root,
    project_key,
    project_root,
    settings_filename,
)


def _make_scoped_install(root: Path) -> Path:
    """Create the marker a project/local scope install leaves behind."""
    content_dir = root / ".claude" / "superclaude"
    content_dir.mkdir(parents=True)
    return content_dir


SC_HOOK_SETTINGS = (
    '{"hooks": {"SessionStart": [{"matcher": "*", "hooks": [{"type": "command",'
    ' "command": "$CLAUDE_PROJECT_DIR/.claude/superclaude/scripts/session_init.py"}]}]}}'
)


def _register_hooks(base: Path, filename: str) -> None:
    """Write the hook registration `install` writes for a scope."""
    base.mkdir(parents=True, exist_ok=True)
    (base / filename).write_text(SC_HOOK_SETTINGS, encoding="utf-8")


def _make_user_install(home: Path, monkeypatch) -> Path:
    """Install at user scope in a fake home, and point Path.home() at it.

    Includes the ~/.claude/CLAUDE.md that installing at user scope writes. That
    file is the reason a fake home is needed rather than a bare directory: its
    import line is identical to the one a project-scope install writes, so any
    test using a marker-only fixture cannot see the two being confused.
    """
    (home / ".claude" / "superclaude").mkdir(parents=True)
    (home / ".claude" / "CLAUDE.md").write_text(
        "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
    )
    _register_hooks(home / ".claude", "settings.json")
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    return home / ".claude"


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


class TestDetectScope:
    """detect_scope names which of the three scopes an install belongs to.

    claude_base only answers "which .claude"; project and local share one
    directory, so the CLAUDE.md import each writes is what separates them.
    Regression target: doctor, verify-drift and audit defaulted to user scope
    and reported a healthy local install as missing, while the startup banner's
    two-way test labelled a local install "project scope".
    """

    def test_user_scope_when_no_project_content(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert detect_scope() == "user"

    def test_home_scoped_install_is_user_not_project(self, tmp_path: Path, monkeypatch):
        """~/.claude/CLAUDE.md holds the same import a project install writes.

        Without a home guard the project branch matched it and named the default
        install scope "project" — the one value the reporting commands exist to
        state correctly.
        """
        home = tmp_path / "home"
        home.mkdir()
        _make_user_install(home, monkeypatch)

        assert detect_scope(home) == "user"

    def test_local_install_rooted_at_home_is_local_not_user(
        self, tmp_path: Path, monkeypatch
    ):
        """Installing local scope at $HOME is legal, so the home guard is not first.

        With the guard ahead of the CLAUDE.local.md test, this read as user
        scope and doctor went looking in settings.json and ~/.claude/CLAUDE.md
        while the install had written settings.local.json and ~/CLAUDE.local.md.
        """
        home = tmp_path / "home"
        home.mkdir()
        _make_scoped_install(home)
        (home / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        _register_hooks(home / ".claude", "settings.local.json")
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))

        assert detect_scope(home) == "local"

    def test_local_scope_from_claude_local_md(self, tmp_path: Path, monkeypatch):
        _make_scoped_install(tmp_path)
        (tmp_path / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert detect_scope() == "local"

    def test_project_scope_from_claude_md(self, tmp_path: Path, monkeypatch):
        _make_scoped_install(tmp_path)
        (tmp_path / ".claude" / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert detect_scope() == "project"

    def test_settings_local_json_breaks_the_tie_without_an_import(
        self, tmp_path: Path, monkeypatch
    ):
        _make_scoped_install(tmp_path)
        (tmp_path / ".claude" / "settings.local.json").write_text(
            "{}", encoding="utf-8"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert detect_scope() == "local"

    def test_project_scope_is_the_fallback_for_installed_content(
        self, tmp_path: Path, monkeypatch
    ):
        _make_scoped_install(tmp_path)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert detect_scope() == "project"

    def test_explicit_root_overrides_the_environment(self, tmp_path: Path, monkeypatch):
        """The CLI passes Path.cwd() so it behaves the same outside a session."""
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        _make_scoped_install(elsewhere)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert detect_scope() == "user"
        assert detect_scope(elsewhere) == "project"

    def test_unreadable_import_file_does_not_raise(self, tmp_path: Path, monkeypatch):
        _make_scoped_install(tmp_path)
        (tmp_path / "CLAUDE.local.md").mkdir()  # a directory, not a readable file
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        assert detect_scope() == "project"


class TestScopeSignalRanking:
    """Signals are ranked by who writes them, strongest first.

    Two earlier orderings each got a real case wrong by trusting a
    hand-writable file: a personal CLAUDE.local.md masked a team's
    project-scope install, and a $HOME guard placed above the local test hid a
    local install rooted at $HOME.
    """

    def test_project_install_survives_a_personal_claude_local_md(
        self, tmp_path: Path, monkeypatch
    ):
        """CLAUDE.local.md is hand-authored — this repo's CLAUDE.md says to write it."""
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project = home / "team"
        _make_scoped_install(project)
        (project / ".claude" / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        _register_hooks(project / ".claude", "settings.json")
        (project / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        assert detect_scope(project) == "project"

    def test_local_hooks_outrank_a_project_import_line(
        self, tmp_path: Path, monkeypatch
    ):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project = home / "proj"
        _make_scoped_install(project)
        (project / ".claude" / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        _register_hooks(project / ".claude", "settings.local.json")

        assert detect_scope(project) == "local"

    def test_foreign_hooks_are_not_evidence(self, tmp_path: Path, monkeypatch):
        """Another plugin's hooks in settings.local.json must not name the scope."""
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project = home / "proj"
        _make_scoped_install(project)
        (project / ".claude" / "settings.local.json").write_text(
            '{"hooks": {"SessionStart": [{"matcher": "*", "hooks": '
            '[{"type": "command", "command": "echo from another plugin"}]}]}}',
            encoding="utf-8",
        )
        (project / ".claude" / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        assert detect_scope(project) == "project"

    def test_import_lines_still_decide_when_no_hooks_are_registered(
        self, tmp_path: Path, monkeypatch
    ):
        """install --keep-settings leaves the weaker signals as the only ones."""
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project = home / "proj"
        _make_scoped_install(project)
        (project / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        assert detect_scope(project) == "local"

    def test_unparseable_settings_file_is_not_hook_evidence(
        self, tmp_path: Path, monkeypatch
    ):
        """A corrupt file must not win the top rung and outrank a real import.

        Its bare existence is still the last-resort tiebreak, which is why this
        pins the ranking rather than the file being ignored outright.
        """
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project = home / "proj"
        _make_scoped_install(project)
        (project / ".claude" / "settings.local.json").write_text(
            "{not json", encoding="utf-8"
        )
        (project / ".claude" / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

        assert detect_scope(project) == "project"


class TestSameDir:
    """same_dir is public because install_paths needs the same comparison."""

    def test_resolves_symlinks(self, tmp_path: Path):
        from superclaude.utils import same_dir

        real = tmp_path / "real"
        real.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real)

        assert same_dir(link, real) is True

    def test_different_directories_are_not_the_same(self, tmp_path: Path):
        from superclaude.utils import same_dir

        left = tmp_path / "a"
        right = tmp_path / "b"
        left.mkdir()
        right.mkdir()

        assert same_dir(left, right) is False


class TestSettingsFilename:
    """Local scope keeps its hooks in the gitignored settings.local.json."""

    def test_local_scope_uses_settings_local_json(self):
        assert settings_filename("local") == "settings.local.json"

    def test_other_scopes_share_settings_json(self):
        assert settings_filename("user") == "settings.json"
        assert settings_filename("project") == "settings.json"


class TestResolveReportingTarget:
    """doctor / verify-drift / audit walk up to the install; install does not.

    Regression target: run from a subdirectory, the read-only commands fell back
    to user scope and reported a healthy local install as absent — the same
    false report that defaulting to user scope produced from the project root.
    """

    def test_walks_up_to_the_install(self, tmp_path: Path):
        from superclaude.cli.install_paths import resolve_reporting_target

        _make_scoped_install(tmp_path)
        (tmp_path / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        deep = tmp_path / "src" / "pkg" / "cli"
        deep.mkdir(parents=True)

        scope, base_path = resolve_reporting_target(start=deep)

        assert scope == "local"
        assert base_path == tmp_path / ".claude"

    def test_explicit_user_scope_never_walks_up(self, tmp_path: Path):
        from superclaude.cli.install_paths import resolve_reporting_target

        _make_scoped_install(tmp_path)

        scope, base_path = resolve_reporting_target("user", start=tmp_path)

        assert scope == "user"
        assert base_path == Path.home() / ".claude"

    def test_explicit_scope_names_the_found_install(self, tmp_path: Path):
        from superclaude.cli.install_paths import resolve_reporting_target

        _make_scoped_install(tmp_path)
        deep = tmp_path / "src"
        deep.mkdir()

        scope, base_path = resolve_reporting_target("local", start=deep)

        assert scope == "local"
        assert base_path == tmp_path / ".claude"

    def test_falls_back_to_user_scope_outside_any_install(
        self, tmp_path: Path, monkeypatch
    ):
        """The real walk-up, not a stub: it must not mistake $HOME for a project.

        Stubbing find_install_root to None here is what let the bug ship — the
        assertion held while the function it replaced was returning $HOME.
        """
        from superclaude.cli.install_paths import resolve_reporting_target

        home = tmp_path / "home"
        home.mkdir()
        base = _make_user_install(home, monkeypatch)
        elsewhere = home / "repos" / "unrelated" / "src"
        elsewhere.mkdir(parents=True)

        scope, base_path = resolve_reporting_target(start=elsewhere)

        assert scope == "user"
        assert base_path == base

    def test_home_is_a_candidate_and_is_named_user_scope(
        self, tmp_path: Path, monkeypatch
    ):
        """Skipping $HOME made detect_scope's local-at-home branch unreachable.

        $HOME is now an ordinary candidate; naming it correctly is
        detect_scope's job, which it does from the settings file install wrote.
        """
        from superclaude.cli.install_paths import (
            find_install_root,
            resolve_reporting_target,
        )

        home = tmp_path / "home"
        home.mkdir()
        base = _make_user_install(home, monkeypatch)
        deep = home / "repos" / "unrelated"
        deep.mkdir(parents=True)

        assert find_install_root(deep) == home
        assert resolve_reporting_target(start=deep) == ("user", base)

    def test_local_install_at_home_reaches_the_cli(self, tmp_path: Path, monkeypatch):
        """detect_scope and resolve_reporting_target must not disagree.

        They did: detect_scope supported a local install at $HOME and had a
        test for it, while find_install_root skipped $HOME so the CLI never
        reached that branch.
        """
        from superclaude.cli.install_paths import resolve_reporting_target

        home = tmp_path / "home"
        home.mkdir()
        _make_scoped_install(home)
        _register_hooks(home / ".claude", "settings.local.json")
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        deep = home / "work"
        deep.mkdir()

        assert detect_scope(home) == "local"
        assert resolve_reporting_target(start=deep) == ("local", home / ".claude")

    def test_a_project_install_under_home_is_still_found(
        self, tmp_path: Path, monkeypatch
    ):
        from superclaude.cli.install_paths import find_install_root

        home = tmp_path / "home"
        home.mkdir()
        _make_user_install(home, monkeypatch)
        project = home / "repos" / "myproject"
        project.mkdir(parents=True)
        _make_scoped_install(project)

        assert find_install_root(project / "src") == project

    def test_explicit_project_scope_names_the_found_install(self, tmp_path: Path):
        from superclaude.cli.install_paths import resolve_reporting_target

        _make_scoped_install(tmp_path)
        (tmp_path / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        deep = tmp_path / "src"
        deep.mkdir()

        scope, base_path = resolve_reporting_target("project", start=deep)

        assert scope == "project"
        assert base_path == tmp_path / ".claude"

    def test_explicit_local_scope_names_the_cwd_when_no_install_is_found(
        self, tmp_path: Path, monkeypatch
    ):
        """--scope local with nothing installed points where install would write."""
        from superclaude.cli.install_paths import resolve_reporting_target

        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        elsewhere = home / "repos" / "unrelated"
        elsewhere.mkdir(parents=True)
        monkeypatch.chdir(elsewhere)

        scope, base_path = resolve_reporting_target("local", start=elsewhere)

        assert scope == "local"
        assert base_path == Path.cwd() / ".claude"

    def test_an_install_above_home_is_never_the_project(
        self, tmp_path: Path, monkeypatch
    ):
        """The walk-up stops at $HOME, inclusive.

        Both default temp roots on Windows sit under the user profile, so a
        test directory's ancestors include the real $HOME and its real
        user-scope install. Walking past the faked $HOME found that install
        and reported it as a project one, which made this suite's outcome
        depend on where pytest put its temp dir.
        """
        from superclaude.cli.install_paths import (
            find_install_root,
            resolve_reporting_target,
        )

        above = tmp_path
        _make_scoped_install(above)  # an install strictly above $HOME
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        deep = home / "repos" / "unrelated"
        deep.mkdir(parents=True)

        assert find_install_root(deep) is None
        assert resolve_reporting_target(start=deep) == ("user", home / ".claude")

    def test_walk_up_reaches_root_when_start_is_outside_home(
        self, tmp_path: Path, monkeypatch
    ):
        from superclaude.cli.install_paths import find_install_root

        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project = tmp_path / "srv" / "app"
        (project / "src").mkdir(parents=True)
        _make_scoped_install(project)

        assert find_install_root(project / "src") == project


def _make_linked_worktree(
    tmp_path: Path, with_install: bool = True
) -> tuple[Path, Path]:
    """Build a main checkout and a linked worktree pointing back at it.

    Mirrors what ``git worktree add`` lays down: the linked checkout's ``.git``
    is a file naming its own gitdir under the main repo, and that gitdir holds
    a ``commondir`` pointing at the main repo's git directory.

    Returns:
        (main worktree root, linked worktree root)
    """
    main = tmp_path / "main"
    main_gitdir = main / ".git"
    (main_gitdir / "worktrees" / "wt").mkdir(parents=True)
    if with_install:
        (main / ".claude" / "superclaude").mkdir(parents=True)
    (main_gitdir / "worktrees" / "wt" / "commondir").write_text(
        "../..\n", encoding="utf-8"
    )

    linked = tmp_path / "wt"
    linked.mkdir()
    (linked / ".git").write_text(
        f"gitdir: {main_gitdir / 'worktrees' / 'wt'}\n", encoding="utf-8"
    )
    return main, linked


class TestLinkedWorktreeAnchors:
    """The one place $CLAUDE_PROJECT_DIR is not a synonym for "this install".

    Claude Code reads the settings file that registered a hook from the MAIN
    worktree, but sets $CLAUDE_PROJECT_DIR to the linked one. Resolving content
    and hook state from the variable alone lands on a directory that usually
    holds no install, and does so silently.
    """

    def test_claude_base_resolves_to_the_main_worktrees_install(
        self, tmp_path, monkeypatch
    ):
        main, linked = _make_linked_worktree(tmp_path)
        home = tmp_path / "home"
        (home / ".claude").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(linked))

        assert claude_base() == main / ".claude"

    def test_project_root_still_names_the_linked_worktree(self, tmp_path, monkeypatch):
        """Code follows the install; per-project data follows the session."""
        _main, linked = _make_linked_worktree(tmp_path)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(linked))

        assert project_root() == linked

    def test_hook_state_follows_the_install_not_the_worktree(
        self, tmp_path, monkeypatch
    ):
        main, linked = _make_linked_worktree(tmp_path)
        home = tmp_path / "home"
        (home / ".claude").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(linked))

        assert hook_state_dir() == main / ".claude" / ".superclaude_hooks"

    def test_worktrees_of_one_repo_keep_distinct_state_filenames(
        self, tmp_path, monkeypatch
    ):
        """Sharing the state DIR is safe only because the key still varies."""
        main, linked = _make_linked_worktree(tmp_path)

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(main))
        main_key = project_key()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(linked))

        assert project_key() != main_key

    def test_main_worktree_without_an_install_falls_back_to_user_scope(
        self, tmp_path, monkeypatch
    ):
        _main, linked = _make_linked_worktree(tmp_path, with_install=False)
        home = tmp_path / "home"
        (home / ".claude").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(linked))

        assert claude_base() == home / ".claude"


class TestMainWorktreeRoot:
    def test_plain_checkout_is_not_a_linked_worktree(self, tmp_path):
        (tmp_path / ".git").mkdir()

        assert main_worktree_root(tmp_path) is None

    def test_directory_without_git_returns_none(self, tmp_path):
        assert main_worktree_root(tmp_path) is None

    def test_pointer_without_gitdir_prefix_returns_none(self, tmp_path):
        (tmp_path / ".git").write_text("not a pointer\n", encoding="utf-8")

        assert main_worktree_root(tmp_path) is None

    def test_pointer_to_a_gitdir_without_commondir_returns_none(self, tmp_path):
        gitdir = tmp_path / "elsewhere"
        gitdir.mkdir()
        (tmp_path / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")

        assert main_worktree_root(tmp_path) is None
