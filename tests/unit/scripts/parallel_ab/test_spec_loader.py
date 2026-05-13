"""Tests for parallel-A/B spec loader (Phase 1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.scripts.parallel_ab.spec_loader import (
    ABSpec,
    SpecError,
    Variant,
    load_spec,
)

FIXTURE_MIN = Path(__file__).parent / "fixtures" / "variants_min.yaml"


def test_loads_minimal_valid_spec():
    spec = load_spec(FIXTURE_MIN)
    assert isinstance(spec, ABSpec)
    assert spec.scenario.input == "/sc:brainstorm test"
    assert spec.scenario.baseline_skill == "brainstorm"
    assert len(spec.variants) == 1
    assert spec.variants[0].id == "A"
    assert spec.runner.cli == "claude -p"
    assert spec.runner.model == "claude-haiku-4-5"


def test_default_timeout_bare_and_oauth_fallback(tmp_path: Path):
    # variants_min.yaml omits these → defaults apply
    spec = load_spec(FIXTURE_MIN)
    assert spec.runner.timeout_seconds == 60
    assert spec.runner.bare is True
    assert spec.runner.oauth_fallback is True


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "spec.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_scenario_input_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
scenario:
  baseline_skill: brainstorm
variants:
  - id: A
    flag: ""
runner:
  cli: "claude -p"
  model: m
""",
    )
    with pytest.raises(SpecError, match="scenario.input"):
        load_spec(p)


def test_duplicate_variant_ids_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
scenario:
  input: x
variants:
  - id: A
    flag: ""
  - id: A
    flag: ""
runner:
  cli: "claude -p"
  model: m
""",
    )
    with pytest.raises(SpecError, match="duplicate"):
        load_spec(p)


def test_empty_variants_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
scenario:
  input: x
variants: []
runner:
  cli: "claude -p"
  model: m
""",
    )
    with pytest.raises(SpecError, match="variants"):
        load_spec(p)


def test_unknown_runner_cli_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
scenario:
  input: x
variants:
  - id: A
    flag: ""
runner:
  cli: "claude-cli"
  model: m
""",
    )
    with pytest.raises(SpecError, match="runner.cli"):
        load_spec(p)


def test_missing_runner_model_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
scenario:
  input: x
variants:
  - id: A
    flag: ""
runner:
  cli: "claude -p"
""",
    )
    with pytest.raises(SpecError, match="runner.model"):
        load_spec(p)


def test_baseline_skill_optional(tmp_path: Path):
    p = _write(
        tmp_path,
        """
scenario:
  input: x
variants:
  - id: A
    flag: ""
runner:
  cli: "claude -p"
  model: m
""",
    )
    spec = load_spec(p)
    assert spec.scenario.baseline_skill is None


def test_extra_args_defaults_to_empty(tmp_path: Path):
    p = _write(
        tmp_path,
        """
scenario:
  input: x
variants:
  - id: A
    flag: "--vs"
runner:
  cli: "claude -p"
  model: m
""",
    )
    spec = load_spec(p)
    assert spec.variants[0].extra_args == ""


def test_variants_are_frozen(tmp_path: Path):
    spec = load_spec(FIXTURE_MIN)
    with pytest.raises(Exception):
        spec.variants[0].id = "Z"  # type: ignore[misc]


def test_variant_dataclass_immutable_tuple():
    spec = load_spec(FIXTURE_MIN)
    assert isinstance(spec.variants, tuple)
    assert isinstance(spec.variants[0], Variant)
