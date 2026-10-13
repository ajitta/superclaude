"""author-check against real documents: the shipped agents and commands.

These are XML bodies written by hand, and several carry prose such as `<3`
or `<5KB` (agents/project-manager.md, commands/pm.md, commands/index-repo.md),
so a tag pattern that mistakes prose for markup shows up here first.
"""

from pathlib import Path

import pytest

from superclaude.cli.author_check import check

_SRC = Path(__file__).resolve().parents[2] / "src" / "superclaude"
_CORPUS = sorted(
    p
    for sub in ("agents", "commands")
    for p in (_SRC / sub).glob("*.md")
    if p.name != "README.md"
)


def test_corpus_is_not_empty():
    assert len(_CORPUS) > 10


@pytest.mark.parametrize("path", _CORPUS, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_xml_structure_rules_pass(path):
    errors = [
        f.render()
        for f in check(path, fmt="xml")
        if f.code in ("X1", "X2") and f.severity == "error"
    ]
    assert not errors, "\n".join(errors)


# Errors from the pointer and tool rules (N1, N2) that are real breaks in the
# shipped content, as `parent/name:code`. A new break or a fixed one both turn
# this red. Inline-code paths are warnings and stay out of it: they are often
# examples or runtime files.
EXPECTED_N_ERRORS: set[str] = set()


def test_pointer_and_tool_errors_are_the_known_set():
    found = {
        f"{p.parent.name}/{p.name}:{f.code}"
        for p in _CORPUS
        for f in check(p)
        if f.code in ("N1", "N2") and f.severity == "error"
    }
    assert found == EXPECTED_N_ERRORS
