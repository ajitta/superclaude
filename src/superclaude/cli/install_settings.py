"""
Settings, Hooks & CLAUDE.md Management for superclaude Installation

Handles settings.json merge/unmerge, hook identification, and CLAUDE.md import management.
This is a leaf dependency with no internal imports.
"""

import codecs
import copy
import functools
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from superclaude.utils import (
    CONSOLE_HOOK_RE,
    SUPERCLAUDE_HOOK_MARKERS,
    UNMARKED_SC_HOOK_COMMANDS,
    atomic_write_json,
    is_legacy_hook_command,
    is_superclaude_hook,
    is_superclaude_inner_hook,
    settings_filename,
)

# Import line to add to CLAUDE.md
CLAUDE_SC_IMPORT = "@superclaude/CLAUDE_SC.md"

# The import every release wrote, as a whole line — `@superclaude/CLAUDE_SC.md`
# (user, project) or `@.claude/superclaude/CLAUDE_SC.md` (local), either path
# separator — with the heading above it ("# SuperClaude Framework" in older
# releases). Anchored to the line: matching `@superclaude/` anywhere deleted a
# user's text from that point on (`docs@superclaude/wiki and stays.` → `docs`).
SC_IMPORT_RE = re.compile(
    r"^(?:# (?:SuperClaude Framework|superclaude)\n)?"
    r"@(?:\.claude[/\\])?superclaude[/\\]CLAUDE_SC\.md[ \t]*(?:\n|\Z)",
    re.MULTILINE,
)

# Entry point of a legacy `<interpreter> <dir>/<name>.py [subcommand]` command
# (releases before the console entry). The current form is
# utils.CONSOLE_HOOK_RE. Both capture the bare name, so a hook registered
# under the old form and shipped under the new one is the same hook.
_HOOK_SCRIPT_RE = re.compile(r"([A-Za-z0-9_]+)\.py(?=\s|$)(.*)$")
# What may follow the entry point and count as its subcommand: a bare word such
# as `harvest-from-hook`. An option (`--quiet`) and a shell operator or
# redirection (`|`, `&&`, `2>>log`) are not subcommands — a user who wraps our
# command in a pipeline still runs the same hook.
_SUBCOMMAND_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*")

