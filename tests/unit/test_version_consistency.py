"""Version + doc-baseline drift lint (I6 / audit P8).

A single source of truth for the package version (``pyproject.toml``) and a
deterministic guard that the version + test-baseline strings echoed in other
files do not silently drift out of sync. Addresses the audit finding that four
sources reported four different version strings (the orphan ``__version__.py``
held ``0.4.0`` while ``pyproject`` shipped ``4.6.0+ajitta``).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_PYPROJECT = _ROOT / "pyproject.toml"
_README = _ROOT / "README.md"
_CLAUDE_MD = _ROOT / "CLAUDE.md"


def _pyproject_version() -> str:
    text = _PYPROJECT.read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    assert m, "pyproject.toml has no [project] version line"
    return m.group(1)


def _first_passing_baseline(text: str) -> str | None:
    """Extract the first 'N passing' test-baseline number, digits only."""
    m = re.search(r"([\d,]+)\s+passing", text)
    return m.group(1).replace(",", "") if m else None


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


def test_readme_version_matches_pyproject():
    """The version advertised in README must match the canonical pyproject version."""
    version = _pyproject_version()
    readme = _README.read_text(encoding="utf-8")
    assert version in readme, (
        f"README.md does not mention the current version {version!r} "
        "(badge / 'Current Stable Version' drifted)"
    )


def test_readme_baseline_matches_claude_md():
    """README and CLAUDE.md must cite the same test-pass baseline."""
    readme_baseline = _first_passing_baseline(_README.read_text(encoding="utf-8"))
    claude_baseline = _first_passing_baseline(_CLAUDE_MD.read_text(encoding="utf-8"))
    if readme_baseline is None or claude_baseline is None:
        pytest.skip("a 'N passing' baseline is not stated in both docs")
    assert readme_baseline == claude_baseline, (
        f"test baseline drift: README says {readme_baseline}, "
        f"CLAUDE.md says {claude_baseline}"
    )
