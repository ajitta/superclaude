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
