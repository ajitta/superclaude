"""CLI entry point for the auto-improve worker.

Usage:
    python -m superclaude.scripts.auto_improve --project . \\
        --eval-cmd 'pytest --json-report' --metric 'summary.passed' \\
        --budget 8h [--smoke-cmd ...] [--cycle-timeout 600] [--mutator-model sonnet]
        [--dry-run] [--status]

Invoked by the `/sc:auto-improve` command after the user confirms eval-cmd
responsibility (Phase 0). Runs in the foreground of the spawned subprocess.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .coordinator import Coordinator, CoordinatorConfig, status_mode


def _parse_duration(value: str) -> int:
    """Accept '8h', '30m', '120s', or a bare integer (seconds)."""
    value = value.strip().lower()
    if value.endswith("h"):
        return int(float(value[:-1]) * 3600)
    if value.endswith("m"):
        return int(float(value[:-1]) * 60)
    if value.endswith("s"):
        return int(float(value[:-1]))
    return int(value)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="auto_improve")
    p.add_argument("--project", default=".", help="repo root (default: cwd)")
    p.add_argument("--eval-cmd", help="shell command emitting JSON metric")
    p.add_argument("--metric", help="jmespath expression to extract metric")
    p.add_argument("--budget", default="8h", help="wall-clock budget (e.g. 8h, 30m)")
    p.add_argument("--cycle-timeout", default="600", help="per-cycle timeout (seconds)")
    p.add_argument("--smoke-cmd", default=None)
    p.add_argument("--mutator-model", default="sonnet")
    p.add_argument("--dry-run", action="store_true", help="record baseline only")
    p.add_argument("--status", action="store_true", help="print summary and exit")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    repo = Path(args.project).resolve()

    if args.status:
        cfg = CoordinatorConfig(
            repo_root=repo,
            eval_cmd="",
            metric_path="",
        )
        sys.stdout.write(status_mode(cfg))
        sys.stdout.write("\n")
        return 0

    if not args.eval_cmd or not args.metric:
        parser.error("--eval-cmd and --metric are required (unless --status)")

    cfg = CoordinatorConfig(
        repo_root=repo,
        eval_cmd=args.eval_cmd,
        metric_path=args.metric,
        budget_seconds=_parse_duration(args.budget),
        cycle_timeout_seconds=_parse_duration(args.cycle_timeout),
        smoke_cmd=args.smoke_cmd,
        mutator_model=args.mutator_model,
    )
    coord = Coordinator(cfg)
    if args.dry_run:
        coord.run_baseline_only()
    else:
        coord.run()
    sys.stdout.write(status_mode(cfg))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
