"""
Session memory lives in the committed project folder `.claude/memories/`.

/sc:save and /sc:load read and write plain markdown files there plus Claude
auto memory; no memory-server tool calls remain. The folder must stay out of
superclaude's git-exclude block so the memories are committed.

Session state goes into an add-only record named by date, machine and branch.
A fixed-name file that every save overwrites conflicts on merge as soon as two
branches or worktrees both save, so no writer may name one. The machine part
keeps two computers on one branch apart on the same day: without it both
updated the same `session_<date>_<branch>.md`
(docs/features/session-memory-multi-machine).
"""

import re
from pathlib import Path

import pytest

from superclaude.cli.install_git_exclude import _collect_entries

SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
SAVE = SRC / "commands" / "save.md"
LOAD = SRC / "commands" / "load.md"

MEMORY_FOLDER = ".claude/memories/"
SESSION_RECORD = "session_[date]_[host-slug]_[branch-slug].md"
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


def test_save_writes_a_branch_scoped_session_record() -> None:
    assert f"{MEMORY_FOLDER}{SESSION_RECORD}" in _read(SAVE)


def test_load_reads_the_record_save_writes() -> None:
    # Old records (no machine part) end in `_[branch-slug].md` too, so one
    # glob reads both.
    assert SESSION_RECORD_GLOB in _flow_step(LOAD, LOAD_MEMORY_STEP)


def test_save_defines_the_host_slug() -> None:
    storage = _read(SAVE).split("<storage>", 1)[1].split("</storage>", 1)[0]
    line = next(
        (ln for ln in storage.splitlines() if ln.strip().startswith("Host slug:")),
        "",
    )
    assert "`hostname`" in line and "[a-z0-9]" in line, (
        "save.md <storage> must define the Host slug from `hostname`"
    )


def test_load_reads_every_machine_record_of_the_newest_date() -> None:
    assert "one per machine" in _flow_step(LOAD, LOAD_MEMORY_STEP)


def _first_flow_step(path: Path) -> str:
    flow = _read(path).split("<flow>", 1)[1].split("</flow>", 1)[0]
    return next(ln.strip() for ln in flow.splitlines() if ln.strip().startswith("1."))


def test_load_starts_with_a_sync_step_that_asks_before_pulling() -> None:
    # Two machines share the records through git: loading before a pull reads
    # the other machine's state from before its last push.
    step = _first_flow_step(LOAD)
    assert step.startswith("1. Sync:"), step
    # Prompts off in both shells: a fetch waiting on a credential prompt would
    # hang every /sc:load and /sc:save until the shell tool timed out.
    for token in (
        "fetch --quiet",
        "git pull --ff-only",
        "[y/n]",
        # On the fetch command itself: a separate `GIT_TERMINAL_PROMPT=0;`
        # statement is not exported in bash, and the prompt still appears.
        "`GIT_TERMINAL_PROMPT=0 git -c credential.interactive=never fetch --quiet`",
        "`$env:GIT_TERMINAL_PROMPT=0; git -c credential.interactive=never fetch --quiet`",
    ):
        assert token in step, f"load.md Sync step lacks {token!r}"


# A bare @{u} is a hashtable literal to PowerShell, and a partly quoted
# '@{u}'...HEAD reaches git as two arguments (usage error, exit 129; seen
# 2026-10-21). Only a whole argument in single quotes works in PowerShell and
# a POSIX shell alike.
_QUOTED_UPSTREAM_ARG = re.compile(r"'[^'\s]*@\{u\}[^'\s]*'(?=[\s`;)]|$)")


@pytest.mark.parametrize(
    ("path", "label"),
    [(LOAD, "Sync"), (SAVE, "Share")],
    ids=["load-sync", "save-share"],
)
def test_upstream_ref_is_quoted(path: Path, label: str) -> None:
    step = _flow_step(path, label)
    assert "@{u}" in step, f"{path.name} {label} step names no upstream ref"
    quoted = len(_QUOTED_UPSTREAM_ARG.findall(step))
    assert quoted == step.count("@{u}"), (
        f"{path.name} {label}: {step.count('@{u}')} upstream refs, "
        f"{quoted} quoted as a whole argument"
    )


def test_save_starts_with_the_load_sync_step() -> None:
    # One definition: save points at load's Sync step instead of restating it,
    # and names the installed file, since /sc:save may run without /sc:load.
    step = _first_flow_step(SAVE)
    assert step.startswith("1. Sync:"), step
    assert "the /sc:load Sync step" in step, step
    assert "commands/sc/load.md" in step, step


