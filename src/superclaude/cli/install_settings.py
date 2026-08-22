"""
Settings, Hooks & CLAUDE.md Management for SuperClaude Installation

Handles settings.json merge/unmerge, hook identification, and CLAUDE.md import management.
This is a leaf dependency with no internal imports.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

from superclaude.utils import atomic_write_json

# Import line to add to CLAUDE.md
CLAUDE_SC_IMPORT = "@superclaude/CLAUDE_SC.md"

# Markers to identify SuperClaude hooks (for merge/replace logic).
# Match is substring-based against `_comment` and `command` fields, but every
# marker is anchored — bare script names like "session_init" would misclassify
# a user's own hook as SC-owned and silently replace/remove it on install/uninstall.
# `[superclaude]` catches `[superclaude] ...` _comment prefixes (incl.
# serena-recommended hooks) and echo-only hook commands.
SUPERCLAUDE_HOOK_MARKERS = [
    "[superclaude]",
    "{{SCRIPTS_PATH}}",  # unresolved template form of the scripts path
    "BLOCKED: destructive",  # legacy inline destructive-Bash blocker command
]

# Resolved {{SCRIPTS_PATH}} form: command references a script under a
# superclaude scripts directory (absolute user-scope path or
# $CLAUDE_PROJECT_DIR/.claude/superclaude/scripts; / or \ separators).
_SC_SCRIPTS_PATH_RE = re.compile(r"superclaude[/\\]scripts[/\\]")
_HOOK_SCRIPT_RE = re.compile(r"([A-Za-z0-9_]+\.py)(?=\s|$)(.*)$")


def _load_settings(settings_file: Path) -> dict:
    """
    Load settings.json file, returning empty dict if not exists or invalid.

    Args:
        settings_file: Path to settings.json

    Returns:
        Dict with settings content, or {} if file doesn't exist/is invalid
    """
    if not settings_file.exists():
        return {}

    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


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
    """Which entry point an inner hook runs: (script filename, subcommand).

    Blind to the interpreter, the directory prefix, flags and the timeout, so
    one hook written with a template path and again with a resolved absolute
    path — or re-shipped with a new option — counts as the same hook. Matching
    on the whole command string instead would append a second copy of every hook
    whose command had drifted, and a doubled loop_guard trips its circuit
    breaker at half the intended error count.

    The subcommand is *not* dropped, though. One script can carry several entry
    points (`insight_writer.py harvest-from-hook` and `… request-from-hook` are
    different hooks on different events), and filename-only identity made a
    release that moved a hook to a new subcommand undeliverable: the old
    registration matched, the new subcommand was called already-present, and the
    wrong entry point kept running.

    Only the first bare argument counts as the subcommand — anything starting
    with `-` is an option, and options are exactly what drifts between releases.

    A command that runs no .py file falls back to its normalised text.
    """
    command = hook.get("command", "")
    match = _HOOK_SCRIPT_RE.search(command)
    if not match:
        return (" ".join(command.split()), "")
    tokens = match.group(2).split()
    subcommand = tokens[0] if tokens and not tokens[0].startswith("-") else ""
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


def _is_superclaude_hook(hook_entry: dict) -> bool:
    """
    Check if a hook entry belongs to SuperClaude.

    Args:
        hook_entry: A hook entry dict with "hooks" array

    Returns:
        True if any hook command references a SuperClaude scripts path
        (template or resolved) or contains an anchored SuperClaude marker,
        or a `_comment` carries the `[superclaude]` tag
    """
    # Check _comment field on the hook entry itself
    comment = hook_entry.get("_comment", "")
    if any(marker in comment for marker in SUPERCLAUDE_HOOK_MARKERS):
        return True

    for hook in hook_entry.get("hooks", []):
        cmd = hook.get("command", "")
        if any(marker in cmd for marker in SUPERCLAUDE_HOOK_MARKERS):
            return True
        if _SC_SCRIPTS_PATH_RE.search(cmd):
            return True
        # Also check _comment on inner hook objects (e.g. test_runner_hook)
        inner_comment = hook.get("_comment", "")
        if any(marker in inner_comment for marker in SUPERCLAUDE_HOOK_MARKERS):
            return True
    return False


def _is_superclaude_inner_hook(hook: dict) -> bool:
    """Whether one inner hook is SuperClaude's, judged on its own command.

    The unit that matters for ownership. A settings entry carries one matcher
    and a list of inner hooks, so a user's own command can sit beside a
    SuperClaude one; judging the whole entry deleted the user's command along
    with ours on `--force` and on uninstall.
    """
    cmd = hook.get("command", "")
    if any(marker in cmd for marker in SUPERCLAUDE_HOOK_MARKERS):
        return True
    if _SC_SCRIPTS_PATH_RE.search(cmd):
        return True
    return any(
        marker in hook.get("_comment", "") for marker in SUPERCLAUDE_HOOK_MARKERS
    )


def _split_entry(hook_entry: dict) -> Tuple[List[dict], List[dict]]:
    """Split one entry's inner hooks into (SuperClaude's, the user's).

    An entry whose own `_comment` carries the marker was written whole by this
    installer, so everything inside it is ours.
    """
    inner = hook_entry.get("hooks", [])
    comment = hook_entry.get("_comment", "")
    if any(marker in comment for marker in SUPERCLAUDE_HOOK_MARKERS):
        return list(inner), []

    sc_hooks = [h for h in inner if _is_superclaude_inner_hook(h)]
    user_hooks = [h for h in inner if not _is_superclaude_inner_hook(h)]
    return sc_hooks, user_hooks


def _strip_sc_inner_hooks(hook_array: List[dict]) -> Tuple[List[dict], bool]:
    """Remove SuperClaude inner hooks, keeping entries that still hold user ones.

    Entry order is preserved, so a user hook stays where the user put it. An
    entry left with nothing inside is dropped rather than written back empty.
    """
    kept: List[dict] = []
    changed = False
    for entry in hook_array:
        sc_hooks, user_hooks = _split_entry(entry)
        if not sc_hooks:
            kept.append(entry)
            continue
        changed = True
        if user_hooks:
            reduced = {key: value for key, value in entry.items() if key != "hooks"}
            reduced["hooks"] = user_hooks
            kept.append(reduced)
    return kept, changed


def _merge_hook_arrays(
    existing: List[dict], new_hooks: List[dict], force: bool = False
) -> List[dict]:
    """
    Merge two hook arrays, preserving user hooks.

    Args:
        existing: Existing hooks array from settings.json
        new_hooks: New SuperClaude hooks to add
        force: If True, replace existing SuperClaude hooks

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

    existing_sc_hooks = [h for h in existing if _is_superclaude_hook(h)]
    if not existing_sc_hooks:
        return existing + new_hooks

    # Non-force: existing entries are authoritative and stay exactly as written,
    # so a user's timeout or matcher edit survives. Only hooks this release ships
    # that are not registered yet get appended. Skipping the whole event type
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
    registered_here = Counter()
    registered_anywhere = Counter()
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

    return existing + additions


