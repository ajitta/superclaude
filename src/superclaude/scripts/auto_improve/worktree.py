"""Worktree manager — git worktree isolation per design Q2.1.

Main repo working tree must remain unmodified throughout the loop.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Worktree:
    path: Path
    branch: str

    @property
    def results_tsv_path(self) -> Path:
        return self.path / "results.tsv"


class WorktreeManager:
    """Creates isolated git worktrees under <repo>/.worktrees/.

    Worktrees are never removed by the loop: results.tsv and the git lineage
    live there for the user to inspect after the run.
    """

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

    def _git(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
