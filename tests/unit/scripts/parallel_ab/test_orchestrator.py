"""Tests for parallel-A/B orchestrator + CLI (Phase 5)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from superclaude.scripts.parallel_ab import orchestrator
from superclaude.scripts.parallel_ab.observation import Observation, Tokens, emit
from superclaude.scripts.parallel_ab.orchestrator import (
    DEFAULT_MAX_PARALLEL,
    OrchestratorError,
    orchestrate,
)
from superclaude.scripts.parallel_ab.spec_loader import RunnerCfg, Scenario, Variant


def _write_spec(tmp_path: Path, n: int = 3) -> Path:
    variants = "\n".join(f'  - id: V{i}\n    flag: "--vs[k:{i + 1}]"' for i in range(n))
    content = (
        "scenario:\n"
        "  input: /sc:brainstorm test\n"
        "  baseline_skill: brainstorm\n"
        "variants:\n"
        f"{variants}\n"
        "runner:\n"
        '  cli: "claude -p"\n'
        "  model: claude-haiku-4-5\n"
    )
    p = tmp_path / "variants.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def _make_fake_runner(behavior: dict[str, str] | None = None):
    """Returns a stub run_variant that writes a canned observation per variant."""

    behavior = behavior or {}

    async def fake(
        variant: Variant,
        scenario: Scenario,
        runner_cfg: RunnerCfg,
        out_dir: Path,
        **_kwargs: Any,
    ) -> Observation:
        kind = behavior.get(variant.id, "ok")
        if kind == "raise":
            raise RuntimeError("simulated runner failure")
        obs = Observation(
            variant_id=variant.id,
            exit_status="ok" if kind == "ok" else kind,
            wall_seconds=1.0,
            tokens=Tokens(input=100, output=200),
        )
        emit(obs, Path(out_dir) / f"obs-{variant.id}.json")
        return obs

    return fake


@pytest.mark.asyncio
async def test_orchestrate_emits_matrix_and_decision(tmp_path: Path):
    spec = _write_spec(tmp_path, n=3)
    decision = await orchestrate(spec, runner_fn=_make_fake_runner())
    assert decision.exists()
    assert decision.name == "decision.md"
    matrix = decision.parent / "matrix.md"
    assert matrix.exists()
    # 3 variants → 3 obs files
    obs_files = list(decision.parent.glob("obs-*.json"))
    assert len(obs_files) == 3


@pytest.mark.asyncio
async def test_too_many_variants_raises(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AB_MAX_PARALLEL", "2")
    spec = _write_spec(tmp_path, n=5)
    with pytest.raises(OrchestratorError, match="AB_MAX_PARALLEL"):
        await orchestrate(spec, runner_fn=_make_fake_runner())


@pytest.mark.asyncio
async def test_default_max_parallel_is_8():
    assert DEFAULT_MAX_PARALLEL == 8


@pytest.mark.asyncio
async def test_per_variant_exception_does_not_abort_batch(tmp_path: Path):
    spec = _write_spec(tmp_path, n=3)
    decision = await orchestrate(
        spec,
        runner_fn=_make_fake_runner({"V1": "raise"}),
    )
    # all 3 obs files exist (failing variant gets error obs synthesized)
    obs_files = list(decision.parent.glob("obs-*.json"))
    assert len(obs_files) == 3
    err_obs = json.loads((decision.parent / "obs-V1.json").read_text(encoding="utf-8"))
    assert err_obs["exit_status"] == "error"


@pytest.mark.asyncio
async def test_explicit_out_dir_override(tmp_path: Path):
    spec = _write_spec(tmp_path, n=2)
    custom = tmp_path / "custom_out"
    decision = await orchestrate(spec, runner_fn=_make_fake_runner(), out_dir=custom)
    assert decision.parent == custom


@pytest.mark.asyncio
async def test_default_out_dir_is_spec_parent(tmp_path: Path):
    sub = tmp_path / "exp"
    sub.mkdir()
    spec = _write_spec(sub, n=2)
    decision = await orchestrate(spec, runner_fn=_make_fake_runner())
    assert decision.parent == sub


@pytest.mark.asyncio
async def test_timeout_env_overrides_runner_cfg(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AB_TIMEOUT_S", "5")
    spec = _write_spec(tmp_path, n=1)

    seen_timeout: dict[str, int] = {}

    async def capture_runner(variant, scenario, runner_cfg, out_dir, **_):
        seen_timeout["t"] = runner_cfg.timeout_seconds
        obs = Observation(
            variant_id=variant.id,
            exit_status="ok",
            wall_seconds=0.0,
        )
        emit(obs, Path(out_dir) / f"obs-{variant.id}.json")
        return obs

    await orchestrate(spec, runner_fn=capture_runner)
    assert seen_timeout["t"] == 5


def test_cli_help_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "superclaude.scripts.parallel_ab", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "variants" in result.stdout.lower() or "spec" in result.stdout.lower()


def test_module_exposes_orchestrate():
    assert callable(orchestrator.orchestrate)