# Hook registrations a release shipped and this one does not (Q13). Install —
# force or not — and uninstall remove a superclaude inner hook that matches:
# skip-if-registered kept these forever, still running script copies under
# superclaude/scripts/ that exit 2, the blocking code, once they are gone. A
# user's own hook on the same event is never touched. Every identity the full
# history (tests/fixtures/shipped_names_history.json) marks as no longer
# shipped is in one of these lists, by digest in RETIRED_HOOK_COMMAND_DIGESTS
# or in UNSUPPORTED_HOOK_COMMANDS; a test fails otherwise.
RETIRED_HOOK_EVENTS = ("Setup", "TaskCompleted", "TeammateIdle")
# (event, entry point, subcommand), as _hook_script_id reads a command.
RETIRED_HOOK_IDS = (
    # 3362816e, reverted on its branch (c147b80c) before the merge
    ("PreToolUse", "test_file_guard", "check"),
    ("SessionStart", "insight_writer", "pending-count"),
    ("Setup", "session_init", ""),
    ("UserPromptSubmit", "skill_activator", ""),
)
# Inline commands, matched whole.
RETIRED_HOOK_COMMANDS = (
    # the jq destructive blockers, replaced by `destructive_guard`
    "jq -r '.tool_input.command // empty' | head -1 | grep -qE "
    r"'rm\s+-rf\s+/\s*$|rm\s+-rf\s+/\*|git\s+push\s+.*--force([^-]|$).*(main|master)'"
    " && echo 'BLOCKED: destructive command detected (--force-with-lease is "
    "allowed)' >&2 && exit 2 || exit 0",
    "jq -r '.tool_input.command // empty' | head -1 | grep -qE "
    r"'rm\s+-rf\s+/\s*$|rm\s+-rf\s+/\*|git\s+push\s+.*--force.*(main|master)'"
    " && echo 'BLOCKED: destructive command detected' >&2 && exit 2 || exit 0",
    # the agent-team echoes
    *UNMARKED_SC_HOOK_COMMANDS,
    "echo '[superclaude] Teammate idle — assign next task'",
    "echo '[superclaude] Task completed — aggregate results'",
)
# The four commands of the second hooks file, hooks/<server>-hooks.json
# (6feae043 → 2a404ecd), which that MCP server's own CLI installs now. Ours only inside a `[superclaude]`
# entry; the same command elsewhere is the server's or the user's. Matched by
# digest (sha256 of the command, first 16 hex digits) because shipped content
# names no MCP server (test_shipped_content_server_neutral.py).
RETIRED_HOOK_COMMAND_DIGESTS = (
    "10956d2eb9974a3b",
    "6930138fca49261e",
    "7c637e399af28226",
    "c6592748289cf003",
)
# The 81343a67 → dc6e0866 hooks.json forms: relative script paths and a bare
# prettier pipeline, never attributable to superclaude once in a settings file
# (`./scripts/session-init.sh` may well be the user's). Unsupported, like the
# one-day `.claude/hooks/<x>.py` era (Q14 b); the CHANGELOG upgrade note says
# how to remove them by hand.
UNSUPPORTED_HOOK_COMMANDS = (
    "./scripts/session-init.sh",
    "./scripts/skill-activator.sh",
    "jq -r '.tool_input.file_path' | xargs -I {} sh -c 'echo \"{}\" | grep -qE "
    r'"\.(ts|tsx|js|jsx)$"'
    ' && npx prettier --write "{}" 2>/dev/null || true\'',
)

# Byte-order marks, longest first where one prefixes another.
_BOMS = (
    (codecs.BOM_UTF8, "UTF-8 with a byte-order mark"),
    (codecs.BOM_UTF16_LE, "UTF-16"),
    (codecs.BOM_UTF16_BE, "UTF-16"),
)


def _encoding_problem(path: Path) -> Optional[str]:
    """Why ``path`` cannot be edited as UTF-8 text, or None (also when it is missing).

    Every file superclaude edits in place — settings, the CLAUDE file, the git
    exclude file — is read and written back as UTF-8. One saved in another
    encoding used to crash the command half-way: uninstall had already deleted
    the content when it reached a UTF-16 settings file, and install had already
    written it. A BOM is refused too: ``json`` rejects it, and a rewrite would
    carry it into the middle of the file. The message names the file and what it
    is, so the user knows what to re-save.
    """
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as e:
        return f"{path} cannot be read ({e})"
    for bom, name in _BOMS:
        if data.startswith(bom):
            return f"{path} is {name}; save it as UTF-8 without a BOM"
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as e:
        return (
            f"{path} is not UTF-8 (byte 0x{data[e.start]:02x} at offset {e.start}, "
            "a legacy code page such as cp949 or cp1252?); save it as UTF-8"
        )
    return None


def _load_settings(settings_file: Path) -> dict:
    """
    Load settings.json file, returning empty dict if not exists or invalid.

    Read-only callers (inventory, doctor, MCP listing) use this. A writer must
    call ``_unwritable_settings`` first: writing hooks into the {} this returns
    for an unparseable file replaces the user's whole settings file with hooks.

    Args:
        settings_file: Path to settings.json

    Returns:
        Dict with settings content, or {} if file doesn't exist/is invalid
    """
    if not settings_file.exists():
        return {}

    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):  # JSONDecodeError and UnicodeDecodeError
        return {}
    return data if isinstance(data, dict) else {}


