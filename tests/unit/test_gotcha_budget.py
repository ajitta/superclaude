"""Every project gotcha entry stays within the length budget.

`.claude/rules/gotchas/README.md` Limits: one entry (a line starting with
`- name: `) is at most ENTRY_BUDGET characters — name, symptom, action and
SSOT pointer; the story behind it goes to a commit body or docs/. The files are
auto-loaded in full by Claude Code, so a paragraph-long entry costs every
session context for no extra behavior (playbook rule: keep it under a page).
"""

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_GOTCHAS = _REPO / ".claude" / "rules" / "gotchas"
ENTRY_BUDGET = 320
_ENTRY = re.compile(r"^- [a-z0-9][a-z0-9-]*: ", re.M)


def _entries(path: Path) -> list[tuple[str, int]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if _ENTRY.match(line):
            out.append((line.split(":", 1)[0][2:], len(line)))
    return out


@pytest.mark.parametrize("path", sorted(_GOTCHAS.glob("*.md")), ids=lambda p: p.name)
def test_every_gotcha_entry_within_budget(path: Path):
    over = [(name, n) for name, n in _entries(path) if n > ENTRY_BUDGET]
    assert not over, (
        f"{path.name}: {len(over)} entr{'y' if len(over) == 1 else 'ies'} over "
        f"{ENTRY_BUDGET} chars: " + ", ".join(f"{n} ({c})" for n, c in over)
    )


def test_budget_is_stated_in_readme():
    text = (_GOTCHAS / "README.md").read_text(encoding="utf-8")
    assert f"{ENTRY_BUDGET} characters" in text, (
        "gotchas/README.md Limits line must state the same budget as ENTRY_BUDGET"
    )


def test_gotcha_files_found():
    assert (_GOTCHAS / "general.md").exists(), "update _GOTCHAS if the folder moved"
