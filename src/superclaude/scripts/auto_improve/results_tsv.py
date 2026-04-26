"""results.tsv I/O — single source of truth for the auto-improve loop.

Schema (design §4): 8 columns, append-only, single writer.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

STATUS_VALUES: frozenset[str] = frozenset(
    {
        "baseline",
        "improved",
        "regressed",
        "smoke_fail",
        "eval_timeout",
        "mutation_error",
    }
)

HEADER = (
    "# cycle_id\ttimestamp\tcommit_hash\tmetric_value\t"
    "status\tdesc\ttokens_used\twall_seconds"
)

_COLUMNS = (
    "cycle_id",
    "timestamp",
    "commit_hash",
    "metric_value",
    "status",
    "desc",
    "tokens_used",
    "wall_seconds",
)


@dataclass(frozen=True)
class ResultRow:
    cycle_id: int
    timestamp: str
    commit_hash: str
    metric_value: float
    status: str
    desc: str
    tokens_used: int
    wall_seconds: int

    def __post_init__(self) -> None:
        if self.status not in STATUS_VALUES:
            raise ValueError(
                f"invalid status {self.status!r}; expected one of {sorted(STATUS_VALUES)}"
            )
        # R3 normative: empty desc is forbidden — enforces mutation rationale.
        # mutation_error rows must still record *some* trace (e.g., the error message).
        if not self.desc:
            raise ValueError("desc must not be empty (R3 normative)")

    def to_tsv_line(self) -> str:
        return "\t".join(str(getattr(self, c)) for c in _COLUMNS)

    @classmethod
    def from_tsv_line(cls, line: str) -> ResultRow:
        parts = line.split("\t")
        if len(parts) != len(_COLUMNS):
            raise ValueError(
                f"expected {len(_COLUMNS)} fields, got {len(parts)} in line {line!r}"
            )
        kwargs: dict[str, object] = {}
        for col, raw in zip(_COLUMNS, parts):
            field_type = next(f.type for f in fields(cls) if f.name == col)
            kwargs[col] = _coerce(raw, field_type)
        return cls(**kwargs)  # type: ignore[arg-type]


def _coerce(raw: str, type_hint: object) -> object:
    if type_hint is int or type_hint == "int":
        return int(raw)
    if type_hint is float or type_hint == "float":
        return float(raw)
    return raw


class ResultsTsv:
    """Append-only writer + reader for results.tsv. Single writer per worktree."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(HEADER + "\n", encoding="utf-8")

    def append(self, row: ResultRow) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(row.to_tsv_line() + "\n")

    def read_all(self) -> list[ResultRow]:
        if not self.path.exists():
            return []
        rows: list[ResultRow] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            rows.append(ResultRow.from_tsv_line(line))
        return rows