def _unwritable_settings(settings_file: Path) -> Optional[str]:
    """Why ``settings_file`` must not be rewritten, or None when it may be.

    A missing file is writable (install creates it), and so is one holding
    nothing but whitespace (``touch settings.json``): there are no settings to
    lose, and it reads as ``{}``. An existing file that is not a JSON object — a
    trailing comma, a comment, an array — is not: the 2026-10-17 audit
    reproduced ``superclaude install`` turning
    ``{"permissions": ..., "model": "opus",}`` into a file holding only hooks.
    """
    if not settings_file.exists():
        return None
    problem = _encoding_problem(settings_file)
    if problem:
        return problem
    if not settings_file.read_bytes().strip():
        return None
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError) as e:
        return f"{settings_file} is not valid JSON ({e}); fix it or move it aside"
    if not isinstance(data, dict):
        return (
            f"{settings_file} is valid JSON but not an object; fix it or move it aside"
        )
    return None


def input_problems(base_path: Path, scope: str, settings: bool = True) -> List[str]:
    """What stops a command from editing this scope's settings and CLAUDE file.

    Checked before the first write or delete, so a command that cannot finish
    refuses with nothing changed instead of failing after it has already
    rewritten or deleted the install. ``settings=False`` leaves the settings
    file out, for a command that will not touch it (``uninstall
    --keep-settings``).
    """
    problems: List[str] = []
    if settings:
        problem = _unwritable_settings(base_path / settings_filename(scope))
        if problem:
            problems.append(problem)
    claude_md, _import_line = _claude_md_target(base_path, scope)
    problem = _encoding_problem(claude_md)
    if problem:
        problems.append(problem)
    return problems


def _save_settings(settings_file: Path, settings: dict) -> Tuple[bool, str]:
    """
    Save settings dict to settings.json file.

    Args:
        settings_file: Path to settings.json
        settings: Settings dict to save

    Returns:
        Tuple of (success, message)
    """
    try:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(settings_file, settings)
        return True, f"Settings saved to {settings_file}"
    except IOError as e:
        return False, f"Failed to save settings: {e}"


def _hook_entry_signature(hook_entry: dict) -> tuple:
    """Return a hashable signature for a hook entry.

    Two entries with the same matcher and the same set of inner hook commands
    (type, command, timeout) are treated as duplicates regardless of any
    surrounding metadata (`_comment`, etc.).
    """
    matcher = hook_entry.get("matcher", "")
    inner = tuple(
        sorted(
            (h.get("type", ""), h.get("command", ""), h.get("timeout"))
            for h in hook_entry.get("hooks", [])
        )
    )
    return (matcher, inner)


def _hook_script_id(hook: dict) -> Tuple[str, str]:
    """Which entry point an inner hook runs: (hook name, subcommand).

    Blind to the command form, the interpreter, the directory prefix, flags and
    the timeout, so one hook registered as `<python> <dir>/loop_guard.py` by a
    previous release and shipped as `superclaude hook loop_guard` now — or
    re-shipped with a new option — counts as the same hook. Matching on the
    whole command string instead would append a second copy of every hook
    whose command had drifted, and a doubled loop_guard trips its circuit
    breaker at half the intended error count.

    The subcommand is *not* dropped, though. One script can carry several entry
    points (`insight_writer harvest-from-hook` and `… request-from-hook` are
    different hooks on different events), and filename-only identity made a
    release that moved a hook to a new subcommand undeliverable: the old
    registration matched, the new subcommand was called already-present, and the
    wrong entry point kept running.

    Only a bare word directly after the entry point counts as the subcommand —
    an option (`-`-prefixed) is exactly what drifts between releases, and a shell
    operator or redirection a user appended is not part of the hook's identity.

    A command in neither form falls back to its normalised text.
    """
    command = hook.get("command", "")
    match = CONSOLE_HOOK_RE.search(command) or _HOOK_SCRIPT_RE.search(command)
    if not match:
        return (" ".join(command.split()), "")
    tokens = match.group(2).split()
    subcommand = tokens[0] if tokens and _SUBCOMMAND_RE.fullmatch(tokens[0]) else ""
    return (match.group(1), subcommand)


