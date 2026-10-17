"""Observation record for the parallel-A/B harness.

One :class:`Observation` per variant run; :func:`emit` writes it as
``obs-<variant>.json`` for the human reader. The aggregator works from the
in-memory objects and never reads these files back.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Tokens:
    input: int = 0
    output: int = 0


@dataclass(frozen=True)
class ToolCall:
    name: str
    count: int


@dataclass(frozen=True)
class Observation:
    variant_id: str
    exit_status: str  # ok | error | timeout | refusal
    tool_calls: tuple[ToolCall, ...] = ()
    tokens: Tokens = field(default_factory=Tokens)
    wall_seconds: float = 0.0
    final_output_sha256: str = ""
    # Set only when exit_status == "refusal": the model's stop_details.category
    # (cyber | bio | reasoning_extraction | ...) or "unknown" when the payload
    # carried the refusal without a category.
    refusal_category: str = ""


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_dict(obs: Observation) -> dict[str, Any]:
    d: dict[str, Any] = {
        "variant_id": obs.variant_id,
        "exit_status": obs.exit_status,
        "tool_calls": [asdict(tc) for tc in obs.tool_calls],
        "tokens": asdict(obs.tokens),
        "wall_seconds": obs.wall_seconds,
        "final_output_sha256": obs.final_output_sha256,
    }
    # Emitted only on a refusal so non-refusal observations keep a fixed shape.
    if obs.refusal_category:
        d["refusal_category"] = obs.refusal_category
    return d


def emit(obs: Observation, path: Path) -> None:
    """Write *obs* as pretty JSON to *path* (parents created if missing)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_to_dict(obs), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
