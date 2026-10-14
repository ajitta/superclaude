"""
Cross-reference integrity linter for SuperClaude content files.

Validates:
- Handoff targets: <handoff next="/sc:X"> → commands/X.md exists
- Agent trigger uniqueness: no duplicate trigger keywords across agents
- Rule citations: every [RNN Name] / RNN in shipped .md → defined in RULES_QUALITY.md
"""

import re
from collections import defaultdict
from pathlib import Path

import pytest

from tests.unit.md_helpers import parse_frontmatter

# Directories
_SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
COMMANDS_DIR = _SRC / "commands"
AGENTS_DIR = _SRC / "agents"
MODES_DIR = _SRC / "modes"
FLAGS_FILE = _SRC / "core" / "FLAGS.md"
RULES_QUALITY_FILE = _SRC / "core" / "rules" / "RULES_QUALITY.md"

# Template patterns that are NOT real handoff targets
HANDOFF_SKIP_PATTERNS = {
    "/sc:[command]",  # Template syntax in help.md
}


def _all_content_files():
    """Collect all .md content files from commands/, agents/, modes/."""
    files = []
    for d in (COMMANDS_DIR, AGENTS_DIR, MODES_DIR):
        if d.exists():
            files.extend(
                f for f in sorted(d.glob("*.md")) if f.stem.upper() != "README"
            )
    return files


def _extract_handoff_targets(content: str) -> list[str]:
    """Extract /sc:X targets from <handoff next="...">."""
    match = re.search(r'<handoff\s+next="([^"]*)"', content)
    if not match:
        return []
    raw = match.group(1)
    return re.findall(r"/sc:([\w-]+)", raw)


# Collect all content files for parametrized tests
ALL_CONTENT_FILES = _all_content_files()
ALL_CONTENT_IDS = [f"{f.parent.name}/{f.stem}" for f in ALL_CONTENT_FILES]

# Available command names (from commands/ filenames)
AVAILABLE_COMMANDS = (
    {f.stem for f in COMMANDS_DIR.glob("*.md") if f.stem.upper() != "README"}
    if COMMANDS_DIR.exists()
    else set()
)


@pytest.fixture(params=ALL_CONTENT_FILES, ids=ALL_CONTENT_IDS)
def content_file(request) -> tuple[str, str]:
    """Yield (id_string, content) for each content file."""
    path: Path = request.param
    content = path.read_text(encoding="utf-8")
    file_id = f"{path.parent.name}/{path.stem}"
    return file_id, content


class TestHandoffIntegrity:
    """<handoff next="/sc:X"> → commands/X.md must exist."""

    def test_handoff_targets_exist(self, content_file):
        file_id, content = content_file
        targets = _extract_handoff_targets(content)
        for target in targets:
            if f"/sc:{target}" in HANDOFF_SKIP_PATTERNS:
                continue
            assert target in AVAILABLE_COMMANDS, (
                f"{file_id}: handoff target '/sc:{target}' not found in commands/ "
                f"(available: {sorted(AVAILABLE_COMMANDS)[:10]}...)"
            )


class TestAgentTriggerUniqueness:
    """Agent trigger keywords should not have exact duplicates."""

    def test_no_duplicate_triggers(self):
        """Each trigger keyword should appear in at most one agent's description."""
        if not AGENTS_DIR.exists():
            pytest.skip("No agents directory")

        trigger_owners = defaultdict(list)
        for agent_file in sorted(AGENTS_DIR.glob("*.md")):
            if agent_file.stem.upper() == "README":
                continue
            content = agent_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            desc = fm.get("description", "")

            # Parse "triggers - keyword1, keyword2" from description
            match = re.search(r"triggers?\s*[-–—]\s*(.+?)(?:\)|$)", desc, re.IGNORECASE)
            if not match:
                continue
            triggers = [
                t.strip().lower() for t in match.group(1).split(",") if t.strip()
            ]
            for trigger in triggers:
                trigger_owners[trigger].append(agent_file.stem)

        duplicates = {
            trigger: owners
            for trigger, owners in trigger_owners.items()
            if len(owners) > 1
        }
        assert not duplicates, "Duplicate trigger keywords found:\n" + "\n".join(
            f"  '{k}': {v}" for k, v in sorted(duplicates.items())
        )


# ─── Rule Citations ──────────────────────────────────────────────

SHIPPED_MD_FILES = sorted(_SRC.rglob("*.md"))
SHIPPED_MD_IDS = [f.relative_to(_SRC).as_posix() for f in SHIPPED_MD_FILES]


def _defined_rules() -> dict[str, str]:
    """Map rule ID → name (e.g. 'R06' → 'Scope') from RULES_QUALITY.md."""
    content = RULES_QUALITY_FILE.read_text(encoding="utf-8")
    return dict(re.findall(r"^\[(R\d{2}) ([^\]]+)\]", content, re.MULTILINE))


DEFINED_RULES = _defined_rules()

# "R06 (Scope)" — a Title Case parenthetical is a rule name; a lowercase one
# ("R03 (pre-fix diagnosis)") is a description and is not compared.
_PAREN_NAME = re.compile(r"\b(R\d{2}) \(((?:[A-Z][\w-]*)(?: [A-Z][\w-]*)*)\)")


def test_rule_definitions_found():
    """Guard against a vacuous pass if the definition format or path changes."""
    assert DEFINED_RULES, (
        "no [RNN Name] definitions extracted from RULES_QUALITY.md — "
        "definition format or file location changed; fix this test's regex/path"
    )


@pytest.mark.parametrize("path", SHIPPED_MD_FILES, ids=SHIPPED_MD_IDS)
def test_rule_citations_defined(path: Path):
    """Every rule citation in shipped content must match a defined rule.

    Full tag: [RNN Name] must equal the definition, so a renamed rule
    (e.g. [R06 Scope] → [R06 Restraint]) fails until citations are re-synced.
    Paren name: RNN (Name) in Title Case must name the defined rule too.
    Bare ID: RNN (as in "apply R18" or "R01–R21") must be a defined ID.
    """
    content = path.read_text(encoding="utf-8")
    full_tags = {f"[{rid} {name}]" for rid, name in DEFINED_RULES.items()}
    bad_tags = set(re.findall(r"\[R\d+ [^\]]*\]", content)) - full_tags
    bad_names = {
        f"{rid} ({name})"
        for rid, name in _PAREN_NAME.findall(content)
        if DEFINED_RULES.get(rid) != name
    }
    bad_ids = set(re.findall(r"\bR\d{2}\b", content)) - DEFINED_RULES.keys()
    assert not bad_tags and not bad_names and not bad_ids, (
        f"{path.relative_to(_SRC).as_posix()}: rule citations not defined in "
        f"RULES_QUALITY.md — tags {sorted(bad_tags)}, "
        f"paren names {sorted(bad_names)}, ids {sorted(bad_ids)}"
    )
