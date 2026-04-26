"""Reporter — morning summary and `--status` output.

Reads results.tsv + PID file and produces a markdown summary suitable
for stdout printing on loop completion or status query.
"""

from __future__ import annotations

import os
from pathlib import Path

from .results_tsv import ResultsTsv


def _is_pid_alive(pid: int) -> bool:
    """Best-effort liveness probe; treats kill(0) errors as 'not alive'."""
    if os.name == "nt":
        # On Windows, kill(0) is unreliable; check via tasklist would be heavy.
        # Existence of the PID file is treated as a sufficient hint.
        return True
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def morning_summary(tsv_path: Path, pid_path: Path) -> str:
    rows = ResultsTsv(Path(tsv_path)).read_all()
    pid_alive = False
    pid_value: int | None = None
    if Path(pid_path).exists():
        try:
            pid_value = int(Path(pid_path).read_text(encoding="utf-8").strip())
            pid_alive = _is_pid_alive(pid_value)
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
