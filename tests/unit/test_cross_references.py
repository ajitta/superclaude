"""
Cross-reference integrity linter for superclaude content files.

Validates:
- Handoff targets: <handoff next="/sc:X"> → commands/X.md exists
- Retired agents: no shipped .md names an agent install_paths retires
- Rule citations: every [RNN Name] / RNN in shipped .md → defined in RULES_QUALITY.md
"""

import re
from pathlib import Path

import pytest

# Directories
_SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
COMMANDS_DIR = _SRC / "commands"
AGENTS_DIR = _SRC / "agents"
MODES_DIR = _SRC / "modes"
FLAGS_FILE = _SRC / "core" / "FLAGS.md"
RULES_QUALITY_FILE = _SRC / "core" / "rules" / "RULES_QUALITY.md"
RULES_KERNEL_FILE = _SRC / "core" / "RULES.md"

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


class TestRetiredAgentNames:
    """No shipped markdown names a retired agent.

    A retired name in a command or agent body points the model at an agent the
    install no longer has (docs/features/agent-roster-audit, finding 9). The
    names come from install_paths.RETIRED_AGENT_FILES, so retiring an agent
    extends this check without editing it. Description overlap between the
    agents that remain is checked by test_description_overlap.py.
    """

    # (path under src/superclaude, name) pairs where the word is not the agent.
    ALLOWED = {("modes/MODE_DeepResearch.md", "deep-research")}

    def test_shipped_markdown_names_no_retired_agent(self):
        from superclaude.cli.install_paths import RETIRED_AGENT_FILES

        stems = [name.removesuffix(".md") for name in RETIRED_AGENT_FILES]
        hits = []
        for path in sorted(_SRC.rglob("*.md")):
            rel = path.relative_to(_SRC).as_posix()
            text = path.read_text(encoding="utf-8")
            for stem in stems:
                if (rel, stem) in self.ALLOWED:
                    continue
                if re.search(rf"(?<![\w-]){re.escape(stem)}(?![\w-])", text):
                    hits.append(f"{rel}: {stem}")
        assert not hits, "retired agent named in shipped content:\n" + "\n".join(hits)


# ─── Rule Citations ──────────────────────────────────────────────

_REPO = _SRC.parent.parent
# Shipped content plus the repo's own authoring rules and gotchas.
CITING_MD_FILES = sorted(_SRC.rglob("*.md")) + sorted(
    (_REPO / ".claude" / "rules").rglob("*.md")
)
CITING_MD_IDS = [f.relative_to(_REPO).as_posix() for f in CITING_MD_FILES]


def _defined_rules() -> dict[str, str]:
    """Map rule ID → name (e.g. 'R06' → 'Scope') from RULES_QUALITY.md."""
    content = RULES_QUALITY_FILE.read_text(encoding="utf-8")
    return dict(re.findall(r"^\[(R\d{2}) ([^\]]+)\]", content, re.MULTILINE))


DEFINED_RULES = _defined_rules()

_FULL_TAG = re.compile(r"\[R\d+ [^\]]*\]")
_RANGE = re.compile(r"\b(R\d{2})[–-](R\d{2})\b")
_BARE_ID = re.compile(r"\bR\d{2}\b")

# Bare IDs allowed outside the definition file: the text that holds them.
_BARE_ID_ALLOWED = {
    # The insights.jsonl `rule` field stores the bare ID ("R18").
    "src/superclaude/commands/insight.md": ["rule (R13, R18...)"],
    # The gotcha is about grepping the bare ID itself.
    ".claude/rules/gotchas/general.md": [r"(e.g., \bR18\b)"],
    # A section anchor in a research doc, not a rule citation.
    ".claude/rules/gotchas/authoring.md": ["§ P-R21"],
}


def test_rule_definitions_found():
    """Guard against a vacuous pass if the definition format or path changes."""
    assert DEFINED_RULES, (
        "no [RNN Name] definitions extracted from RULES_QUALITY.md — "
        "definition format or file location changed; fix this test's regex/path"
    )


def test_quality_kernel_pointers_resolve():
    """RULES_QUALITY.md lines that defer to the kernel ("kernel `<scope_discipline>`")
    must name a section that exists in core/RULES.md; a renamed kernel section
    would otherwise leave those rules pointing at nothing."""
    pointers = set(
        re.findall(r"kernel `<(\w+)>`", RULES_QUALITY_FILE.read_text(encoding="utf-8"))
    )
    assert pointers, "no kernel `<section>` pointers found in RULES_QUALITY.md"
    kernel_tags = set(
        re.findall(r"<(\w+)[\s>]", RULES_KERNEL_FILE.read_text(encoding="utf-8"))
    )
    assert pointers <= kernel_tags, (
        f"RULES_QUALITY.md points to kernel sections missing from core/RULES.md: "
        f"{sorted(pointers - kernel_tags)}"
    )


@pytest.mark.parametrize("path", CITING_MD_FILES, ids=CITING_MD_IDS)
def test_rule_citations_defined(path: Path):
    """Rules are cited as [RNN Name], matching the definition in RULES_QUALITY.md.

    A renamed rule (e.g. [R06 Scope] → [R06 Restraint]) fails until citations
    are re-synced. A bare RNN is allowed only inside RULES_QUALITY.md (names
    on the same page), in a range (R01–R21), or in _BARE_ID_ALLOWED — and
    there it must still be a defined ID.
    """
    rel = path.relative_to(_REPO).as_posix()
    content = path.read_text(encoding="utf-8")
    full_tags = {f"[{rid} {name}]" for rid, name in DEFINED_RULES.items()}
    bad_tags = set(_FULL_TAG.findall(content)) - full_tags

    rest = _FULL_TAG.sub("", content)
    listed_ids = {rid for pair in _RANGE.findall(rest) for rid in pair}
    rest = _RANGE.sub("", rest)
    allowed = _BARE_ID_ALLOWED.get(rel, [])
    stale = [text for text in allowed if text not in content]
    assert not stale, f"{rel}: _BARE_ID_ALLOWED entries no longer in the file: {stale}"
    for text in allowed:
        listed_ids |= set(_BARE_ID.findall(text))
        rest = rest.replace(text, "")
    bare = set(_BARE_ID.findall(rest))
    in_definition_file = path == RULES_QUALITY_FILE

    undefined = (listed_ids | bare) - DEFINED_RULES.keys()
    bare_outside = set() if in_definition_file else bare
    assert not bad_tags and not undefined and not bare_outside, (
        f"{rel}: rule citations must be [RNN Name] matching RULES_QUALITY.md — "
        f"mismatched tags {sorted(bad_tags)}, undefined ids {sorted(undefined)}, "
        f"bare ids {sorted(bare_outside)}"
    )
