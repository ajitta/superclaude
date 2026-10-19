"""Upgrade scenarios built from captured legacy installs (install/upgrade audit).

Each ``tests/fixtures/legacy_installs/<era>.json`` records what a real old
installer left on disk, captured once from a sandbox run of that release
(docs/features/install-upgrade-audit/02-scenarios.md). Content the installer
reads — agents, SKILL.md and every file of a retired skill, settings, CLAUDE
files, exclude files — is kept as exact text in ``_blobs.json``; everything
else is a sha256 the builder writes as a stub. Machine paths are tokens:
``$HOME``, ``$PROJECT``, ``$PYTHON``, ``$UVCACHE``. No network, no git history:
the fixtures are the history.

The defects the audit found are pinned here by ID, each test written red
before its fix (docs/features/install-upgrade-audit/03-findings.md).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path, PurePath, PureWindowsPath
from typing import NamedTuple

import pytest
from click.testing import CliRunner

from superclaude.cli import install_mcp
from superclaude.cli.doctor import run_doctor
from superclaude.cli.install_components import install_all
from superclaude.cli.install_git_exclude import add_git_exclude, remove_git_exclude
from superclaude.cli.install_inventory import uninstall_all
from superclaude.cli.install_paths import shipped_names
from superclaude.cli.install_settings import CLAUDE_SC_IMPORT, remove_claude_md_import
from superclaude.cli.main import main
from superclaude.utils import settings_filename
from tests.conftest import init_git_repo
from tests.unit.cli_helpers import all_output

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
LEGACY = FIXTURES / "legacy_installs"
BLOBS = json.loads((LEGACY / "_blobs.json").read_text(encoding="utf-8"))
ERAS = sorted(p.stem for p in LEGACY.glob("*.json") if not p.name.startswith("_"))


def load_era(era: str) -> dict:
    return json.loads((LEGACY / f"{era}.json").read_text(encoding="utf-8"))


def sandbox(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    """An empty home and a git project under ``tmp_path``; return (home, project).

    HOME and CLAUDE_PROJECT_DIR point into ``tmp_path`` (gotcha test-anchor-env)
    and the project is a real git repository, because the exclude block and the
    agent-memory guard both ask git.
    """
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    init_git_repo(project, commit=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    monkeypatch.chdir(project)
    return home, project


def scope_base(home: Path, project: Path, scope: str) -> Path:
    return home / ".claude" if scope == "user" else project / ".claude"


TOKEN_NAMES = ("HOME", "PROJECT", "PYTHON", "UVCACHE")


class WindowsEraPath(PureWindowsPath):
    """A Windows path for code that only reads the path, on any platform.

    ``str`` is the backslash form and ``as_posix`` the forward-slash form, as
    on Windows, where the two differ; on Linux they are the same string, so a
    test that must tell them apart (which form a fixture or the product writes
    or undoes) builds its path from this class. ``resolve``, which a pure path
    lacks, is the identity: the path stands for an absolute one.
    """

    def resolve(self, strict: bool = False) -> WindowsEraPath:
        return self


def _era_path(path: PurePath) -> str:
    """``path`` as the captured eras wrote a resolved placeholder: forward slashes."""
    return path.as_posix()


def fixture_tokens(tmp_path: Path, home: Path, project: Path) -> dict[str, str]:
    """The machine paths of one sandbox, in the form the captured eras wrote.

    The captured eras (66b37a7e, b933fd65 and later) resolved `{{SKILLS_PATH}}`
    and `{{SCRIPTS_PATH}}` in SKILL.md with ``.resolve().as_posix()`` (757e3649
    → b806c61c) and the hook commands' `{{SCRIPTS_PATH}}` and `{{PYTHON_BIN}}`
    with ``.replace("\\", "/")``: forward slashes on every platform. Only the
    eight unreleased commits cd2f8aab → e1b2fbe7 wrote ``str(...resolve())``
    (backslashes on Windows), which `_placeholder_forms` undoes too; no
    captured era is from them. Replacing `$HOME` with ``str(home)`` gave
    Windows `C:\\...\\home/.claude/skills/...`, a mixed form no installer wrote
    and the placeholder undo does not know, so confidence-check and
    simplicity-coach survived there (run 39208943288).
    """
    return {
        "PYTHON": _era_path(Path(sys.executable)),
        "UVCACHE": _era_path(tmp_path / "uvcache"),
        "PROJECT": _era_path(project.resolve()),
        "HOME": _era_path(home.resolve()),
    }


def resolve_tokens(text: str, tokens: dict[str, str], *, as_json: bool = False) -> str:
    """``text`` with each ``$TOKEN`` replaced by its machine path.

    A JSON file carries machine paths as JSON strings, so the value is
    JSON-escaped there; with the forward-slash forms of ``fixture_tokens`` that
    changes nothing, and a value holding a quote or backslash stays valid JSON.
    """
    for token in TOKEN_NAMES:
        value = tokens[token]
        text = text.replace(f"${token}", json.dumps(value)[1:-1] if as_json else value)
    return text


def build_legacy_install(
    tmp_path: Path, era: str, monkeypatch
) -> tuple[Path, Path, Path]:
    """Lay out ``era``'s captured install under ``tmp_path``; return (home, project, base)."""
    doc = load_era(era)
    home, project = sandbox(tmp_path, monkeypatch)
    tokens = fixture_tokens(tmp_path, home, project)

    for key, entry in doc["files"].items():
        root, rel = key.split("/", 1)
        target = (home if root == "$HOME" else project) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if "blob" in entry:
            target.write_text(
                resolve_tokens(
                    BLOBS[entry["blob"]], tokens, as_json=rel.endswith(".json")
                ),
                encoding="utf-8",
                newline="",
            )
        else:
            target.write_text(f"stub {entry['sha256']}\n", encoding="utf-8")
    for key in doc["empty_dirs"]:
        root, rel = key.split("/", 1)
        ((home if root == "$HOME" else project) / rel).mkdir(
            parents=True, exist_ok=True
        )
    return home, project, scope_base(home, project, doc["scope"])


def fresh_install(tmp_path: Path, monkeypatch, scope: str) -> tuple[Path, Path, Path]:
    """This release installed at ``scope`` in a fresh sandbox; return (home, project, base)."""
    home, project = sandbox(tmp_path, monkeypatch)
    base = scope_base(home, project, scope)
    success, message = install_all(base_path=base, force=False, scope=scope)
    assert success, message
    return home, project, base


def snapshot(root: Path) -> dict[str, bytes | None]:
    """Every file (its bytes) and directory (None) under ``root``.

    Git's own internals are left out, except ``info/exclude``, which install
    and uninstall edit.
    """
    tree: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        parts = path.relative_to(root).parts
        if ".git" in parts and parts[-2:] != ("info", "exclude"):
            continue
        tree["/".join(parts)] = path.read_bytes() if path.is_file() else None
    return tree


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


def test_fixture_tokens_are_forward_slash_paths(tmp_path: Path) -> None:
    """Windows run 39208943288: `$HOME/.claude/skills/...` became
    `C:\\...\\home/.claude/skills/...`, so no placeholder undo matched and
    confidence-check and simplicity-coach survived every removal. The captured
    eras wrote forward slashes everywhere (as_posix, `.replace("\\", "/")`).
    A ``WindowsEraPath`` home shows ``str(home)`` as backslashes on Linux
    too."""
    assert _era_path(PureWindowsPath(r"C:\a\home")) == "C:/a/home"
    windows_home = WindowsEraPath(r"C:\Users\me\home")
    assert "\\" in str(windows_home)
    assert (
        fixture_tokens(tmp_path, windows_home, tmp_path / "project")["HOME"]
        == "C:/Users/me/home"
    )

    tokens = fixture_tokens(tmp_path, tmp_path / "home", tmp_path / "project")

    assert set(tokens) == set(TOKEN_NAMES)
    for value in tokens.values():
        assert "\\" not in value, value
    assert tokens["HOME"] == (tmp_path / "home").resolve().as_posix()
    assert (
        resolve_tokens("$HOME/.claude/skills/x", tokens)
        == tokens["HOME"] + "/.claude/skills/x"
    )
    assert (
        resolve_tokens('"$HOME"', {**tokens, "HOME": 'C:/a"b'}, as_json=True)
        == '"C:/a\\"b"'
    )


