"""Aggregate N variant observations into matrix.md + decision.md."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .observation import Observation

FIXED_COLS = (
    "variant",
    "exit",
    "wall_s",
    "input_tok",
    "output_tok",
    "tools",
    "sha",
)


def aggregate(out_dir: Path, observations: Iterable[Observation]) -> tuple[Path, Path]:
    """Render *observations* (this run's, any order) to matrix.md + decision.md
    under *out_dir*; return the two paths.

    The ``obs-*.json`` files on disk are for the human reader only and are
    never read back, so a stale file from an earlier run cannot enter the
    matrix or the decision.
    """
    out_dir = Path(out_dir)
    obs_list = sorted(observations, key=lambda o: o.variant_id)

    matrix_path = out_dir / "matrix.md"
    decision_path = out_dir / "decision.md"
    matrix_path.write_text(_render_matrix(obs_list), encoding="utf-8")
    decision_path.write_text(_render_decision(obs_list), encoding="utf-8")
    return matrix_path, decision_path


def _tools_summary(obs: Observation) -> str:
    if not obs.tool_calls:
        return "—"
    return ", ".join(f"{tc.name}×{tc.count}" for tc in obs.tool_calls)


def _row(obs: Observation) -> str:
    sha_short = obs.final_output_sha256[:8] if obs.final_output_sha256 else "—"
    exit_cell = obs.exit_status
    if obs.refusal_category:
        exit_cell = f"{obs.exit_status} ({obs.refusal_category})"
    cells = [
        obs.variant_id,
        exit_cell,
        f"{obs.wall_seconds:.1f}",
        str(obs.tokens.input),
        str(obs.tokens.output),
        _tools_summary(obs),
        sha_short,
    ]
    return "| " + " | ".join(cells) + " |"


def _render_matrix(obs_list: list[Observation]) -> str:
    header = "| " + " | ".join(FIXED_COLS) + " |"
    sep = "|" + "|".join(["---"] * len(FIXED_COLS)) + "|"
    rows = [_row(o) for o in obs_list]
    return "\n".join([header, sep, *rows]) + "\n"


def _render_decision(obs_list: list[Observation]) -> str:
    passing = [o for o in obs_list if o.exit_status == "ok"]
    if not passing:
        return (
            "## Decision\n\n"
            "No clear winner — all variants failed "
            f"(N={len(obs_list)}). Inspect matrix.md for individual exit statuses.\n"
        )
    # cheapest = fastest wall, then fewest output tokens
    winner = min(
        passing,
        key=lambda o: (o.wall_seconds, o.tokens.output, o.variant_id),
    )
    losers = [o.variant_id for o in obs_list if o.variant_id != winner.variant_id]
    return (
        "## Decision\n\n"
        f"Recommended winner: **{winner.variant_id}** "
        f"({winner.wall_seconds:.1f}s, {winner.tokens.output} output tokens, "
        f"{len(winner.tool_calls)} tool-call kinds). "
        f"Other variants: {', '.join(losers) if losers else '—'}. "
        "See matrix.md for full side-by-side comparison.\n"
    )
