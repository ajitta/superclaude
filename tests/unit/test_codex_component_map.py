"""Component-inventory drift lint for the codex improvement guides.

``docs/codex/prompting_session_raw/02_component_and_delivery_map.md`` §1 is the
single place the guide set records how many of each component ship in
``src/superclaude/``. The guides were written once and then drifted: nine commits
changed ``src/`` before anyone recounted, and the MCP row still said 6 after the
Sequential doc was removed.

The existing doc lint (``test_version_consistency.py``) compares documents to each
other, so a stale number passes as long as every copy is stale. This one counts the
source tree directly, which is the only comparison that catches that failure.

Scope note: only the stable inventory is pinned here. Volatile measurements (test
counts, coverage, description char totals) live in
``08_current_findings_and_backlog.md`` with their re-measurement commands, and are
deliberately not gated — a check that fails on every commit gets ignored.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from superclaude.cli.install_paths import COMPONENTS

_ROOT = Path(__file__).resolve().parents[2]
_PKG = _ROOT / "src" / "superclaude"
_MAP_DOC = (
    _ROOT
    / "docs"
    / "codex"
    / "prompting_session_raw"
    / "02_component_and_delivery_map.md"
)


def _component_dir(component: str) -> Path:
    """Source directory for a component, per the installer's own mapping."""
    return _PKG / COMPONENTS[component][0]


def _count_md(directory: Path, pattern: str = "*.md") -> int:
    """Markdown files matching pattern, minus the directory README."""
    return sum(1 for p in directory.glob(pattern) if p.name != "README.md")


def _always_loaded_core() -> int:
    """Core files imported by CLAUDE_SC.md — the always-loaded kernel."""
    text = (_PKG / "CLAUDE_SC.md").read_text(encoding="utf-8")
    return len(re.findall(r"^@core/\S+\.md\s*$", text, flags=re.MULTILINE))


def _hook_entry_scripts() -> tuple[int, int]:
    """(distinct scripts, total registrations) referenced by hooks.json."""
    raw = (_PKG / "hooks" / "hooks.json").read_text(encoding="utf-8")
    refs = re.findall(r"([A-Za-z0-9_]+\.py)", json.dumps(json.loads(raw)))
    return len(set(refs)), len(refs)


def _actual_counts() -> dict[str, int]:
    distinct_hooks, _ = _hook_entry_scripts()
    return {
        "agents/*.md": _count_md(_component_dir("agents")),
        "commands/*.md": _count_md(_component_dir("commands")),
        "core always-loaded": _always_loaded_core(),
        "core/rules/*.md": _count_md(_component_dir("core") / "rules"),
        "modes/MODE_*.md": _count_md(_component_dir("modes"), "MODE_*.md"),
        "modes/*CONFIG*.md": _count_md(_component_dir("modes"), "*CONFIG*.md"),
        "mcp/MCP_*.md": _count_md(_component_dir("mcp"), "MCP_*.md"),
        "skills/*/SKILL.md": len(list(_component_dir("skills").glob("*/SKILL.md"))),
        "templates/docs-scaffold/*": len(
            [
                p
                for p in (_component_dir("templates") / "docs-scaffold").iterdir()
                if p.is_file()
            ]
        ),
        "distinct hook entry scripts": distinct_hooks,
        "전체 Python module": len(list(_PKG.rglob("*.py"))),
    }


# Doc row label -> key in _actual_counts(). The doc is Korean prose; matching on
# the backticked path keeps the mapping readable when a row is reworded.
_ROW_KEYS = {
    "`agents/*.md`": "agents/*.md",
    "`commands/*.md`": "commands/*.md",
    "`core` always-loaded": "core always-loaded",
    "`core/rules/*.md`": "core/rules/*.md",
    "`modes/MODE_*.md`": "modes/MODE_*.md",
    "`modes/*CONFIG*.md`": "modes/*CONFIG*.md",
    "`mcp/MCP_*.md`": "mcp/MCP_*.md",
    "`skills/*/SKILL.md`": "skills/*/SKILL.md",
    "`templates/docs-scaffold/*`": "templates/docs-scaffold/*",
    "distinct hook entry scripts": "distinct hook entry scripts",
    "전체 Python module": "전체 Python module",
}


def _documented_counts() -> dict[str, int]:
    """Parse the §1 snapshot table into {key: count}."""
    text = _MAP_DOC.read_text(encoding="utf-8")
    found: dict[str, int] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = _ROW_KEYS.get(cells[0])
        if key is None or not cells[1].isdigit():
            continue
        found[key] = int(cells[1])
    return found


def test_snapshot_table_covers_every_row():
    """Every row this test knows how to count must be present in the doc."""
    documented = _documented_counts()
    missing = set(_ROW_KEYS.values()) - set(documented)
    assert not missing, (
        f"02 §1 snapshot table lost rows: {sorted(missing)}. "
        "Either restore the row or drop it from _ROW_KEYS."
    )


@pytest.mark.parametrize("key", sorted(_ROW_KEYS.values()))
def test_documented_count_matches_source(key):
    """The documented inventory must equal what the source tree actually holds."""
    documented = _documented_counts()[key]
    actual = _actual_counts()[key]
    assert documented == actual, (
        f"02 §1 says {key} = {documented}, source has {actual}. "
        f"Recount and update {_MAP_DOC.relative_to(_ROOT)} §1."
    )


def test_hook_registration_note_matches_hooks_json():
    """The §1 role cell claims N hooks.json registrations; hold it to that."""
    _, registrations = _hook_entry_scripts()
    text = _MAP_DOC.read_text(encoding="utf-8")
    match = re.search(r"`hooks\.json`의 (\d+)개 등록", text)
    assert match, "02 §1 no longer states the hooks.json registration count"
    assert int(match.group(1)) == registrations, (
        f"02 §1 says {match.group(1)} hooks.json registrations, "
        f"hooks.json has {registrations}"
    )
