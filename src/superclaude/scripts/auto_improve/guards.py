"""Four guards enforcing overnight safety.

- BudgetGuard       : wall-clock deadline
- PlateauDetector   : 5 consecutive non-improvements -> stop
- RegressionBlock   : score < baseline -> rollback signal
- SmokeGate         : per-cycle smoke check before mutation

Every check returns a bool: True = keep going, False = the guard tripped.
The coordinator decides what to write to results.tsv for each stop (the
mutation rationale for a regression, a fixed desc for a smoke failure), so
the guards carry no reason text of their own.
"""

from __future__ import annotations

import subprocess
import time
from collections import deque
from typing import Optional

from superclaude.utils import run_shell


class BudgetGuard:
    def __init__(self, deadline_monotonic: float):
        self.deadline = deadline_monotonic

    def check(self) -> bool:
        return time.monotonic() < self.deadline


class PlateauDetector:
    """Tracks N most-recent scores; fails when window is full and no improvement."""

    def __init__(self, window: int = 5):
        self.window = window
        self._scores: deque[float] = deque(maxlen=window)
        self._best: Optional[float] = None

    def record(self, score: float) -> None:
        self._scores.append(score)
        if self._best is None or score > self._best:
            self._best = score
            self._scores.clear()
            self._scores.append(score)

    def check(self) -> bool:
        # Window full and best did not change while it filled -> plateau.
        return len(self._scores) < self.window


class RegressionBlock:
    def __init__(self, baseline: float):
        self.baseline = baseline

    def check_score(self, score: Optional[float]) -> bool:
        # A missing metric (extraction failed) is treated as a regression.
        return score is not None and score >= self.baseline


class SmokeGate:
    """Runs a pre-cycle check; falls back to eval_cmd under the same timeout.

    The fallback used to be capped at a fixed 30 s, so an eval that passed the
    baseline under the cycle timeout timed out on every cycle's smoke check.
    """

    def __init__(
        self,
        smoke_cmd: Optional[str],
        eval_cmd: str,
        timeout: int = 30,
        cwd: Optional[str] = None,
    ):
        self.smoke_cmd = smoke_cmd
        self.eval_cmd = eval_cmd
        self.timeout = timeout
        self.cwd = cwd

    def check(self) -> bool:
        cmd = self.smoke_cmd if self.smoke_cmd else self.eval_cmd
        try:
            proc = run_shell(cmd, timeout=self.timeout, cwd=self.cwd)
        except subprocess.TimeoutExpired:
            return False
        return proc.returncode == 0
