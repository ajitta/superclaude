"""Unit tests for install_git_exclude module.

Covers add/remove of the SC local-scope marker block in
``.git/info/exclude``, idempotency, legacy ``.gitignore`` migration,
non-git silent skip, and worktree pointer-file handling.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """A bare-minimum project root with a regular ``.git/`` directory."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "info").mkdir()
    return tmp_path


@pytest.fixture
def non_git_dir(tmp_path: Path) -> Path:
    """A directory with no ``.git`` at all."""
    return tmp_path


@pytest.fixture
def worktree_dir(tmp_path: Path) -> Path:
    """A linked worktree as ``git worktree add`` lays it out.

    Layout:
        tmp_path/main/.git/                          ← common gitdir
        tmp_path/main/.git/info/                     ← the info/ git reads
        tmp_path/main/.git/worktrees/feature/        ← worktree-specific gitdir
        tmp_path/main/.git/worktrees/feature/commondir  ← "../.." (relative)
        tmp_path/main/.git/worktrees/feature/info/   ← present, never read
        tmp_path/feature/.git                        ← worktree pointer file

    The ``commondir`` file is what git itself writes; the per-worktree
    ``info/`` is created too so a regression back to it has somewhere to
    land and the assertions can see it.
    """
    main = tmp_path / "main"
    main.mkdir()
    main_gitdir = main / ".git"
    main_gitdir.mkdir()
    (main_gitdir / "info").mkdir()
    worktree_gitdir = main_gitdir / "worktrees" / "feature"
    worktree_gitdir.mkdir(parents=True)
    (worktree_gitdir / "info").mkdir()
    (worktree_gitdir / "commondir").write_text("../..\n", encoding="utf-8")

    worktree_root = tmp_path / "feature"
    worktree_root.mkdir()
    (worktree_root / ".git").write_text(
        f"gitdir: {worktree_gitdir}\n", encoding="utf-8"
    )
    return worktree_root


