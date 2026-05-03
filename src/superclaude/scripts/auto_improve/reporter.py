"""Reporter — morning summary and `--status` output.

Reads results.tsv + PID file and produces a markdown summary suitable
for stdout printing on loop completion or status query.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from .results_tsv import ResultsTsv


_STALE_PID_THRESHOLD_S = 24 * 3600  # PID file older than this is treated as crashed


def _is_pid_alive(pid: int, pid_file: Path | None = None) -> bool:
    """Best-effort liveness probe.

    POSIX: `os.kill(pid, 0)` is reliable.
    Windows: `os.kill(pid, 0)` exists but errors don't disambiguate "no such
    pid" from "permission denied"; fall back to mtime — if the pid file was
    last touched more than 24h ago, treat as stale (worker would have rotated
    the file or terminated long before then).
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        # Windows path: kill(0) raises EINVAL on alive pids and EACCES/ENOENT
        # ambiguously. Use mtime as the disambiguator.
        if os.name == "nt" and pid_file is not None and pid_file.exists():
            try:
                age = time.time() - pid_file.stat().st_mtime
                return age < _STALE_PID_THRESHOLD_S
            except OSError:
                return False
        return False
    return True


def morning_summary(tsv_path: Path, pid_path: Path) -> str:
    rows = ResultsTsv(Path(tsv_path)).read_all()
    pid_alive = False
    pid_value: int | None = None
    pid_path_obj = Path(pid_path)
    if pid_path_obj.exists():
        try:
            pid_value = int(pid_path_obj.read_text(encoding="utf-8").strip())
            pid_alive = _is_pid_alive(pid_value, pid_file=pid_path_obj)
        except (ValueError, OSError):
            pid_alive = False

    lines: list[str] = ["# auto-improve summary", ""]

    if pid_alive and pid_value is not None:
        lines.append(f"**Status**: active (running, PID {pid_value})")
    else:
        lines.append("**Status**: not running")
    lines.append("")

    if not rows:
        lines.append("_No cycles recorded — no history yet._")
        return "\n".join(lines)

    baseline = rows[0]
    best = max(rows, key=lambda r: r.metric_value)
    total_tokens = sum(r.tokens_used for r in rows)
    delta = best.metric_value - baseline.metric_value

    lines.append(f"**Cycles**: {len(rows)}")
    lines.append(f"**Baseline metric**: {baseline.metric_value}")
    lines.append(
        f"**Best metric**: {best.metric_value} "
        f"({'+' if delta >= 0 else ''}{delta} vs baseline) at cycle {best.cycle_id}"
    )
    lines.append(f"**Total tokens used**: {total_tokens}")
    lines.append("")
    lines.append("## Recent cycles")
    for r in rows[-5:]:
        lines.append(
            f"- #{r.cycle_id} [{r.status}] metric={r.metric_value} desc={r.desc!r}"
        )
    return "\n".join(lines)