@pytest.mark.parametrize("era", ["66b37a7ep-user", "b933fd65p-user"])
@pytest.mark.parametrize("skill", ["confidence-check", "simplicity-coach"])
def test_fixture_skill_md_passes_the_gate_in_its_windows_form(
    era: str, skill: str
) -> None:
    """The fixture's SKILL.md for a Windows home, checked against the digest
    table: with the era's forward-slash form, undoing `<base>/skills` as
    `_placeholder_forms` does with ``as_posix`` yields a shipped digest. The
    fixture fix itself (``fixture_tokens`` giving that form) is pinned by
    `test_fixture_tokens_are_forward_slash_paths`."""
    from superclaude.cli.retired_skill_files import RETIRED_SKILL_FILES

    doc = load_era(era)
    blob = BLOBS[doc["files"][f"$HOME/.claude/skills/{skill}/SKILL.md"]["blob"]]
    home = PureWindowsPath(r"C:\Users\me\AppData\Local\Temp\pytest-0\test0\home")
    tokens = {name: "unused" for name in TOKEN_NAMES} | {"HOME": _era_path(home)}
    written = resolve_tokens(blob, tokens).encode("utf-8")
    skills = _era_path(home / ".claude" / "skills").encode("utf-8")

    assert skills in written, written[:200]
    undone = written.replace(skills, b"{{SKILLS_PATH}}")
    digest = hashlib.sha256(undone.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert digest in RETIRED_SKILL_FILES[skill]["SKILL.md"]


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
    # The era wrote the interpreter and the paths with forward slashes on
    # every platform (fixture_tokens), so the forms to look for are those.
    tokens = fixture_tokens(tmp_path, home, project)
    assert any(tokens["PYTHON"] in c for c in _commands(base / "settings.json"))

    success, message = install_all(base_path=base, force=False, scope="project")

    assert success, message
    text = (base / "settings.json").read_text(encoding="utf-8")
    for form in (sys.executable, tokens["PYTHON"], str(project), tokens["PROJECT"]):
        assert form not in text, form
    assert str(home) not in text and tokens["HOME"] not in text
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


# --- C-01, C-02, C-03, C-19: input preflight (Q16 a) -------------------------
#
# Every command validates the files it edits before its first write or delete,
# and refuses one that is not plain UTF-8 or not a JSON object: exit 1, the tree
# unchanged, the file and its encoding named.

SCOPES = ("user", "project", "local")
CLAUDE_TEXT = "# 내 규칙\n\n항상 한국어로 답하세요.\n"


def _encode(text: str, kind: str) -> bytes:
    if kind == "trailing-comma":
        return (text.rstrip().rstrip("}").rstrip() + ",\n}\n").encode("utf-8")
    if kind == "not-an-object":
        return b"[]\n"
    # cp949 cannot hold an em dash; a cp949 editor's save replaces it too.
    return text.encode(kind, errors="replace")


def settings_path(base: Path, scope: str) -> Path:
    return base / settings_filename(scope)


def claude_path(base: Path, scope: str) -> Path:
    return base.parent / "CLAUDE.local.md" if scope == "local" else base / "CLAUDE.md"


def corrupt_settings(settings: Path, kind: str) -> None:
    """Re-save ``settings`` as ``kind``, with a non-ASCII value so the bytes really differ."""
    data = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
    data["note"] = "한글"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_bytes(
        _encode(json.dumps(data, ensure_ascii=False, indent=2) + "\n", kind)
    )


def corrupt_claude(claude_md: Path, kind: str) -> None:
    text = claude_md.read_text(encoding="utf-8") if claude_md.exists() else CLAUDE_TEXT
    claude_md.parent.mkdir(parents=True, exist_ok=True)
    claude_md.write_bytes(_encode(CLAUDE_TEXT + "\n" + text, kind))


# What the refusal names for each kind of bad input.
NAMED = {
    "utf-16": "UTF-16",
    "utf-8-sig": "byte-order mark",
    "cp949": "not UTF-8",
    "trailing-comma": "not valid JSON",
    "not-an-object": "not an object",
}


@pytest.mark.parametrize("scope", SCOPES)
@pytest.mark.parametrize("encoding", ["utf-16", "cp949"])
def test_c01_uninstall_refuses_undecodable_settings_before_deleting(
    tmp_path: Path, monkeypatch, scope: str, encoding: str
) -> None:
    """C-01: a UTF-16 or cp949 settings file used to crash uninstall after it had
    deleted every file, leaving the hooks registered and CLAUDE.md importing a
    deleted file."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    settings = settings_path(base, scope)
    corrupt_settings(settings, encoding)
    before = snapshot(tmp_path)

    success, message = uninstall_all(base_path=base, scope=scope)

    assert not success, message
    assert str(settings) in message and NAMED[encoding] in message, message
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("scope", SCOPES)
@pytest.mark.parametrize("kind", ["trailing-comma", "utf-8-sig"])
def test_c02_uninstall_refuses_malformed_or_bom_settings(
    tmp_path: Path, monkeypatch, scope: str, kind: str
) -> None:
    """C-02: a settings file that does not parse read as "No hooks", exit 0 —
    every hook stayed registered while all content was deleted."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    settings = settings_path(base, scope)
    corrupt_settings(settings, kind)
    before = snapshot(tmp_path)

    success, message = uninstall_all(base_path=base, scope=scope)

    assert not success, message
    assert "No hooks" not in message
    assert str(settings) in message and NAMED[kind] in message, message
    assert snapshot(tmp_path) == before


# (file, kind, scope): every bad input once, the scopes rotated between them.
BAD_INPUTS = [
    ("settings", "trailing-comma", "user"),
    ("settings", "utf-8-sig", "project"),
    ("settings", "utf-16", "local"),
    ("settings", "cp949", "user"),
    ("settings", "not-an-object", "project"),
    ("claude", "cp949", "local"),
    ("claude", "utf-16", "user"),
    ("claude", "utf-8-sig", "project"),
]
COMMANDS = {
    "install": ["install"],
    "update": ["update"],
    "doctor": ["doctor", "--verbose"],
    "uninstall-dry-run": ["uninstall", "--dry-run"],
}


@pytest.mark.parametrize("command", list(COMMANDS))
@pytest.mark.parametrize(("which", "kind", "scope"), BAD_INPUTS, ids=lambda v: str(v))
def test_c03_bad_input_refused_before_any_write(
    tmp_path: Path, monkeypatch, command: str, which: str, kind: str, scope: str
) -> None:
    """C-03: install and update wrote every file before failing on the input,
    and doctor and `uninstall --dry-run` raised a traceback."""
    if command == "install":
        home, project = sandbox(tmp_path, monkeypatch)
        base = scope_base(home, project, scope)
    else:
        home, project, base = fresh_install(tmp_path, monkeypatch, scope)
    target = (
        settings_path(base, scope) if which == "settings" else claude_path(base, scope)
    )
    (corrupt_settings if which == "settings" else corrupt_claude)(target, kind)
    before = snapshot(tmp_path)

    result = CliRunner().invoke(main, [*COMMANDS[command], "--scope", scope])

    output = all_output(result)
    assert result.exception is None or isinstance(result.exception, SystemExit), output
    assert result.exit_code == 1, output
    assert str(target) in output and NAMED[kind] in output, output
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("data", [b"", b"\n  \n"], ids=["zero-byte", "whitespace"])
@pytest.mark.parametrize("scope", SCOPES)
def test_v4_empty_settings_file_reads_as_an_empty_object(
    tmp_path: Path, monkeypatch, scope: str, data: bytes
) -> None:
    """V-4: `touch settings.json` holds no settings to lose, yet install, doctor
    and uninstall refused it as invalid JSON."""
    home, project = sandbox(tmp_path, monkeypatch)
    base = scope_base(home, project, scope)
    settings = settings_path(base, scope)
    settings.parent.mkdir(parents=True)
    settings.write_bytes(data)

    for command in (["install"], ["doctor"], ["uninstall", "-y"]):
        result = CliRunner().invoke(main, [*command, "--scope", scope])
        output = all_output(result)
        assert result.exit_code == 0, (command, output)
        assert "not valid JSON" not in output, (command, output)
        if command == ["install"]:
            assert json.loads(settings.read_text(encoding="utf-8"))["hooks"], output
    assert not (base / "superclaude").exists()


def _plant_cp949_exclude(project: Path) -> Path:
    exclude = project / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_bytes() if exclude.exists() else b""
    exclude.write_bytes(existing + "# 한글 exclude\nscratch/\n".encode("cp949"))
    return exclude


def test_c19_undecodable_exclude_refused_before_any_write(
    tmp_path: Path, monkeypatch
) -> None:
    """C-19: a non-UTF-8 info/exclude crashed a local install at its last step."""
    home, project = sandbox(tmp_path, monkeypatch)
    exclude = _plant_cp949_exclude(project)
    before = snapshot(tmp_path)

    success, message = install_all(base_path=project / ".claude", scope="local")

    assert not success, message
    assert str(exclude) in message and "not UTF-8" in message, message
    assert snapshot(tmp_path) == before


def test_c19_add_git_exclude_reports_undecodable_exclude(
    tmp_path: Path, monkeypatch
) -> None:
    _home, project = sandbox(tmp_path, monkeypatch)
    exclude = _plant_cp949_exclude(project)
    before = exclude.read_bytes()

    success, message = add_git_exclude(project, "local")

    assert not success, message
    assert "not UTF-8" in message, message
    assert exclude.read_bytes() == before


def test_c19_doctor_fails_while_local_exclude_block_missing(
    tmp_path: Path, monkeypatch
) -> None:
    """C-19: doctor called a local install healthy while git saw all of it."""
    _home, project, _base = fresh_install(tmp_path, monkeypatch, "local")

    def exclude_check() -> dict:
        checks = run_doctor(scope="local")["checks"]
        found = [c for c in checks if "exclude" in c["name"]]
        assert len(found) == 1, [c["name"] for c in checks]
        return found[0]

    assert exclude_check()["passed"]
    ok, message = remove_git_exclude(project)
    assert ok, message
    check = exclude_check()
    assert not check["passed"], check


# --- C-07: import removal anchored to SC's own lines ------------------------


@pytest.mark.parametrize(
    ("scope", "import_line"),
    [
        ("user", "@superclaude/CLAUDE_SC.md"),
        ("local", "@.claude/superclaude/CLAUDE_SC.md"),
    ],
)
def test_c07_import_removal_keeps_user_lines(
    tmp_path: Path, scope: str, import_line: str
) -> None:
    """C-07: any line holding `@superclaude/` lost everything from there to its
    end — `docs@superclaude/wiki and stays.` became `docs`."""
    base = tmp_path / ".claude"
    base.mkdir()
    user_text = (
        "# Team notes\n"
        "Our wiki lives at docs@superclaude/wiki and stays.\n"
        "see @.claude/superclaude/x\n"
    )
    target = claude_path(base, scope)
    target.write_text(user_text + f"\n# superclaude\n{import_line}\n", encoding="utf-8")

    success, message = remove_claude_md_import(base, scope=scope)

    assert success, message
    assert target.read_text(encoding="utf-8") == user_text


# --- C-13, C-14: `uninstall --remove-mcp` -----------------------------------

FOREIGN_PLAYWRIGHT = {
    "type": "stdio",
    "command": "my-own-playwright",
    "args": ["--mine"],
}
# What `claude mcp add ... tavily -- npx -y tavily-mcp@latest` records.
SC_TAVILY = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "tavily-mcp@latest"],
    "env": {},
}


def write_mcp_servers(home: Path, project: Path, scope: str, servers: dict) -> None:
    """Register ``servers`` where Claude Code keeps ``scope``'s MCP servers."""
    if scope == "project":
        (project / ".mcp.json").write_text(
            json.dumps({"mcpServers": servers}), encoding="utf-8"
        )
        return
    doc = (
        {"mcpServers": servers}
        if scope == "user"
        else {"projects": {str(project.resolve()): {"mcpServers": servers}}}
    )
    (home / ".claude.json").write_text(json.dumps(doc), encoding="utf-8")


def record_claude_calls(monkeypatch) -> list[list[str]]:
    """Answer every `claude` call with success and record its argv."""
    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(install_mcp, "_run_command", fake_run)
    monkeypatch.setattr(shutil, "which", lambda name, *a, **k: f"/stub/{name}")
    return calls


