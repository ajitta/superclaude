"""Aggregate N variant observations into matrix.md + decision.md."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .observation import Observation, validate

FIXED_COLS = (
    "variant",
    "exit",
    "wall_s",
    "input_tok",
    "output_tok",
    "tools",
    "sha",
)


def aggregate(obs_dir: Path) -> tuple[Path, Path]:
    """Read every ``obs-*.json`` under *obs_dir* and emit matrix.md + decision.md.

    Returns the two output paths. Raises :class:`FileNotFoundError` if no
    observation files are present.
    """
    obs_dir = Path(obs_dir)
    obs_paths = sorted(obs_dir.glob("obs-*.json"))
    if not obs_paths:
        raise FileNotFoundError(f"no obs-*.json files in {obs_dir}")

    obs_list: list[Observation] = []
    for p in obs_paths:
        data = json.loads(p.read_text(encoding="utf-8"))
        obs_list.append(validate(data))
    obs_list.sort(key=lambda o: o.variant_id)

    matrix_path = obs_dir / "matrix.md"
    decision_path = obs_dir / "decision.md"
    matrix_path.write_text(_render_matrix(obs_list), encoding="utf-8")
    decision_path.write_text(_render_decision(obs_list), encoding="utf-8")
    return matrix_path, decision_path


def _axes_columns(obs_list: Iterable[Observation]) -> list[str]:
    keys: set[str] = set()
    for o in obs_list:
        keys.update(o.axes.keys())
    return sorted(keys)


def _tools_summary(obs: Observation) -> str:
    if not obs.tool_calls:
        return "—"
    return ", ".join(f"{tc.name}×{tc.count}" for tc in obs.tool_calls)


def _row(obs: Observation, axes_cols: list[str]) -> str:
    sha_short = obs.final_output_sha256[:8] if obs.final_output_sha256 else "—"
    cells = [
        obs.variant_id,
        obs.exit_status,
        f"{obs.wall_seconds:.1f}",
        str(obs.tokens.input),
        str(obs.tokens.output),
        _tools_summary(obs),
        sha_short,
    ]
    for col in axes_cols:
        cells.append(obs.axes.get(col, "—"))
    return "| " + " | ".join(cells) + " |"


def _render_matrix(obs_list: list[Observation]) -> str:
    axes_cols = _axes_columns(obs_list)
    header_cells = list(FIXED_COLS) + axes_cols
    header = "| " + " | ".join(header_cells) + " |"
    sep = "|" + "|".join(["---"] * len(header_cells)) + "|"
    rows = [_row(o, axes_cols) for o in obs_list]
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
