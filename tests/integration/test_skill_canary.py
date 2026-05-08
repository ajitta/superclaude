"""Per-skill canary fixture for trigger regression coverage.

Each shipped skill MAY ship a `canary.yaml` next to its `SKILL.md`. Each entry
is a (trigger, expected_pattern) tuple; the test invokes `claude -p '<trigger>'`
and asserts the response body matches `expected_pattern` (case-insensitive).

Marked `@pytest.mark.canary` so it is excluded from the default `make test`
run (network + slow). Invoke explicitly with:

    uv run python -m pytest tests/integration/test_skill_canary.py -m canary -v

Defaults: `--model haiku`, 60s timeout. `--bare` is auto-enabled when
`ANTHROPIC_API_KEY` is set (skips hooks/MCP/plugin-sync/CLAUDE.md
auto-discovery → ~6s total instead of ~2min). OAuth-based local runs
fall back to full startup automatically. Override via env vars:
`CANARY_MODEL=sonnet` or `CANARY_TIMEOUT=90` for stricter validation.

Source: docs/specs/retrospective-followups-discovery-ajitta-2026-04-25.md (A1).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Iterator

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "src" / "superclaude" / "skills"
# Default to Haiku for cheaper/faster routing checks; override with CANARY_MODEL
# (e.g., CANARY_MODEL=sonnet) when validating a specific model's behavior.
CANARY_MODEL = os.getenv("CANARY_MODEL", "haiku")
SUBPROCESS_TIMEOUT = int(os.getenv("CANARY_TIMEOUT", "60"))


def _iter_canary_cases() -> Iterator[tuple[str, str, str]]:
    for canary_file in sorted(SKILLS_ROOT.glob("*/canary.yaml")):
        skill_name = canary_file.parent.name
        entries = yaml.safe_load(canary_file.read_text(encoding="utf-8")) or []
        for entry in entries:
            yield skill_name, entry["trigger"], entry["expected_pattern"]


_CANARY_CASES = list(_iter_canary_cases())


@pytest.mark.canary
@pytest.mark.parametrize(
    ("skill", "trigger", "pattern"),
    _CANARY_CASES,
    ids=[f"{s}::{t[:40]}" for s, t, _ in _CANARY_CASES],
)
def test_skill_trigger_canary(skill: str, trigger: str, pattern: str) -> None:
    """Invoke `claude -p` with the trigger; assert response matches the pattern.

    Failure means the trigger no longer routes to the skill (regression),
    OR the skill's response stopped containing the expected marker.
    """
    cmd = ["claude", "-p", trigger, "--model", CANARY_MODEL]
    # `--bare` strips hooks/MCP/plugin-sync/CLAUDE.md for fast startup but
    # forces ANTHROPIC_API_KEY auth (no OAuth/keychain). Auto-enable only
    # when the env var is present so OAuth-based local runs still work.
    if os.getenv("ANTHROPIC_API_KEY"):
        cmd.append("--bare")
    cmd.extend(["--output-format", "json"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
        check=False,
    )
    assert result.returncode == 0, (
        f"claude -p failed for skill={skill}: rc={result.returncode}\n"
        f"stderr={result.stderr[:500]}"
    )

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(f"non-JSON output from claude -p: {exc}\nstdout={result.stdout[:500]}")

    response = payload.get("result") or payload.get("response") or result.stdout
    assert re.search(pattern, response, flags=re.IGNORECASE), (
        f"skill={skill} trigger={trigger!r} did not produce expected pattern={pattern!r}\n"
        f"response head: {response[:500]}"
    )


def test_canary_manifest_count_baseline() -> None:
    """Smoke check: at least 2 reference manifests ship with the framework."""
    manifest_count = sum(1 for _ in SKILLS_ROOT.glob("*/canary.yaml"))
    assert manifest_count >= 2, (
        f"expected ≥2 reference canary manifests, found {manifest_count}"
    )