@pytest.mark.parametrize("scope", SCOPES)
def test_c13_remove_mcp_keeps_a_foreign_server_of_the_same_name(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """C-13: a user's own `playwright` (their command, not the registry's) was
    removed at every scope; README says user servers are preserved (Q12 a)."""
    home, project = sandbox(tmp_path, monkeypatch)
    write_mcp_servers(
        home, project, scope, {"playwright": FOREIGN_PLAYWRIGHT, "tavily": SC_TAVILY}
    )
    calls = record_claude_calls(monkeypatch)

    _removed, _skipped, failed, messages = install_mcp.uninstall_mcp_servers(
        scope=scope, project_root=None if scope == "user" else project
    )

    removes = [c for c in calls if "remove" in c]
    assert failed == 0, messages
    assert not [c for c in removes if "playwright" in c], removes
    assert [c for c in removes if "tavily" in c], removes


def _no_claude_on_path(tmp_path: Path, monkeypatch) -> None:
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    assert shutil.which("claude") is None


def test_c14_remove_mcp_without_claude_reports_a_failure(
    tmp_path: Path, monkeypatch
) -> None:
    """C-14: with no `claude` on PATH the plugin check raised FileNotFoundError."""
    sandbox(tmp_path, monkeypatch)
    _no_claude_on_path(tmp_path, monkeypatch)

    _removed, _skipped, failed, messages = install_mcp.uninstall_mcp_servers(
        scope="user"
    )

    assert failed == 1, messages
    assert any("claude" in m and "PATH" in m for m in messages), messages


def test_c14_uninstall_remove_mcp_without_claude_deletes_nothing(
    tmp_path: Path, monkeypatch
) -> None:
    """C-14: the traceback came after everything else was deleted, and the
    summary never printed."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    _no_claude_on_path(tmp_path, monkeypatch)
    before = snapshot(tmp_path)

    success, message = uninstall_all(base_path=base, scope="user", keep_mcp=False)

    assert not success, message
    assert "claude" in message and "--remove-mcp" in message, message
    assert snapshot(tmp_path) == before


# --- C-04, C-05: `update` and remediation lines stay in scope (Q4 a) ---------
#
# `update` refreshes an install and creates none: at a scope with no install it
# refuses and names the install it found. `install --force` that creates a
# scope says so. A command printed as advice carries `--scope`, and where to run
# it when that matters, so following it verbatim acts on the install diagnosed.

# A quoted command a message tells the user to run, and where.
_ADVICE = re.compile(r"'superclaude [^']*--scope (\w+)'( from \S+)?")


def test_c04_update_refuses_a_scope_with_no_install(
    tmp_path: Path, monkeypatch
) -> None:
    """C-04: `update` with no `--scope` at a local-only install created a full
    user install in ~/.claude (main.py `update`, default user)."""
    home, project, _base = fresh_install(tmp_path, monkeypatch, "local")
    before = snapshot(tmp_path)

    result = CliRunner().invoke(main, ["update"])

    output = all_output(result)
    assert result.exit_code == 1, output
    assert f"'superclaude update --scope local' from {project}" in output, output
    assert not (home / ".claude").exists()
    assert snapshot(tmp_path) == before


def test_c04_update_from_a_subdirectory_names_the_install_above(
    tmp_path: Path, monkeypatch
) -> None:
    """`update --scope local` from `src/` wrote a second, nested install there."""
    _home, project, _base = fresh_install(tmp_path, monkeypatch, "local")
    sub = project / "src"
    sub.mkdir()
    monkeypatch.chdir(sub)
    before = snapshot(tmp_path)

    result = CliRunner().invoke(main, ["update", "--scope", "local"])

    output = all_output(result)
    assert result.exit_code == 1, output
    assert f"'superclaude update --scope local' from {project}" in output, output
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize(
    ("installed", "asked"), [("project", "local"), ("local", "project")]
)
def test_v3_update_refuses_another_scopes_install_in_the_same_base(
    tmp_path: Path, monkeypatch, installed: str, asked: str
) -> None:
    """V-3: project and local share ./.claude, so `update --scope local` over an
    uncommitted project install passed the has-an-install check and created a
    local install (settings.local.json, CLAUDE.local.md) on top of it."""
    _home, project, _base = fresh_install(tmp_path, monkeypatch, installed)
    before = snapshot(tmp_path)

    result = CliRunner().invoke(main, ["update", "--scope", asked])

    output = all_output(result)
    assert result.exit_code == 1, output
    assert f"'superclaude update --scope {installed}' from {project}" in output, output
    assert f"--scope {asked}'" not in output, output
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("era", ERAS)
def test_v3_update_still_refreshes_every_era_at_its_scope(
    tmp_path: Path, monkeypatch, era: str
) -> None:
    """The scope check reads the install's own evidence; every captured era's
    install must read as the scope it was made at, or `update` refuses it."""
    _home, _project, _base = build_legacy_install(tmp_path, era, monkeypatch)

    result = CliRunner().invoke(main, ["update", "--scope", load_era(era)["scope"]])

    output = all_output(result)
    assert result.exit_code == 0, output


def test_c04_install_force_creating_a_scope_warns(tmp_path: Path, monkeypatch) -> None:
    """Q4 a: `install --force` is a refresh; creating a scope with it is the
    sync-scope-creates trap, so it says so and names the install it found."""
    home, project, _base = fresh_install(tmp_path, monkeypatch, "local")

    result = CliRunner().invoke(main, ["install", "--force", "--scope", "user"])

    output = all_output(result)
    assert result.exit_code == 0, output
    warning = [
        line
        for line in output.splitlines()
        if line.startswith("⚠️") and str(home / ".claude") in line
    ]
    assert warning, output
    assert f"'superclaude update --scope local' from {project}" in output, output

    again = CliRunner().invoke(main, ["install", "--force", "--scope", "user"])
    assert again.exit_code == 0, all_output(again)
    assert str(project) not in all_output(again)


@pytest.mark.parametrize("scope", SCOPES)
def test_c05_drift_remediation_carries_the_scope(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """C-05: verify-drift advised a bare `install --force`; followed from a local
    project, it wrote a user install."""
    _home, project, base = fresh_install(tmp_path, monkeypatch, scope)
    analyze = base / "commands" / "sc" / "analyze.md"
    analyze.write_text(
        analyze.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8"
    )

    result = CliRunner().invoke(main, ["verify-drift"])

    output = all_output(result)
    assert result.exit_code == 1, output
    assert "'superclaude install --force'" not in output, output
    # The same command install and doctor name: `update` is the refresh of an
    # install, where `install --force` would also create one.
    assert "'superclaude update --scope" in output, output
    advice = _ADVICE.findall(output)
    assert advice, output
    for named, where in advice:
        assert named == scope, output
        assert where == ("" if scope == "user" else f" from {project}"), output


@pytest.mark.parametrize("era", ERAS)
def test_c05_every_command_install_prints_carries_the_scope(
    tmp_path: Path, monkeypatch, era: str
) -> None:
    """Q4 a: a `superclaude` command in install's output, followed verbatim from
    any directory, acts on the install it was printed for."""
    _home, _project, base = build_legacy_install(tmp_path, era, monkeypatch)
    scope = load_era(era)["scope"]

    _success, message = install_all(base_path=base, force=False, scope=scope)

    named = re.findall(r"superclaude (?:install|update|uninstall)\b[^'`\n]*", message)
    for command in named:
        assert f"--scope {scope}" in command, message


# --- C-06: the `memory: user` era at project scope (owner ruling b) ----------


def _memory_values(base: Path) -> set[str]:
    return {
        line
        for name in shipped_names("agents")
        if (base / "agents" / name).exists()
        for line in (base / "agents" / name).read_text(encoding="utf-8").splitlines()
        if line.startswith("memory:")
    }


def test_c06_memory_user_era_project_install_advises_update_in_scope(
    tmp_path: Path, monkeypatch
) -> None:
    """C-06: a project install from the `memory: user` era was refused for good,
    and the advice (`--scope user`) wrote or uninstalled the user scope. The
    refusal stays; the advice stays in this scope."""
    _home, project, base = build_legacy_install(
        tmp_path, "d174e600-project", monkeypatch
    )
    before = snapshot(tmp_path)

    success, message = install_all(base_path=base, force=False, scope="project")

    assert not success, message
    assert "--scope user" not in message, message
    assert f"'superclaude update --scope project' from {project}" in message, message
    assert snapshot(tmp_path) == before


def test_c06_update_rewrites_era_agents_to_the_project_store(
    tmp_path: Path, monkeypatch
) -> None:
    """The advice works: `update --scope project` rewrites `memory:` and says
    where agent memory moves from and to."""
    home, _project, base = build_legacy_install(
        tmp_path, "d174e600-project", monkeypatch
    )
    assert _memory_values(base) == {"memory: user"}

    result = CliRunner().invoke(main, ["update", "--scope", "project"])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert _memory_values(base) == {"memory: project"}
    assert str(home / ".claude" / "agent-memory") in output, output
    assert str(base / "agent-memory") in output, output


@pytest.mark.parametrize(
    ("scope", "planted"), [("project", "user"), ("local", "user"), ("user", "local")]
)
def test_c06_conflict_advice_never_names_another_base(
    tmp_path: Path, monkeypatch, scope: str, planted: str
) -> None:
    """Owner rule with C-06: conflict advice never names a scope whose base is
    not this one. User scope's base is ~/.claude; project and local are the
    `.claude` of the directory the command runs from, so advice naming them
    says where."""
    home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    for name in shipped_names("agents"):
        agent = base / "agents" / name
        agent.write_text(
            agent.read_text(encoding="utf-8").replace(
                f"memory: {scope}\n", f"memory: {planted}\n"
            ),
            encoding="utf-8",
        )

    success, message = install_all(base_path=base, force=False, scope=scope)

    assert not success, message
    advice = _ADVICE.findall(message)
    assert advice, message
    assert len(advice) == message.count("--scope "), message
    for named, where in advice:
        if named == "user":
            assert base == home / ".claude", message
        else:
            assert where == f" from {base.parent}", message


# --- C-15: CLAUDE_CONFIG_DIR (Q15 b) ------------------------------------------


def test_c15_install_and_doctor_name_a_differing_config_dir(
    tmp_path: Path, monkeypatch
) -> None:
    """C-15: with CLAUDE_CONFIG_DIR elsewhere Claude Code never reads ~/.claude,
    and neither install nor doctor said so."""
    home, _project = sandbox(tmp_path, monkeypatch)
    config = tmp_path / "cc"
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    install = CliRunner().invoke(main, ["install", "--scope", "user"])
    assert install.exit_code == 0, all_output(install)
    plain = run_doctor(scope="user")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))

    install = CliRunner().invoke(main, ["install", "--force", "--scope", "user"])
    doctor = CliRunner().invoke(main, ["doctor", "--scope", "user"])

    for result in (install, doctor):
        output = all_output(result)
        warned = [line for line in output.splitlines() if "CLAUDE_CONFIG_DIR" in line]
        assert warned, output
        assert str(config) in output and str(home / ".claude") in output, output
    # A warning, not a failed check: the doctor verdict is unchanged.
    assert [c["passed"] for c in run_doctor(scope="user")["checks"]] == [
        c["passed"] for c in plain["checks"]
    ]
    assert not config.exists()


def test_c15_no_warning_when_config_dir_is_the_default(
    tmp_path: Path, monkeypatch
) -> None:
    home, _project = sandbox(tmp_path, monkeypatch)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(home / ".claude"))

    install = CliRunner().invoke(main, ["install", "--scope", "user"])
    doctor = CliRunner().invoke(main, ["doctor", "--scope", "user"])

    assert "CLAUDE_CONFIG_DIR" not in all_output(install)
    assert "CLAUDE_CONFIG_DIR" not in all_output(doctor)


# --- C-18: one exclude file per clone ---------------------------------------


def add_linked_worktree(main_root: Path, worktree: Path) -> Path:
    """A linked worktree of ``main_root`` as git lays one out, built by hand.

    ``commondir`` is what makes git read the main repository's ``info/exclude``
    (gotcha git-common-dir-paths); without it the pointer reads as a submodule.
    """
    name = worktree.name
    admin = main_root / ".git" / "worktrees" / name
    admin.mkdir(parents=True)
    (admin / "commondir").write_text("../..\n", encoding="utf-8")
    (admin / "gitdir").write_text(f"{worktree / '.git'}\n", encoding="utf-8")
    (admin / "HEAD").write_text(f"ref: refs/heads/{name}\n", encoding="utf-8")
    worktree.mkdir()
    (worktree / ".git").write_text(f"gitdir: {admin}\n", encoding="utf-8")
    return worktree


def _ignored(root: Path, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(root), "check-ignore", "-q", path], check=False
        ).returncode
        == 0
    )


def test_c18_project_install_reports_replacing_a_worktree_local_block(
    tmp_path: Path, monkeypatch
) -> None:
    """C-18: a project install in the main worktree replaced the clone's local
    block, so the linked worktree's local install became visible to git, and
    the only output was "refreshed with SC project block"."""
    _home, project = sandbox(tmp_path, monkeypatch)
    worktree = add_linked_worktree(project, tmp_path / "wt")
    common = project / ".git" / "info" / "exclude"
    git_path = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "--git-path", "info/exclude"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert Path(git_path).resolve() == common.resolve()

    monkeypatch.chdir(worktree)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(worktree))
    ok, message = install_all(base_path=worktree / ".claude", scope="local")
    assert ok, message
    assert _ignored(worktree, ".claude/superclaude/CLAUDE_SC.md")

    monkeypatch.chdir(project)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    ok, message = install_all(base_path=project / ".claude", scope="project")

    assert ok, message
    assert not _ignored(worktree, ".claude/superclaude/CLAUDE_SC.md")
    warning = [
        line
        for line in message.splitlines()
        if "⚠️" in line and "local" in line and "worktree" in line
    ]
    assert warning, message


# --- C-08, C-09: retired names and hook identities (Q10 a, Q13 a) -------------
#
# `shipped_names_history.json` (scripts/gen_shipped_names.py, full history) is
# the record of everything a release could have installed. Every identity it
# marks as not shipped now has to be on a retired list, and install (force or
# not), `update` and uninstall remove what matches, and only what is
# superclaude's.

HISTORY = json.loads((FIXTURES / "shipped_names_history.json").read_text("utf-8"))
REGENERATE = (
    "the shipped-names history is stale or a retired name is unlisted: regenerate "
    "it from a full clone (uv run python scripts/gen_shipped_names.py), then list "
    "every identity it marks shipped_now: false"
)


def retired_names(kind: str) -> set[str]:
    return {row["name"] for row in HISTORY["names"][kind] if not row["shipped_now"]}


def _plant_user_content(home: Path) -> None:
    """A skill and an agent of the user's own next to the legacy install."""
    skill = home / ".claude" / "skills" / "my-skill"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text("---\nname: my-skill\n---\nmine\n", "utf-8")
    (home / ".claude" / "agents" / "my-agent.md").write_text("mine\n", "utf-8")


def _left(base: Path) -> list[str]:
    return sorted(
        [
            f"agents/{n}"
            for n in retired_names("agents")
            if (base / "agents" / n).exists()
        ]
        + [
            f"skills/{n}"
            for n in retired_names("skills")
            if (base / "skills" / n).exists()
        ]
    )


@pytest.mark.parametrize("operation", ["install", "install --force", "uninstall"])
def test_c08_retired_agents_and_skills_do_not_survive(
    tmp_path: Path, monkeypatch, operation: str
) -> None:
    """C-08: pm-agent.md, deep-research-agent.md and the 11 b933fd65 process
    skills (using-superclaude: "Loaded at session start") survived install and
    uninstall; the user's own skill and agent stay."""
    home, _project, base = build_legacy_install(tmp_path, "b933fd65p-user", monkeypatch)
    _plant_user_content(home)
    assert len(_left(base)) == 17

    if operation == "uninstall":
        success, message = uninstall_all(base_path=base, scope="user")
    else:
        force = operation.endswith("--force")
        success, message = install_all(base_path=base, force=force, scope="user")

    assert success, message
    assert _left(base) == [], message
    assert (base / "skills" / "my-skill" / "SKILL.md").exists()
    assert (base / "agents" / "my-agent.md").exists()


@pytest.mark.parametrize("operation", ["install", "uninstall"])
def test_c08_another_collections_skill_under_a_retired_name_is_kept(
    tmp_path: Path, monkeypatch, operation: str
) -> None:
    """Ten of the process skills share their names with another public skill
    collection; a `brainstorming/` that is not superclaude's text is the user's."""
    home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    theirs = base / "skills" / "brainstorming" / "SKILL.md"
    theirs.parent.mkdir(parents=True)
    theirs.write_text(
        "---\nname: brainstorming\ndescription: Use before any creative work\n---\n",
        "utf-8",
    )

    if operation == "uninstall":
        success, message = uninstall_all(base_path=base, scope="user")
    else:
        success, message = install_all(base_path=base, force=True, scope="user")

    assert success, message
    assert theirs.exists(), message


def test_q10_every_retired_name_is_on_a_retired_list() -> None:
    """Q10 a guard: a name any release shipped and this one does not is listed,
    so install and uninstall can reach it."""
    from superclaude.cli import install_paths

    assert retired_names("agents") <= set(install_paths.RETIRED_AGENT_FILES), REGENERATE
    assert retired_names("output-styles") == set(), REGENERATE
    assert retired_names("skills") <= set(install_paths.LEGACY_SKILL_NAMES), REGENERATE


@pytest.mark.parametrize(
    ("kind", "table", "names"),
    [
        ("skill", "RETIRED_SKILL_DIGESTS", "LEGACY_SKILL_NAMES"),
        ("agent", "RETIRED_AGENT_DIGESTS", "RETIRED_AGENT_FILES"),
    ],
)
def test_q10_retired_digests_cover_every_shipped_revision(
    kind: str, table: str, names: str
) -> None:
    """A retired name is removed by content (V-1), so its table must match every
    revision that shipped under it, or an upgrade from that revision keeps it."""
    from superclaude.cli import install_paths

    digests = getattr(install_paths, table, {})
    assert set(digests) == set(getattr(install_paths, names)), REGENERATE
    for name, listed in digests.items():
        recorded = {d[:16] for d in HISTORY[f"retired_{kind}_digests"][name]}
        assert set(listed) == recorded, (name, REGENERATE)


# --- V-1: a retired name is superclaude's only by content (P7) ---------------
#
# `pm-agent` and `using-superclaude` are ordinary names; the retired lists
# removed any file under them, so a user's own agent or skill went at install
# with no backup. Every retired agent and skill is removed only when its text
# is a revision superclaude shipped, like the process skills before it.


def _plant_same_name_user_content(base: Path) -> dict[Path, bytes]:
    """The user's own file under every retired agent and skill name."""
    planted = {}
    for name in retired_names("agents"):
        path = base / "agents" / name
        planted[path] = f"---\nname: {Path(name).stem}\n---\nmy own agent\n".encode()
    for name in retired_names("skills"):
        path = base / "skills" / name / "SKILL.md"
        planted[path] = f"---\nname: {name}\n---\nmy notes\n".encode()
    for path, data in planted.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return planted


@pytest.mark.parametrize(
    "operation", ["install", "install --force", "update", "uninstall -y"]
)
@pytest.mark.parametrize("scope", SCOPES)
def test_v1_users_own_file_under_a_retired_name_survives(
    tmp_path: Path, monkeypatch, scope: str, operation: str
) -> None:
    """V-1: install deleted the user's own `pm-agent.md`, `deep-research-agent.md`
    and `skills/using-superclaude/` by name (a team's committed agent too)."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    planted = _plant_same_name_user_content(base)

    result = CliRunner().invoke(main, [*operation.split(), "--scope", scope])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert {p: p.read_bytes() if p.exists() else None for p in planted} == planted


@pytest.mark.parametrize("scope", SCOPES)
def test_v1_verify_drift_ignores_a_users_file_under_a_retired_name(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """V-1: the user's own `pm-agent.md` read as EXTRA, exit 1 forever (C-11)."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    _plant_same_name_user_content(base)

    result = CliRunner().invoke(main, ["verify-drift", "--scope", scope, "--verbose"])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert "EXTRA" not in output and "RETIRED" not in output, output


def _era_retired_files(era: str) -> list[str]:
    names = {f"agents/{n}" for n in retired_names("agents")} | {
        f"skills/{n}/SKILL.md" for n in retired_names("skills")
    }
    return [
        key for key in load_era(era)["files"] if key.partition("/.claude/")[2] in names
    ]


@pytest.mark.parametrize("operation", ["update", "uninstall"])
@pytest.mark.parametrize("era", [era for era in ERAS if _era_retired_files(era)])
def test_v1_shipped_retired_copies_still_go(
    tmp_path: Path, monkeypatch, era: str, operation: str
) -> None:
    """The content gate keeps removing what superclaude shipped: every captured
    era's retired agents and skills, as that era's installer wrote them."""
    _home, _project, base = build_legacy_install(tmp_path, era, monkeypatch)
    scope = load_era(era)["scope"]
    assert _left(base)

    if operation == "uninstall":
        success, message = uninstall_all(base_path=base, scope=scope)
    else:
        success, message = install_all(base_path=base, force=True, scope=scope)

    assert success, message
    assert _left(base) == [], message


@pytest.mark.parametrize("scope", ["user", "local"])
def test_v1_a_retired_agent_rewritten_to_the_scope_still_goes(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """Install rewrites `memory: project` to the scope (385baaf2 on), so a user
    or local copy of a retired agent is not byte-equal to any revision."""
    from superclaude.cli.install_components import _rewrite_agent_memory_scope

    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    shipped = _era_blob("b933fd65p-user", "$HOME/.claude/agents/pm-agent.md")
    rewritten = _rewrite_agent_memory_scope(shipped, scope)
    assert rewritten != shipped
    (base / "agents" / "pm-agent.md").write_text(rewritten, "utf-8", newline="")

    success, message = install_all(base_path=base, force=True, scope=scope)

    assert success, message
    assert not (base / "agents" / "pm-agent.md").exists(), message


@pytest.mark.parametrize("scope", ["project", "local"])
def test_v1_a_retired_skill_with_a_relative_skills_path_still_goes(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """Install resolved `{{SKILLS_PATH}}` in SKILL.md (cd2f8aab → b806c61c:
    ``str`` until e1b2fbe7, ``as_posix`` from 757e3649), to `.claude/skills`
    at project scope (local too, from 2026-03); the captured eras carry only
    the absolute form."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    shipped = _era_blob(
        "b933fd65p-user", "$HOME/.claude/skills/confidence-check/SKILL.md"
    )
    assert "$HOME/.claude/skills/" in shipped
    skill = base / "skills" / "confidence-check" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(shipped.replace("$HOME/.claude/skills", ".claude/skills"), "utf-8")

    success, message = uninstall_all(base_path=base, scope=scope)

    assert success, message
    assert not skill.parent.exists(), message


@pytest.mark.parametrize("scope", ["user", "local"])
def test_v1_a_retired_skill_in_the_str_era_form_still_goes(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """The eight unreleased commits cd2f8aab → e1b2fbe7 resolved
    `{{SKILLS_PATH}}` with ``str(...resolve())`` and wrote SKILL.md in text
    mode: backslashes and CRLF on Windows. No captured era is from them, so
    this writes that form itself. On Linux ``str`` is the ``as_posix`` form;
    the Windows job is where this pins the ``str`` entry of
    `_placeholder_forms` end to end."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    shipped = _era_blob(
        "b933fd65p-user", "$HOME/.claude/skills/confidence-check/SKILL.md"
    )
    assert "$HOME/.claude/skills/" in shipped
    skill = base / "skills" / "confidence-check" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    text = shipped.replace("$HOME/.claude/skills", str((base / "skills").resolve()))
    skill.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    success, message = uninstall_all(base_path=base, scope=scope)

    assert success, message
    assert not skill.parent.exists(), message


def test_placeholder_forms_undo_the_str_form_on_every_platform(
    tmp_path: Path,
) -> None:
    """`_placeholder_forms` undoes the ``str`` form (backslashes on Windows)
    as well as ``as_posix``: a SKILL.md from the cd2f8aab → e1b2fbe7 installers
    on Windows is superclaude's text. `_placeholder_forms` only reads its path,
    so a ``WindowsEraPath`` skill dir gives the Windows forms on Linux, where
    only the ``str`` entry matches the file."""
    from superclaude.cli.install_paths import _is_shipped_skill_file, _placeholder_forms
    from superclaude.cli.retired_skill_files import RETIRED_SKILL_FILES

    windows_skill_dir = WindowsEraPath(r"C:\Users\me\.claude\skills\confidence-check")
    skills = str(windows_skill_dir.parent)
    scripts = str(windows_skill_dir.parent.parent / "superclaude" / "scripts")
    assert "\\" in skills
    shipped = _era_blob(
        "b933fd65p-user", "$HOME/.claude/skills/confidence-check/SKILL.md"
    )
    text = shipped.replace("$HOME/.claude/skills", skills)
    skill_dir = tmp_path / "skills" / "confidence-check"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    digests = RETIRED_SKILL_FILES["confidence-check"]["SKILL.md"]

    forms = _placeholder_forms(windows_skill_dir)

    assert (skills.encode(), scripts.encode()) in forms
    assert _is_shipped_skill_file(skill_dir / "SKILL.md", digests, forms)
    posix_only = [form for form in forms if b"\\" not in form[0]]
    assert posix_only and len(posix_only) < len(forms)
    assert not _is_shipped_skill_file(skill_dir / "SKILL.md", digests, posix_only)


# --- W-1: a retired skill loses only the files superclaude shipped ------------
#
# A retired skill directory whose SKILL.md is superclaude's was removed whole
# (`rmtree`), with a file the user added there and a shipped file they edited.
# Now only a file whose path and text are a shipped revision of that skill goes
# (cli/retired_skill_files.py); the rest stays, directories go once empty, and
# a symlink is never followed. The ownership gate is still SKILL.md: a skill
# whose SKILL.md the user edited is theirs, helpers and all.

W1_ERA = "ec6fa7e2p-user"
W1_SKILL = "verbalized-sampling"
W1_OPERATIONS = ["install", "install --force", "update", "uninstall -y"]
_KEPT_LINE = re.compile(r"Kept (\d+) file\(s\) in (.+?): ")


class _W1Copy(NamedTuple):
    of: str


def _w1_shipped() -> dict[str, str]:
    """W1_SKILL's files as W1_ERA's installer wrote them, by path in the skill."""
    prefix = f"$HOME/.claude/skills/{W1_SKILL}/"
    files = {
        key[len(prefix) :]: BLOBS[entry["blob"]]
        for key, entry in load_era(W1_ERA)["files"].items()
        if key.startswith(prefix)
    }
    assert "SKILL.md" in files and "references/theory.md" in files, files
    return files


def _plant_w1_skill(base: Path, case: dict) -> Path:
    """``add`` maps a path to its text, or to ``_W1Copy(<shipped path>)`` for a
    copy of that shipped file; ``crlf`` writes every file with CRLF endings."""
    skill = base / "skills" / W1_SKILL
    shipped = _w1_shipped()
    files = dict(shipped)
    for rel, text in case["add"].items():
        files[rel] = shipped[text.of] if isinstance(text, _W1Copy) else text
    for rel, suffix in case["edit"].items():
        files[rel] = shipped[rel] + suffix
    for rel, text in files.items():
        if case.get("crlf"):
            text = text.replace("\r\n", "\n").replace("\n", "\r\n")
        (skill / rel).parent.mkdir(parents=True, exist_ok=True)
        (skill / rel).write_text(text, encoding="utf-8", newline="")
    return skill


def _tree(skill: Path) -> dict[str, bytes]:
    return {
        path.relative_to(skill).as_posix(): path.read_bytes()
        for path in skill.rglob("*")
        if path.is_file()
    }


def _kept_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if _KEPT_LINE.search(line)]


W1_CASES = {
    "shipped-only": {"add": {}, "edit": {}, "kept": set(), "ours": True},
    # A Windows checkout with core.autocrlf installs CRLF copies.
    "shipped-only-crlf": {
        "add": {},
        "edit": {},
        "kept": set(),
        "ours": True,
        "crlf": True,
    },
    # Shipped text at a path that skill never shipped it at is the user's copy.
    "copy-elsewhere": {
        "add": {
            "backup/SKILL.md": _W1Copy("SKILL.md"),
            "theory.md": _W1Copy("references/theory.md"),
        },
        "edit": {},
        "kept": {"backup/SKILL.md", "theory.md"},
        "ours": True,
    },
    "user-file": {
        "add": {"my-notes.md": "my notes\n"},
        "edit": {},
        "kept": {"my-notes.md"},
        "ours": True,
    },
    "edited-helper": {
        "add": {},
        "edit": {"references/theory.md": "\nmy correction\n"},
        "kept": {"references/theory.md"},
        "ours": True,
    },
    "nested-user-dir": {
        "add": {
            "mine/deeper/notes.txt": "deep notes\n",
            "references/mine.md": "my reference\n",
        },
        "edit": {},
        "kept": {"mine/deeper/notes.txt", "references/mine.md"},
        "ours": True,
    },
    # SKILL.md edited: the skill is the user's, its unchanged helpers with it.
    "edited-skill-md": {
        "add": {},
        "edit": {"SKILL.md": "\nmy rule\n"},
        "kept": {
            "SKILL.md",
            "references/examples.md",
            "references/paper-methodology.md",
            "references/theory.md",
        },
        "ours": False,
    },
}


@pytest.mark.parametrize("case", W1_CASES)
@pytest.mark.parametrize("operation", W1_OPERATIONS)
@pytest.mark.parametrize("scope", SCOPES)
def test_w1_retired_skill_loses_only_the_files_superclaude_shipped(
    tmp_path: Path, monkeypatch, scope: str, operation: str, case: str
) -> None:
    """W-1: a retired skill whose SKILL.md is shipped text was rmtree'd, taking
    a file the user added there and a shipped file the user edited."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    spec = W1_CASES[case]
    skill = _plant_w1_skill(base, spec)
    before = _tree(skill)

    result = CliRunner().invoke(main, [*operation.split(), "--scope", scope])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert "Traceback" not in output, output
    after = _tree(skill) if skill.exists() else {}
    assert after == {rel: before[rel] for rel in spec["kept"]}, output
    if not spec["kept"]:
        assert not skill.exists(), output
    assert not (skill / "references").exists() or any(
        rel.startswith("references/") for rel in spec["kept"]
    ), "an emptied directory was left behind"
    kept = _kept_lines(output)
    if spec["ours"] and spec["kept"]:
        assert len(kept) == 1, output
        count, where = _KEPT_LINE.search(kept[0]).groups()
        assert int(count) == len(spec["kept"]), kept
        assert where.replace("\\", "/").endswith(f"skills/{W1_SKILL}"), kept
    else:
        assert kept == [], output


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except (OSError, NotImplementedError) as e:  # Windows without the privilege
        pytest.skip(f"cannot create a symlink here: {e}")


@pytest.mark.parametrize("operation", ["install", "uninstall -y"])
@pytest.mark.parametrize("scope", SCOPES)
def test_w1_a_symlink_inside_a_retired_skill_is_kept_and_never_followed(
    tmp_path: Path, monkeypatch, scope: str, operation: str
) -> None:
    """superclaude never shipped a symlink: one in a retired skill is the
    user's, even at a shipped path pointing at shipped text, and what it points
    at is outside the skill."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    skill = _plant_w1_skill(base, W1_CASES["shipped-only"])
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "theory.md").write_text(
        _w1_shipped()["references/theory.md"], encoding="utf-8", newline=""
    )
    (outside / "SKILL.md").write_text(
        _w1_shipped()["SKILL.md"], encoding="utf-8", newline=""
    )
    outside_before = snapshot(outside)
    (skill / "references" / "theory.md").unlink()
    _symlink(skill / "references" / "theory.md", outside / "theory.md")
    _symlink(skill / "linked", outside)

    result = CliRunner().invoke(main, [*operation.split(), "--scope", scope])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert snapshot(outside) == outside_before, output
    assert (skill / "references" / "theory.md").is_symlink(), output
    assert (skill / "linked").is_symlink(), output
    assert not (skill / "SKILL.md").exists(), output
    assert not (skill / "references" / "examples.md").exists(), output
    kept = _kept_lines(output)
    assert len(kept) == 1 and _KEPT_LINE.search(kept[0]).group(1) == "2", output


