"""Worktree manager — git worktree isolation per design Q2.1.

Main repo working tree must remain unmodified throughout the loop.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .results_tsv import ResultsTsv


@dataclass(frozen=True)
class Worktree:
    path: Path
    branch: str

    @property
    def results_tsv_path(self) -> Path:
        return self.path / "results.tsv"

    def init_results_tsv(self) -> None:
        ResultsTsv(self.results_tsv_path).init()


class WorktreeManager:
    """Creates and removes isolated git worktrees under <repo>/.worktrees/."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)

    def create(self) -> Worktree:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.repo_root / ".worktrees" / f"auto-improve-{timestamp}"
        path.parent.mkdir(parents=True, exist_ok=True)
        branch = f"auto-improve/{timestamp}"
        # `-b <branch>` creates the branch from HEAD; isolates the lineage.
        self._git(["worktree", "add", "-b", branch, str(path)])
        return Worktree(path=path, branch=branch)

    def cleanup(self, wt: Worktree) -> None:
        # `--force` covers the case where the worktree contains uncommitted changes
        # from a mid-cycle rollback.
        self._git(["worktree", "remove", "--force", str(wt.path)])
        # `worktree remove` should delete the directory, but be defensive on Windows
        # where stale .git/worktrees metadata occasionally lingers.
        if wt.path.exists():
            shutil.rmtree(wt.path, ignore_errors=True)
        # Best-effort branch cleanup; ignore failure if branch was already pruned.
        try:
            self._git(["branch", "-D", wt.branch])
        except subprocess.CalledProcessError:
            pass

    def _git(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