def _dedup_hook_array(hooks: List[dict]) -> List[dict]:
    """Remove duplicate hook entries, preserving first occurrence.

    Idempotent: running on an already-clean array is a no-op. Used both to
    clean accumulated duplicates from prior installs (e.g., third-party
    installers re-adding identical entries without checking) and to keep
    merged arrays clean.
    """
    seen = set()
    deduped = []
    for entry in hooks:
        sig = _hook_entry_signature(entry)
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append(entry)
    return deduped


def _split_entry(hook_entry: dict) -> Tuple[List[dict], List[dict]]:
    """Split one entry's inner hooks into (superclaude's, the user's).

    An entry whose own `_comment` carries the marker was written whole by this
    installer, so everything inside it is ours.
    """
    inner = hook_entry.get("hooks", [])
    comment = hook_entry.get("_comment", "")
    if any(marker in comment for marker in SUPERCLAUDE_HOOK_MARKERS):
        return list(inner), []

    sc_hooks = [h for h in inner if is_superclaude_inner_hook(h)]
    user_hooks = [h for h in inner if not is_superclaude_inner_hook(h)]
    return sc_hooks, user_hooks


def _strip_sc_inner_hooks(
    hook_array: List[dict], select: Optional[Callable[[dict], bool]] = None
) -> Tuple[List[dict], bool]:
    """Remove superclaude inner hooks, keeping entries that still hold user ones.

    Entry order is preserved, so a user hook stays where the user put it. An
    entry left with nothing inside is dropped rather than written back empty.
    ``select``, when given, narrows the removal to the superclaude hooks it
    accepts; the others stay as written.
    """
    kept: List[dict] = []
    changed = False
    for entry in hook_array:
        sc_hooks, _user_hooks = _split_entry(entry)
        removed = {id(h) for h in sc_hooks if select is None or select(h)}
        if not removed:
            kept.append(entry)
            continue
        changed = True
        rest = [h for h in entry.get("hooks", []) if id(h) not in removed]
        if rest:
            reduced = {key: value for key, value in entry.items() if key != "hooks"}
            reduced["hooks"] = rest
            kept.append(reduced)
    return kept, changed


def _is_retired_hook(event: str, hook: dict) -> bool:
    """Whether an inner hook on ``event`` is a registration no release ships now."""
    if event in RETIRED_HOOK_EVENTS:
        return True
    command = hook.get("command", "").strip()
    if command in RETIRED_HOOK_COMMANDS:
        return True
    if _command_digest(command) in RETIRED_HOOK_COMMAND_DIGESTS:
        return True
    return (event, *_hook_script_id(hook)) in RETIRED_HOOK_IDS


def _command_digest(command: str) -> str:
    return hashlib.sha256(command.encode("utf-8")).hexdigest()[:16]


def _strip_retired_hooks(hooks: dict) -> int:
    """Remove superclaude's retired registrations in place; return how many went."""
    removed = 0
    for event, array in list(hooks.items()):
        if not isinstance(array, list):
            continue
        before = sum(len(_split_entry(e)[0]) for e in array if isinstance(e, dict))
        kept, changed = _strip_sc_inner_hooks(
            array, functools.partial(_is_retired_hook, event)
        )
        if not changed:
            continue
        removed += before - sum(len(_split_entry(e)[0]) for e in kept)
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    return removed