@pytest.mark.parametrize("operation", ["install", "uninstall -y"])
@pytest.mark.parametrize("scope", SCOPES)
def test_w1_a_symlinked_retired_skill_directory_is_left_alone(
    tmp_path: Path, monkeypatch, scope: str, operation: str
) -> None:
    """A retired name that is a symlink to a directory elsewhere is the user's
    link: rmtree refused it (an install failure) and nothing may follow it."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    elsewhere = _plant_w1_skill(tmp_path / "elsewhere", W1_CASES["shipped-only"])
    before = snapshot(elsewhere)
    link = base / "skills" / W1_SKILL
    _symlink(link, elsewhere)

    result = CliRunner().invoke(main, [*operation.split(), "--scope", scope])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert link.is_symlink(), output
    assert snapshot(elsewhere) == before, output


@pytest.mark.parametrize("case", ["shipped-only", "user-file", "nested-user-dir"])
@pytest.mark.parametrize("scope", SCOPES)
def test_w1_uninstall_dry_run_says_what_stays_and_changes_nothing(
    tmp_path: Path, monkeypatch, scope: str, case: str
) -> None:
    home, project, base = fresh_install(tmp_path, monkeypatch, scope)
    spec = W1_CASES[case]
    skill = _plant_w1_skill(base, spec)
    before = (snapshot(home), snapshot(project))

    result = CliRunner().invoke(main, ["uninstall", "--dry-run", "--scope", scope])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert (snapshot(home), snapshot(project)) == before, output
    assert "[DRY-RUN] Would remove: 1 skill(s) from a pre-removal release" in output
    keep = re.findall(r"\[DRY-RUN\] Would keep (\d+) file\(s\) in (.+?): ", output)
    if spec["kept"]:
        assert [int(n) for n, _ in keep] == [len(spec["kept"])], output
        assert keep[0][1].replace("\\", "/").endswith(f"skills/{W1_SKILL}"), output
    else:
        assert keep == [], output
    assert skill.exists()


@pytest.mark.parametrize("scope", SCOPES)
def test_w1_a_second_install_removes_and_reports_nothing(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """Once reduced to the user's files the directory is the user's: a repeat
    install neither touches it nor mentions it."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    spec = {
        "add": {"my-notes.md": "my notes\n", "mine/notes.txt": "deep\n"},
        "edit": {"references/theory.md": "\nmy correction\n"},
    }
    skill = _plant_w1_skill(base, spec)
    first = CliRunner().invoke(main, ["install", "--scope", scope])
    assert first.exit_code == 0, all_output(first)
    assert len(_kept_lines(all_output(first))) == 1, all_output(first)
    after_first = _tree(skill)
    assert set(after_first) == {"my-notes.md", "mine/notes.txt", "references/theory.md"}

    second = CliRunner().invoke(main, ["install", "--scope", scope])

    output = all_output(second)
    assert second.exit_code == 0, output
    assert _tree(skill) == after_first, output
    assert "pre-removal" not in output and _kept_lines(output) == [], output


