"""
Structural validation tests for command markdown files.

Validates frontmatter fields, XML structure, and cross-field consistency
for all command definitions in src/superclaude/commands/.
"""

import re
from pathlib import Path

import pytest
import yaml

COMMANDS_DIR = Path(__file__).parent.parent.parent / "src" / "superclaude" / "commands"

# Agent/skill-only fields that should never appear in command frontmatter
_SCHEMAS_PATH = (
    Path(__file__).parent.parent.parent / ".claude" / "rules" / "schemas.yaml"
)
_SCHEMAS = yaml.safe_load(_SCHEMAS_PATH.read_text(encoding="utf-8"))
FORBIDDEN_FIELDS = set(_SCHEMAS["forbidden_command_fields"])

# All command .md files (excluding README and __init__.py)
COMMAND_FILES = sorted(
    [f for f in COMMANDS_DIR.glob("*.md") if f.name not in ("README.md", "__init__.py")]
)
COMMAND_IDS = [f.stem for f in COMMAND_FILES]

# Command descriptions are model-facing: /sc:* commands are exposed to the model,
# which decides whether to invoke them. Every description encodes an invocation
# contract — a positive cue (references its own /sc:<name>) and a negative gate
# ("Do NOT auto-trigger on …" / "NOT auto-fire on …") that stops the model
# over-firing the command on adjacent phrasing. Hallucination-priming vocab is
# deliberately NOT checked for commands: that failure mode is agent-persona-
# specific (107-trial study); commands are user-invoked workflows, not personas.
NEGATIVE_TRIGGER_GATE = re.compile(r"auto-?(trigger|fire)", re.IGNORECASE)

# A command doc that tells the model to run a superclaude script with a bare
# `python`/`python3` prescribes an invocation that only resolves by luck of
# PATH: ~/.claude/superclaude/ ships content, not the package, so the script's
# `superclaude.*` imports fail under any interpreter but one holding the
# package. Console subcommands (`superclaude insight`, `superclaude hook`,
# `superclaude auto-improve`) are the only invocations that always carry a
# resolving interpreter — the hooks themselves run `superclaude hook <name>`.
# `{{SCRIPTS_PATH}}` was the install-time template that releases before the
# console entry resolved to ~/.claude/superclaude/scripts/ — i.e. exactly the
# broken invocation — and a doc still spelling it is still caught. The `uv run`
# prefix is the one legitimate bare-module form (dev checkout) and is exempt.
_BARE_PYTHON_PRESCRIPTION = re.compile(
    r"(?<!uv run )python3?\s+"
    r"(?:-m\s+superclaude\b|[^\s`]*(?:superclaude|\{\{SCRIPTS_PATH\}\})[^\s`]*\.py)"
)
# Gotcha lines quote the broken form on purpose; they carry this identifier.
_BARE_PYTHON_EXEMPT = "never-bare-python"


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


def extract_xml_attr(text: str, tag: str, attr: str) -> str | None:
    """Extract an attribute value from the first occurrence of an XML tag."""
    pattern = rf"<{tag}\b[^>]*\b{attr}=[\"']([^\"']*)[\"']"
    match = re.search(pattern, text)
    return match.group(1) if match else None


def extract_xml_content(text: str, tag: str) -> str | None:
    """Extract text content from the first occurrence of an XML tag."""
    pattern = rf"<{tag}\b[^>]*>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None


@pytest.fixture(params=COMMAND_FILES, ids=COMMAND_IDS)
def command(request) -> tuple[str, str, dict[str, str]]:
    """Yield (stem, content, frontmatter) for each command file."""
    path: Path = request.param
    content = path.read_text()
    fm = parse_frontmatter(content)
    return path.stem, content, fm


class TestCommandFrontmatter:
    """Validate YAML frontmatter in every command file."""

    def test_has_frontmatter(self, command):
        stem, content, fm = command
        assert fm, f"{stem}: missing YAML frontmatter (--- block)"

    def test_has_description(self, command):
        stem, content, fm = command
        assert "description" in fm, f"{stem}: frontmatter missing 'description'"
        assert len(fm["description"]) > 10, f"{stem}: description too short"

    def test_no_forbidden_fields(self, command):
        """Commands should not contain agent/skill-only fields."""
        stem, content, fm = command
        found = set(fm.keys()) & FORBIDDEN_FIELDS
        assert not found, f"{stem}: frontmatter contains forbidden field(s): {found}"


