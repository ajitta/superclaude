"""A plan doc marked complete must have no open task checkbox.

RULES_DOCS `<doc_output_convention>`: `status: complete` only when every task
checkbox is checked; departures go under `## Deviations`. The /sc:implement
Integrate step writes both. Nothing else looks at the boxes, so a skipped step
used to fail silently (gotchas/general.md `plan-checklist-vs-status`).
"""

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_PLAN_GLOBS = ("docs/features/*/*plan*.md", "docs/plans/*.md")
_STATUS = re.compile(r"^status:\s*(\S+)", re.M)
_OPEN_BOX = re.compile(r"^\s*- \[ \]", re.M)


def _plan_docs() -> list[Path]:
    found: list[Path] = []
    for pattern in _PLAN_GLOBS:
        found.extend(sorted(_REPO.glob(pattern)))
    return found


@pytest.mark.parametrize(
    "plan", _plan_docs(), ids=lambda p: str(p.relative_to(_REPO)).replace("\\", "/")
)
def test_complete_plan_has_no_open_checkbox(plan: Path):
    text = plan.read_text(encoding="utf-8")
    status = _STATUS.search(text)
    if not status or status.group(1) != "complete":
        pytest.skip("not a completed plan")
    open_boxes = len(_OPEN_BOX.findall(text))
    assert open_boxes == 0, (
        f"{plan.relative_to(_REPO)} is `status: complete` but has {open_boxes} "
        "unchecked task box(es) — check the box the code backs, or record the "
        "departure under `## Deviations` and leave status at `implementing`"
    )


def test_plan_doc_glob_finds_something():
    """Guard the globs: a renamed convention must not turn this into a no-op."""
    assert _plan_docs(), "no plan docs matched — update _PLAN_GLOBS"