def test_save_offers_to_share_and_never_pushes_unasked() -> None:
    step = _flow_step(SAVE, "Share")
    assert step, "save.md has no Share step"
    for token in ("git push", "memory files only", "only those files"):
        assert token in step, f"save.md Share step lacks {token!r}"
    # One yes for the commit, a second one for the push.
    assert step.count("[y/n]") >= 2, step
    # The pathspec on the commit itself keeps whatever else was staged out;
    # `git add -- <files>` alone would leave a bare `git commit` passing.
    assert re.search(r"git commit [^`]*-- <files>`", step), step
    # Git refuses a partial commit during a merge or cherry-pick; during a
    # conflicted revert it makes one and silently drops the revert state.
    assert "a merge, cherry-pick or revert in progress" in step, step
    # Those cases are ruled out before the first question, not after a yes.
    assert step.index("in progress") < step.index("[y/n]"), step


def test_share_runs_after_every_step_that_writes() -> None:
    # Checkpoint and Validate still write or fix memory files; a Share before
    # them commits and pushes an incomplete, unvalidated set.
    flow = _read(SAVE).split("<flow>", 1)[1].split("</flow>", 1)[0]
    top = [ln.strip() for ln in flow.splitlines() if re.match(r"^\s*\d+\.\s", ln)]
    assert top[-1].startswith(f"{len(top)}. Share:"), top[-1]


def test_save_never_edits_another_machines_record() -> None:
    assert "a record another machine wrote is never edited" in _flow_step(
        SAVE, "Persist (memory folder)"
    )


def test_load_takes_the_branch_from_the_record_header() -> None:
    # A branch slug may hold `_` (`fix_x`), so the filename alone can misread
    # machine and branch; the `branch:` first line settles it, both before the
    # newest date is chosen and in the any-branch fallback.
    step = _flow_step(LOAD, LOAD_MEMORY_STEP)
    filter_at = step.find("whose `branch:` line names the current branch")
    newest_at = step.find("has the newest date")
    assert 0 <= filter_at < newest_at, step
    assert "reported as the branch its `branch:` line names" in step, step
    # Filtering every day's record of the branch must not Read them whole.
    assert "Grep `^branch:`" in step, step


@pytest.mark.parametrize("path", [SAVE, LOAD], ids=["save", "load"])
def test_no_fixed_name_session_file(path: Path) -> None:
    text = _read(path)
    for name in OVERWRITTEN_NAMES:
        assert name not in text, f"{path.name} still names {name!r}"


LOAD_MEMORY_STEP = "Load (memory folder)"


def _flow_step(path: Path, label: str) -> str:
    """The `N. <label>: ...` line of the command's <flow>, found by label so a
    step added in front does not move it."""
    flow = _read(path).split("<flow>", 1)[1].split("</flow>", 1)[0]
    pattern = re.compile(rf"^\d+(?:\.\d+)?\.\s+{re.escape(label)}:")
    return next(
        (line.strip() for line in flow.splitlines() if pattern.match(line.strip())),
        "",
    )


def _load_flow_step_keys() -> list[str]:
    match = re.search(r"Read (.*?) when present", _flow_step(LOAD, LOAD_MEMORY_STEP))
    if match is None:
        return []
    return [key.strip() for key in match.group(1).split(",") if key.strip()]


def test_every_key_load_reads_has_a_writer() -> None:
    # Fixed-name keys load.md reads must be written by /sc:save; the retired
    # project-manager agent was the only writer of pm_context, so load.md
    # stopped reading it (docs/features/agent-roster-audit).
    keys = _load_flow_step_keys()
    assert keys, (
        "load.md Load (memory folder) step names no keys between 'Read ' and "
        "' when present'"
    )
    save = _read(SAVE)
    missing = [key for key in keys if f"{MEMORY_FOLDER}{key}.md" not in save]
    assert not missing, f"load.md reads keys save.md does not write: {missing}"


@pytest.mark.parametrize("scope", ["local", "project"])
def test_memory_folder_is_not_git_excluded(scope: str) -> None:
    probe = ".claude/memories/probe.md"
    for entry in _collect_entries(scope):
        if entry.endswith("/"):
            covered = probe.startswith(entry)
        else:
            covered = probe == entry
        assert not covered, f"{scope} exclude entry {entry!r} hides {probe}"