class TestCommandInvocationContract:
    """Command descriptions are a model-facing invocation contract.

    /sc:* commands are exposed to the model, which decides whether to invoke
    them; every description references its own slash command (positive cue) and
    carries a 'Do NOT auto-trigger' negative gate (prevents over-firing). These
    deterministic lints guard that contract — the command-shaped counterpart to
    the agent description-interface lint (test_agent_structure.py). See
    docs/research/agent-native-design-ajitta-2026-05-31.md (P1-B extension).
    """

    def test_description_references_own_slash_command(self, command):
        stem, content, fm = command
        desc = fm.get("description", "")
        assert f"/sc:{stem}" in desc, (
            f"{stem}: description does not reference its own '/sc:{stem}' "
            f"invocation. The model reads the description to route slash commands; "
            f"the positive cue must name the command."
        )

    def test_description_has_negative_trigger_gate(self, command):
        stem, content, fm = command
        desc = fm.get("description", "")
        assert NEGATIVE_TRIGGER_GATE.search(desc), (
            f"{stem}: description has no 'Do NOT auto-trigger …' negative gate. "
            f"Without it the model may over-invoke this command on adjacent "
            f"phrasing instead of waiting for explicit /sc:{stem}."
        )


class TestDescriptionDoesNotOutrunTheBody:
    """A description must not claim what the body gates.

    Two shapes got through the existing lints, which are lexical only. `git.md`
    said invoking it "approves history-rewriting ops" while `<approval_required>`
    listed those same three operations as needing approval — one reading of that
    sentence is that typing the command *is* the approval. And
    `troubleshoot.md` said it "writes a failing test and applies the fix"
    unconditionally, while the fix is behind `--fix` and `<bounds><never>` says
    risky fixes need confirm.

    The description is read by the model as the routing contract, so a claim it
    makes there outranks a qualification the body makes later.
    """

    APPROVAL_VERBS = re.compile(r"\bapprove[sd]?\b|\bauthoriz\w*\b|\bgrants?\b")

    def test_no_approval_claim_when_the_body_requires_approval(self, command):
        stem, content, fm = command
        if "<approval_required>" not in content:
            return
        desc = fm.get("description", "")
        match = self.APPROVAL_VERBS.search(desc)
        assert match is None, (
            f"{stem}: description says {match.group(0)!r} while the body lists "
            f"operations under <approval_required>. Invoking a command cannot be "
            f"the approval for the operations it gates — say what the command "
            f"does and leave approval to the body."
        )

    def test_an_opt_in_mutation_is_named_with_its_flag(self, command):
        """A `--fix`-style flag is opt-in; the description must say so."""
        stem, content, fm = command
        if "--fix" not in content:
            return
        desc = fm.get("description", "")
        claims_fix = re.search(r"applies the fix|applies fixes|apply the fix", desc)
        if not claims_fix:
            return
        assert "--fix" in desc, (
            f"{stem}: description claims it applies the fix, but the fix is behind "
            f"the opt-in --fix flag. Name the flag or drop the claim."
        )


class TestCommandXMLStructure:
    """Validate XML component structure in every command file."""

    def test_has_component_open(self, command):
        stem, content, _ = command
        assert "<component" in content, f"{stem}: missing <component> tag"

    def test_has_component_close(self, command):
        stem, content, _ = command
        assert "</component>" in content, f"{stem}: missing </component>"

    def test_component_name_matches(self, command):
        stem, content, _ = command
        name = extract_xml_attr(content, "component", "name")
        assert name == stem, f"{stem}: component name='{name}' != filename '{stem}'"

    def test_component_type_is_command(self, command):
        stem, content, _ = command
        ctype = extract_xml_attr(content, "component", "type")
        assert ctype == "command", (
            f"{stem}: component type='{ctype}', expected 'command'"
        )

    def test_has_role(self, command):
        stem, content, _ = command
        assert re.search(r"<role[\s>]", content), (
            f"{stem}: missing <role> section (accepts <role> or <role command=...>)"
        )

    def test_has_mission(self, command):
        stem, content, _ = command
        mission = extract_xml_content(content, "mission")
        assert mission, f"{stem}: missing or empty <mission>"


