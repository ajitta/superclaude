"""Upgrade scenarios built from captured legacy installs (install/upgrade audit).

Each ``tests/fixtures/legacy_installs/<era>.json`` records what a real old
installer left on disk, captured once from a sandbox run of that release
(docs/features/install-upgrade-audit/02-scenarios.md). Content the installer
reads — agents, SKILL.md, settings, CLAUDE files, exclude files — is kept as
exact text in ``_blobs.json``; everything else is a sha256 the builder writes as
a stub. Machine paths are tokens: ``$HOME``, ``$PROJECT``, ``$PYTHON``,
``$UVCACHE``. No network, no git history: the fixtures are the history.

Only behaviour the current code already gets right is asserted here. The
defects the audit found get their red tests with their fixes
(docs/features/install-upgrade-audit/03-findings.md).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

from superclaude.cli.install_components import install_all
from superclaude.cli.install_paths import shipped_names
from tests.conftest import init_git_repo

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
LEGACY = FIXTURES / "legacy_installs"
BLOBS = json.loads((LEGACY / "_blobs.json").read_text(encoding="utf-8"))
ERAS = sorted(p.stem for p in LEGACY.glob("*.json") if not p.name.startswith("_"))


def load_era(era: str) -> dict:
    return json.loads((LEGACY / f"{era}.json").read_text(encoding="utf-8"))


def build_legacy_install(
    tmp_path: Path, era: str, monkeypatch
) -> tuple[Path, Path, Path]:
    """Lay out ``era``'s captured install under ``tmp_path``; return (home, project, base).

    HOME and CLAUDE_PROJECT_DIR point into ``tmp_path`` (gotcha test-anchor-env)
    and the project is a real git repository, because the exclude block and the
    agent-memory guard both ask git.
    """
    doc = load_era(era)
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    init_git_repo(project, commit=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    monkeypatch.chdir(project)
    tokens = {
        "$PYTHON": sys.executable,
        "$UVCACHE": str(tmp_path / "uvcache"),
        "$PROJECT": str(project),
        "$HOME": str(home),
    }

    def resolve(text: str) -> str:
        for token, value in tokens.items():
            text = text.replace(token, value)
        return text

    for key, entry in doc["files"].items():
        root, rel = key.split("/", 1)
        target = (home if root == "$HOME" else project) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if "blob" in entry:
            target.write_text(
                resolve(BLOBS[entry["blob"]]), encoding="utf-8", newline=""
            )
        else:
            target.write_text(f"stub {entry['sha256']}\n", encoding="utf-8")
    for key in doc["empty_dirs"]:
        root, rel = key.split("/", 1)
        ((home if root == "$HOME" else project) / rel).mkdir(
            parents=True, exist_ok=True
        )
    base = home / ".claude" if doc["scope"] == "user" else project / ".claude"
    return home, project, base


def _commands(settings_file: Path) -> list[str]:
    data = json.loads(settings_file.read_text(encoding="utf-8"))
    return [
        hook["command"]
        for array in data.get("hooks", {}).values()
        for entry in array
        for hook in entry.get("hooks", [])
    ]


# --- the fixtures themselves ------------------------------------------------

_EMAIL = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)


def _strings(value) -> list[str]:
    """Every string in a parsed JSON document, keys included."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for k, v in value.items() for s in [k, *_strings(v)]]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


@pytest.mark.parametrize(
    "path",
    sorted(LEGACY.glob("*.json")) + [FIXTURES / "shipped_names_history.json"],
    ids=lambda p: p.name,
)
def test_fixture_carries_no_machine_data(path: Path) -> None:
    """A captured install names no real home, uv cache entry or email address.

    Decoded strings, not the raw file: a JSON-escaped newline before a
    decorator (`\\n@pytest.mark`) would read as an address.
    """
    text = "\n".join(_strings(json.loads(path.read_text(encoding="utf-8"))))
    assert "/home/" not in text
    assert "/Users/" not in text
    assert "archive-v0" not in text
    assert _EMAIL.findall(text) == []


@pytest.mark.parametrize("era", ERAS)
def test_every_era_builds(tmp_path: Path, monkeypatch, era: str) -> None:
    """Every blob a fixture cites exists, and the built tree is an install."""
    doc = load_era(era)
    missing = [
        k for k, v in doc["files"].items() if "blob" in v and v["blob"] not in BLOBS
    ]
    assert missing == []
    _home, _project, base = build_legacy_install(tmp_path, era, monkeypatch)
    assert (base / "commands" / "sc").is_dir()


def test_shipped_names_history_lists_every_current_name() -> None:
    """The retirement guard's input knows everything this release ships."""
    history = json.loads(
        (FIXTURES / "shipped_names_history.json").read_text(encoding="utf-8")
    )
    for kind in ("agents", "output-styles", "skills"):
        recorded = {row["name"] for row in history["names"][kind] if row["shipped_now"]}
        assert recorded == shipped_names(kind), kind


# --- upgrade behaviour the current code gets right --------------------------


def test_committed_project_upgrade_drops_machine_paths(
    tmp_path: Path, monkeypatch
) -> None:
    """U5: a teammate's non-force install leaves no interpreter or home path in
    the committed settings.json (install_settings._migrate_legacy_commands)."""
    home, project, base = build_legacy_install(
        tmp_path, "19575ac4p-project", monkeypatch
    )
    assert any(sys.executable in c for c in _commands(base / "settings.json"))

    success, message = install_all(base_path=base, force=False, scope="project")

    assert success, message
    text = (base / "settings.json").read_text(encoding="utf-8")
    assert sys.executable not in text
    assert str(project) not in text and str(home) not in text
    assert "superclaude/scripts" not in text


def test_python_bin_era_commands_rewritten_once(tmp_path: Path, monkeypatch) -> None:
    """U6: the {{PYTHON_BIN}} + $CLAUDE_PROJECT_DIR commands become console
    commands, and no shipped hook is registered twice."""
    _home, _project, base = build_legacy_install(
        tmp_path, "77b5821c-project", monkeypatch
    )

    success, message = install_all(base_path=base, force=False, scope="project")

    assert success, message
    commands = _commands(base / "settings.json")
    assert not [c for c in commands if "superclaude/scripts" in c]
    console = [c for c in commands if c.startswith("superclaude hook ")]
    shipped = json.loads(
        (
            Path(__file__).resolve().parents[2] / "src/superclaude/hooks/hooks.json"
        ).read_text(encoding="utf-8")
    )
    expected = sorted(
        hook["command"]
        for array in shipped["hooks"].values()
        for entry in array
        for hook in entry["hooks"]
    )
    assert sorted(console) == expected


def test_gitignore_era_block_moves_to_exclude(tmp_path: Path, monkeypatch) -> None:
    """U7: the local-scope block leaves .gitignore for .git/info/exclude and the
    user's own .gitignore lines stay byte-identical."""
    _home, project, base = build_legacy_install(
        tmp_path, "b85651c0p-local", monkeypatch
    )
    gitignore = project / ".gitignore"
    original = gitignore.read_text(encoding="utf-8")
    assert "# >>> superclaude" in original
    gitignore.write_text("node_modules/\n" + original, encoding="utf-8")

    success, message = install_all(base_path=base, force=False, scope="local")

    assert success, message
    after = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    assert "superclaude" not in after
    assert after == "node_modules/\n"
    exclude = (project / ".git" / "info" / "exclude").read_text(encoding="utf-8")
    assert "# >>> superclaude >>>" in exclude
