"""Version + doc-count drift lint (I6 / audit P8).

A single source of truth for the package version (``pyproject.toml``) and a
deterministic guard that the version strings and content counts echoed in other
files do not silently drift out of sync. Addresses the audit finding that four
sources reported four different version strings (the orphan ``__version__.py``
held ``0.4.0`` while ``pyproject`` shipped ``4.6.0+ajitta``).

The test-pass-count baseline that used to be linted here was deleted
2026-08-30: it compared the three doc copies to each other and never to the
suite, so all three could be stale together and stay green, while every commit
that added a test had to edit all three. See
``test_docs_do_not_hardcode_a_pass_count``.

Two shapes of guard live here, and the difference is the whole lesson:

* **presence** -- ``assert value in doc`` or a regex pinned to one phrasing.
  It proves *one* copy is current and says nothing about its siblings. README
  stated the command count in several shapes while a presence lint watched a
  single one, so the rest rode along green.
* **absence / total** -- assert *every* occurrence of a shape matches the
  source, and assert the shape is still there to match. A pattern that has
  stopped matching is watching nothing, which is how a presence lint fails;
  ``required`` below is what keeps this form from decaying into that one.
  Pin a derived value to the function that counts the tree, never to another
  doc copy.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_PYPROJECT = _ROOT / "pyproject.toml"
_README = _ROOT / "README.md"
_CLAUDE_MD = _ROOT / "CLAUDE.md"
_AGENTS_MD = _ROOT / "AGENTS.md"
_COMMANDS_DIR = _ROOT / "src" / "superclaude" / "commands"
_SC_DISPATCHER = _COMMANDS_DIR / "sc.md"
_HELP = _COMMANDS_DIR / "help.md"

# Docs an agent auto-loads; none of them may restate the suite's pass count.
_AGENT_DOCS = (_README, _CLAUDE_MD, _AGENTS_MD)
_PASS_COUNT_RE = re.compile(r"\d[\d,]*\s+(?:passing|passed)")

_COMPONENTS_DIR = _ROOT / "src" / "superclaude"
_RULES_DIR = _ROOT / ".claude" / "rules"

# A sentence whose truth value expires on its own -- a dated claim about the
# present, or a promise to re-check later. Frozen evidence for a durable rule
# ("Measured 2026-07-25: ...", "commit S390 measured ...", "needs Opus 4.7+")
# is deliberately not matched: the test is expiry, not the presence of a date.
_EXPIRING_PRESENT_RE = re.compile(
    r"(?i)\bas of \d{4}-\d{2}-\d{2}"
    r"|\b(?:re-)?verify quarterly\b"
    r"|\blast reviewed\b"
    r"|^#+ Current .*\(\d+\)$",
    re.MULTILINE,
)


def _command_file_count() -> int:
    """Number of shipped /sc command files (commands/*.md minus the README)."""
    return sum(1 for p in _COMMANDS_DIR.glob("*.md") if p.name != "README.md")


def _component_counts() -> dict[str, int]:
    """Count each content type from the source tree -- the only authority."""

    def _md(sub: str, pattern: str = "*.md") -> int:
        d = _COMPONENTS_DIR / sub
        return sum(1 for f in d.glob(pattern) if f.name != "README.md")

    skills = _COMPONENTS_DIR / "skills"
    return {
        "commands": _md("commands"),
        "agents": _md("agents"),
        "modes": _md("modes", "MODE_*.md"),
        "mcp": _md("mcp", "MCP_*.md"),
        "skills": sum(
            1 for d in skills.iterdir() if d.is_dir() and not d.name.startswith("_")
        ),
    }


def _no_expiry_docs() -> list[Path]:
    """Docs whose sentences must not expire on their own.

    Not all of these are always-loaded -- ``.claude/rules/*.md`` load on their
    ``paths:`` globs and ``core/rules/*.md`` are injected by context_loader on
    matching triggers. What they share is that an agent is routed to them and
    reads them as current fact, so a self-expiring sentence misleads.

    ``gotchas/`` is excluded on purpose: it is the sanctioned home for dated
    observations and has its own eviction (``# Last reviewed:`` plus the
    /sc:reflect 90-day check). Sorted and de-duplicated so parametrize ids are
    stable and unique.
    """
    docs = [_README, _CLAUDE_MD, _AGENTS_MD]
    docs += [p for p in _RULES_DIR.rglob("*.md") if "gotchas" not in p.parts]
    docs += list((_COMPONENTS_DIR / "core").rglob("*.md"))
    docs += list(_COMPONENTS_DIR.glob("*/README.md"))
    return sorted(set(docs))


def _commands_block_entry_count(text: str) -> int | None:
    """Count ``- name:`` entries inside a component's <commands> block."""
    m = re.search(r"<commands>(.*?)</commands>", text, re.DOTALL)
    if not m:
        return None
    return len(re.findall(r"(?m)^\s*-\s+[\w-]+:", m.group(1)))


def _pyproject_version() -> str:
    text = _PYPROJECT.read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    assert m, "pyproject.toml has no [project] version line"
    return m.group(1)


def test_pyproject_is_the_single_version_source():
    """The runtime package version must equal the pyproject canonical version."""
    import superclaude

    assert superclaude.__version__ == _pyproject_version()


def test_orphan_version_module_removed():
    """The stale ``__version__.py`` (held 0.4.0) must not be reintroduced."""
    orphan = _ROOT / "src" / "superclaude" / "__version__.py"
    assert not orphan.exists(), (
        "src/superclaude/__version__.py is an orphan version source — delete it; "
        "the canonical version lives in pyproject.toml / __init__.py"
    )


@pytest.mark.parametrize("path", _AGENT_DOCS, ids=lambda p: p.name)
def test_docs_do_not_hardcode_a_pass_count(path):
    """No doc may restate the suite's pass count.

    Deleted 2026-08-30. The count lived in three docs, so every commit that
    added a test had to edit all three, and the lint that guarded it compared
    the copies to each other rather than to the suite -- all three could be
    stale together and stay green. The load-bearing invariant is "pytest exits
    0", which CI asserts directly.
    """
    hit = _PASS_COUNT_RE.search(path.read_text(encoding="utf-8"))
    assert hit is None, (
        f"{path.name} hardcodes a test pass count ({hit.group(0)!r}) -- remove it. "
        "The suite's exit code is the signal; a number in prose only goes stale."
    )


def test_readme_version_matches_pyproject():
    """The version advertised in README must match the canonical pyproject version."""
    version = _pyproject_version()
    readme = _README.read_text(encoding="utf-8")
    assert version in readme, (
        f"README.md does not mention the current version {version!r} "
        "(badge / 'Current Stable Version' drifted)"
    )


def test_sc_dispatcher_version_matches_pyproject():
    """The /sc:sc dispatcher <meta> version must match the canonical pyproject version."""
    version = _pyproject_version()
    text = _SC_DISPATCHER.read_text(encoding="utf-8")
    assert version in text, (
        f"commands/sc.md <meta> version drifted — does not mention {version!r}"
    )


# Every shape in which README states a component count: (counter key, pattern,
# required). The pattern is deliberately broad -- narrow phrasing is how the
# presence-form predecessor failed, and how a first draft of this test failed
# too: pinning `(\d+) slash commands` let a reword to "12 commands" pass green
# with the wrong number. `required` asserts the shape is still present, so a
# pattern that has stopped matching fails loudly instead of watching nothing.
_README_COUNT_PATTERNS = [
    ("commands", re.compile(r"(\d+)\s+(?:slash\s+)?commands\b", re.I), True),
    ("commands", re.compile(r"\|\s*Slash commands \((\d+)\)"), True),
    ("agents", re.compile(r"(\d+)\s+agents\b", re.I), False),
    ("agents", re.compile(r"\|\s*Agents \((\d+)\)"), True),
    ("modes", re.compile(r"(\d+)\s+(?:adaptive\s+)?modes\b", re.I), True),
    ("modes", re.compile(r"\|\s*Modes \((\d+)\)"), True),
    ("mcp", re.compile(r"(\d+)\s+(?:curated\s+)?(?:MCP\s+)?servers\b", re.I), False),
    ("mcp", re.compile(r"\|\s*MCP servers \((\d+)\)"), True),
    ("skills", re.compile(r"(\d+)\s+(?:procedural\s+)?skills\b", re.I), True),
    ("skills", re.compile(r"\|\s*Skills \((\d+)\)"), True),
]

# The headline badge table: label row, separator row, bold-number row, adjacent.
# Line-bounded on purpose -- an unbounded gap let the label row pair with an
# unrelated five-number row elsewhere in the file and validate the wrong table.
_BADGE_TABLE_RE = re.compile(
    r"\|\s*Commands\s*\|\s*Agents\s*\|\s*Modes\s*\|\s*MCP Servers\s*\|\s*Skills\s*\|[^\n]*\n"
    r"\|[^\n]*\n"
    r"\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*"
    r"\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|"
)


@pytest.mark.parametrize(
    ("key", "pattern", "required"),
    _README_COUNT_PATTERNS,
    ids=[f"{k}-{i}" for i, (k, _, _) in enumerate(_README_COUNT_PATTERNS)],
)
def test_every_readme_component_count_matches_source(key, pattern, required):
    """Every stated component count must equal the source-tree count.

    Pinned to the tree, never to another doc copy: copies go stale together and
    stay green (see this module's docstring).
    """
    expected = _component_counts()[key]
    found = [int(m) for m in pattern.findall(_README.read_text(encoding="utf-8"))]
    if required:
        assert found, (
            f"README no longer states {key} in the shape {pattern.pattern!r}, so "
            "this lint is watching nothing. Re-anchor the pattern to the new "
            "wording, or drop its row from _README_COUNT_PATTERNS deliberately."
        )
    wrong = [n for n in found if n != expected]
    assert not wrong, (
        f"README states {key} = {wrong} but the tree has {expected}. "
        f"Recount with the source, not with another doc."
    )


def test_readme_badge_table_matches_source():
    """The headline badge table's five numbers must equal the source counts."""
    m = _BADGE_TABLE_RE.search(_README.read_text(encoding="utf-8"))
    assert m, "README.md has no Commands/Agents/Modes/MCP Servers/Skills badge table"
    counts = _component_counts()
    stated = dict(
        zip(("commands", "agents", "modes", "mcp", "skills"), map(int, m.groups()))
    )
    assert stated == counts, f"README badge table says {stated}, tree has {counts}"


def test_readme_lists_every_command_and_no_phantoms():
    """The README command roster must be exactly the set of command files.

    A hand-maintained inventory drifts in both directions: `/sc:workflow` was
    listed for months after its file was renamed to `/sc:roadmap`, and four
    shipped commands were never added.
    """
    text = _README.read_text(encoding="utf-8")
    start = text.find("## \U0001f4cb **All Commands**")
    assert start != -1, "README.md has no 'All Commands' section to lint"
    end = text.find("**Source files:**", start)
    listed = set(
        re.findall(r"`/sc:([a-z-]+)`", text[start : end if end != -1 else None])
    )
    actual = {f.stem for f in _COMMANDS_DIR.glob("*.md") if f.name != "README.md"}
    assert listed == actual, (
        f"README command roster drifted -- missing: {sorted(actual - listed)}; "
        f"listed but not shipped: {sorted(listed - actual)}"
    )


@pytest.mark.parametrize(
    "path", _no_expiry_docs(), ids=lambda p: str(p.relative_to(_ROOT))
)
def test_routed_docs_carry_no_expiring_claim(path):
    """A doc an agent is routed to may not state a claim whose truth expires.

    Admissible: invariants, plus frozen evidence for them -- a past-tense
    measurement, a version floor, a citation. A date is fine; an expiring truth
    value is not. Route the rest: task state to TodoWrite, progress to the
    commit body or docs/features/<slug>/, a dated observation to
    .claude/rules/gotchas/<domain>.md (the one surface with eviction), a
    derived count to the command or test that computes it.
    """
    hit = _EXPIRING_PRESENT_RE.search(path.read_text(encoding="utf-8"))
    assert hit is None, (
        f"{path.relative_to(_ROOT)} states an expiring claim ({hit.group(0)!r}). "
        "Name the routine event that falsifies it; if nothing here notices that "
        "event, it is not an invariant -- route it out of this file."
    )


@pytest.mark.parametrize("path", [_SC_DISPATCHER, _HELP], ids=["sc", "help"])
def test_dispatcher_lists_every_command(path):
    """The /sc:sc and /sc:help <commands> blocks must list every command file."""
    n = _command_file_count()
    count = _commands_block_entry_count(path.read_text(encoding="utf-8"))
    assert count is not None, f"{path.name} has no <commands> block"
    assert count == n, (
        f"{path.name} <commands> lists {count} entries but {n} command files exist"
    )