@pytest.mark.parametrize("scope", SCOPES)
def test_w1_verify_drift_and_doctor_follow_what_install_removes(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """RETIRED (and doctor's `retired` advisory) while the skill still holds
    superclaude's files; none once install has reduced it to the user's."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    skill = _plant_w1_skill(
        base,
        {
            "add": {"my-notes.md": "my notes\n"},
            "edit": {"references/theory.md": "\nmy correction\n"},
        },
    )
    drift = CliRunner().invoke(main, ["verify-drift", "--scope", scope, "--verbose"])
    assert drift.exit_code == 1, all_output(drift)
    assert f"{W1_SKILL}/: RETIRED" in all_output(drift), all_output(drift)
    assert any("1 retired" in a for a in run_doctor(scope=scope)["advisories"])

    install = CliRunner().invoke(main, ["install", "--scope", scope])
    assert install.exit_code == 0, all_output(install)

    drift = CliRunner().invoke(main, ["verify-drift", "--scope", scope, "--verbose"])
    output = all_output(drift)
    assert drift.exit_code == 0, output
    assert "RETIRED" not in output and W1_SKILL not in output, output
    assert not any("retired" in a for a in run_doctor(scope=scope)["advisories"])
    assert set(_tree(skill)) == {"my-notes.md", "references/theory.md"}


def test_w1_skill_md_is_removed_last(tmp_path: Path, monkeypatch) -> None:
    """SKILL.md is what marks the directory superclaude's: removed last, an
    interrupted removal leaves the rest for the next run to find."""
    from superclaude.cli.install_paths import legacy_skill_files

    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    skill = _plant_w1_skill(base, W1_CASES["user-file"])

    ours, kept = legacy_skill_files(skill)

    assert ours[-1] == skill / "SKILL.md"
    assert sorted(p.relative_to(skill).as_posix() for p in ours) == sorted(
        _w1_shipped()
    )
    assert kept == [skill / "my-notes.md"]


@pytest.mark.parametrize("operation", W1_OPERATIONS)
@pytest.mark.parametrize("scope", SCOPES)
def test_w1_a_later_skills_error_keeps_the_earlier_kept_notice(
    tmp_path: Path, monkeypatch, scope: str, operation: str
) -> None:
    """An OSError on the second retired skill dropped the first one's Kept line,
    and its SKILL.md was already gone, so no later run could say it again."""
    from superclaude.cli import install_components, install_inventory, install_paths

    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    skill = _plant_w1_skill(base, W1_CASES["user-file"])
    other = base / "skills" / "finishing-a-development-branch"
    other.mkdir(parents=True)
    (other / "SKILL.md").write_text(
        _era_blob(W1_ERA, f"$HOME/.claude/skills/{other.name}/SKILL.md"),
        encoding="utf-8",
        newline="",
    )
    (other / "my-notes.md").write_text("my notes\n", encoding="utf-8")
    calls: list[Path] = []

    def second_fails(skill_dir: Path) -> int:
        calls.append(skill_dir)
        if len(calls) == 2:
            raise PermissionError(13, "Permission denied", str(skill_dir))
        return install_paths.remove_legacy_skill(skill_dir)

    for module in (install_components, install_inventory):
        monkeypatch.setattr(module, "remove_legacy_skill", second_fails)

    result = CliRunner().invoke(main, [*operation.split(), "--scope", scope])

    output = all_output(result)
    assert len(calls) == 2 and set(calls) == {skill, other}, output
    assert "Permission denied" in output, output
    done = calls[0]
    assert not (done / "SKILL.md").exists(), output
    kept = _kept_lines(output)
    assert len(kept) == 1, output
    count, where = _KEPT_LINE.search(kept[0]).groups()
    assert int(count) == 1, kept
    assert where.replace("\\", "/").endswith(f"skills/{done.name}"), kept


def _generator():
    """scripts/gen_shipped_names.py as a module."""
    import importlib.util

    script = Path(__file__).resolve().parents[2] / "scripts" / "gen_shipped_names.py"
    spec = importlib.util.spec_from_file_location("gen_shipped_names", script)
    assert spec and spec.loader
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    return generator


def test_w1_retired_skill_files_module_is_generated_from_the_fixture() -> None:
    """cli/retired_skill_files.py is what the generator renders from the
    shipped-names history; editing either alone fails here."""
    generator = _generator()
    from superclaude.cli import install_paths, retired_skill_files

    rendered = generator.render_retired_skill_files(HISTORY)
    committed = Path(retired_skill_files.__file__).read_text(encoding="utf-8")
    assert committed == rendered, REGENERATE
    assert set(HISTORY["retired_skill_files"]) == set(install_paths.LEGACY_SKILL_NAMES)
    for name, files in HISTORY["retired_skill_files"].items():
        assert {d[:16] for d in files["SKILL.md"]} == {
            d[:16] for d in HISTORY["retired_skill_digests"][name]
        }, (name, REGENERATE)


def test_w1_the_generator_reads_every_parent_of_a_merge(
    tmp_path: Path, monkeypatch, isolated_git_config
) -> None:
    """The history was read along first parents only, so a revision reachable
    only through a merge's second parent (a pull of the public master, a branch
    someone installed from) was missing: confidence-check at c69190a2, four
    SKILL.md files at 0fb95e7f, whose installs kept the whole retired skill."""
    generator = _generator()
    skill = "src/superclaude/skills/old"
    hooks = "src/superclaude/hooks/hooks.json"
    no_hooks = '{"hooks": {}}\n'
    side_hook = json.dumps(
        {
            "hooks": {
                "PreToolUse": [
                    {
                        "hooks": [
                            {"command": "superclaude hook side_guard check"},
                        ]
                    }
                ]
            }
        }
    )
    repo = init_git_repo(
        tmp_path / "repo",
        files={f"{skill}/SKILL.md": "v1\n", f"{skill}/ref.md": "r1\n", hooks: no_hooks},
    )

    def commit(files: dict[str, str | None], message: str) -> None:
        for rel, text in files.items():
            if text is None:
                shutil.rmtree(repo / rel)
                continue
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", message], cwd=repo, check=True)

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)

    git("checkout", "-qb", "side")
    commit(
        {
            f"{skill}/SKILL.md": "v2\n",
            f"{skill}/ref.md": "r2\n",
            "src/superclaude/skills/side-only/SKILL.md": "s\n",
            hooks: side_hook,
        },
        "side",
    )
    commit({"src/superclaude/skills/side-only": None, hooks: no_hooks}, "side back")
    git("checkout", "-q", "main")
    commit({f"{skill}/SKILL.md": "v3\n"}, "main")
    # The merge keeps the first parent's tree: path-limited history
    # simplification drops the side branch as well as --first-parent does.
    git("merge", "-q", "-s", "ours", "side", "-m", "merge side")
    commit({skill: None}, "retire old")
    for kind in generator.DIRS.values():
        (repo / kind).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(generator, "REPO", repo)

    def digests(*texts: str) -> list[str]:
        return sorted(hashlib.sha256(t.encode()).hexdigest() for t in texts)

    assert generator.retired_digests("HEAD", "skills", ["old"]) == {
        "old": digests("v1\n", "v2\n", "v3\n")
    }
    assert generator.retired_skill_files("HEAD", ["old"]) == {
        "old": {
            "SKILL.md": digests("v1\n", "v2\n", "v3\n"),
            "ref.md": digests("r1\n", "r2\n"),
        }
    }
    assert set(generator.collect_names("HEAD")["skills"]) == {"old", "side-only"}
    _events, ids, *_ = generator.collect_hooks("HEAD")
    assert ("PreToolUse", "side_guard", "check") in ids


RETIRED_EVENTS = ("Setup", "TeammateIdle", "TaskCompleted")
USER_SETUP = {"hooks": [{"type": "command", "command": "~/bin/my-setup.sh"}]}
USER_IDLE = {"hooks": [{"type": "command", "command": "echo 'my own idle note'"}]}
SC_ECHOES = (
    "echo 'Teammate idle — assign next task'",
    "echo 'Task completed — aggregate results'",
)
_PENDING_COUNT = re.compile(r"pending-count(?!-)")


def _plant_retired_neighbours(settings: Path, home: Path) -> None:
    """User hooks on the retired events, and the pending-count registration of
    f823f933 → 79032ccc (no captured era carries it)."""
    data = json.loads(settings.read_text(encoding="utf-8"))
    hooks = data.setdefault("hooks", {})
    hooks.setdefault("Setup", []).append(USER_SETUP)
    hooks.setdefault("TeammateIdle", []).append(USER_IDLE)
    scripts = home / ".claude" / "superclaude" / "scripts"
    hooks["SessionStart"].append(
        {
            "matcher": "startup",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {scripts}/insight_writer.py pending-count",
                }
            ],
        }
    )
    settings.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _registrations(settings: Path) -> list[tuple[str, str]]:
    data = json.loads(settings.read_text(encoding="utf-8"))
    return [
        (event, hook["command"])
        for event, array in data.get("hooks", {}).items()
        for entry in array
        for hook in entry.get("hooks", [])
    ]


@pytest.mark.parametrize("force", [False, True], ids=["install", "force"])
@pytest.mark.parametrize("era", ["66b37a7ep-user", "d174e600-user", "77b5821c-project"])
def test_c09_retired_hook_registrations_removed(
    tmp_path: Path, monkeypatch, era: str, force: bool
) -> None:
    """C-09: a non-force install kept `Setup session_init`, `skill_activator`,
    `insight_writer pending-count` and the jq blocker (in a committed project
    file too), and every install kept the unmarked `[experimental]` echoes. The
    user's own hooks on those events stay; superclaude/scripts/ is untouched."""
    home, _project, base = build_legacy_install(tmp_path, era, monkeypatch)
    scope = load_era(era)["scope"]
    settings = settings_path(base, scope)
    _plant_retired_neighbours(settings, home)
    scripts = base / "superclaude" / "scripts"
    scripts_before = snapshot(scripts)

    success, message = install_all(base_path=base, force=force, scope=scope)

    assert success, message
    left = _registrations(settings)
    commands = [command for _event, command in left]
    assert [(e, c) for e, c in left if e in RETIRED_EVENTS and "my" not in c] == [], (
        message
    )
    assert not [c for c in commands if "skill_activator" in c], left
    assert not [c for c in commands if _PENDING_COUNT.search(c)], left
    assert not [c for c in commands if c.startswith("jq ")], left
    assert not [c for c in commands if c in SC_ECHOES], left
    assert ("Setup", USER_SETUP["hooks"][0]["command"]) in left
    assert ("TeammateIdle", USER_IDLE["hooks"][0]["command"]) in left
    assert snapshot(scripts) == scripts_before


