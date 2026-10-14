"""Structure of the shipped /sc-author skill and its references.

The references are written for the projects superclaude is installed into,
from Anthropic's published guidance (each file's `sources`), not from this
repository's rules files (docs/features/authoring-skill/05-plan.md D18-D20).
"""

import re
from pathlib import Path

import pytest
import yaml

from superclaude.cli.author_check import check, mask_code

_SRC = Path(__file__).resolve().parents[2] / "src" / "superclaude"
_SKILL = _SRC / "skills" / "sc-author"
_REFS_DIR = _SKILL / "references"
REFS = [
    "skill.md",
    "agent.md",
    "command.md",
    "output-style.md",
    "memory.md",
    "format-xml.md",
    "quality.md",
]
_MODEL_ID = re.compile(r"claude-[a-z0-9]+(?:-[0-9]+)+")


def _frontmatter(path: Path) -> dict:
    match = re.match(r"\A---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    assert match, f"{path.name} has no frontmatter"
    return yaml.safe_load(match.group(1)) or {}


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S
    )
    assert match, f"no `## {heading}` section"
    return match.group(1)


def _prompt_model_ids() -> set[str]:
    """Model IDs /sc-prompt resolves to: where the repository adds a new model."""
    text = (_SRC / "skills" / "sc-prompt" / "SKILL.md").read_text(encoding="utf-8")
    return set(re.findall(r"→ '(claude-[a-z0-9-]+)'", text))


class TestReferences:
    @pytest.mark.parametrize("name", REFS)
    def test_exists_with_sources(self, name):
        sources = _frontmatter(_REFS_DIR / name).get("sources")
        assert sources, f"{name}: no `sources`"
        for source in sources:
            assert str(source["url"]).startswith("https://"), source
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source["retrieved"]))

    def test_model_rows_follow_sc_prompt(self):
        """A model /sc-prompt supports needs its row, read from its guide."""
        text = (_REFS_DIR / "quality.md").read_text(encoding="utf-8")
        rows = set()
        for line in _section(text, "Model differences").splitlines():
            if line.startswith("|"):
                first = line.strip("|").split("|")[0]
                rows.update(_MODEL_ID.findall(first))
        assert rows == _prompt_model_ids(), (
            "/sc-prompt supports a model quality.md has no row for (or the "
            "reverse) — re-read that model's prompting guide, update the row "
            "and its `sources` date"
        )

    @pytest.mark.parametrize("name", REFS)
    def test_example_count(self, name):
        text = mask_code((_REFS_DIR / name).read_text(encoding="utf-8"))
        count = len(re.findall(r"<example[\s>]", text))
        assert count in (0, 3, 4, 5), f"{name}: {count} examples (0 or 3-5)"

    def test_quality_judgment_sections(self):
        text = (_REFS_DIR / "quality.md").read_text(encoding="utf-8")
        for heading in (
            "Load set",
            "Judgment questions",
            "Keep",
            "Harm",
            "Removal evidence",
            "Model differences",
        ):
            assert re.search(rf"^## {heading}\s*$", text, re.M), heading

    @pytest.mark.parametrize("name", REFS)
    def test_passes_the_checker(self, name):
        errors = [
            f.render()
            for f in check(_REFS_DIR / name, type_="generic")
            if f.severity == "error"
        ]
        assert not errors, "\n".join(errors)

    def test_no_superclaude_vocabulary(self):
        """D20: the references carry nothing from this repository's own rules."""
        banned = re.compile(
            r"/sc:|<component|<handoff|<bounds|RULES_|CLAUDE_SC|\bR\d{2}\b"
            r"|src/superclaude|docs/features|\.claude/rules/gotchas",
            re.I,
        )
        hits = []
        # SKILL.md too: the installed skill must not depend on this repository.
        for path in [_SKILL / "SKILL.md", *sorted(_REFS_DIR.iterdir())]:
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                cleaned = re.sub(r"superclaude author-check", "", line, flags=re.I)
                cleaned = re.sub(r"\bsc-author\b", "", cleaned)
                if banned.search(cleaned) or "superclaude" in cleaned.lower():
                    hits.append(f"{path.name}:{number}: {line.strip()}")
        assert not hits, "\n".join(hits)


class TestSkillManifest:
    _PATH = _SKILL / "SKILL.md"
    _STEPS = ("Resolve", "Load-set", "Load", "Draft", "Neighbors", "Check", "Hand-off")

    def _body(self) -> str:
        text = self._PATH.read_text(encoding="utf-8")
        return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)

    def test_frontmatter(self):
        fm = _frontmatter(self._PATH)
        assert fm["name"] == "sc-author"
        assert fm["disable-model-invocation"] is True
        assert fm.get("argument-hint")
        tools = fm["allowed-tools"]
        tools = tools if isinstance(tools, list) else str(tools).split()
        assert "Bash(superclaude author-check *)" in tools
        assert "PowerShell(superclaude author-check *)" in tools
        description = str(fm["description"])
        assert len(description) <= 1536
        assert not re.match(r"\s*(I|You|We)\b", description)

    def test_body_size(self):
        assert len(self._body().strip().splitlines()) <= 150

    def test_steps_in_order(self):
        labels = re.findall(r"^\d+\.\s+\**([A-Z][\w-]*)", self._body(), re.M)
        assert tuple(labels) == self._STEPS

    def test_links_every_reference(self):
        body = self._body()
        for name in [*REFS, "fields.yaml"]:
            assert f"${{CLAUDE_SKILL_DIR}}/references/{name}" in body, name

    def test_check_step_skips_without_the_checker(self):
        body = self._body()
        assert re.search(r"not found, skip this step", body)
        assert "/doctor prompt-audit <path>" in body

    def test_check_step_passes_the_load_set(self):
        assert re.search(r"superclaude author-check [^\n]*--with", self._body())

    def test_passes_the_checker(self):
        findings = check(self._PATH)
        assert not [f.render() for f in findings if f.severity == "error"]
