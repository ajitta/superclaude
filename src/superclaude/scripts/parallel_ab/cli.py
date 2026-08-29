"""CLI entry: ``python -m superclaude.scripts.parallel_ab <variants.yaml>``."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from .orchestrator import OrchestratorError, orchestrate


def _build_parser(
    prog: str = "python -m superclaude.scripts.parallel_ab",
) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=prog,
        description=(
            "Run N variants in parallel via claude -p and emit matrix.md + decision.md."
        ),
    )
    p.add_argument(
        "spec",
        type=Path,
        help="Path to variants.yaml spec file",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Override output directory (default: spec file parent)",
    )
    return p


def main(
    argv: list[str] | None = None,
    prog: str = "python -m superclaude.scripts.parallel_ab",
) -> int:
    args = _build_parser(prog).parse_args(argv)
    try:
        decision = asyncio.run(orchestrate(args.spec, out_dir=args.out_dir))
    except OrchestratorError as exc:
        sys.stderr.write(f"orchestrator error: {exc}\n")
        return 2
    except FileNotFoundError as exc:
        sys.stderr.write(f"file not found: {exc}\n")
        return 3
    sys.stdout.write(f"{decision}\n")
    return 0


if __name__ == "__main__":  # pragma: no cover — exercised via __main__.py
    raise SystemExit(main())