def test_c09_uninstall_removes_the_unmarked_echoes(tmp_path: Path, monkeypatch) -> None:
    """The `[experimental]` echoes carried no marker, so uninstall left them."""
    home, _project, base = build_legacy_install(tmp_path, "d174e600-user", monkeypatch)
    _plant_retired_neighbours(base / "settings.json", home)

    success, message = uninstall_all(base_path=base, scope="user")

    assert success, message
    left = _registrations(base / "settings.json")
    assert sorted(left) == sorted(
        [
            ("Setup", USER_SETUP["hooks"][0]["command"]),
            ("TeammateIdle", USER_IDLE["hooks"][0]["command"]),
        ]
    ), message


SERENA = "serena-hooks activate --client=claude-code"


def test_c09_retired_serena_hooks_go_only_when_superclaude_wrote_them(
    tmp_path: Path, monkeypatch
) -> None:
    """6feae043 → 2a404ecd merged Serena's hooks in `[superclaude]` entries; Serena
    now installs the same commands itself, unmarked, and those are not ours."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    data = json.loads((base / "settings.json").read_text(encoding="utf-8"))
    ours = {
        "_comment": "[superclaude] serena-recommended (snapshot 2026-04-27)",
        "matcher": "",
        "hooks": [{"type": "command", "command": SERENA}],
    }
    theirs = {"matcher": "", "hooks": [{"type": "command", "command": SERENA}]}
    data["hooks"]["SessionStart"][:0] = [ours, theirs]
    (base / "settings.json").write_text(json.dumps(data), encoding="utf-8")

    success, message = install_all(base_path=base, force=False, scope="user")

    assert success, message
    after = json.loads((base / "settings.json").read_text(encoding="utf-8"))
    serena = [
        entry
        for entry in after["hooks"]["SessionStart"]
        if any(hook["command"] == SERENA for hook in entry["hooks"])
    ]
    assert serena == [theirs], message


@pytest.mark.parametrize("operation", ["install", "install --force", "uninstall -y"])
def test_c09_a_branch_only_hook_registration_goes(
    tmp_path: Path, monkeypatch, operation: str
) -> None:
    """3362816e registered `test_file_guard check`, reverted 14 minutes later on
    the same branch: only a first-parent walk of the history missed it, and a
    sync from that branch left a hook that now exits 1 on every Edit and Write."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    data = json.loads((base / "settings.json").read_text(encoding="utf-8"))
    command = "superclaude hook test_file_guard check"
    data["hooks"]["PreToolUse"].append(
        {
            "matcher": "Edit|Write",
            "hooks": [
                {
                    "_comment": "[superclaude] safety — blocks Edit/Write on test "
                    "files while `superclaude hook test_file_guard lock` is set",
                    "type": "command",
                    "command": command,
                    "timeout": 5,
                }
            ],
        }
    )
    (base / "settings.json").write_text(json.dumps(data), encoding="utf-8")

    result = CliRunner().invoke(main, [*operation.split(), "--scope", "user"])

    assert result.exit_code == 0, all_output(result)
    settings = base / "settings.json"
    left = _registrations(settings) if settings.exists() else []
    assert ("PreToolUse", command) not in left, all_output(result)


def test_q13_every_retired_hook_identity_is_listed() -> None:
    """Q10/Q13 guard over every hooks.json revision: each event, entry point and
    inline command no longer shipped is retired, or named unsupported (Q14 b)."""
    from superclaude.cli import install_settings

    retired_events = set(getattr(install_settings, "RETIRED_HOOK_EVENTS", ()))
    retired_ids = set(getattr(install_settings, "RETIRED_HOOK_IDS", ()))
    retired_commands = set(getattr(install_settings, "RETIRED_HOOK_COMMANDS", ()))
    digests = set(getattr(install_settings, "RETIRED_HOOK_COMMAND_DIGESTS", ()))
    unsupported = set(getattr(install_settings, "UNSUPPORTED_HOOK_COMMANDS", ()))
    events = {r["event"] for r in HISTORY["hook_events"] if not r["shipped_now"]}
    ids = {
        (r["event"], r["entry_point"], r["subcommand"])
        for r in HISTORY["hook_ids"]
        if not r["shipped_now"]
    }
    shipped_ids = {
        (r["event"], r["entry_point"], r["subcommand"])
        for r in HISTORY["hook_ids"]
        if r["shipped_now"]
    }
    by_digest = {
        hashlib.sha256(r["command"].encode("utf-8")).hexdigest()[:16]: r["command"]
        for r in HISTORY["inline_hook_commands"]
    }
    inline = {command for d, command in by_digest.items() if d not in digests}

    assert digests and digests <= set(by_digest), REGENERATE
    assert events <= retired_events, REGENERATE
    assert ids <= retired_ids, REGENERATE
    assert inline <= retired_commands | unsupported, REGENERATE
    shipped_events = {r["event"] for r in HISTORY["hook_events"] if r["shipped_now"]}
    assert not retired_events & shipped_events
    assert not retired_ids & shipped_ids