def _merge_hook_arrays(
    existing: List[dict],
    new_hooks: List[dict],
    force: bool = False,
    stats: Optional[dict] = None,
) -> List[dict]:
    """
    Merge two hook arrays, preserving user hooks.

    Args:
        existing: Existing hooks array from settings.json
        new_hooks: New superclaude hooks to add
        force: If True, replace existing superclaude hooks
        stats: When given, ``stats["rewritten"]`` accumulates how many legacy
            commands the non-force merge rewrote to the console form

    Returns:
        Merged hooks array
    """
    if force:
        # Replace ours, in place: an entry that also holds a user hook keeps that
        # hook at its original position, and only entries left empty disappear.
        # Rebuilding as `user_entries + new_hooks` instead hoisted every user
        # entry ahead of ours, silently changing execution order.
        kept, _changed = _strip_sc_inner_hooks(existing)
        return kept + new_hooks

    existing_sc_hooks = [h for h in existing if is_superclaude_hook(h)]
    if not existing_sc_hooks:
        return existing + new_hooks

    # Non-force: existing entries are authoritative and stay as written — matcher,
    # timeout, position — so a user's edit survives; the one exception is a
    # legacy-form command, which _migrate_legacy_commands rewrites. Only hooks
    # this release ships that are not registered yet get appended. Skipping the whole event type
    # instead — as this used to — froze an install's hook set at whatever existed
    # when it was first written, while its content kept updating.
    #
    # Counted, not just a set: a release may ship one script twice under the same
    # matcher (two subcommands), and a set would call the second one
    # already-present and drop it. Each registration covers one shipped hook.
    #
    # Two passes, because the matcher is the user's to edit. The first consumes
    # exact (matcher, entry point) matches, which is what a legitimate two-matcher
    # shipping needs. The second lets an entry point registered under *some* other
    # matcher count, so narrowing `clear|compact|startup` to `clear|startup` keeps
    # the user's matcher instead of appending a second registration that then runs
    # the same hook twice per session.
    registered_here: Counter[Tuple[str, Tuple[str, str]]] = Counter()
    registered_anywhere: Counter[Tuple[str, str]] = Counter()
    for entry in existing_sc_hooks:
        matcher = entry.get("matcher", "")
        sc_hooks, _user_hooks = _split_entry(entry)
        for hook in sc_hooks:
            hook_id = _hook_script_id(hook)
            registered_here[(matcher, hook_id)] += 1
            registered_anywhere[hook_id] += 1

    unmatched = []
    for entry in new_hooks:
        matcher = entry.get("matcher", "")
        for hook in entry.get("hooks", []):
            hook_id = _hook_script_id(hook)
            if registered_here[(matcher, hook_id)] > 0:
                registered_here[(matcher, hook_id)] -= 1
                registered_anywhere[hook_id] -= 1
            else:
                unmatched.append((entry, hook, hook_id))

    missing_by_entry: dict = {}
    for entry, hook, hook_id in unmatched:
        if registered_anywhere[hook_id] > 0:
            registered_anywhere[hook_id] -= 1
            continue
        missing_by_entry.setdefault(id(entry), (entry, []))[1].append(hook)

    additions = []
    for entry, missing in missing_by_entry.values():
        addition = {key: value for key, value in entry.items() if key != "hooks"}
        addition["hooks"] = missing
        additions.append(addition)

    migrated, rewritten = _migrate_legacy_commands(existing, new_hooks)
    if stats is not None:
        stats["rewritten"] = stats.get("rewritten", 0) + rewritten
    return migrated + additions


