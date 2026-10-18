"""Tests for parallel-A/B observation record (Phase 2)."""

from __future__ import annotations

import json
from pathlib import Path

from superclaude.scripts.parallel_ab.observation import (
    Observation,
    Tokens,
    ToolCall,
    compute_sha256,
    emit,
)


def _sample() -> Observation:
    return Observation(
        variant_id="B",
        exit_status="ok",
        tool_calls=(ToolCall(name="Grep", count=3), ToolCall(name="Read", count=2)),
        tokens=Tokens(input=1240, output=3200),
        wall_seconds=18.4,
        final_output_sha256="abc123",
    )


def test_emit_writes_documented_shape(tmp_path: Path):
    out = tmp_path / "obs.json"
    emit(_sample(), out)
    assert json.loads(out.read_text(encoding="utf-8")) == {
        "variant_id": "B",
        "exit_status": "ok",
        "tool_calls": [{"name": "Grep", "count": 3}, {"name": "Read", "count": 2}],
        "tokens": {"input": 1240, "output": 3200},
        "wall_seconds": 18.4,
        "final_output_sha256": "abc123",
    }


def test_emit_creates_parent_dirs(tmp_path: Path):
    out = tmp_path / "nested" / "dir" / "obs.json"
    emit(_sample(), out)
    assert out.exists()


def test_refusal_category_emitted_only_on_refusal(tmp_path: Path):
    refused = Observation(variant_id="r", exit_status="refusal", refusal_category="bio")
    emit(refused, tmp_path / "obs-r.json")
    assert (
        json.loads((tmp_path / "obs-r.json").read_text(encoding="utf-8"))[
            "refusal_category"
        ]
        == "bio"
    )
    emit(_sample(), tmp_path / "obs-ok.json")
    assert "refusal_category" not in json.loads(
        (tmp_path / "obs-ok.json").read_text(encoding="utf-8")
    )


def test_compute_sha256_stable():
    assert compute_sha256("hello") == compute_sha256("hello")
    assert compute_sha256("a") != compute_sha256("b")
    # known hash for "hello"
    expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert compute_sha256("hello") == expected
