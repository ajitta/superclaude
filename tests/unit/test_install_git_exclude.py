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
    """A worktree-style directory: ``.git`` is a file pointing to a gitdir.

    Layout:
        tmp_path/main/.git/                          ← main repo gitdir
        tmp_path/main/.git/worktrees/feature/        ← worktree-specific gitdir
        tmp_path/main/.git/worktrees/feature/info/   ← worktree info dir
        tmp_path/feature/.git                        ← worktree pointer file
    """
    main = tmp_path / "main"
    main.mkdir()
    main_gitdir = main / ".git"
    main_gitdir.mkdir()
    (main_gitdir / "info").mkdir()
    worktree_gitdir = main_gitdir / "worktrees" / "feature"
    worktree_gitdir.mkdir(parents=True)
    (worktree_gitdir / "info").mkdir()

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

    def test_worktree_pointer_resolves_to_worktree_info_exclude(
        self, worktree_dir: Path
    ):
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        result = _resolve_git_exclude_file(worktree_dir)
        assert result is not None
        assert result.name == "exclude"
        assert "worktrees" in result.parts
        assert "feature" in result.parts

    def test_malformed_git_pointer_file_returns_none(self, tmp_path: Path):
        (tmp_path / ".git").write_text("not a gitdir pointer\n", encoding="utf-8")
        from superclaude.cli.install_git_exclude import _resolve_git_exclude_file

        assert _resolve_git_exclude_file(tmp_path) is None


class TestAddLocalGitExclude:
    def test_creates_block_in_empty_repo(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_END,
            MARKER_START,
            add_local_git_exclude,
        )

        ok, msg = add_local_git_exclude(git_repo)
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
        from superclaude.cli.install_git_exclude import add_local_git_exclude

        ok, _ = add_local_git_exclude(git_repo)
        assert ok
        content = exclude_file.read_text(encoding="utf-8")
        assert ".beads/" in content
        assert "**/RECOVERY*.md" in content
        assert "# existing" in content

    def test_idempotent_no_duplication(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_START,
            add_local_git_exclude,
        )

        add_local_git_exclude(git_repo)
        add_local_git_exclude(git_repo)
        content = (git_repo / ".git" / "info" / "exclude").read_text(encoding="utf-8")
        assert content.count(MARKER_START) == 1

    def test_non_git_dir_silent_skip(self, non_git_dir: Path):
        from superclaude.cli.install_git_exclude import add_local_git_exclude

        ok, msg = add_local_git_exclude(non_git_dir)
        assert ok
        assert "Not a git repository" in msg
        assert not (non_git_dir / ".gitignore").exists()

    def test_worktree_writes_to_worktree_gitdir(self, worktree_dir: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_START,
            add_local_git_exclude,
        )

        ok, _ = add_local_git_exclude(worktree_dir)
        assert ok
        # Resolve the worktree pointer to find the actual exclude file
        pointer = (worktree_dir / ".git").read_text(encoding="utf-8").strip()
        gitdir = Path(pointer.removeprefix("gitdir: ").strip())
        exclude_file = gitdir / "info" / "exclude"
        assert exclude_file.exists()
        assert MARKER_START in exclude_file.read_text(encoding="utf-8")

    def test_legacy_gitignore_block_migrated(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_END,
            MARKER_START,
            add_local_git_exclude,
        )

        legacy = (
            "# project shared\n"
            "node_modules/\n"
            f"\n{MARKER_START}\n.claude/commands/sc/\n{MARKER_END}\n"
        )
        gitignore = git_repo / ".gitignore"
        gitignore.write_text(legacy, encoding="utf-8")
        ok, _ = add_local_git_exclude(git_repo)
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
            add_local_git_exclude,
            remove_local_git_exclude,
        )

        exclude_file = git_repo / ".git" / "info" / "exclude"
        exclude_file.write_text("# template\n.beads/\n", encoding="utf-8")
        add_local_git_exclude(git_repo)
        ok, _ = remove_local_git_exclude(git_repo)
        assert ok
        content = exclude_file.read_text(encoding="utf-8")
        assert MARKER_START not in content
        assert ".beads/" in content
        assert "# template" in content

    def test_no_block_present_is_success(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import remove_local_git_exclude

        ok, msg = remove_local_git_exclude(git_repo)
        assert ok
        assert "no SC local block" in msg.lower() or "not found" in msg.lower()

    def test_non_git_dir_is_success(self, non_git_dir: Path):
        from superclaude.cli.install_git_exclude import remove_local_git_exclude

        ok, _ = remove_local_git_exclude(non_git_dir)
        assert ok

    def test_legacy_gitignore_block_also_removed(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            MARKER_END,
            MARKER_START,
            remove_local_git_exclude,
        )

        legacy = (
            f"# shared\nnode_modules/\n\n"
            f"{MARKER_START}\n.claude/commands/sc/\n{MARKER_END}\n"
        )
        gitignore = git_repo / ".gitignore"
        gitignore.write_text(legacy, encoding="utf-8")
        ok, _ = remove_local_git_exclude(git_repo)
        assert ok
        gi_content = gitignore.read_text(encoding="utf-8")
        assert MARKER_START not in gi_content
        assert "node_modules/" in gi_content


class TestHasFunctions:
    def test_has_exclude_block_true_after_add(self, git_repo: Path):
        from superclaude.cli.install_git_exclude import (
            add_local_git_exclude,
            has_exclude_block,
        )

        assert not has_exclude_block(git_repo)
        add_local_git_exclude(git_repo)
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
