"""
Session memory lives in the committed project folder `.claude/memories/`.

/sc:save and /sc:load read and write plain markdown files there plus Claude
auto memory; no memory-server tool calls remain. The folder must stay out of
SuperClaude's git-exclude block so the memories are committed.
"""

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


@pytest.mark.parametrize("scope", ["local", "project"])
def test_memory_folder_is_not_git_excluded(scope: str) -> None:
    probe = ".claude/memories/probe.md"
    for entry in _collect_entries(scope):
        if entry.endswith("/"):
            covered = probe.startswith(entry)
        else:
            covered = probe == entry
        assert not covered, f"{scope} exclude entry {entry!r} hides {probe}"