def _migrate_legacy_commands(
    existing: List[dict], new_hooks: List[dict]
) -> Tuple[List[dict], int]:
    """Rewrite our legacy-form commands to the shipped form, and nothing else.

    The command string is not the user's to edit — matcher, timeout and position
    are. A `<python> <dir>/<name>.py` registration from a release before the
    console entry names the installing machine's interpreter and checkout,
    which is exactly what a committed project-scope settings.json must not
    carry; leaving it in place on the default (non-force) upgrade exposed those
    bytes for commit the moment install stopped excluding the file. Only
    legacy-form commands are touched: a console-form command with a pinned
    directory (`~/.local/bin/superclaude hook x`) is the user's own workaround
    for a narrow hook-shell PATH and stays, and only a console-form replacement
    is written: this is a migration to the console entry, not a general command
    refresh. Entries that change are copied, not mutated, so the caller's "did
    anything change" comparison stays honest. Returns the migrated array and the
    number of commands rewritten.
    """
    shipped_by_id: dict = {}
    for entry in new_hooks:
        for hook in entry.get("hooks", []):
            shipped_by_id.setdefault(_hook_script_id(hook), hook.get("command", ""))

    migrated: List[dict] = []
    rewritten = 0
    for entry in existing:
        sc_hooks, _user_hooks = _split_entry(entry)
        ours = {id(hook) for hook in sc_hooks}
        inner: List[dict] = []
        changed = False
        for hook in entry.get("hooks", []):
            command = hook.get("command", "")
            replacement = shipped_by_id.get(_hook_script_id(hook))
            if (
                id(hook) in ours
                and is_legacy_hook_command(command)
                and replacement
                and CONSOLE_HOOK_RE.search(replacement)
                and replacement != command
            ):
                inner.append({**hook, "command": replacement})
                changed = True
                rewritten += 1
            else:
                inner.append(hook)
        migrated.append({**entry, "hooks": inner} if changed else entry)
    return migrated, rewritten


def merge_hooks_to_settings(
    base_path: Path, hooks_config: dict, scope: str, force: bool = False
) -> Tuple[bool, str]:
    """
    Merge hooks.json content into settings.json.

    This function merges superclaude hooks into the settings.json file,
    preserving any existing user hooks.

    Args:
        base_path: Installation base path (.claude directory)
        hooks_config: Parsed hooks.json content
        scope: Installation scope ("user", "project", or "local")
        force: Replace existing superclaude hooks if True

    Returns:
        Tuple of (success, message)

    Scope behavior:
        - user: Merges to ~/.claude/settings.json
        - project: Merges to ./.claude/settings.json (team-shared: every
          command is `superclaude hook <name>`, so the file is the same bytes
          on every checkout and stays tracked)
        - local: Merges to ./.claude/settings.local.json (CC auto-gitignores)
    """
    filename = settings_filename(scope)
    settings_file = base_path / filename
    new_hooks = hooks_config.get("hooks", {})

    if not new_hooks:
        return True, "No hooks to merge"

    # Never merge into a file that cannot be read back as an object: the {}
    # _load_settings returns for it would be written over the user's config.
    problem = _unwritable_settings(settings_file)
    if problem:
        return False, problem

    # Load existing settings
    settings = _load_settings(settings_file)

    # Initialize hooks section if not exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    existing_hooks = settings["hooks"]
    before = copy.deepcopy(existing_hooks)
    stats: dict = {}

    # Registrations no release ships go first, in both modes: a non-force merge
    # keeps every existing superclaude entry, so it never reached them.
    retired = _strip_retired_hooks(existing_hooks)

    # `--force` means "replace with what this release ships", and that has to
    # include events this release no longer ships. Walking only the new config's
    # event types left a superclaude hook on a retired event firing forever,
    # calling a script that is not installed any more. User hooks on the same
    # event are kept by the same inner-hook rule as everywhere else.
    if force:
        for hook_type in list(existing_hooks.keys()):
            if hook_type in new_hooks:
                continue
            hook_array = existing_hooks[hook_type]
            if not isinstance(hook_array, list):
                continue
            kept, changed = _strip_sc_inner_hooks(hook_array)
            if not changed:
                continue
            if kept:
                existing_hooks[hook_type] = kept
            else:
                del existing_hooks[hook_type]

    # Merge each hook type (SessionStart, PostToolUse, etc.)
    for hook_type, new_hook_array in new_hooks.items():
        existing_array = existing_hooks.get(hook_type, [])

        # Dedup existing entries first. Third-party installers
        # may re-add identical entries on each install without checking; running
        # `make sync-user` N times accumulates N copies of unmarked hooks.
        # Deduping on every merge is idempotent and bounds growth.
        existing_array = _dedup_hook_array(existing_array)

        merged_array = _merge_hook_arrays(existing_array, new_hook_array, force, stats)
        existing_hooks[hook_type] = _dedup_hook_array(merged_array)

    settings["hooks"] = existing_hooks

    # Written only when the hooks section changed. An unconditional rewrite
    # re-serialised a file another writer (Claude Code's own settings UI, an
    # editor) had last saved with a trailing newline or other formatting, so
    # every teammate's install dirtied the committed file while reporting that
    # nothing needed merging.
    if existing_hooks == before:
        hint = "" if force else " (--force to replace)"
        return True, f"Hooks already registered in {settings_file}{hint}"

    success, save_msg = _save_settings(settings_file, settings)
    if not success:
        return False, save_msg

    rewritten = stats.get("rewritten", 0)
    notes = []
    if rewritten > 0:
        notes.append(
            f"{rewritten} legacy command(s) rewritten to `superclaude hook <name>`"
        )
    if retired > 0:
        notes.append(f"{retired} retired registration(s) removed")
    note = f" ({'; '.join(notes)})" if notes else ""
    return True, f"Hooks merged to {settings_file}{note}"


