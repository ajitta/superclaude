"""`make release` notes come from the CHANGELOG entry of the released version.

The recipe used to take the first `## [` section. Once bumps started keeping an
empty `## [Unreleased]` heading above the new version, that section was empty
and v4.29.2 and v4.29.3 shipped GitHub releases with blank notes; nothing failed.
These tests run the recipe's own awk program, so a regression turns them red.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"

_AWK_RE = re.compile(
    r"""awk -v v="\$\$V" '([^']+)' CHANGELOG\.md > \.release-notes\.md"""
)

needs_awk = pytest.mark.skipif(shutil.which("awk") is None, reason="needs awk")


def _release_recipe() -> str:
    text = MAKEFILE.read_text(encoding="utf-8")
    return text.split("\nrelease:", 1)[1].split("\n\n", 1)[0]


def _program() -> str:
    match = _AWK_RE.search(_release_recipe())
    assert match, 'release recipe no longer extracts notes with `awk -v v="$$V"`'
    return match.group(1).replace("$$", "$")  # make escaping → shell text


def _notes(changelog: str, version: str, tmp_path: Path) -> str:
    path = tmp_path / "CHANGELOG.md"
    path.write_text(changelog, encoding="utf-8")
    return subprocess.run(
        ["awk", "-v", f"v={version}", _program(), str(path)],
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout


CHANGELOG = (
    "# Changelog\n\n## [Unreleased]\n\n"
    "## [1.2.0] - 2026-10-19\n\n### Fixed\n\n- second\n\n"
    "## [1.1.0] - 2026-10-18\n\n### Added\n\n- first\n"
)


@needs_awk
def test_notes_skip_an_empty_unreleased_heading(tmp_path):
    assert _notes(CHANGELOG, "1.2.0", tmp_path).strip() == "### Fixed\n\n- second"


@needs_awk
def test_notes_stop_at_the_next_version(tmp_path):
    assert _notes(CHANGELOG, "1.1.0", tmp_path).strip() == "### Added\n\n- first"


@needs_awk
def test_notes_for_a_missing_version_are_empty(tmp_path):
    assert _notes(CHANGELOG, "1.3.0", tmp_path).strip() == ""
    # a prefix of a real version is not that version
    assert _notes(CHANGELOG, "1.2", tmp_path).strip() == ""


@needs_awk
def test_current_version_has_notes(tmp_path):
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version = re.search(r'^version = "(.*)"', pyproject, re.M).group(
        1
    )  # = recipe's sed
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert _notes(changelog, version, tmp_path).strip(), (
        f"CHANGELOG.md has no non-empty entry for {version}"
    )


def _recipe_lines(*needles: str) -> str:
    """The recipe lines containing each needle, unescaped for sh, in order."""
    lines = []
    for line in _release_recipe().splitlines():
        if any(n in line for n in needles):
            lines.append(line.strip().removesuffix("\\").strip().replace("$$", "$"))
    assert len(lines) == len(needles), lines
    return "\n".join(lines)


needs_sh = pytest.mark.skipif(
    shutil.which("sh") is None or shutil.which("awk") is None, reason="needs sh, awk"
)


@needs_sh
@pytest.mark.parametrize(
    ("version", "ok"), [("1.2.0", True), ("1.3.0", False), ("", False)]
)
def test_empty_notes_stop_the_release(tmp_path, version, ok):
    """Runs the recipe's extract + guard lines: an empty entry exits non-zero
    and leaves no notes file behind."""
    (tmp_path / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    script = f"V='{version}'\n" + _recipe_lines(
        "> .release-notes.md", "grep -q '[^[:space:]]' .release-notes.md"
    )
    proc = subprocess.run(
        ["sh", "-c", script], cwd=tmp_path, capture_output=True, encoding="utf-8"
    )
    assert (proc.returncode == 0) is ok, proc.stdout + proc.stderr
    assert (tmp_path / ".release-notes.md").exists() is ok


def test_guard_runs_before_gh_and_the_stable_push():
    recipe = _release_recipe()
    guard = recipe.find("grep -q '[^[:space:]]' .release-notes.md")
    assert guard != -1, "release must refuse empty notes"
    assert guard < recipe.find("gh release create")
    assert guard < recipe.find("refs/heads/stable")


_GH_REPO_RE = re.compile(
    r"^export GH_REPO := \$\(shell git remote get-url origin 2>/dev/null \| sed -E '([^']+)'\)$",
    re.M,
)


@pytest.mark.skipif(shutil.which("sed") is None, reason="needs sed")
@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/o/r.git",
        "https://github.com/o/r",
        "git@github.com:o/r.git",
        "git@github.com:o/r",
        "ssh://git@github.com/o/r.git",
    ],
)
def test_gh_repo_is_owner_slash_name_of_origin(url):
    """A fork clone's gh default can be the upstream; `ci` and `release` would
    then dispatch runs and create the release there. GH_REPO pins them to origin."""
    match = _GH_REPO_RE.search(MAKEFILE.read_text(encoding="utf-8"))
    assert match, "Makefile no longer derives GH_REPO from origin"
    expr = match.group(1).replace("$$", "$")
    out = subprocess.run(
        ["sed", "-E", expr], input=url + "\n", capture_output=True, encoding="utf-8"
    ).stdout.strip()
    assert out == "o/r"
