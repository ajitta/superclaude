"""Tests for parallel-A/B aggregator (Phase 4)."""

from __future__ import annotations

from pathlib import Path

from superclaude.scripts.parallel_ab.aggregator import aggregate
from superclaude.scripts.parallel_ab.observation import Observation, Tokens


def _ok_obs(vid: str, wall: float = 10.0, output_tokens: int = 1000) -> Observation:
    return Observation(
        variant_id=vid,
        exit_status="ok",
        tokens=Tokens(input=500, output=output_tokens),
        wall_seconds=wall,
        final_output_sha256=f"{vid.lower() * 4}1234567890",
    )


def _err_obs(vid: str) -> Observation:
    return Observation(variant_id=vid, exit_status="error", wall_seconds=0.5)


def _refusal_obs(vid: str, category: str = "cyber") -> Observation:
    return Observation(
        variant_id=vid,
        exit_status="refusal",
        wall_seconds=1.0,
        refusal_category=category,
    )


def test_two_variants_emit_matrix_and_decision(tmp_path: Path):
    matrix_path, decision_path = aggregate(tmp_path, [_ok_obs("A"), _ok_obs("B")])
    assert matrix_path.exists()
    assert decision_path.exists()
    matrix = matrix_path.read_text(encoding="utf-8")
    assert "| A |" in matrix
    assert "| B |" in matrix


def test_only_given_observations_are_aggregated(tmp_path: Path):
    # Leftover obs-*.json from an earlier run (e.g. a removed variant) must
    # not be read back into the matrix or the decision.
    (tmp_path / "obs-old.json").write_text(
        '{"variant_id": "old", "exit_status": "ok", "wall_seconds": 0.1}',
        encoding="utf-8",
    )
    matrix_path, decision_path = aggregate(tmp_path, [_ok_obs("A", wall=5.0)])
    assert "| old |" not in matrix_path.read_text(encoding="utf-8")
    decision = decision_path.read_text(encoding="utf-8")
    assert "**A**" in decision
    assert "old" not in decision


def test_matrix_sorted_by_variant_id(tmp_path: Path):
    matrix_path, _ = aggregate(tmp_path, [_ok_obs("C"), _ok_obs("A"), _ok_obs("B")])
    text = matrix_path.read_text(encoding="utf-8")
    idx_a = text.index("| A |")
    idx_b = text.index("| B |")
    idx_c = text.index("| C |")
    assert idx_a < idx_b < idx_c


def test_all_fail_says_no_clear_winner(tmp_path: Path):
    _, decision_path = aggregate(tmp_path, [_err_obs("A"), _err_obs("B")])
    text = decision_path.read_text(encoding="utf-8")
    assert "no clear winner" in text.lower()


def test_picks_cheapest_passing_variant(tmp_path: Path):
    # A passes slow, B passes fast, C errors → B wins
    _, decision_path = aggregate(
        tmp_path, [_ok_obs("A", wall=20.0), _ok_obs("B", wall=5.0), _err_obs("C")]
    )
    text = decision_path.read_text(encoding="utf-8")
    assert "**B**" in text
    assert "winner" in text.lower() or "recommended" in text.lower()


def test_tie_break_by_output_tokens(tmp_path: Path):
    # same wall_seconds, B uses fewer output tokens → B wins
    _, decision_path = aggregate(
        tmp_path,
        [
            _ok_obs("A", wall=10.0, output_tokens=3000),
            _ok_obs("B", wall=10.0, output_tokens=1500),
        ],
    )
    assert "**B**" in decision_path.read_text(encoding="utf-8")


def test_sha256_truncated_to_8_chars(tmp_path: Path):
    obs = Observation(
        variant_id="A",
        exit_status="ok",
        final_output_sha256="0123456789abcdef0123456789abcdef",
    )
    matrix_path, _ = aggregate(tmp_path, [obs])
    text = matrix_path.read_text(encoding="utf-8")
    assert "01234567" in text
    assert "0123456789abcdef0123456789abcdef" not in text


def test_decision_paragraph_non_empty(tmp_path: Path):
    _, decision_path = aggregate(tmp_path, [_ok_obs("A")])
    assert len(decision_path.read_text(encoding="utf-8").strip()) > 20


def test_refusal_row_renders_category_in_exit_cell(tmp_path: Path):
    matrix_path, decision_path = aggregate(
        tmp_path, [_refusal_obs("A", "cyber"), _ok_obs("B")]
    )
    matrix = matrix_path.read_text(encoding="utf-8")
    assert "| A | refusal (cyber) |" in matrix
    assert "| B | ok |" in matrix
    # a refused variant never wins
    assert "**B**" in decision_path.read_text(encoding="utf-8")


def test_all_refused_means_no_winner(tmp_path: Path):
    _, decision_path = aggregate(tmp_path, [_refusal_obs("A", "reasoning_extraction")])
    assert "No clear winner" in decision_path.read_text(encoding="utf-8")