class TestCommandCrossFieldConsistency:
    """Validate that frontmatter and XML body are consistent."""

    def test_mission_matches_description(self, command):
        """Mission text should share 30%+ significant words with description."""
        stem, content, fm = command
        mission = extract_xml_content(content, "mission") or ""
        desc = fm.get("description", "")
        stopwords = {"with", "that", "this", "from", "through", "about", "into"}
        mission_words = {
            w.lower() for w in re.findall(r"[a-zA-Z]{4,}", mission)
        } - stopwords
        desc_lower = desc.lower()
        matches = [w for w in mission_words if w in desc_lower]
        threshold = max(1, len(mission_words) * 0.3)
        assert len(matches) >= threshold, (
            f"{stem}: description shares only {len(matches)}/{len(mission_words)} "
            f"words with mission (need {threshold:.0f}). "
            f"Missing: {mission_words - set(matches)}"
        )

    def test_has_bounds(self, command):
        """<bounds> must use sub-tag form: <does>, <never>, optional <fallback>.

        Per .claude/rules/command-authoring.md and xml-prose-format.md.
        Legacy attribute, body-labeled, and hedging-labeled (<should>/<avoid>)
        forms are rejected (commit S390 + hedging-drop rule, measured
        Opus 4.7-era, retained under later flagships).
        """
        stem, content, _ = command
        assert "<bounds>" in content, (
            f"{stem}: missing <bounds> opening tag (sub-tag form)"
        )
        body = extract_xml_content(content, "bounds")
        assert body, f"{stem}: <bounds> body is empty"
        assert re.search(r"<does>.+?</does>", body, re.DOTALL), (
            f"{stem}: <bounds> missing <does> sub-tag"
        )
        assert re.search(r"<never>.+?</never>", body, re.DOTALL), (
            f"{stem}: <bounds> missing <never> sub-tag"
        )
        assert not re.search(r"<bounds\s+\w+\s*=", content), (
            f"{stem}: <bounds> uses legacy attribute form — convert to sub-tag form"
        )
        assert not re.search(
            r"^\s*-\s+(Should|Avoid|Does|Never|Fallback):\s+", body, re.MULTILINE
        ), f"{stem}: <bounds> uses legacy body-labeled form — convert to sub-tag form"
        assert not re.search(r"<should>|<avoid>", content), (
            f"{stem}: <bounds> uses legacy <should>/<avoid> sub-tags — rename to <does>/<never>"
        )

    def test_has_handoff(self, command):
        stem, content, _ = command
        assert "<handoff " in content, f"{stem}: missing <handoff> tag"


class TestCommandMinimumContent:
    """Validate that command files have sufficient content."""

    def test_minimum_length(self, command):
        stem, content, _ = command
        assert len(content) > 300, (
            f"{stem}: command file too short ({len(content)} chars)"
        )

    def test_no_empty_sections(self, command):
        """Check for empty major sections."""
        stem, content, _ = command
        empty_patterns = [
            r"<role[^>]*>\s*</role>",
            r"<flow>\s*</flow>",
        ]
        for pattern in empty_patterns:
            assert not re.search(pattern, content), (
                f"{stem}: empty section found matching {pattern}"
            )


class TestCommandDocsPrescribeConsoleEntry:
    """No command doc may prescribe a bare-python invocation of a SC script.

    The install tree ships content, not the package, so
    `python3 ~/.claude/superclaude/scripts/X.py` and
    `python -m superclaude.scripts.X` raise ModuleNotFoundError for any
    interpreter not holding the package. Hooks dodge this by running
    `superclaude hook <name>` — the console script — and a console subcommand
    is likewise the only invocation a command doc may hand the model. Lines
    carrying the `never-bare-python` identifier are exempt: those gotchas quote
    the broken form deliberately.
    """

    def test_no_bare_python_prescription(self, command):
        stem, content, _ = command
        prescriptions = [
            line
            for line in content.splitlines()
            if _BARE_PYTHON_PRESCRIPTION.search(line)
            and _BARE_PYTHON_EXEMPT not in line
        ]
        assert prescriptions == [], (
            f"{stem}: prescribes bare python for a superclaude script; "
            f"use the console subcommand instead: {prescriptions}"
        )


# A guard nobody probes is a guard nobody knows is inverted: the sweep above
# passes just as happily on a regex that matches nothing. These pin what the
# pattern must catch and what it must leave alone.
@pytest.mark.parametrize(
    ("line", "is_prescription"),
    [
        ("3. Spawn worker: `python -m superclaude.scripts.auto_improve [args]`", True),
        ("run `python3 ~/.claude/superclaude/scripts/insight_writer.py review`", True),
        ("run `python3 {{SCRIPTS_PATH}}/insight_writer.py --review`", True),
        ("`uv run python -m superclaude.scripts.parallel_ab spec.yaml`", False),
        ("/sc:auto-improve . --eval-cmd 'python eval.py' --metric pass_rate", False),
        ("3. Spawn worker: `superclaude auto-improve [args]`", False),
    ],
    ids=[
        "bare-module",
        "resolved-install-path",
        "scripts-path-template",
        "uv-run-dev-form",
        "users-own-eval-cmd",
        "console-subcommand",
    ],
)
def test_bare_python_pattern_discriminates(line, is_prescription):
    assert bool(_BARE_PYTHON_PRESCRIPTION.search(line)) is is_prescription
