"""
Session memory lives in the committed project folder `.claude/memories/`.

/sc:save and /sc:load read and write plain markdown files there plus Claude
auto memory; no memory-server tool calls remain. The folder must stay out of
SuperClaude's git-exclude block so the memories are committed.
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
    for key in ("pm_context", "last_session", "next_actions"):
        assert key in text, f"project-manager.md lost the {key!r} key"


def _load_flow_step_one_keys() -> list[str]:
    text = _read(LOAD)
    flow = text.split("<flow>", 1)[1].split("</flow>", 1)[0]
    step = next(
        line.strip() for line in flow.splitlines() if line.strip().startswith("1.")
    )
    match = re.search(r"Read (.*?) when present", step)
    if match is None:
        return []
    return [key.strip() for key in match.group(1).split(",") if key.strip()]


def _project_manager_session_end() -> str:
    # Up to the next sentence start (". " + capital) or the end of the line, so
    # an abbreviation such as "e.g." inside the sentence does not cut it short.
    match = re.search(r"Session end:.*?(?=\.\s+[A-Z]|$)", _read(PROJECT_MANAGER), re.M)
    return match.group(0) if match else ""


# Keys only the project-manager agent writes; /sc:save writes every other key
# /sc:load reads by name.
PROJECT_MANAGER_ONLY_KEYS = {"pm_context"}


def test_every_key_load_reads_has_a_writer() -> None:
    keys = _load_flow_step_one_keys()
    assert keys, (
        "load.md <flow> step 1 names no keys between 'Read ' and ' when present'"
    )
    save_text = _read(SAVE)
    session_end = _project_manager_session_end()
    missing = [
        f"{key} (save.md)"
        for key in keys
        if key not in PROJECT_MANAGER_ONLY_KEYS
        and f"{MEMORY_FOLDER}{key}.md" not in save_text
    ] + [
        f"{key} (project-manager.md Session end)"
        for key in keys
        if key in PROJECT_MANAGER_ONLY_KEYS
        and f"{MEMORY_FOLDER}{key}.md" not in session_end
    ]
    assert not missing, f"load.md reads keys their owner does not write: {missing}"


@pytest.mark.parametrize("scope", ["local", "project"])
def test_memory_folder_is_not_git_excluded(scope: str) -> None:
    probe = ".claude/memories/probe.md"
    for entry in _collect_entries(scope):
        if entry.endswith("/"):
            covered = probe.startswith(entry)
        else:
            covered = probe == entry
        assert not covered, f"{scope} exclude entry {entry!r} hides {probe}"