def uninstall_hooks_from_settings(
    base_path: Path, scope: str = "user"
) -> Tuple[bool, str]:
    """
    Remove superclaude hooks from settings.json (or settings.local.json for local scope),
    preserving user hooks.

    Args:
        base_path: Installation base path (.claude directory)
        scope: Installation scope

    Returns:
        Tuple of (success, message)
    """
    filename = settings_filename(scope)
    settings_file = base_path / filename

    if not settings_file.exists():
        return True, f"No {filename} found (nothing to clean)"

    settings = _load_settings(settings_file)

    if "hooks" not in settings or not settings["hooks"]:
        return True, f"No hooks in {filename}"

    existing_hooks = settings["hooks"]
    cleaned_any = False

    # Remove superclaude hooks from each hook type, per inner hook: a user
    # command sharing an entry with ours has to survive uninstall.
    for hook_type, hook_array in list(existing_hooks.items()):
        if not isinstance(hook_array, list):
            continue
        user_hooks, changed = _strip_sc_inner_hooks(hook_array)

        if changed:
            cleaned_any = True

        if user_hooks:
            existing_hooks[hook_type] = user_hooks
        else:
            # Remove empty hook type
            del existing_hooks[hook_type]

    # If no hooks remain, remove hooks section entirely
    if not existing_hooks:
        del settings["hooks"]

    # A settings file left empty holds nothing but what superclaude wrote: delete
    # it. At user scope only when this run removed our hooks — the global file
    # usually predates superclaude, and a `{}` the user keeps is not ours to drop.
    if not settings and (scope in ("local", "project") or cleaned_any):
        try:
            settings_file.unlink()
            return (
                True,
                f"superclaude hooks removed and empty {filename} deleted",
            )
        except OSError as e:
            return False, f"Failed to delete empty {settings_file}: {e}"

    # Save updated settings
    success, save_msg = _save_settings(settings_file, settings)

    if not success:
        return False, save_msg

    if cleaned_any:
        return True, f"superclaude hooks removed from {settings_file}"
    else:
        return True, f"No superclaude hooks found in {filename}"


def _claude_md_target(base_path: Path, scope: str) -> Tuple[Path, str]:
    """
    Resolve the CLAUDE.md target file and the import line for a scope.

    - user/project: base_path/CLAUDE.md with `@superclaude/CLAUDE_SC.md` (import
      resolves relative to CLAUDE.md's directory)
    - local: project_root/CLAUDE.local.md with `@.claude/superclaude/CLAUDE_SC.md`
      (CLAUDE.local.md lives at project root per CC docs; must walk into .claude/)
    """
    if scope == "local":
        project_root = base_path.parent
        return project_root / "CLAUDE.local.md", "@.claude/superclaude/CLAUDE_SC.md"
    return base_path / "CLAUDE.md", CLAUDE_SC_IMPORT


