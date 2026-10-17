"""Structure of the shipped /sc-prompt skill and its references.

/sc-prompt was a command whose body carried the per-model mirror, the request
configuration and the evidence behind its removal rows: 30 KB loaded on every
run, of which one model's column was used. The body now keeps the procedure and
the detector; each model's mirror and the evidence are references read on
demand.
"""

import re
from pathlib import Path

from superclaude.cli.author_check import check
from tests.unit.md_helpers import load_frontmatter, markdown_body

_SKILL = (
    Path(__file__).resolve().parents[2] / "src" / "superclaude" / "skills" / "sc-prompt"
)
_PATH = _SKILL / "SKILL.md"
_REFS_DIR = _SKILL / "references"
_STEPS = ("Capture", "Resolve", "Diagnose", "Apply", "Rewrite", "Report", "Emit")
_MIRRORS = ("opus.md", "fable-5-1.md", "sonnet-5-5.md")


def _model_ids() -> set[str]:
    return set(re.findall(r"→ '(claude-[a-z0-9-]+)'", markdown_body(_PATH)))


def test_frontmatter():
    fm = load_frontmatter(_PATH)
    assert fm["name"] == "sc-prompt"
    assert "disable-model-invocation" not in fm, (
        "the skill writes nothing without --out; it stays model-invocable"
    )
    assert fm.get("argument-hint")
    description = str(fm["description"])
    assert len(description) <= 1536
    assert not re.match(r"\s*(I|You|We)\b", description)
    assert "Not for" in description


def test_steps_in_order():
    labels = re.findall(r"^\d+\.\s+\*\*([A-Z][\w-]*)", markdown_body(_PATH), re.M)
    assert tuple(labels) == _STEPS


def test_body_stays_procedure():
    """Reference data moved back into the body is the defect this split fixed."""
    assert len(markdown_body(_PATH).encode("utf-8")) <= 16_000


def test_links_every_reference_and_nothing_missing():
    body = markdown_body(_PATH)
    linked = set(re.findall(r"\$\{CLAUDE_SKILL_DIR\}/references/([\w.-]+)", body))
    shipped = {p.name for p in _REFS_DIR.iterdir() if p.is_file()}
    assert linked == shipped


def test_references_list_their_sources():
    for path in _REFS_DIR.glob("*.md"):
        sources = load_frontmatter(path).get("sources")
        assert sources, f"{path.name}: no `sources`"
        for source in sources:
            assert str(source.get("url", "")).startswith("https://") or (
                source.get("file") and source.get("section")
            ), (path.name, source)
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source["retrieved"]))


def test_every_resolved_model_has_one_mirror_file():
    covered: dict[str, list[str]] = {}
    for name in _MIRRORS:
        title = next(
            line
            for line in (_REFS_DIR / name).read_text(encoding="utf-8").splitlines()
            if line.startswith("# ")
        )
        for model in re.findall(r"'(claude-[a-z0-9-]+)'", title):
            covered.setdefault(model, []).append(name)
    assert set(covered) == _model_ids()
    assert all(len(files) == 1 for files in covered.values()), covered


def test_passes_the_checker():
    findings = check(_PATH)
    assert not [f.render() for f in findings if f.severity == "error"]
