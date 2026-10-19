"""Upgrade scenarios built from captured legacy installs (install/upgrade audit).

Each ``tests/fixtures/legacy_installs/<era>.json`` records what a real old
installer left on disk, captured once from a sandbox run of that release
(docs/features/install-upgrade-audit/02-scenarios.md). Content the installer
reads — agents, SKILL.md, settings, CLAUDE files, exclude files — is kept as
exact text in ``_blobs.json``; everything else is a sha256 the builder writes as
a stub. Machine paths are tokens: ``$HOME``, ``$PROJECT``, ``$PYTHON``,
``$UVCACHE``. No network, no git history: the fixtures are the history.

The defects the audit found are pinned here by ID, each test written red
before its fix (docs/features/install-upgrade-audit/03-findings.md).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from superclaude.cli import install_mcp
from superclaude.cli.doctor import run_doctor
from superclaude.cli.install_components import install_all
from superclaude.cli.install_git_exclude import add_git_exclude, remove_git_exclude
from superclaude.cli.install_inventory import uninstall_all
from superclaude.cli.install_paths import shipped_names
from superclaude.cli.install_settings import remove_claude_md_import
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


def build_legacy_install(
    tmp_path: Path, era: str, monkeypatch
) -> tuple[Path, Path, Path]:
    """Lay out ``era``'s captured install under ``tmp_path``; return (home, project, base)."""
    doc = load_era(era)
    home, project = sandbox(tmp_path, monkeypatch)
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