def check_claude_md_import(base_path: Path, scope: str = "user") -> Tuple[bool, str]:
    """
    Check if CLAUDE.md (or CLAUDE.local.md for local scope) has the CLAUDE_SC.md import.

    Args:
        base_path: Base installation path
        scope: Installation scope

    Returns:
        Tuple of (has_import: bool, status_message: str)
    """
    claude_md, import_line = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    if not claude_md.exists():
        return False, f"{target_label} not found"

    # doctor delegates this check, and doctor must report rather than traceback:
    # the code it replaced caught OSError and returned a failing result. A file
    # install would refuse to edit fails here too, with the same reason.
    problem = _encoding_problem(claude_md)
    if problem:
        return False, problem
    content = claude_md.read_text(encoding="utf-8")

    # The import line, with either path separator: a Windows-authored file may
    # carry `@.claude\superclaude\CLAUDE_SC.md`.
    if import_line in content or import_line.replace("/", "\\") in content:
        return True, f"{target_label} already imports CLAUDE_SC.md"

    return False, f"{target_label} does not import CLAUDE_SC.md"


def update_claude_md_import(base_path: Path, scope: str = "user") -> Tuple[bool, str]:
    """
    Add CLAUDE_SC.md import to CLAUDE.md (or CLAUDE.local.md for local scope) if not present.

    Args:
        base_path: Base installation path
        scope: Installation scope

    Returns:
        Tuple of (success: bool, message: str)
    """
    claude_md, import_line = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    # Check if already has import
    has_import, status = check_claude_md_import(base_path, scope)

    if has_import:
        return True, status

    # Create or update CLAUDE.md / CLAUDE.local.md
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")

        if import_line not in content:
            if not content.endswith("\n"):
                content += "\n"
            content += f"\n# superclaude\n{import_line}\n"

        claude_md.write_text(content, encoding="utf-8")
        return True, f"{target_label} updated with CLAUDE_SC.md import"
    else:
        header = (
            "# Claude Code Configuration (personal, gitignored)"
            if scope == "local"
            else "# Claude Code Configuration"
        )
        content = f"""{header}

# superclaude
{import_line}
"""
        claude_md.parent.mkdir(parents=True, exist_ok=True)
        claude_md.write_text(content, encoding="utf-8")
        return True, f"{target_label} created with CLAUDE_SC.md import"


def remove_claude_md_import(base_path: Path, scope: str = "user") -> Tuple[bool, str]:
    """
    Remove @superclaude/CLAUDE_SC.md import from CLAUDE.md (or CLAUDE.local.md for local scope).

    Args:
        base_path: Installation base path (.claude directory)
        scope: Installation scope

    Returns:
        Tuple of (success, message)
    """
    claude_md, _ = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    if not claude_md.exists():
        return True, f"No {target_label} found (nothing to clean)"

    try:
        content = claude_md.read_text(encoding="utf-8")
        original_content = content

        content = SC_IMPORT_RE.sub("", content)

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)
        stripped = content.strip()

        if content == original_content:
            return True, f"No superclaude import found in {target_label}"

        # A file holding nothing but the heading install writes when it creates
        # the file is superclaude's: remove it. Local and project scope also
        # remove a file left empty; the global ~/.claude/CLAUDE.md usually
        # predates superclaude, so there only the heading-only file goes.
        SC_HEADERS = {  # noqa: N806 — function-local constant
            "# Claude Code Configuration (personal, gitignored)",
            "# Claude Code Configuration",
        }
        if stripped in SC_HEADERS or (scope in ("local", "project") and not stripped):
            claude_md.unlink()
            return True, f"{target_label} removed (no user content after SC cleanup)"

        claude_md.write_text(stripped + "\n", encoding="utf-8")
        return True, f"superclaude import removed from {target_label}"

    except Exception as e:
        return False, f"Failed to update {target_label}: {e}"
