"""The install docs offer three paths in order (docs/features/fork-first-install).

README.md and the Pages site list Quick install (the release as-is), then Clone
install (your own copy from a local clone), then Fork install (that copy in your
GitHub fork, the recommended one). They drop the contributor path (the project
has no contributors) and keep the clone and fork paths free of ``make``, which
many machines lack (Windows).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_README = _ROOT / "README.md"
_PAGES = _ROOT / "docs" / "index.html"

# Install paths in their required order, as each doc marks their start.
_README_PATHS = (
    "## ⚡ **Quick Installation**",
    "## 📥 **Clone install**",
    "## 🍴 **Fork install (recommended)**",
)
_PAGES_PATHS = (
    '<section id="install"',
    '<section id="develop"',
    '<section id="fork"',
)
_PAGES_NAV = ('href="#install"', 'href="#develop"', 'href="#fork"')


def _positions(text: str, markers: tuple, doc: str) -> list:
    found = [text.find(m) for m in markers]
    missing = [m for m, i in zip(markers, found) if i == -1]
    assert not missing, f"{doc} lacks {missing}"
    return found


def _readme_custom_paths(text: str) -> str:
    """Clone install through the end of Fork install."""
    start = _positions(text, _README_PATHS, "README.md")[1]
    end = text.find("\n## ", text.find(_README_PATHS[2]) + 1)
    return text[start:] if end == -1 else text[start:end]


def _pages_custom_paths(text: str) -> str:
    """The #develop (clone) and #fork sections."""
    start = _positions(text, _PAGES_PATHS, "docs/index.html")[1]
    end = text.find("<section", text.find(_PAGES_PATHS[2]) + 1)
    return text[start:] if end == -1 else text[start:end]


# doc name -> (path, clone+fork extractor, pattern of a make command line)
_INSTALL_DOCS = {
    "README.md": (_README, _readme_custom_paths, re.compile(r"(?m)^\s*make\s")),
    "docs/index.html": (_PAGES, _pages_custom_paths, re.compile(r"<code>make\s")),
}

_CONTRIBUTOR_RE = re.compile(r"contributor|pull request|PRs-welcome", re.I)


def test_readme_orders_quick_clone_fork():
    text = _README.read_text(encoding="utf-8")
    found = _positions(text, _README_PATHS, "README.md")
    assert found == sorted(found), "README.md: order must be Quick, Clone, Fork install"


def test_pages_orders_quick_clone_fork():
    text = _PAGES.read_text(encoding="utf-8")
    found = _positions(text, _PAGES_PATHS, "docs/index.html")
    assert found == sorted(found), (
        "docs/index.html: sections must be install, develop, fork"
    )
    nav = text[text.find("<nav") : text.find("</nav>")]
    links = _positions(nav, _PAGES_NAV, "the docs/index.html nav")
    assert links == sorted(links), "docs/index.html: nav must list Install, Clone, Fork"


@pytest.mark.parametrize("name", list(_INSTALL_DOCS))
def test_install_doc_has_no_contributor_path(name: str):
    path, _, _ = _INSTALL_DOCS[name]
    hit = _CONTRIBUTOR_RE.search(path.read_text(encoding="utf-8"))
    assert hit is None, f"{name} still has contributor wording: {hit.group(0)!r}"


@pytest.mark.parametrize("name", list(_INSTALL_DOCS))
def test_clone_and_fork_paths_need_no_make(name: str):
    path, section_of, make_re = _INSTALL_DOCS[name]
    section = section_of(path.read_text(encoding="utf-8"))
    hit = make_re.search(section)
    assert hit is None, (
        f"{name}: the clone/fork path runs make: {hit.group(0).strip()!r}"
    )
