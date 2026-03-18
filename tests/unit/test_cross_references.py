"""
Cross-reference integrity linter for SuperClaude content files.

Validates:
- Handoff targets: <handoff next="/sc:X"> → commands/X.md exists
- Persona references: <personas p="arch|be"> → FLAGS.md persona_index valid
- MCP server references: <mcp servers="seq|c7"> → MCP_*.md exists
- Agent trigger uniqueness: no duplicate trigger keywords across agents
"""

import re
from collections import defaultdict
from pathlib import Path

import pytest

# Directories
_SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
COMMANDS_DIR = _SRC / "commands"
AGENTS_DIR = _SRC / "agents"
MODES_DIR = _SRC / "modes"
MCP_DIR = _SRC / "mcp"
FLAGS_FILE = _SRC / "core" / "FLAGS.md"

# Static MCP abbreviation → filename mapping
MCP_ABBREV_MAP = {
    "seq": "MCP_Sequential.md",
    "c7": "MCP_Context7.md",
    "play": "MCP_Playwright.md",
    "perf": "MCP_Chrome-DevTools.md",
    "morph": "MCP_Morphllm.md",
    "magic": "MCP_Magic.md",
    "serena": "MCP_Serena.md",
    "tavily": "MCP_Tavily.md",
}

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
                f for f in sorted(d.glob("*.md"))
                if f.stem.upper() != "README"
            )
    return files


def _extract_handoff_targets(content: str) -> list[str]:
    """Extract /sc:X targets from <handoff next="...">."""
    match = re.search(r'<handoff\s+next="([^"]*)"', content)
    if not match:
        return []
    raw = match.group(1)
    return re.findall(r"/sc:([\w-]+)", raw)


def _extract_persona_refs(content: str) -> list[str]:
    """Extract persona abbreviations from <personas p="...">."""
    match = re.search(r'<personas\s+p="([^"]*)"', content)
    if not match:
        return []
    return [p.strip() for p in match.group(1).split("|") if p.strip()]


def _extract_mcp_refs(content: str) -> list[str]:
    """Extract MCP server abbreviations from <mcp servers="...">."""
    match = re.search(r'<mcp\s+servers="([^"]*)"', content)
    if not match:
        return []
    return [s.strip() for s in match.group(1).split("|") if s.strip()]


def _parse_persona_index() -> set[str]:
    """Parse persona abbreviations from FLAGS.md persona_index."""
    if not FLAGS_FILE.exists():
        return set()
    content = FLAGS_FILE.read_text(encoding="utf-8")
    match = re.search(r"<persona_index[^>]*>(.*?)</persona_index>", content, re.DOTALL)
    if not match:
        return set()
    # Format: "arch=system-architect(...) | fe=frontend-architect(...) | ..."
    raw = match.group(1).strip()
    abbreviations = set()
    for entry in raw.split("|"):
        entry = entry.strip()
        if "=" in entry:
            abbrev = entry.split("=")[0].strip()
            if abbrev:
                abbreviations.add(abbrev)
    return abbreviations


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter from markdown text."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


# Collect all content files for parametrized tests
ALL_CONTENT_FILES = _all_content_files()
ALL_CONTENT_IDS = [f"{f.parent.name}/{f.stem}" for f in ALL_CONTENT_FILES]

# Available command names (from commands/ filenames)
AVAILABLE_COMMANDS = {
    f.stem for f in COMMANDS_DIR.glob("*.md")
    if f.stem.upper() != "README"
} if COMMANDS_DIR.exists() else set()

# Persona abbreviations from FLAGS.md
PERSONA_ABBREVIATIONS = _parse_persona_index()


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


class TestPersonaIntegrity:
    """<personas p="arch|be"> → each abbreviation must be in FLAGS.md persona_index."""

    def test_persona_refs_valid(self, content_file):
        file_id, content = content_file
        refs = _extract_persona_refs(content)
        if not refs:
            pytest.skip("No persona references")
        for ref in refs:
            assert ref in PERSONA_ABBREVIATIONS, (
                f"{file_id}: persona '{ref}' not in FLAGS.md persona_index "
                f"(valid: {sorted(PERSONA_ABBREVIATIONS)})"
            )


class TestMcpServerIntegrity:
    """<mcp servers="seq|c7"> → abbreviation valid and mapped file exists."""

    def test_mcp_abbreviations_valid(self, content_file):
        file_id, content = content_file
        refs = _extract_mcp_refs(content)
        if not refs:
            pytest.skip("No MCP server references")
        for ref in refs:
            assert ref in MCP_ABBREV_MAP, (
                f"{file_id}: MCP abbreviation '{ref}' not in MCP_ABBREV_MAP "
                f"(valid: {sorted(MCP_ABBREV_MAP.keys())})"
            )

    def test_mcp_mapped_files_exist(self, content_file):
        file_id, content = content_file
        refs = _extract_mcp_refs(content)
        if not refs:
            pytest.skip("No MCP server references")
        for ref in refs:
            if ref not in MCP_ABBREV_MAP:
                continue  # Caught by abbreviation test
            expected_file = MCP_DIR / MCP_ABBREV_MAP[ref]
            assert expected_file.exists(), (
                f"{file_id}: MCP '{ref}' maps to {MCP_ABBREV_MAP[ref]} "
                f"but file not found at {expected_file}"
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
            triggers = [t.strip().lower() for t in match.group(1).split(",") if t.strip()]
            for trigger in triggers:
                trigger_owners[trigger].append(agent_file.stem)

        duplicates = {
            trigger: owners
            for trigger, owners in trigger_owners.items()
            if len(owners) > 1
        }
        assert not duplicates, (
            f"Duplicate trigger keywords found:\n"
            + "\n".join(f"  '{k}': {v}" for k, v in sorted(duplicates.items()))
        )
