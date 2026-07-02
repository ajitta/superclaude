"""Orchestrate N parallel variant runners + aggregate results."""

from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import Awaitable, Callable

from .aggregator import aggregate
from .observation import Observation, emit
from .runner import run_variant
from .spec_loader import ABSpec, RunnerCfg, Scenario, Variant, load_spec

DEFAULT_MAX_PARALLEL = 8

RunnerFn = Callable[..., Awaitable[Observation]]


class OrchestratorError(RuntimeError):
    """Raised on orchestration-level failures (e.g., AB_MAX_PARALLEL exceeded)."""


def _resolve_max_parallel() -> int:
    raw = os.environ.get("AB_MAX_PARALLEL")
    if raw is None:
        return DEFAULT_MAX_PARALLEL
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_MAX_PARALLEL


def _resolve_timeout(cfg: RunnerCfg) -> RunnerCfg:
    raw = os.environ.get("AB_TIMEOUT_S")
    if raw is None:
        return cfg
    try:
        return replace(cfg, timeout_seconds=int(raw))
    except ValueError:
        return cfg


async def _run_one(
    runner_fn: RunnerFn,
    variant: Variant,
    scenario: Scenario,
    cfg: RunnerCfg,
    out_dir: Path,
) -> Observation:
    try:
        return await runner_fn(variant, scenario, cfg, out_dir)
    except Exception as exc:  # noqa: BLE001 — preserve batch even when one runner crashes
        sys.stderr.write(f"[parallel-ab] variant {variant.id} crashed: {exc!r}\n")
        obs = Observation(variant_id=variant.id, exit_status="error")
        emit(obs, out_dir / f"obs-{variant.id}.json")
        return obs


async def orchestrate(
    spec_path: Path,
    *,
    out_dir: Path | None = None,
    runner_fn: RunnerFn = run_variant,
) -> Path:
    """Run every variant in *spec_path* and aggregate observations.

    Returns the path to ``decision.md``.
    """
    spec: ABSpec = load_spec(Path(spec_path))
    max_parallel = _resolve_max_parallel()
    if len(spec.variants) > max_parallel:
        raise OrchestratorError(
            f"AB_MAX_PARALLEL={max_parallel} exceeded by spec with "
            f"{len(spec.variants)} variants"
        )

    runner_cfg = _resolve_timeout(spec.runner)
    out = Path(out_dir) if out_dir is not None else Path(spec_path).parent
    out.mkdir(parents=True, exist_ok=True)

    tasks = [
        _run_one(runner_fn, v, spec.scenario, runner_cfg, out) for v in spec.variants
    ]
    await asyncio.gather(*tasks)

    _matrix, decision = aggregate(out)
    return decision
