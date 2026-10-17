"""Tests for worktree manager — git worktree isolation per design Q2.1."""

from superclaude.scripts.auto_improve.worktree import WorktreeManager


def test_create_worktree_at_expected_path(git_repo):
    wt = WorktreeManager(git_repo).create()
    assert wt.path.parent.name == ".worktrees"
    assert wt.path.name.startswith("auto-improve-")
    assert (wt.path / "README.md").exists()
    assert wt.results_tsv_path == wt.path / "results.tsv"


def test_main_repo_unmodified_after_create(git_repo):
    snapshot = sorted(p.name for p in git_repo.iterdir() if p.name != ".worktrees")
    WorktreeManager(git_repo).create()
    after = sorted(p.name for p in git_repo.iterdir() if p.name != ".worktrees")
    assert snapshot == after
