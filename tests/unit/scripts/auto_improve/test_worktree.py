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
    wt = WorktreeManager(repo).create()
    assert wt.path.parent.name == ".worktrees"
    assert wt.path.name.startswith("auto-improve-")
    assert (wt.path / "README.md").exists()
    assert wt.results_tsv_path == wt.path / "results.tsv"


def test_main_repo_unmodified_after_create(repo):
    snapshot = sorted(p.name for p in repo.iterdir() if p.name != ".worktrees")
    WorktreeManager(repo).create()
    after = sorted(p.name for p in repo.iterdir() if p.name != ".worktrees")
    assert snapshot == after