def merge_hooks_to_settings(
    base_path: Path, hooks_config: dict, scope: str, force: bool = False
) -> Tuple[bool, str]:
    """
    Merge hooks.json content into settings.json.

    This function merges SuperClaude hooks into the settings.json file,
    preserving any existing user hooks.

    Args:
        base_path: Installation base path (.claude directory)
        hooks_config: Transformed hooks config (paths already substituted)
        scope: Installation scope ("user", "project", or "target")
        force: Replace existing SuperClaude hooks if True

    Returns:
        Tuple of (success, message)

    Scope behavior:
        - user: Merges to ~/.claude/settings.json (absolute paths)
        - project: Merges to ./.claude/settings.json (team-shared)
        - local: Merges to ./.claude/settings.local.json (CC auto-gitignores)
        - target: Merges to {target}/.claude/settings.json (absolute paths)
    """
    settings_filename = "settings.local.json" if scope == "local" else "settings.json"
    settings_file = base_path / settings_filename
    new_hooks = hooks_config.get("hooks", {})

    if not new_hooks:
        return True, "No hooks to merge"

    # Load existing settings
    settings = _load_settings(settings_file)

    # Initialize hooks section if not exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    existing_hooks = settings["hooks"]
    merged_any = False
    skipped_any = False

    # `--force` means "replace with what this release ships", and that has to
    # include events this release no longer ships. Walking only the new config's
    # event types left a SuperClaude hook on a retired event firing forever,
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
            merged_any = True
            if kept:
                existing_hooks[hook_type] = kept
            else:
                del existing_hooks[hook_type]

    # Merge each hook type (SessionStart, PostToolUse, etc.)
    for hook_type, new_hook_array in new_hooks.items():
        existing_array = existing_hooks.get(hook_type, [])

        # Dedup existing entries first. Third-party installers (e.g., Serena)
        # may re-add identical entries on each install without checking; running
        # `make sync-user` N times accumulates N copies of unmarked hooks.
        # Deduping on every merge is idempotent and bounds growth.
        existing_array = _dedup_hook_array(existing_array)

        merged_array = _merge_hook_arrays(existing_array, new_hook_array, force)
        merged_array = _dedup_hook_array(merged_array)
        existing_hooks[hook_type] = merged_array
        if merged_array == existing_array:
            skipped_any = True
        else:
            merged_any = True

    settings["hooks"] = existing_hooks

    # Save updated settings
    success, save_msg = _save_settings(settings_file, settings)

    if not success:
        return False, save_msg

    if skipped_any and not merged_any:
        return True, f"Hooks already registered in {settings_file} (--force to replace)"
    elif skipped_any:
        return True, f"New hooks merged to {settings_file}, the rest already registered"
    else:
        return True, f"Hooks merged to {settings_file}"


