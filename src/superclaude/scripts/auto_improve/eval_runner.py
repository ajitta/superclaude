"""EvalRunner — shell-driven objective metric extraction.

Runs an arbitrary shell command, parses stdout as JSON, applies a jmespath
expression, and returns a coerced float metric. Hard timeout per cycle
enforced via subprocess.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import jmespath


@dataclass(frozen=True)
class EvalResult:
    metric_value: Optional[float]
    exit_code: int
    wall_seconds: int
    stderr: str
    timed_out: bool


def run_eval(
    cmd: str,
    metric_path: str,
    timeout: int,
    cwd: Optional[str] = None,
) -> EvalResult:
    """Execute `cmd` via shell, extract metric_path from JSON stdout.

    `cwd` matters: the mutator edits files in the worktree, so eval-cmd MUST
    run there too. Without it, eval measures the parent repo's unchanged
    files and the metric stays pinned to baseline forever.
    """
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        return EvalResult(
            metric_value=None,
            exit_code=-1,
            wall_seconds=int(time.monotonic() - start),
            stderr=str(exc),
            timed_out=True,
        )

    wall = int(time.monotonic() - start)
    metric = _extract_metric(proc.stdout, metric_path)
    return EvalResult(
        metric_value=metric,
        exit_code=proc.returncode,
        wall_seconds=wall,
        stderr=proc.stderr,
        timed_out=False,
    )


def _extract_metric(stdout: str, metric_path: str) -> Optional[float]:
    if not stdout.strip():
        return None
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    try:
        value = jmespath.search(metric_path, payload)
    except jmespath.exceptions.JMESPathError:
        return None
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
