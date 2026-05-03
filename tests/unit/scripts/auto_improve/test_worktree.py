"""Tests for worktree manager — git worktree isolation per design Q2.1."""

import subprocess

import pytest

from superclaude.scripts.auto_improve.worktree import WorktreeManager


def _run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)


@pytest.fixture
def repo(tmp_path):
    """Initialise a minimal git repo with one commit."""
    _run(["git", "init", "-b", "main"], cwd=tmp_path)
    _run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path)
    _run(["git", "config", "user.name", "Test"], cwd=tmp_path)
    seed = tmp_path / "README.md"
    seed.write_text("seed\n", encoding="utf-8")
    _run(["git", "add", "."], cwd=tmp_path)
    _run(["git", "commit", "-m", "seed"], cwd=tmp_path)
    return tmp_path


def test_create_worktree_at_expected_path(repo):
    mgr = WorktreeManager(repo)
    wt = mgr.create()
    try:
        assert wt.path.parent.name == ".worktrees"
        assert wt.path.name.startswith("auto-improve-")
        assert (wt.path / "README.md").exists()
    finally:
        mgr.cleanup(wt)


def test_cleanup_removes_worktree(repo):
    mgr = WorktreeManager(repo)
    wt = mgr.create()
    path = wt.path
    assert path.exists()
    mgr.cleanup(wt)
    assert not path.exists()


def test_init_creates_results_tsv_inside_worktree(repo):
    mgr = WorktreeManager(repo)
    wt = mgr.create()
    try:
        wt.init_results_tsv()
        tsv = wt.results_tsv_path
        assert tsv.exists()
        assert tsv.parent == wt.path
        first_line = tsv.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith("# cycle_id")
    finally:
        mgr.cleanup(wt)


def test_main_repo_unmodified_after_create_cleanup(repo):
    snapshot = sorted(p.name for p in repo.iterdir() if p.name != ".worktrees")
    mgr = WorktreeManager(repo)
    wt = mgr.create()
    mgr.cleanup(wt)
    after = sorted(p.name for p in repo.iterdir() if p.name != ".worktrees")
    assert snapshot == after
