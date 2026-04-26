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


def run_eval(cmd: str, metric_path: str, timeout: int) -> EvalResult:
    """Execute `cmd` via shell, extract metric_path from JSON stdout."""
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
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
