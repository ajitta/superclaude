"""Four guards enforcing overnight safety.

- BudgetGuard       : wall-clock deadline
- PlateauDetector   : 5 consecutive non-improvements -> stop
- RegressionBlock   : score < baseline -> rollback signal
- SmokeGate         : per-cycle smoke check before mutation

All guards expose the common GuardVerdict interface.
"""

from __future__ import annotations

import subprocess
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GuardVerdict:
    pass_: bool
    reason: str


class BudgetGuard:
    def __init__(self, deadline_monotonic: float):
        self.deadline = deadline_monotonic

    def check(self) -> GuardVerdict:
        if time.monotonic() < self.deadline:
            return GuardVerdict(pass_=True, reason="budget remaining")
        return GuardVerdict(pass_=False, reason="budget exhausted")


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

    def check(self) -> GuardVerdict:
        if len(self._scores) < self.window:
            return GuardVerdict(pass_=True, reason="window not yet full")
        # Window is full and best did not change while it filled -> plateau.
        return GuardVerdict(
            pass_=False, reason=f"plateau: {self.window} cycles without improvement"
        )


class RegressionBlock:
    def __init__(self, baseline: float):
        self.baseline = baseline

    def check_score(self, score: Optional[float]) -> GuardVerdict:
        if score is None:
            return GuardVerdict(
                pass_=False, reason="metric extraction failed (treated as regression)"
            )
        if score < self.baseline:
            return GuardVerdict(
                pass_=False,
                reason=f"regression: {score} < baseline {self.baseline}",
            )
        return GuardVerdict(
            pass_=True, reason=f"score {score} >= baseline {self.baseline}"
        )


class SmokeGate:
    """Runs a fast pre-cycle check; falls back to eval_cmd with short timeout."""

    FALLBACK_TIMEOUT_S = 30

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

    def check(self) -> GuardVerdict:
        cmd = self.smoke_cmd if self.smoke_cmd else self.eval_cmd
        timeout = self.timeout if self.smoke_cmd else self.FALLBACK_TIMEOUT_S
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.cwd,
            )
        except subprocess.TimeoutExpired:
            return GuardVerdict(pass_=False, reason="smoke timed out")
        if proc.returncode != 0:
            return GuardVerdict(
                pass_=False, reason=f"smoke failed (exit {proc.returncode})"
            )
        return GuardVerdict(pass_=True, reason="smoke ok")
