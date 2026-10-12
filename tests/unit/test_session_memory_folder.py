"""
Session memory lives in the committed project folder `.claude/memories/`.

/sc:save and /sc:load read and write plain markdown files there plus Claude
auto memory; no memory-server tool calls remain. The folder must stay out of
SuperClaude's git-exclude block so the memories are committed.

Session state goes into an add-only record named by date and branch. A
fixed-name file that every save overwrites conflicts on merge as soon as two
branches or worktrees both save, so no writer may name one.
"""

import re
from pathlib import Path

import pytest

from superclaude.cli.install_git_exclude import _collect_entries

SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
SAVE = SRC / "commands" / "save.md"
LOAD = SRC / "commands" / "load.md"
PROJECT_MANAGER = SRC / "agents" / "project-manager.md"

MEMORY_FOLDER = ".claude/memories/"
SESSION_RECORD = "session_[date]_[branch-slug].md"
SESSION_RECORD_GLOB = "session_*_[branch-slug].md"
# Fixed-name files every save used to overwrite.
OVERWRITTEN_NAMES = ("last_session", "next_actions")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", [SAVE, LOAD], ids=["save", "load"])
def test_save_and_load_name_the_memory_folder(path: Path) -> None:
    assert MEMORY_FOLDER in _read(path)


@pytest.mark.parametrize("path", [SAVE, LOAD], ids=["save", "load"])
def test_save_and_load_use_no_memory_server_tools(path: Path) -> None:
    text = _read(path)
    for token in (
        "write_memory",
        "read_memory",
        "list_memories",
        "onboarding()",
        ".serena",
    ):
        assert token not in text, f"{path.name} still mentions {token!r}"


def test_project_manager_session_keys_live_in_memory_folder() -> None:
    text = _read(PROJECT_MANAGER)
    assert MEMORY_FOLDER in text
    for key in ("pm_context", SESSION_RECORD.removesuffix(".md")):
        assert key in text, f"project-manager.md lost the {key!r} key"


def test_save_writes_a_branch_scoped_session_record() -> None:
    assert f"{MEMORY_FOLDER}{SESSION_RECORD}" in _read(SAVE)


def test_project_manager_session_end_writes_the_same_record() -> None:
    assert f"{MEMORY_FOLDER}{SESSION_RECORD}" in _project_manager_session_end()


def test_load_reads_the_record_save_writes() -> None:
    assert SESSION_RECORD_GLOB in _load_flow_step_one()


@pytest.mark.parametrize(
    "path", [SAVE, LOAD, PROJECT_MANAGER], ids=["save", "load", "project-manager"]
)
def test_no_fixed_name_session_file(path: Path) -> None:
    text = _read(path)
    for name in OVERWRITTEN_NAMES:
        assert name not in text, f"{path.name} still names {name!r}"


def _load_flow_step_one() -> str:
    flow = _read(LOAD).split("<flow>", 1)[1].split("</flow>", 1)[0]
    return next(
        line.strip() for line in flow.splitlines() if line.strip().startswith("1.")
    )


def _load_flow_step_one_keys() -> list[str]:
    match = re.search(r"Read (.*?) when present", _load_flow_step_one())
    if match is None:
        return []
    return [key.strip() for key in match.group(1).split(",") if key.strip()]


def _project_manager_session_end() -> str:
    # Up to the next sentence start (". " + capital) or the end of the line, so
    # an abbreviation such as "e.g." inside the sentence does not cut it short.
    match = re.search(r"Session end:.*?(?=\.\s+[A-Z]|$)", _read(PROJECT_MANAGER), re.M)
    return match.group(0) if match else ""


def test_every_key_load_reads_has_a_writer() -> None:
    # Fixed-name keys are project state only the project-manager agent writes.
    keys = _load_flow_step_one_keys()
    assert keys, (
        "load.md <flow> step 1 names no keys between 'Read ' and ' when present'"
    )
    session_end = _project_manager_session_end()
    missing = [key for key in keys if f"{MEMORY_FOLDER}{key}.md" not in session_end]
    assert not missing, (
        f"load.md reads keys project-manager.md Session end does not write: {missing}"
    )


@pytest.mark.parametrize("scope", ["local", "project"])
def test_memory_folder_is_not_git_excluded(scope: str) -> None:
    probe = ".claude/memories/probe.md"
    for entry in _collect_entries(scope):
        if entry.endswith("/"):
            covered = probe.startswith(entry)
        else:
            covered = probe == entry
        assert not covered, f"{scope} exclude entry {entry!r} hides {probe}"