class TestResolveGitExcludeFile:
    def test_regular_repo_returns_info_exclude(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        result = _resolve_git_exclude_file(git_repo)
        assert result == git_repo / ".git" / "info" / "exclude"

    def test_non_git_dir_returns_none(self, non_git_dir: Path):
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        assert _resolve_git_exclude_file(non_git_dir) is None

    def test_worktree_pointer_resolves_to_the_common_info_exclude(
        self, worktree_dir: Path
    ):
        """Git reads ``info/`` through the common dir; the per-worktree
        ``info/exclude`` is never consulted (git 2.55, measured 2026-09-05).
        Until that day this resolver returned the per-worktree file."""
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        result = _resolve_git_exclude_file(worktree_dir)
        expected = worktree_dir.parent / "main" / ".git" / "info" / "exclude"
        assert result == expected.resolve()
        assert "worktrees" not in result.parts

    def test_absolute_commondir_is_followed(self, tmp_path: Path):
        """``commondir`` may be absolute (worktrees can live anywhere)."""
        common = tmp_path / "elsewhere" / "repo.git"
        (common / "info").mkdir(parents=True)
        gitdir = common / "worktrees" / "wt"
        gitdir.mkdir(parents=True)
        (gitdir / "commondir").write_text(f"{common}\n", encoding="utf-8")
        root = tmp_path / "wt"
        root.mkdir()
        (root / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        assert _resolve_git_exclude_file(root) == common / "info" / "exclude"

    def test_pointer_without_commondir_uses_the_gitdir_itself(self, tmp_path: Path):
        """A submodule's ``.git`` is also a pointer file, but its gitdir
        (``.git/modules/<name>``) is a complete git directory with no
        ``commondir`` — its own ``info/exclude`` is the one git reads."""
        superproject = tmp_path / "super"
        gitdir = superproject / ".git" / "modules" / "sub"
        (gitdir / "info").mkdir(parents=True)
        root = superproject / "sub"
        root.mkdir()
        (root / ".git").write_text("gitdir: ../.git/modules/sub\n", encoding="utf-8")
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        assert _resolve_git_exclude_file(root) == gitdir.resolve() / "info" / "exclude"

    def test_stale_commondir_returns_none_and_creates_nothing(self, tmp_path: Path):
        """A worktree whose repository moved or was deleted still has a
        ``commondir``; following it blindly had ``add_git_exclude`` mkdir the
        vanished git directory and report success (probed 2026-09-05)."""
        gone = tmp_path / "GONE" / "repo.git"
        gitdir = tmp_path / "stale-gitdir"
        gitdir.mkdir()
        (gitdir / "commondir").write_text(f"{gone}\n", encoding="utf-8")
        root = tmp_path / "wt"
        root.mkdir()
        (root / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")
        from superclaude.cli.install_git_exclude import (
            _resolve_git_exclude_file,
            add_git_exclude,
        )

        assert _resolve_git_exclude_file(root) is None
        ok, msg = add_git_exclude(root)
        assert ok and "Not a git repository" in msg
        assert not gone.exists(), "conjured a git directory for a stale worktree"

    def test_malformed_git_pointer_file_returns_none(self, tmp_path: Path):
        (tmp_path / ".git").write_text("not a gitdir pointer\n", encoding="utf-8")
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        assert _resolve_git_exclude_file(tmp_path) is None


class TestAddLocalGitExclude:
    def test_creates_block_in_empty_repo(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_END,
            MARKER_START,
            add_git_exclude,
        )

        ok, msg = add_git_exclude(git_repo)
        assert ok, msg
        exclude = (git_repo / ".git" / "info" / "exclude").read_text(encoding="utf-8")
        assert MARKER_START in exclude
        assert MARKER_END in exclude
        assert ".claude/commands/sc/" in exclude
        assert "CLAUDE.local.md" in exclude

    def test_preserves_existing_exclude_content(self, git_repo: Path):
        exclude_file = git_repo / ".git" / "info" / "exclude"
        exclude_file.write_text(
            "# existing\n.beads/\n**/RECOVERY*.md\n", encoding="utf-8"
        )
        from superclaude.cli.install_git_exclude import add_git_exclude

        ok, _ = add_git_exclude(git_repo)
        assert ok
        content = exclude_file.read_text(encoding="utf-8")
        assert ".beads/" in content
        assert "**/RECOVERY*.md" in content
        assert "# existing" in content

    def test_idempotent_no_duplication(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_START,
            add_git_exclude,
        )

        add_git_exclude(git_repo)
        add_git_exclude(git_repo)
        content = (git_repo / ".git" / "info" / "exclude").read_text(encoding="utf-8")
        assert content.count(MARKER_START) == 1

    def test_non_git_dir_silent_skip(self, non_git_dir: Path):
        from superclaude.cli.install_git_exclude import add_git_exclude

        ok, msg = add_git_exclude(non_git_dir)
        assert ok
        assert "Not a git repository" in msg
        assert not (non_git_dir / ".gitignore").exists()

    def test_worktree_writes_to_the_common_exclude(self, worktree_dir: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_START,
            add_git_exclude,
        )

        ok, _ = add_git_exclude(worktree_dir)
        assert ok
        main_gitdir = worktree_dir.parent / "main" / ".git"
        common_exclude = main_gitdir / "info" / "exclude"
        assert MARKER_START in common_exclude.read_text(encoding="utf-8")
        dead_exclude = main_gitdir / "worktrees" / "feature" / "info" / "exclude"
        assert not dead_exclude.exists(), "wrote the file git never reads"

    def test_worktree_remove_and_has_act_on_the_clones_one_file(
        self, worktree_dir: Path
    ):
        """One exclude file per clone: a block written from the worktree is
        visible from the main checkout, and removing it from the worktree
        un-excludes the main checkout too — git's layout, not a choice."""
        from superclaude.cli.install_git_exclude import (
            MARKER_START,
            add_git_exclude,
            has_exclude_block,
            remove_git_exclude,
        )

        main_root = worktree_dir.parent / "main"
        ok, _ = add_git_exclude(worktree_dir)
        assert ok
        assert has_exclude_block(worktree_dir)
        assert has_exclude_block(main_root)

        ok, msg = remove_git_exclude(worktree_dir)
        assert ok and "removed" in msg
        assert not has_exclude_block(worktree_dir)
        assert not has_exclude_block(main_root)
        common_exclude = main_root / ".git" / "info" / "exclude"
        assert MARKER_START not in common_exclude.read_text(encoding="utf-8")

    def test_legacy_gitignore_block_migrated(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_END,
            MARKER_START,
            add_git_exclude,
        )

        legacy = (
            "# project shared\n"
            "node_modules/\n"
            f"\n{MARKER_START}\n.claude/commands/sc/\n{MARKER_END}\n"
        )
        gitignore = git_repo / ".gitignore"
        gitignore.write_text(legacy, encoding="utf-8")
        ok, _ = add_git_exclude(git_repo)
        assert ok
        # Legacy gitignore should no longer contain the SC block
        gi_content = gitignore.read_text(encoding="utf-8")
        assert MARKER_START not in gi_content
        assert "node_modules/" in gi_content
        # New location should
        exclude_content = (git_repo / ".git" / "info" / "exclude").read_text(
            encoding="utf-8"
        )
        assert MARKER_START in exclude_content


class TestRemoveLocalGitExclude:
    def test_removes_block_preserves_other_content(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_START,
            add_git_exclude,
            remove_git_exclude,
        )

        exclude_file = git_repo / ".git" / "info" / "exclude"
        exclude_file.write_text("# template\n.beads/\n", encoding="utf-8")
        add_git_exclude(git_repo)
        ok, _ = remove_git_exclude(git_repo)
        assert ok
        content = exclude_file.read_text(encoding="utf-8")
        assert MARKER_START not in content
        assert ".beads/" in content
        assert "# template" in content

    def test_no_block_present_is_success(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import remove_git_exclude

        ok, msg = remove_git_exclude(git_repo)
        assert ok
        assert "no SC local block" in msg.lower() or "not found" in msg.lower()

    def test_non_git_dir_is_success(self, non_git_dir: Path):
        from superclaude.cli.install_git_exclude import remove_git_exclude

        ok, _ = remove_git_exclude(non_git_dir)
        assert ok

    def test_legacy_gitignore_block_also_removed(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_END,
            MARKER_START,
            remove_git_exclude,
        )

        legacy = (
            f"# shared\nnode_modules/\n\n"
            f"{MARKER_START}\n.claude/commands/sc/\n{MARKER_END}\n"
        )
        gitignore = git_repo / ".gitignore"
        gitignore.write_text(legacy, encoding="utf-8")
        ok, _ = remove_git_exclude(git_repo)
        assert ok
        gi_content = gitignore.read_text(encoding="utf-8")
        assert MARKER_START not in gi_content
        assert "node_modules/" in gi_content


class TestHasFunctions:
    def test_has_exclude_block_true_after_add(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            add_git_exclude,
            has_exclude_block,
        )

        assert not has_exclude_block(git_repo)
        add_git_exclude(git_repo)
        assert has_exclude_block(git_repo)

    def test_has_legacy_gitignore_block_true_when_present(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_END,
            MARKER_START,
            has_legacy_gitignore_block,
        )

        gitignore = git_repo / ".gitignore"
        gitignore.write_text(f"{MARKER_START}\n.foo\n{MARKER_END}\n", encoding="utf-8")
        assert has_legacy_gitignore_block(git_repo)

    def test_has_legacy_false_when_no_gitignore(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import has_legacy_gitignore_block

        assert not has_legacy_gitignore_block(git_repo)


class TestAgentMemoryLocalIsExcluded:
    """Local scope is the personal, gitignored install — its memory must be too.

    Creating the store at install time makes this material: without the entry,
    the first agent to write memory leaves untracked files in a team repository.
    """

    def test_entry_present(self):
        from superclaude.cli.install_git_exclude import _collect_entries

        assert ".claude/agent-memory-local/" in _collect_entries()


class TestFrameworkStateIsExcluded:
    """Runtime state the framework writes into the worktree must not be untracked.

    A local install left `.claude/.superclaude_hooks/` and any un-promoted
    `.claude/insights.pending.jsonl` visible to `git status`, which is both noise
    in the user's own diff and the signal the Stop hook reads as "this session
    changed code".
    """

    def test_runtime_paths_are_listed(self):
        from superclaude.cli.install_git_exclude import _collect_entries

        entries = _collect_entries()

        for path in (
            ".claude/.superclaude_hooks/",
            ".claude/insights.pending.jsonl",
            ".claude/agent-memory/",
            ".claude/agent-memory-local/",
        ):
            assert path in entries, f"{path} is written at runtime but not excluded"


class TestProjectScopeBlock:
    """What project scope may and may not keep out of the team's history.

    Project scope exists so the team shares `.claude/` — content and the hook
    registration alike. Every hook command is `superclaude hook <name>`, so
    settings.json and hooks/hooks.json are the same bytes on every checkout,
    and nothing an install writes is per-developer except runtime state.
    (Releases before the console entry baked the installing machine's absolute
    interpreter into both, and had to exclude them per clone.)
    """

    def test_block_excludes_only_runtime_state(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import _collect_entries

        entries = _collect_entries("project")

        assert entries == [
            ".claude/.superclaude_hooks/",
            ".claude/insights.pending.jsonl",
        ]

    def test_block_leaves_shared_content_tracked(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import _collect_entries

        entries = _collect_entries("project")

        for shared in (
            ".claude/superclaude/",
            ".claude/commands/sc/",
            ".claude/settings.json",
            ".claude/hooks/hooks.json",
        ):
            assert shared not in entries, (
                f"{shared} is machine-independent content; excluding it would "
                "defeat the scope"
            )
        assert not any(e.startswith(".claude/agents/") for e in entries)

    def test_local_scope_still_excludes_everything_it_installs(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import _collect_entries

        entries = _collect_entries("local")

        assert ".claude/superclaude/" in entries
        assert ".claude/commands/sc/" in entries
        assert ".claude/settings.local.json" in entries

    def test_written_block_reflects_the_scope(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_START,
            add_git_exclude,
        )

        ok, msg = add_git_exclude(git_repo, "project")

        assert ok, msg
        content = (git_repo / ".git" / "info" / "exclude").read_text(encoding="utf-8")
        assert MARKER_START in content
        assert ".claude/.superclaude_hooks/" in content
        assert ".claude/settings.json" not in content
        assert ".claude/superclaude/" not in content


class TestMarkerGenerationMigration:
    """The marker lost its ``(local scope)`` label once project scope used it.

    An install predating the rename must have its block replaced, not joined by
    a second one — two blocks would leave stale patterns behind forever.
    """

    def test_legacy_block_is_replaced_not_duplicated(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            _LEGACY_MARKER_PAIRS,
            MARKER_START,
            add_git_exclude,
        )

        legacy_start, legacy_end = _LEGACY_MARKER_PAIRS[0]
        exclude_file = git_repo / ".git" / "info" / "exclude"
        exclude_file.write_text(
            f"{legacy_start}\n.claude/stale-entry/\n{legacy_end}\n",
            encoding="utf-8",
        )

        ok, msg = add_git_exclude(git_repo, "local")

        assert ok, msg
        content = exclude_file.read_text(encoding="utf-8")
        assert legacy_start not in content
        assert ".claude/stale-entry/" not in content
        assert content.count(MARKER_START) == 1

    def test_removal_strips_a_legacy_block(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            _LEGACY_MARKER_PAIRS,
            remove_git_exclude,
        )

        legacy_start, legacy_end = _LEGACY_MARKER_PAIRS[0]
        exclude_file = git_repo / ".git" / "info" / "exclude"
        exclude_file.write_text(
            f"user-pattern\n{legacy_start}\n.claude/superclaude/\n{legacy_end}\n",
            encoding="utf-8",
        )

        ok, msg = remove_git_exclude(git_repo)

        assert ok, msg
        content = exclude_file.read_text(encoding="utf-8")
        assert legacy_start not in content
        assert "user-pattern" in content


def _real_repo(tmp_path: Path, monkeypatch) -> Path:
    """A real repository — `git check-ignore` needs one, the fake `.git/` of
    the `git_repo` fixture is not enough. The developer's global git config is
    shut out so a machine-wide excludes file cannot decide these tests."""
    import subprocess

    empty = tmp_path / "empty-gitconfig"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return tmp_path


class TestFindTeamIgnores:
    """`git check-ignore -v` names the rule that hides a registration file."""

    def test_a_gitignore_rule_is_reported_with_its_source_and_line(
        self, tmp_path: Path, monkeypatch
    ):
        from superclaude.cli.install_git_exclude import find_team_ignores

        repo = _real_repo(tmp_path, monkeypatch)
        (repo / ".gitignore").write_text(
            "# team rules\n.claude/settings.json\n", encoding="utf-8"
        )

        found = find_team_ignores(
            repo, [".claude/settings.json", ".claude/hooks/hooks.json"]
        )

        assert found == [(".gitignore", "2", ".claude/settings.json")]

    def test_nothing_ignored_is_an_empty_list(self, tmp_path: Path, monkeypatch):
        from superclaude.cli.install_git_exclude import find_team_ignores

        assert (
            find_team_ignores(
                _real_repo(tmp_path, monkeypatch), [".claude/settings.json"]
            )
            == []
        )

    def test_a_tracked_file_is_never_reported(self, tmp_path: Path, monkeypatch):
        """git's own rule: an already-committed registration stays quiet even
        when a later ignore rule matches it."""
        import subprocess

        from superclaude.cli.install_git_exclude import find_team_ignores

        repo = _real_repo(tmp_path, monkeypatch)
        target = repo / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        target.write_text("{}", encoding="utf-8")
        git = ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run([*git, "add", ".claude/settings.json"], check=True)
        subprocess.run([*git, "commit", "-q", "-m", "track"], check=True)
        (repo / ".gitignore").write_text(".claude/settings.json\n", encoding="utf-8")

        assert find_team_ignores(repo, [".claude/settings.json"]) == []

    def test_a_non_repository_is_an_empty_list(self, tmp_path: Path):
        from superclaude.cli.install_git_exclude import find_team_ignores

        assert find_team_ignores(tmp_path, [".claude/settings.json"]) == []

    def test_a_negation_that_whitelists_the_file_is_not_an_ignore(
        self, tmp_path: Path, monkeypatch
    ):
        """`.claude/*` + `!.claude/settings.json` is the common way to commit the
        registration while hiding the rest of .claude; check-ignore -v prints the
        negation as the winning rule, and it must not be reported as hiding."""
        from superclaude.cli.install_git_exclude import find_team_ignores

        repo = _real_repo(tmp_path, monkeypatch)
        (repo / ".gitignore").write_text(
            ".claude/*\n!.claude/settings.json\n", encoding="utf-8"
        )

        found = find_team_ignores(
            repo, [".claude/settings.json", ".claude/hooks/hooks.json"]
        )

        assert found == [(".gitignore", "1", ".claude/hooks/hooks.json")]

    def test_a_per_clone_exclude_rule_is_not_a_team_rule(
        self, tmp_path: Path, monkeypatch
    ):
        from superclaude.cli.install_git_exclude import find_team_ignores

        repo = _real_repo(tmp_path, monkeypatch)
        (repo / ".git" / "info").mkdir(exist_ok=True)
        (repo / ".git" / "info" / "exclude").write_text(
            ".claude/settings.json\n", encoding="utf-8"
        )

        assert find_team_ignores(repo, [".claude/settings.json"]) == []


class TestCheckIgnoreParsing:
    """The `-v` line format, incl. a Windows drive letter in the source."""

    def test_a_drive_letter_source_keeps_its_line_number(self):
        from superclaude.cli.install_git_exclude import _parse_check_ignore

        line = "C:/Users/alice/.gitignore_global:3:.claude/settings.json\t.claude/settings.json"

        assert _parse_check_ignore(line + "\n") == [
            ("C:/Users/alice/.gitignore_global", "3", ".claude/settings.json")
        ]

    def test_negations_and_info_exclude_sources_are_dropped(self):
        from superclaude.cli.install_git_exclude import _parse_check_ignore

        stdout = (
            ".gitignore:2:!.claude/settings.json\t.claude/settings.json\n"
            ".git/info/exclude:49:.claude/hooks/hooks.json\t.claude/hooks/hooks.json\n"
            ".gitignore:7:.claude/agents/\t.claude/agents/x.md\n"
        )

        assert _parse_check_ignore(stdout) == [
            (".gitignore", "7", ".claude/agents/x.md")
        ]
