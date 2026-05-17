"""Tests for parallel-A/B observation schema (Phase 2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from superclaude.scripts.parallel_ab.observation import (
    Observation,
    ObservationError,
    Tokens,
    ToolCall,
    compute_sha256,
    emit,
    validate,
)


def _sample_dict() -> dict:
    return {
        "variant_id": "B",
        "exit_status": "ok",
        "tool_calls": [
            {"name": "Grep", "count": 3},
            {"name": "Read", "count": 2},
        ],
        "files_touched": [],
        "clarifying_questions": 1,
        "tokens": {"input": 1240, "output": 3200},
        "wall_seconds": 18.4,
        "final_output_sha256": "abc123",
        "axes": {
            "think_before": "explicit assumption stated",
            "simplicity": "k=5 → 5 perspectives, no extra blocks",
            "surgical": "no file edits attempted",
            "goal_driven": "criterion implicit",
        },
    }


def test_round_trip_via_validate_then_emit(tmp_path: Path):
    d = _sample_dict()
    obs = validate(d)
    assert isinstance(obs, Observation)
    out = tmp_path / "obs.json"
    emit(obs, out)
    reloaded = json.loads(out.read_text(encoding="utf-8"))
    assert reloaded == d


def test_observation_fields_typed():
    obs = validate(_sample_dict())
    assert obs.variant_id == "B"
    assert obs.exit_status == "ok"
    assert isinstance(obs.tokens, Tokens)
    assert obs.tokens.input == 1240
    assert isinstance(obs.tool_calls[0], ToolCall)
    assert obs.tool_calls[0].name == "Grep"
    assert obs.tool_calls[0].count == 3


def test_missing_variant_id_raises():
    d = _sample_dict()
    del d["variant_id"]
    with pytest.raises(ObservationError, match="variant_id"):
        validate(d)


def test_missing_exit_status_raises():
    d = _sample_dict()
    del d["exit_status"]
    with pytest.raises(ObservationError, match="exit_status"):
        validate(d)


def test_invalid_exit_status_raises():
    d = _sample_dict()
    d["exit_status"] = "bogus"
    with pytest.raises(ObservationError, match="exit_status"):
        validate(d)


def test_unknown_top_level_key_warns_but_loads():
    d = _sample_dict()
    d["future_field"] = "ignored"
    with pytest.warns(UserWarning, match="future_field"):
        obs = validate(d)
    assert obs.variant_id == "B"


def test_compute_sha256_stable():
    assert compute_sha256("hello") == compute_sha256("hello")
    assert compute_sha256("a") != compute_sha256("b")
    # known hash for "hello"
    expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert compute_sha256("hello") == expected


def test_axes_round_trip_arbitrary_keys():
    d = _sample_dict()
    d["axes"] = {"custom_axis": "value"}
    obs = validate(d)
    assert obs.axes == {"custom_axis": "value"}


def test_emit_creates_parent_dirs(tmp_path: Path):
    obs = validate(_sample_dict())
    out = tmp_path / "nested" / "dir" / "obs.json"
    emit(obs, out)
    assert out.exists()


def test_tokens_default_zero_when_missing():
    d = _sample_dict()
    del d["tokens"]
    obs = validate(d)
    assert obs.tokens.input == 0
    assert obs.tokens.output == 0


def test_tool_calls_default_empty_when_missing():
    d = _sample_dict()
    del d["tool_calls"]
    obs = validate(d)
    assert obs.tool_calls == ()


def test_files_touched_default_empty_when_missing():
    d = _sample_dict()
    del d["files_touched"]
    obs = validate(d)
    assert obs.files_touched == ()
