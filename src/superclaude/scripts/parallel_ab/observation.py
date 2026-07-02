"""Observation schema for parallel-A/B harness.

Matches the JSON schema in
``docs/specs/parallel-ab-harness-design-ajitta-2026-05-14.md``.
"""

from __future__ import annotations

import hashlib
import json
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

EXIT_STATUSES = {"ok", "error", "timeout"}

KNOWN_KEYS = {
    "variant_id",
    "exit_status",
    "tool_calls",
    "files_touched",
    "clarifying_questions",
    "tokens",
    "wall_seconds",
    "final_output_sha256",
    "axes",
}


class ObservationError(ValueError):
    """Raised when an observation dict fails validation."""


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
    exit_status: str
    tool_calls: tuple[ToolCall, ...] = ()
    files_touched: tuple[str, ...] = ()
    clarifying_questions: int = 0
    tokens: Tokens = field(default_factory=Tokens)
    wall_seconds: float = 0.0
    final_output_sha256: str = ""
    axes: dict[str, str] = field(default_factory=dict)


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require(d: dict[str, Any], key: str) -> Any:
    if key not in d:
        raise ObservationError(f"missing required key: {key}")
    return d[key]


def validate(d: dict[str, Any]) -> Observation:
    """Validate a raw dict + return a typed :class:`Observation`.

    Unknown top-level keys emit a :class:`UserWarning` but do not raise
    (forward-compatibility).
    """
    if not isinstance(d, dict):
        raise ObservationError("observation must be a mapping")

    unknown = set(d.keys()) - KNOWN_KEYS
    for key in sorted(unknown):
        warnings.warn(
            f"unknown observation key: {key!r} (forward-compat; ignored)",
            UserWarning,
            stacklevel=2,
        )

    variant_id = _require(d, "variant_id")
    exit_status = _require(d, "exit_status")
    if exit_status not in EXIT_STATUSES:
        raise ObservationError(
            f"exit_status must be one of {sorted(EXIT_STATUSES)}; got {exit_status!r}"
        )

    tool_calls_raw = d.get("tool_calls") or []
    tool_calls = tuple(
        ToolCall(name=str(tc["name"]), count=int(tc["count"])) for tc in tool_calls_raw
    )

    files_touched = tuple(str(f) for f in (d.get("files_touched") or []))

    tokens_raw = d.get("tokens") or {}
    tokens = Tokens(
        input=int(tokens_raw.get("input", 0)),
        output=int(tokens_raw.get("output", 0)),
    )

    return Observation(
        variant_id=str(variant_id),
        exit_status=str(exit_status),
        tool_calls=tool_calls,
        files_touched=files_touched,
        clarifying_questions=int(d.get("clarifying_questions", 0)),
        tokens=tokens,
        wall_seconds=float(d.get("wall_seconds", 0.0)),
        final_output_sha256=str(d.get("final_output_sha256", "")),
        axes=dict(d.get("axes") or {}),
    )


def _to_dict(obs: Observation) -> dict[str, Any]:
    return {
        "variant_id": obs.variant_id,
        "exit_status": obs.exit_status,
        "tool_calls": [asdict(tc) for tc in obs.tool_calls],
        "files_touched": list(obs.files_touched),
        "clarifying_questions": obs.clarifying_questions,
        "tokens": asdict(obs.tokens),
        "wall_seconds": obs.wall_seconds,
        "final_output_sha256": obs.final_output_sha256,
        "axes": dict(obs.axes),
    }


def emit(obs: Observation, path: Path) -> None:
    """Write *obs* as pretty JSON to *path* (parents created if missing)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_to_dict(obs), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
