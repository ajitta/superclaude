"""Tests for parallel-A/B aggregator (Phase 4)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from superclaude.scripts.parallel_ab.aggregator import aggregate

FIXTURES = Path(__file__).parent / "fixtures"


def _copy_fixtures(dst: Path, names: list[str]) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for n in names:
        shutil.copy(FIXTURES / n, dst / n.replace("obs_", "obs-").replace(".json", ".json"))


def _write_obs(dst: Path, obs: dict) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(obs, indent=2), encoding="utf-8")


def _ok_obs(vid: str, wall: float = 10.0, output_tokens: int = 1000) -> dict:
    return {
        "variant_id": vid,
        "exit_status": "ok",
        "tool_calls": [],
        "files_touched": [],
        "clarifying_questions": 0,
        "tokens": {"input": 500, "output": output_tokens},
        "wall_seconds": wall,
        "final_output_sha256": f"{vid.lower()*4}1234567890",
        "axes": {"think_before": f"{vid} note"},
    }


def _err_obs(vid: str) -> dict:
    return {
        "variant_id": vid,
        "exit_status": "error",
        "tool_calls": [],
        "files_touched": [],
        "clarifying_questions": 0,
        "tokens": {"input": 0, "output": 0},
        "wall_seconds": 0.5,
        "final_output_sha256": "",
        "axes": {},
    }


def test_two_variants_emit_matrix_and_decision(tmp_path: Path):
    _copy_fixtures(tmp_path, ["obs_a.json", "obs_b.json"])
    matrix_path, decision_path = aggregate(tmp_path)
    assert matrix_path.exists()
    assert decision_path.exists()
    matrix = matrix_path.read_text(encoding="utf-8")
    # both ids appear
    assert "| A |" in matrix
    assert "| B |" in matrix


def test_matrix_sorted_by_variant_id(tmp_path: Path):
    _write_obs(tmp_path / "obs-C.json", _ok_obs("C"))
    _write_obs(tmp_path / "obs-A.json", _ok_obs("A"))
    _write_obs(tmp_path / "obs-B.json", _ok_obs("B"))
    matrix_path, _ = aggregate(tmp_path)
    text = matrix_path.read_text(encoding="utf-8")
    # find variant rows in order
    idx_a = text.index("| A |")
    idx_b = text.index("| B |")
    idx_c = text.index("| C |")
    assert idx_a < idx_b < idx_c


def test_all_fail_says_no_clear_winner(tmp_path: Path):
    _write_obs(tmp_path / "obs-A.json", _err_obs("A"))
    _write_obs(tmp_path / "obs-B.json", _err_obs("B"))
    _, decision_path = aggregate(tmp_path)
    text = decision_path.read_text(encoding="utf-8")
    assert "no clear winner" in text.lower()


def test_picks_cheapest_passing_variant(tmp_path: Path):
    # A passes slow, B passes fast, C errors → B wins
    _write_obs(tmp_path / "obs-A.json", _ok_obs("A", wall=20.0))
    _write_obs(tmp_path / "obs-B.json", _ok_obs("B", wall=5.0))
    _write_obs(tmp_path / "obs-C.json", _err_obs("C"))
    _, decision_path = aggregate(tmp_path)
    text = decision_path.read_text(encoding="utf-8")
    assert "B" in text
    # winner declared explicitly
    assert "winner" in text.lower() or "recommended" in text.lower()


def test_tie_break_by_output_tokens(tmp_path: Path):
    # same wall_seconds, B uses fewer output tokens → B wins
    _write_obs(tmp_path / "obs-A.json", _ok_obs("A", wall=10.0, output_tokens=3000))
    _write_obs(tmp_path / "obs-B.json", _ok_obs("B", wall=10.0, output_tokens=1500))
    _, decision_path = aggregate(tmp_path)
    text = decision_path.read_text(encoding="utf-8")
    assert "B" in text


def test_sha256_truncated_to_8_chars(tmp_path: Path):
    _write_obs(
        tmp_path / "obs-A.json",
        {**_ok_obs("A"), "final_output_sha256": "0123456789abcdef0123456789abcdef"},
    )
    matrix_path, _ = aggregate(tmp_path)
    text = matrix_path.read_text(encoding="utf-8")
    assert "01234567" in text
    # the full hash should not appear in matrix (truncated)
    assert "0123456789abcdef0123456789abcdef" not in text


def test_dynamic_axes_columns_union(tmp_path: Path):
    _write_obs(
        tmp_path / "obs-A.json",
        {**_ok_obs("A"), "axes": {"think_before": "x", "simplicity": "y"}},
    )
    _write_obs(
        tmp_path / "obs-B.json",
        {**_ok_obs("B"), "axes": {"simplicity": "z", "surgical": "q"}},
    )
    matrix_path, _ = aggregate(tmp_path)
    header = matrix_path.read_text(encoding="utf-8").splitlines()[0]
    assert "think_before" in header
    assert "simplicity" in header
    assert "surgical" in header


def test_empty_obs_dir_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        aggregate(tmp_path)


def test_ignores_unrelated_files(tmp_path: Path):
    _write_obs(tmp_path / "obs-A.json", _ok_obs("A"))
    (tmp_path / "matrix.md").write_text("stale", encoding="utf-8")  # should not be parsed as obs
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    matrix_path, _ = aggregate(tmp_path)
    assert matrix_path.exists()


def test_decision_paragraph_non_empty(tmp_path: Path):
    _write_obs(tmp_path / "obs-A.json", _ok_obs("A"))
    _, decision_path = aggregate(tmp_path)
    assert len(decision_path.read_text(encoding="utf-8").strip()) > 20