def uninstall_hooks_from_settings(
    base_path: Path, scope: str = "user"
) -> Tuple[bool, str]:
    """
    Remove SuperClaude hooks from settings.json (or settings.local.json for local scope),
    preserving user hooks.

    Args:
        base_path: Installation base path (.claude directory)
        scope: Installation scope

    Returns:
        Tuple of (success, message)
    """
    settings_filename = "settings.local.json" if scope == "local" else "settings.json"
    settings_file = base_path / settings_filename

    if not settings_file.exists():
        return True, f"No {settings_filename} found (nothing to clean)"

    settings = _load_settings(settings_file)

    if "hooks" not in settings or not settings["hooks"]:
        return True, f"No hooks in {settings_filename}"

    existing_hooks = settings["hooks"]
    cleaned_any = False

    # Remove SuperClaude hooks from each hook type, per inner hook: a user
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

    # For local/project scope: if the settings file is now empty (only SC content), delete it.
    # User scope is excluded — global settings.json is likely to hold user config independent of SC.
    if scope in ("local", "project") and not settings:
        try:
            settings_file.unlink()
            return (
                True,
                f"SuperClaude hooks removed and empty {settings_filename} deleted",
            )
        except OSError as e:
            return False, f"Failed to delete empty {settings_file}: {e}"

    # Save updated settings
    success, save_msg = _save_settings(settings_file, settings)

    if not success:
        return False, save_msg

    if cleaned_any:
        return True, f"SuperClaude hooks removed from {settings_file}"
    else:
        return True, f"No SuperClaude hooks found in {settings_filename}"


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


def check_claude_md_import(
    base_path: Path = None, scope: str = "user"
) -> Tuple[bool, str]:
    """
    Check if CLAUDE.md (or CLAUDE.local.md for local scope) has the CLAUDE_SC.md import.

    Args:
        base_path: Base installation path
        scope: Installation scope

    Returns:
        Tuple of (has_import: bool, status_message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    claude_md, import_line = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    if not claude_md.exists():
        return False, f"{target_label} not found"

    content = claude_md.read_text(encoding="utf-8")

    # Check for import pattern (with or without leading @, cross-platform paths)
    escaped = re.escape(import_line)
    patterns = [
        escaped,
        escaped.replace("/", r"\\"),  # Windows backslash variant
    ]

    for pattern in patterns:
        if re.search(pattern, content):
            return True, f"{target_label} already imports CLAUDE_SC.md"

    return False, f"{target_label} does not import CLAUDE_SC.md"


def update_claude_md_import(
    base_path: Path = None, force: bool = False, scope: str = "user"
) -> Tuple[bool, str]:
    """
    Add CLAUDE_SC.md import to CLAUDE.md (or CLAUDE.local.md for local scope) if not present.

    Args:
        base_path: Base installation path
        force: Force update even if import exists
        scope: Installation scope

    Returns:
        Tuple of (success: bool, message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    claude_md, import_line = _claude_md_target(base_path, scope)
    target_label = claude_md.name

    # Check if already has import
    has_import, status = check_claude_md_import(base_path, scope)

    if has_import and not force:
        return True, status

    # Create or update CLAUDE.md / CLAUDE.local.md
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")

        # If force, replace any existing superclaude imports
        if force:
            content = re.sub(r"@\.claude/superclaude/[^\n]+\n?", "", content)
            content = re.sub(r"@superclaude/[^\n]+\n?", "", content)
            content = re.sub(r"@superclaude\\[^\n]+\n?", "", content)

        if import_line not in content:
            if not content.endswith("\n"):
                content += "\n"
            content += f"\n# SuperClaude Framework\n{import_line}\n"

        claude_md.write_text(content, encoding="utf-8")
        return True, f"{target_label} updated with CLAUDE_SC.md import"
    else:
        header = (
            "# Claude Code Configuration (personal, gitignored)"
            if scope == "local"
            else "# Claude Code Configuration"
        )
        content = f"""{header}

# SuperClaude Framework
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

        # Remove SuperClaude import lines and related comments (all variants)
        content = re.sub(
            r"# SuperClaude Framework\n@\.claude/superclaude/[^\n]+\n?", "", content
        )
        content = re.sub(
            r"# SuperClaude Framework\n@superclaude/[^\n]+\n?", "", content
        )
        content = re.sub(r"@\.claude/superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"@superclaude/[^\n]+\n?", "", content)
        content = re.sub(r"@superclaude\\[^\n]+\n?", "", content)

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)
        stripped = content.strip()

        if content == original_content:
            return True, f"No SuperClaude import found in {target_label}"

        # For local/project scope: if CLAUDE.md/CLAUDE.local.md has no user content
        # (empty or only the SC-created header), remove it entirely.
        # User scope is excluded — global CLAUDE.md is likely to hold user config independent of SC.
        SC_HEADERS = {  # noqa: N806 — function-local constant
            "# Claude Code Configuration (personal, gitignored)",
            "# Claude Code Configuration",
        }
        if scope in ("local", "project") and (not stripped or stripped in SC_HEADERS):
            claude_md.unlink()
            return True, f"{target_label} removed (no user content after SC cleanup)"

        claude_md.write_text(stripped + "\n", encoding="utf-8")
        return True, f"SuperClaude import removed from {target_label}"

    except Exception as e:
        return False, f"Failed to update {target_label}: {e}"
