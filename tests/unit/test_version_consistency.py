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


def _command_file_count() -> int:
    """Number of shipped /sc command files (commands/*.md minus the README)."""
    return sum(1 for p in _COMMANDS_DIR.glob("*.md") if p.name != "README.md")


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


def test_readme_command_count_matches_files():
    """README 'List all N commands' must equal the actual command-file count."""
    n = _command_file_count()
    m = re.search(r"List all (\d+) commands", _README.read_text(encoding="utf-8"))
    assert m, "README.md has no 'List all N commands' line to lint"
    assert int(m.group(1)) == n, (
        f"README claims {m.group(1)} commands but {n} command files exist"
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
