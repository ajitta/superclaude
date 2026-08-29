"""CLI entry point for the auto-improve worker.

Usage:
    superclaude auto-improve --project . \\
        --eval-cmd 'pytest --json-report' --metric 'summary.passed' \\
        --budget 8h [--smoke-cmd ...] [--cycle-timeout 600] [--mutator-model sonnet]
        [--dry-run] [--status]

Inside a dev checkout, `uv run python -m superclaude.scripts.auto_improve` is the
equivalent invocation; a bare `python -m ...` resolves only if the package
happens to be importable for whichever interpreter is first on PATH.

Invoked by the `/sc:auto-improve` command after the user confirms eval-cmd
responsibility (Phase 0). Runs in the foreground of the spawned subprocess.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .coordinator import Coordinator, CoordinatorConfig, status_mode


def _parse_duration(value: str) -> int:
    """Accept '8h', '30m', '120s', or a bare integer (seconds). Must be positive.

    Used as an argparse ``type=`` converter, so a malformed value surfaces as a
    usage error (exit 2) instead of a raw traceback out of this module.

    Non-positive values are rejected for the same reason: they parse fine but
    are already expired when the run starts. ``--budget 0`` (or ``-5``) makes
    ``BudgetGuard`` fail its first check, so the loop breaks before a single
    cycle and the morning ``--status`` shows a truncated run with no error;
    a non-positive ``--cycle-timeout`` makes every ``subprocess.run`` raise
    ``TimeoutExpired`` immediately, which surfaces as a bogus eval failure.
    """
    normalized = value.strip().lower()
    try:
        if normalized.endswith("h"):
            seconds = int(float(normalized[:-1]) * 3600)
        elif normalized.endswith("m"):
            seconds = int(float(normalized[:-1]) * 60)
        elif normalized.endswith("s"):
            seconds = int(float(normalized[:-1]))
        else:
            seconds = int(normalized)
    except (ValueError, OverflowError):
        raise argparse.ArgumentTypeError(
            f"invalid duration {value!r}: expected 8h, 30m, 120s, "
            "or a bare integer (seconds)"
        ) from None
    if seconds <= 0:
        raise argparse.ArgumentTypeError(
            f"invalid duration {value!r}: must be a positive number of seconds "
            "(a non-positive budget or timeout is already expired at start)"
        )
    return seconds


def _build_parser(prog: str = "auto_improve") -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=prog)
    p.add_argument("--project", default=".", help="repo root (default: cwd)")
    p.add_argument("--eval-cmd", help="shell command emitting JSON metric")
    p.add_argument("--metric", help="jmespath expression to extract metric")
    p.add_argument(
        "--budget",
        default="8h",
        type=_parse_duration,
        help="wall-clock budget (e.g. 8h, 30m)",
    )
    p.add_argument(
        "--cycle-timeout",
        default="600",
        type=_parse_duration,
        help="per-cycle timeout (seconds)",
    )
    p.add_argument("--smoke-cmd", default=None)
    p.add_argument("--mutator-model", default="sonnet")
    p.add_argument(
        "--scope",
        default="**",
        help="glob restricting mutator edits (advisory, default: **)",
    )
    p.add_argument("--dry-run", action="store_true", help="record baseline only")
    p.add_argument("--status", action="store_true", help="print summary and exit")
    return p


def main(argv: list[str] | None = None, prog: str = "auto_improve") -> int:
    parser = _build_parser(prog)
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
        budget_seconds=args.budget,
        cycle_timeout_seconds=args.cycle_timeout,
        smoke_cmd=args.smoke_cmd,
        mutator_model=args.mutator_model,
        scope_glob=args.scope,
    )
    coord = Coordinator(cfg)
    if args.dry_run:
        coord.run_baseline_only()
    else:
        coord.run()
    sys.stdout.write(status_mode(cfg))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover — exercised via __main__.py
    raise SystemExit(main())
