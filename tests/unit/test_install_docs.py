"""The install docs recommend forking first (docs/features/fork-first-install).

README.md and the Pages site put "fork it and run your own copy" ahead of the
release install, drop the contributor path (the project has no contributors),
and keep the fork path free of ``make``, which many machines lack (Windows).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_README = _ROOT / "README.md"

_FORK_HEADING = "## 🍴 **Recommended: fork and make it your own**"
_QUICK_HEADING = "## ⚡ **Quick Installation**"


def _readme_fork_section(text: str) -> str:
    start, end = text.find(_FORK_HEADING), text.find(_QUICK_HEADING)
    assert start != -1, f"README.md lacks {_FORK_HEADING!r}"
    assert end != -1, f"README.md lacks {_QUICK_HEADING!r}"
    return text[start:end]


# doc name -> (path, fork-section extractor, pattern of a make command line)
_INSTALL_DOCS = {
    "README.md": (_README, _readme_fork_section, re.compile(r"(?m)^\s*make\s")),
}

_CONTRIBUTOR_RE = re.compile(r"contributor|pull request|PRs-welcome", re.I)


def test_readme_recommends_fork_first():
    text = _README.read_text(encoding="utf-8")
    fork, quick = text.find(_FORK_HEADING), text.find(_QUICK_HEADING)
    assert fork != -1, f"README.md lacks {_FORK_HEADING!r}"
    assert quick != -1, f"README.md lacks {_QUICK_HEADING!r}"
    assert fork < quick, "README.md: the fork section must come before Quick Installation"


@pytest.mark.parametrize("name", list(_INSTALL_DOCS))
def test_install_doc_has_no_contributor_path(name: str):
    path, _, _ = _INSTALL_DOCS[name]
    hit = _CONTRIBUTOR_RE.search(path.read_text(encoding="utf-8"))
    assert hit is None, f"{name} still has contributor wording: {hit.group(0)!r}"


@pytest.mark.parametrize("name", list(_INSTALL_DOCS))
def test_fork_path_needs_no_make(name: str):
    path, section_of, make_re = _INSTALL_DOCS[name]
    section = section_of(path.read_text(encoding="utf-8"))
    hit = make_re.search(section)
    assert hit is None, f"{name}: the fork path runs make: {hit.group(0).strip()!r}"