# --- C-11: verify-drift and the shared directories (Q9 a) --------------------


def _era_blob(era: str, key: str) -> str:
    return BLOBS[load_era(era)["files"][key]["blob"]]


@pytest.mark.parametrize("scope", SCOPES)
def test_c11_users_own_agents_and_styles_are_not_drift(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """C-11: the user's own agent and style read as EXTRA, so verify-drift
    exited 1 forever on a clean install."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    (base / "agents" / "my-agent.md").write_text("mine\n", encoding="utf-8")
    (base / "output-styles" / "my-style.md").write_text("mine\n", encoding="utf-8")

    result = CliRunner().invoke(main, ["verify-drift", "--scope", scope, "--verbose"])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert "my-agent" not in output and "my-style" not in output, output


def test_c11_retired_superclaude_skill_and_agent_are_reported(
    tmp_path: Path, monkeypatch
) -> None:
    """A stale SC skill dir was invisible (EXTRA was looked for only inside
    shipped skill dirs): it is RETIRED now. An ever-shipped agent name is EXTRA."""
    home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    era = "b933fd65p-user"
    skill = base / "skills" / "using-superclaude" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        _era_blob(era, "$HOME/.claude/skills/using-superclaude/SKILL.md"), "utf-8"
    )
    (base / "agents" / "pm-agent.md").write_text(
        _era_blob(era, "$HOME/.claude/agents/pm-agent.md"), "utf-8"
    )

    result = CliRunner().invoke(main, ["verify-drift", "--scope", "user", "--verbose"])

    output = all_output(result)
    assert result.exit_code == 1, output
    assert "using-superclaude/: RETIRED" in output, output
    assert "pm-agent.md: EXTRA" in output, output


# --- C-10: stale content reads as stale (Q3 a) --------------------------------
#
# A non-force install keeps skip-if-exists, says how many kept files differ and
# how to refresh them; doctor reports drift, missing content, obsolete hook
# registrations and agents pointed at another scope's memory as advisories
# (exit code unchanged); `--list-all` never puts ✅ beside "obsolete".

BASE_CHECKS = ("Hooks in settings.json", "CLAUDE_SC.md", "CLAUDE.md import")
_DIFFER = re.compile(r"(\d+) installed file\(s\) differ")


def _verdicts(result: dict) -> dict[str, bool]:
    return {c["name"]: c["passed"] for c in result["checks"]}


def test_c10_non_force_install_says_how_many_files_differ(
    tmp_path: Path, monkeypatch
) -> None:
    """C-10 / Q3 a: skip semantics stay, and the skipped drift is reported."""
    from superclaude.cli.verify_drift import verify_drift

    _home, _project, base = build_legacy_install(tmp_path, "v4.20.1-user", monkeypatch)

    success, message = install_all(base_path=base, force=False, scope="user")

    assert success, message
    drifted = verify_drift(base)["total_drifted"]
    assert drifted > 0
    lines = [line for line in message.splitlines() if _DIFFER.search(line)]
    assert lines, message
    assert int(_DIFFER.search(lines[0]).group(1)) == drifted, lines
    assert "'superclaude update --scope user'" in lines[0], lines


def test_c10_doctor_advises_on_drift_and_deleted_content(
    tmp_path: Path, monkeypatch
) -> None:
    """C-10: doctor said "healthy" with 76 drifted files and with deleted
    commands. The verdicts stay; an advisory names the count and the refresh."""
    _home, _project, base = build_legacy_install(tmp_path, "v4.20.1-user", monkeypatch)
    install_all(base_path=base, force=False, scope="user")

    result = run_doctor(scope="user")

    assert all(_verdicts(result)[name] for name in BASE_CHECKS), result
    drift = [a for a in result["advisories"] if _DIFFER.search(a)]
    assert drift, result["advisories"]
    assert "'superclaude update --scope user'" in drift[0]

    (base / "commands" / "sc" / "analyze.md").unlink()
    result = run_doctor(scope="user")
    assert any("1 missing" in a for a in result["advisories"]), result["advisories"]


def _plant_registration(base: Path, command: str) -> None:
    data = json.loads((base / "settings.json").read_text(encoding="utf-8"))
    data["hooks"]["UserPromptSubmit"].append(
        {"hooks": [{"type": "command", "command": command}]}
    )
    (base / "settings.json").write_text(json.dumps(data), encoding="utf-8")


def test_c10_obsolete_registration_is_an_advisory_and_not_a_tick(
    tmp_path: Path, monkeypatch
) -> None:
    """C-10: `--list-all` put ✅ on a hooks row that named obsolete entries, and
    doctor was silent about them. (An unknown `superclaude hook` name exits 1,
    which blocks nothing: an advisory.)"""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    _plant_registration(base, "superclaude hook dropped_hook")

    advisories = run_doctor(scope="user")["advisories"]
    listing = CliRunner().invoke(main, ["install", "--list-all", "--scope", "user"])

    assert any("1 obsolete" in a for a in advisories), advisories
    output = all_output(listing)
    row = [line for line in output.splitlines() if "Hooks registered" in line]
    assert row and "✅" not in row[0], output


def test_c10_doctor_fails_on_a_registration_whose_script_is_gone(
    tmp_path: Path, monkeypatch
) -> None:
    """C-10, D1-scripts-gone: a legacy registration whose script copy is gone
    exits 2 in Claude Code, which blocks the prompt; doctor called that healthy."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    _plant_registration(base, f"python3 {base}/superclaude/scripts/skill_activator.py")

    result = run_doctor(scope="user")

    hooks = next(c for c in result["checks"] if c["name"] == "Hooks in settings.json")
    assert not hooks["passed"], hooks
    assert any("skill_activator" in line for line in hooks["details"]), hooks


@pytest.mark.parametrize("scope", ["user", "local"])
def test_c10_update_says_where_pre_rewrite_agent_memory_moves(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """U9: `update` over a pre-v4.20.1 install rewrites `memory: project` to the
    scope, moving where agents keep memory, and said nothing about it."""
    _home, _project, base = build_legacy_install(
        tmp_path, f"ec6fa7e2p-{scope}", monkeypatch
    )
    assert _memory_values(base) == {"memory: project"}

    result = CliRunner().invoke(main, ["update", "--scope", scope])

    output = all_output(result)
    assert result.exit_code == 0, output
    assert _memory_values(base) == {f"memory: {scope}"}
    moved = [line for line in output.splitlines() if "Agent memory moves" in line]
    assert moved and "memory: project" in moved[0], output


def test_c10_doctor_labels_its_advisories(tmp_path: Path, monkeypatch) -> None:
    """The advisory lines say they are advisories, so a passing run reads right."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    (base / "commands" / "sc" / "analyze.md").unlink()

    result = CliRunner().invoke(main, ["doctor", "--scope", "user"])

    output = all_output(result)
    assert "Advisories" in output, output


def test_c10_doctor_names_agents_on_another_scopes_memory(
    tmp_path: Path, monkeypatch
) -> None:
    """C-10: a non-force upgrade from before v4.20.1 keeps `memory: project` on
    every old agent, so agent memory still lands in every project."""
    _home, _project, base = build_legacy_install(
        tmp_path, "ec6fa7e2p-user", monkeypatch
    )
    success, message = install_all(base_path=base, force=False, scope="user")
    assert success, message

    advisories = run_doctor(scope="user")["advisories"]

    memory = [a for a in advisories if "memory: project" in a]
    assert memory, advisories
    assert "'superclaude update --scope user'" in memory[0]


def test_c10_clean_install_has_no_advisory(tmp_path: Path, monkeypatch) -> None:
    _home, _project, _base = fresh_install(tmp_path, monkeypatch, "user")
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)

    assert run_doctor(scope="user")["advisories"] == []


# --- C-12: uninstall leaves no superclaude-made state (Q11 b) ----------------


def test_c12_uninstall_leaves_no_state_superclaude_made(
    tmp_path: Path, monkeypatch
) -> None:
    """C-12: after a fresh user install, uninstall left an empty agent-memory/,
    a CLAUDE.md holding only `# Claude Code Configuration` and a `{}`
    settings.json the install had created."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    assert (base / "agent-memory").is_dir()

    success, message = uninstall_all(base_path=base, scope="user")

    assert success, message
    assert not (base / "agent-memory").exists(), message
    assert not (base / "CLAUDE.md").exists(), message
    assert not (base / "settings.json").exists(), message


def test_c12_uninstall_keeps_what_the_user_put_there(
    tmp_path: Path, monkeypatch
) -> None:
    """Q11 b: a memory dir goes only when empty, CLAUDE.md only when it holds
    nothing but SC's heading, settings.json only when SC's hooks were all of it."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    memory = base / "agent-memory" / "verifier" / "MEMORY.md"
    memory.parent.mkdir(parents=True)
    memory.write_text("learned\n", encoding="utf-8")
    claude_md = base / "CLAUDE.md"
    claude_md.write_text(
        claude_md.read_text(encoding="utf-8") + "\nAlways answer in Korean.\n", "utf-8"
    )
    data = json.loads((base / "settings.json").read_text(encoding="utf-8"))
    data["model"] = "opus"
    (base / "settings.json").write_text(json.dumps(data), encoding="utf-8")

    success, message = uninstall_all(base_path=base, scope="user")

    assert success, message
    assert memory.read_text(encoding="utf-8") == "learned\n"
    assert "Always answer in Korean." in claude_md.read_text(encoding="utf-8")
    assert "CLAUDE_SC" not in claude_md.read_text(encoding="utf-8")
    assert json.loads((base / "settings.json").read_text(encoding="utf-8")) == {
        "model": "opus"
    }


def test_c12_local_uninstall_warns_when_agent_memory_loses_its_exclude(
    tmp_path: Path, monkeypatch
) -> None:
    """C-12: a non-empty agent-memory-local/ stays, and uninstall removes the
    exclude block that hid it, with no warning; git then offers it for commit."""
    _home, project, base = fresh_install(tmp_path, monkeypatch, "local")
    memory = base / "agent-memory-local" / "verifier" / "MEMORY.md"
    memory.parent.mkdir(parents=True)
    memory.write_text("learned\n", encoding="utf-8")
    assert _ignored(project, ".claude/agent-memory-local/verifier/MEMORY.md")

    success, message = uninstall_all(base_path=base, scope="local")

    assert success, message
    assert memory.exists()
    assert not _ignored(project, ".claude/agent-memory-local/verifier/MEMORY.md")
    warning = [
        line
        for line in message.splitlines()
        if line.startswith("⚠️") and "agent-memory-local" in line
    ]
    assert warning, message
    assert "git" in warning[0]


def test_c12_empty_local_memory_store_goes_quietly(tmp_path: Path, monkeypatch) -> None:
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "local")

    success, message = uninstall_all(base_path=base, scope="local")

    assert success, message
    assert not (base / "agent-memory-local").exists(), message
    assert "⚠️" not in message


# --- C-20: the CLAUDE file keeps every byte outside superclaude's block -------

# What `remove_claude_md_import` used to normalise: Windows line endings (the
# whole file came back LF), runs of blank lines (collapsed to one) and blank
# edges (stripped).
C20_TEXTS = {
    "crlf": "# Team notes\r\n\r\n\r\nkeep the run above\r\n",
    "blank-runs": "\n\n# Team notes\n\n\n\nkeep the run above\n\n\n",
    "no-final-newline": "# Team notes\nlast line, no newline",
}


def _import_line(scope: str) -> str:
    return "@.claude/superclaude/CLAUDE_SC.md" if scope == "local" else CLAUDE_SC_IMPORT


@pytest.mark.parametrize("layout", list(C20_TEXTS))
@pytest.mark.parametrize("scope", SCOPES)
def test_c20_install_appends_only_its_block_and_uninstall_removes_only_it(
    tmp_path: Path, monkeypatch, scope: str, layout: str
) -> None:
    """C-20: install rewrote a CRLF file as LF; uninstall collapsed blank-line
    runs and stripped both edges. The block goes in the file's own line ending,
    and uninstall takes back exactly that block. A file without a final newline
    keeps the one the import line needed: uninstall cannot tell it from the
    user's own."""
    home, project = sandbox(tmp_path, monkeypatch)
    base = scope_base(home, project, scope)
    target = claude_path(base, scope)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = C20_TEXTS[layout]
    target.write_bytes(text.encode("utf-8"))
    nl = "\r\n" if "\r\n" in text else "\n"
    joined = (text if text.endswith("\n") else text + nl).encode("utf-8")

    success, message = install_all(base_path=base, force=False, scope=scope)

    assert success, message
    block = f"{nl}# superclaude{nl}{_import_line(scope)}{nl}".encode("utf-8")
    assert target.read_bytes() == joined + block

    success, message = uninstall_all(base_path=base, scope=scope)

    assert success, message
    assert target.read_bytes() == joined


def _c20_removals(import_line: str) -> list[tuple[str, str, str]]:
    """(id, before, after) for an import removal that touches nothing else."""
    block = f"\n# superclaude\n{import_line}\n"
    middle = f"a\n\n\n{block[1:]}\n\nb\n"
    return [
        ("block-mid-file", middle, middle.replace(block, "", 1)),
        ("import-alone-crlf", f"{import_line}\r\n\r\nMy notes\r\n", "\r\nMy notes\r\n"),
        (
            "old-heading-crlf",
            f"# Mine\r\n\r\n# SuperClaude Framework\r\n{import_line}\r\n",
            "# Mine\r\n",
        ),
        (
            "trailing-spaces-kept",
            f"a  \n\n# superclaude\n{import_line}\nb \n",
            "a  \nb \n",
        ),
    ]


@pytest.mark.parametrize("scope", ["user", "local"])
def test_c20_import_removal_touches_no_other_line(tmp_path: Path, scope: str) -> None:
    import_line = _import_line(scope)
    base = tmp_path / ".claude"
    base.mkdir()
    target = claude_path(base, scope)
    for case, before, after in _c20_removals(import_line):
        target.write_bytes(before.encode("utf-8"))

        success, message = remove_claude_md_import(base, scope=scope)

        assert success, (case, message)
        assert target.read_bytes() == after.encode("utf-8"), case


def test_c20_heading_only_crlf_file_still_goes(tmp_path: Path) -> None:
    """The file install created, saved by an editor with CRLF, is still superclaude's."""
    base = tmp_path / ".claude"
    base.mkdir()
    claude_md = base / "CLAUDE.md"
    claude_md.write_bytes(
        f"# Claude Code Configuration\r\n\r\n# superclaude\r\n{CLAUDE_SC_IMPORT}\r\n".encode()
    )

    success, message = remove_claude_md_import(base, scope="user")

    assert success, message
    assert not claude_md.exists(), message


# --- C-21: settings writes keep mode and layout, and refuse a read-only file --

# Layouts an editor or Claude Code's own settings UI leaves: each must come back
# byte-for-byte after install and uninstall (I2 check c and d).
C21_LAYOUTS = {
    "two-space-newline": '{\n  "model": "opus"\n}\n',
    "four-space-no-newline": '{\n    "model": "opus"\n}',
    "tabs-crlf": '{\r\n\t"model": "opus"\r\n}\r\n',
    "one-line": '{"model": "opus"}',
    "non-ascii": '{\n  "statusLine": {\n    "command": "echo 안녕"\n  }\n}\n',
    "escaped": '{\n  "statusLine": {\n    "command": "echo \\uc548\\ub155"\n  }\n}\n',
}
_INDENT = re.compile(r'\n([ \t]+)"')
_not_root = pytest.mark.skipif(
    getattr(os, "geteuid", lambda: 1)() == 0, reason="root ignores file modes"
)
_posix_modes = pytest.mark.skipif(
    sys.platform == "win32", reason="Windows has only the read-only bit"
)


@pytest.mark.parametrize("layout", list(C21_LAYOUTS))
@pytest.mark.parametrize("scope", SCOPES)
def test_c21_settings_keep_their_layout_across_install_and_uninstall(
    tmp_path: Path, monkeypatch, scope: str, layout: str
) -> None:
    """C-21: every settings write re-serialised the file (two-space, LF, no
    trailing newline, ASCII escapes), so install dirtied a committed file and
    uninstall never gave the original bytes back."""
    home, project = sandbox(tmp_path, monkeypatch)
    base = scope_base(home, project, scope)
    settings = settings_path(base, scope)
    settings.parent.mkdir(parents=True, exist_ok=True)
    original = C21_LAYOUTS[layout].encode("utf-8")
    settings.write_bytes(original)

    success, message = install_all(base_path=base, force=False, scope=scope)

    assert success, message
    installed = settings.read_bytes()
    assert json.loads(installed.decode("utf-8")).get("hooks"), installed
    assert installed.endswith(b"\n") == original.endswith(b"\n"), installed
    assert (b"\r\n" in installed) == (b"\r\n" in original), installed
    indent = _INDENT.search(original.decode("utf-8"))
    if indent:
        assert _INDENT.search(installed.decode("utf-8")).group(1) == indent.group(1)
    else:
        assert b"\n" not in installed.rstrip(b"\r\n"), installed
    assert installed.isascii() == original.isascii(), installed

    success, message = uninstall_all(base_path=base, scope=scope)

    assert success, message
    assert settings.read_bytes() == original


@_posix_modes
@pytest.mark.parametrize("scope", SCOPES)
def test_c21_settings_keep_their_permission_mode(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """C-21: the atomic write left every settings file 0600 (mkstemp), whatever
    mode the user's file had; a new one gets what a plain open() would."""
    home, project = sandbox(tmp_path, monkeypatch)
    base = scope_base(home, project, scope)
    settings = settings_path(base, scope)
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text('{"model": "opus"}\n', encoding="utf-8")
    settings.chmod(0o640)

    success, message = install_all(base_path=base, force=False, scope=scope)

    assert success, message
    assert stat.S_IMODE(settings.stat().st_mode) == 0o640

    success, message = uninstall_all(base_path=base, scope=scope)

    assert success, message
    assert stat.S_IMODE(settings.stat().st_mode) == 0o640


@_posix_modes
def test_c21_a_new_settings_file_gets_the_umask_mode(
    tmp_path: Path, monkeypatch
) -> None:
    _home, _project, base = fresh_install(tmp_path, monkeypatch, "user")
    umask = os.umask(0)
    os.umask(umask)

    assert stat.S_IMODE((base / "settings.json").stat().st_mode) == 0o666 & ~umask


RO_COMMANDS = {
    "install": ["install"],
    "update": ["update"],
    "uninstall": ["uninstall", "-y"],
    "uninstall-dry-run": ["uninstall", "--dry-run"],
}


def _edited_file(tmp_path: Path, base: Path, scope: str, which: str) -> Path:
    """The scope's settings, CLAUDE or git exclude file: the files a command edits."""
    from superclaude.cli.install_settings import _claude_md_target

    if which == "settings":
        return settings_path(base, scope)
    if which == "claude":
        return _claude_md_target(base, scope)[0]
    return tmp_path / "project" / ".git" / "info" / "exclude"


RO_FILES = [
    (which, scope)
    for which in ("settings", "claude", "exclude")
    for scope in SCOPES
    if which != "exclude" or scope != "user"
]


@_not_root
@pytest.mark.parametrize("command", list(RO_COMMANDS))
@pytest.mark.parametrize(("which", "scope"), RO_FILES)
def test_c21_a_read_only_input_file_is_refused_before_any_write(
    tmp_path: Path, monkeypatch, command: str, which: str, scope: str
) -> None:
    """C-21 (E2-ro-settings): a 0444 settings file was replaced with exit 0, the
    temp-file rename never asking the file. Refused like the other input
    preflights: exit 1, the file named, nothing written or deleted. The CLAUDE
    file and the git exclude file the same (06c Y-3): a 0444 CLAUDE.md passed
    the preflight and install wrote 117 files, then died on a traceback."""
    if command == "install":
        home, project = sandbox(tmp_path, monkeypatch)
        base = scope_base(home, project, scope)
        target = _edited_file(tmp_path, base, scope, which)
        target.parent.mkdir(parents=True, exist_ok=True)
        if which == "settings":
            target.write_text('{"model": "opus"}\n', encoding="utf-8")
        elif which == "claude":
            target.write_text(CLAUDE_TEXT, encoding="utf-8", newline="")
        else:
            target.write_text("*.swp\n", encoding="utf-8")
    else:
        _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
        target = _edited_file(tmp_path, base, scope, which)
    assert target.is_file()
    target.chmod(0o444)
    before = snapshot(tmp_path)

    result = CliRunner().invoke(main, [*RO_COMMANDS[command], "--scope", scope])

    output = all_output(result)
    assert result.exception is None or isinstance(result.exception, SystemExit), output
    assert result.exit_code == 1, output
    assert target.name in output and "read-only" in output, output
    assert snapshot(tmp_path) == before
    assert stat.S_IMODE(target.stat().st_mode) == 0o444


@_not_root
@pytest.mark.parametrize("scope", SCOPES)
def test_c21_doctor_passes_on_a_read_only_settings_file(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """doctor writes nothing, so a file install would refuse to edit is healthy to it."""
    _home, _project, base = fresh_install(tmp_path, monkeypatch, scope)
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    settings_path(base, scope).chmod(0o444)

    result = run_doctor(scope=scope)

    assert result["passed"], result["checks"]


_symlinks = pytest.mark.skipif(
    sys.platform == "win32", reason="symlinks need a privilege on Windows"
)


@_symlinks
@pytest.mark.parametrize("scope", SCOPES)
def test_c21_a_symlinked_settings_file_stays_a_symlink(
    tmp_path: Path, monkeypatch, scope: str
) -> None:
    """06c Y-1: the atomic write renamed its temp file over the link, so a
    settings file a dotfiles manager symlinks (stow, chezmoi) became a plain
    file holding the hooks and the repository copy never got them. The write
    now goes to the link's target and the link stays."""
    home, project = sandbox(tmp_path, monkeypatch)
    base = scope_base(home, project, scope)
    settings = settings_path(base, scope)
    settings.parent.mkdir(parents=True, exist_ok=True)
    target = tmp_path / "dotfiles" / "claude" / settings.name
    target.parent.mkdir(parents=True)
    original = '{\n\t"model": "opus"\n}\n'.encode("utf-8")
    target.write_bytes(original)
    target.chmod(0o640)
    settings.symlink_to(target)

    success, message = install_all(base_path=base, force=False, scope=scope)

    assert success, message
    assert settings.is_symlink() and settings.resolve() == target.resolve()
    installed = target.read_bytes()
    assert json.loads(installed.decode("utf-8")).get("hooks"), installed
    assert b'\n\t"' in installed and installed.endswith(b"\n"), installed
    assert stat.S_IMODE(target.stat().st_mode) == 0o640
    assert [p.name for p in settings.parent.iterdir() if p.suffix == ".tmp"] == []

    success, message = uninstall_all(base_path=base, scope=scope)

    assert success, message
    assert settings.is_symlink()
    assert target.read_bytes() == original


@_symlinks
def test_c21_atomic_write_text_writes_through_a_symlink(tmp_path: Path) -> None:
    """The temp file is made next to the target, so the rename stays on one
    filesystem, and the link is what the caller finds afterwards."""
    from superclaude.utils import atomic_write_text

    target = tmp_path / "store" / "settings.json"
    target.parent.mkdir()
    target.write_text("{}", encoding="utf-8")
    target.chmod(0o600)
    link = tmp_path / "live" / "settings.json"
    link.parent.mkdir()
    link.symlink_to(target)

    atomic_write_text(link, '{"a": 1}\n')

    assert link.is_symlink() and link.readlink() == target
    assert target.read_text(encoding="utf-8") == '{"a": 1}\n'
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert sorted(p.name for p in link.parent.iterdir()) == ["settings.json"]
    assert sorted(p.name for p in target.parent.iterdir()) == ["settings.json"]
