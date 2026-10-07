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
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
_STATUS = re.compile(r"^status:\s*['\"]?([A-Za-z-]+)", re.M)
_OPEN_BOX = re.compile(r"^\s*- \[ \]", re.M)


def _plan_docs() -> list[Path]:
    found: list[Path] = []
    for pattern in _PLAN_GLOBS:
        found.extend(sorted(_REPO.glob(pattern)))
    return found


def _complete_plans() -> list[Path]:
    """Filter at collection so plans still in progress add no skips."""
    complete = []
    for plan in _plan_docs():
        frontmatter = _FRONTMATTER.match(plan.read_text(encoding="utf-8"))
        status = frontmatter and _STATUS.search(frontmatter.group(1))
        if status and status.group(1).lower() == "complete":
            complete.append(plan)
    return complete


@pytest.mark.parametrize(
    "plan",
    _complete_plans(),
    ids=lambda p: str(p.relative_to(_REPO)).replace("\\", "/"),
)
def test_complete_plan_has_no_open_checkbox(plan: Path):
    text = plan.read_text(encoding="utf-8")
    open_boxes = len(_OPEN_BOX.findall(text))
    assert open_boxes == 0, (
        f"{plan.relative_to(_REPO)} is `status: complete` but has {open_boxes} "
        "unchecked task box(es) — check the box the code backs, mark a task "
        "dropped by decision `- [x] ~~task~~` with its reason under "
        "`## Deviations`, or leave status at `implementing`"
    )


def test_plan_doc_glob_finds_something():
    """Guard the globs: a renamed convention must not turn this into a no-op."""
    assert _plan_docs(), "no plan docs matched — update _PLAN_GLOBS"
