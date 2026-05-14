"""End-to-end validation for the Parallel A/B Harness.

Gated on ``AB_E2E=1`` — CI has no ``claude -p`` auth, so this is opt-in and
skipped by default. When enabled it runs the real 4-variant brainstorm
scenario through :func:`orchestrate` and asserts the artifacts land.

    AB_E2E=1 uv run pytest tests/integration/test_parallel_ab_e2e.py -v
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from superclaude.scripts.parallel_ab.orchestrator import orchestrate

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPO_ROOT / "docs" / "experiments" / "brainstorm-ab-2026-05-14" / "variants.yaml"


@pytest.mark.skipif(
    not os.getenv("AB_E2E"),
    reason="set AB_E2E=1 to run; needs real `claude -p` auth",
)
def test_parallel_ab_e2e(tmp_path: Path) -> None:
    """Orchestrate the 4-variant spec and assert matrix + decision artifacts."""
    decision = asyncio.run(orchestrate(SPEC, out_dir=tmp_path))

    obs_files = sorted(tmp_path.glob("obs-*.json"))
    assert len(obs_files) == 4, f"expected 4 obs files, got {[p.name for p in obs_files]}"

    matrix = tmp_path / "matrix.md"
    assert matrix.is_file(), "matrix.md not emitted"
    data_rows = [
        line
        for line in matrix.read_text(encoding="utf-8").splitlines()
        if line.startswith("|") and not set(line) <= set("| -:")
    ]
    # header row + 4 variant rows
    assert len(data_rows) == 5, f"expected header + 4 variant rows, got {len(data_rows)}"

    assert decision.is_file() and decision.name == "decision.md"
    assert decision.read_text(encoding="utf-8").strip(), "decision.md is empty"
