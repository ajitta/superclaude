"""Coordinator — the auto-improve state machine.

State transitions:
    INIT -> CONFIRM -> BASELINE -> LOOP[smoke -> mutate -> eval -> commit/rollback]
                          |             |
                          +-> exit≠0    +-> plateau / budget / regression -> REPORT

The coordinator owns:
  - worktree lifecycle (create on entry, cleanup on exit)
  - PID file on loop start / removal on exit
  - the four guards
  - results.tsv writes (single writer)
  - mutator invocation
  - git commits / rollbacks
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .eval_runner import run_eval
from .guards import (
    BudgetGuard,
    PlateauDetector,
    RegressionBlock,
    SmokeGate,
)
from .mutator import MutationResult, Mutator
from .reporter import morning_summary
from .results_tsv import ResultRow, ResultsTsv
from .worktree import Worktree, WorktreeManager


@dataclass(frozen=True)
class CoordinatorConfig:
    repo_root: Path
    eval_cmd: str
    metric_path: str
    budget_seconds: int = 8 * 3600
    cycle_timeout_seconds: int = 600
    smoke_cmd: Optional[str] = None
    mutator_model: str = "sonnet"
    plateau_window: int = 5
    # Glob restricting which files the mutator may edit. Forwarded to the
    # mutator system prompt; not enforced at fs level (R2 v0.1: mutator's
    # tool surface is already Edit/Write/Read, no shell — scope is advisory).
    scope_glob: str = "**"


class Coordinator:
    def __init__(self, config: CoordinatorConfig):
        self.config = config
        self._wt_mgr = WorktreeManager(config.repo_root)
        self._worktree: Optional[Worktree] = None
        self._tsv: Optional[ResultsTsv] = None
        self._baseline_metric: Optional[float] = None
        self._cycle_id: int = 0

    # --- public entry points ---

    def run_baseline_only(self) -> Path:
        """Phase 0 only — used for --dry-run or test fixtures."""
        self._setup()
        try:
            self._record_baseline_or_die()
            return self.tsv_path
        finally:
            self._teardown()

    def run(self) -> int:
        """Full Phase 0 + Phase 1 loop. Returns total cycles written."""
        self._setup()
        try:
            self._record_baseline_or_die()

            deadline = time.monotonic() + self.config.budget_seconds
            budget = BudgetGuard(deadline_monotonic=deadline)
            plateau = PlateauDetector(window=self.config.plateau_window)
            regression = RegressionBlock(baseline=self._baseline_metric or 0.0)
            plateau.record(self._baseline_metric or 0.0)

            while True:
                if not budget.check().pass_:
                    break
                if not self._run_smoke():
                    self._record_row(status="smoke_fail", desc="smoke gate failed",
                                     metric=0.0, tokens=0, wall=0, commit_hash="-")
                    self._cycle_id += 1
                    if not budget.check().pass_:
                        break
                    continue
                mut = self._run_mutator_cycle(regression, plateau)
                if mut == "stop":
                    break
        finally:
            self._teardown()
        return self._cycle_id

    # --- internal phases ---

    def _setup(self) -> None:
        self._worktree = self._wt_mgr.create()
        self._tsv = ResultsTsv(self._worktree.results_tsv_path)
        self._tsv.init()
        self._cycle_id = 0
        self.pid_path.write_text(str(os.getpid()), encoding="utf-8")

    def _teardown(self) -> None:
        # Worktree itself is intentionally preserved — it contains results.tsv
        # plus the git lineage, which the user inspects post-run. Caller may
        # explicitly delete the directory if desired.
        if self._worktree is not None:
            pid = self.pid_path
            if pid.exists():
                try:
                    pid.unlink()
                except OSError:
                    pass

    def _record_baseline_or_die(self) -> None:
        result = run_eval(
            self.config.eval_cmd,
            self.config.metric_path,
            timeout=self.config.cycle_timeout_seconds,
        )
        if result.metric_value is None or result.exit_code != 0:
            sys.stderr.write(
                f"dry-run baseline failed (exit={result.exit_code}, "
                f"metric={result.metric_value}): {result.stderr[:200]}\n"
            )
            self._teardown()
            raise SystemExit(2)
        self._baseline_metric = result.metric_value
        self._record_row(
            status="baseline",
            desc="dry-run baseline",
            metric=result.metric_value,
            tokens=0,
            wall=result.wall_seconds,
            commit_hash="-",
        )
        self._cycle_id = 1

    def _run_smoke(self) -> bool:
        gate = SmokeGate(
            smoke_cmd=self.config.smoke_cmd,
            eval_cmd=self.config.eval_cmd,
            timeout=self.config.cycle_timeout_seconds,
        )
        return gate.check().pass_

    def _run_mutator_cycle(
        self,
        regression: RegressionBlock,
        plateau: PlateauDetector,
    ) -> str:
        mut_result = self._invoke_mutator()
        if mut_result.error is not None:
            self._record_row(
                status="mutation_error",
                desc=mut_result.error[:200],
                metric=0.0,
                tokens=mut_result.tokens_used,
                wall=0,
                commit_hash="-",
            )
            self._cycle_id += 1
            return "continue"

        eval_result = run_eval(
            self.config.eval_cmd,
            self.config.metric_path,
            timeout=self.config.cycle_timeout_seconds,
        )
        if eval_result.timed_out:
            self._git_rollback()
            self._record_row(
                status="eval_timeout",
                desc=mut_result.rationale[:200],
                metric=0.0,
                tokens=mut_result.tokens_used,
                wall=eval_result.wall_seconds,
                commit_hash="-",
            )
            self._cycle_id += 1
            return "continue"

        verdict = regression.check_score(eval_result.metric_value)
        if not verdict.pass_:
            self._git_rollback()
            self._record_row(
                status="regressed",
                desc=mut_result.rationale[:200],
                metric=eval_result.metric_value or 0.0,
                tokens=mut_result.tokens_used,
                wall=eval_result.wall_seconds,
                commit_hash="-",
            )
            self._cycle_id += 1
            # Feed plateau detector so a streak of regressions still terminates.
            self._record_regression_for_plateau(plateau, eval_result.metric_value)
            if not plateau.check().pass_:
                return "stop"
            return "continue"

        commit_hash = self._git_commit(mut_result.rationale)
        self._record_row(
            status="improved",
            desc=mut_result.rationale[:200],
            metric=eval_result.metric_value or 0.0,
            tokens=mut_result.tokens_used,
            wall=eval_result.wall_seconds,
            commit_hash=commit_hash,
        )
        self._cycle_id += 1

        if eval_result.metric_value is not None:
            plateau.record(eval_result.metric_value)
            if eval_result.metric_value > (self._baseline_metric or 0.0):
                self._baseline_metric = eval_result.metric_value
                regression.baseline = eval_result.metric_value
        if not plateau.check().pass_:
            return "stop"
        return "continue"

    def _record_regression_for_plateau(
        self, plateau: PlateauDetector, score: Optional[float]
    ) -> None:
        if score is not None:
            plateau.record(score)

    # --- I/O helpers ---

    def _invoke_mutator(self) -> MutationResult:
        assert self._worktree is not None
        scoped_prompt = (
            f"Edit only files matching glob: {self.config.scope_glob}\n\n"
            if self.config.scope_glob and self.config.scope_glob != "**"
            else ""
        )
        from .mutator import DEFAULT_PROMPT

        return Mutator(
            model=self.config.mutator_model,
            prompt=scoped_prompt + DEFAULT_PROMPT,
            timeout=self.config.cycle_timeout_seconds,
        ).mutate(worktree_path=self._worktree.path)

    def _git_commit(self, rationale: str) -> str:
        assert self._worktree is not None
        cwd = self._worktree.path
        subprocess.run(
            ["git", "add", "-A"], cwd=cwd, capture_output=True, text=True, check=False
        )
        subprocess.run(
            ["git", "commit", "-m", f"auto-improve: {rationale[:60]}"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return (proc.stdout or "-").strip() or "-"

    def _git_rollback(self) -> None:
        assert self._worktree is not None
        subprocess.run(
            ["git", "checkout", "--", "."],
            cwd=self._worktree.path,
            capture_output=True,
            text=True,
            check=False,
        )
        subprocess.run(
            ["git", "clean", "-fd"],
            cwd=self._worktree.path,
            capture_output=True,
            text=True,
            check=False,
        )

    def _record_row(
        self,
        *,
        status: str,
        desc: str,
        metric: float,
        tokens: int,
        wall: int,
        commit_hash: str,
    ) -> None:
        assert self._tsv is not None
        # desc must be non-empty (R3 normative); coerce here so guards never
        # see a blank-row write.
        safe_desc = desc.strip() or status
        self._tsv.append(
            ResultRow(
                cycle_id=self._cycle_id,
                timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                commit_hash=commit_hash,
                metric_value=metric,
                status=status,
                desc=safe_desc,
                tokens_used=tokens,
                wall_seconds=wall,
            )
        )

    # --- properties ---

    @property
    def tsv_path(self) -> Path:
        assert self._worktree is not None, "tsv_path is only valid inside run()"
        return self._worktree.results_tsv_path

    @property
    def pid_path(self) -> Path:
        assert self._worktree is not None, "pid_path is only valid inside run()"
        return self._worktree.path / "auto_improve.pid"


def status_mode(config: CoordinatorConfig) -> str:
    """Read the most-recent worktree's results.tsv (if any) and emit summary."""
    worktrees_dir = config.repo_root / ".worktrees"
    if not worktrees_dir.exists():
        return "# auto-improve summary\n\n_No prior runs._"
    candidates = sorted(
        (p for p in worktrees_dir.iterdir() if p.name.startswith("auto-improve-")),
        reverse=True,
    )
    if not candidates:
        return "# auto-improve summary\n\n_No prior runs._"
    last = candidates[0]
    return morning_summary(last / "results.tsv", last / "auto_improve.pid")
