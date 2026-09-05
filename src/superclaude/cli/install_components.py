"""
Component Installation & Orchestration for SuperClaude

Handles installing individual components, hooks/scripts, CLAUDE_SC.md,
and the top-level install_all orchestration.
"""

import json
import shutil
from pathlib import Path
from typing import List, Tuple

from superclaude import __version__
from superclaude.utils import is_legacy_hook_command, settings_filename

from .install_git_exclude import add_git_exclude, find_team_ignores
from .install_paths import (
    COMPONENTS,
    _get_package_root,
    _get_source_dir,
    _get_target_dir,
    find_legacy_skills,
    probe_console_script,
)
from .install_settings import (
    CLAUDE_SC_IMPORT,
    _is_superclaude_hook,
    _load_settings,
    _split_entry,
    check_claude_md_import,
    merge_hooks_to_settings,
    update_claude_md_import,
)

# All MCP docs are now operational guides (workflow patterns, decision rules, integration strategies)
# complementing CC's native tool search which handles tool discovery.
MCP_DOCS_SKIP: set = set()


def _rewrite_agent_memory_scope(content: str, scope: str) -> str:
    """Rewrite agent frontmatter `memory:` to match install scope.

    Source agents ship `memory: project`. Installing globally (`user`) or as
    personal-scope (`local`) requires a matching memory location so agent
    memory is not written into foreign cwds (user scope) or accidentally
    committed to the team repo (local scope).
    """
    if scope not in {"user", "project", "local"}:
        return content
    return content.replace("memory: project\n", f"memory: {scope}\n", 1)


# Where each scope's agents keep memory, per .claude/rules/agent-authoring.md.
# `target` is absent deliberately: it has no documented memory location, and
# guessing one would scatter agent memory into an arbitrary directory.
_AGENT_MEMORY_DIRS = {
    "user": "agent-memory",
    "project": "agent-memory",
    "local": "agent-memory-local",
}


def ensure_agent_memory_dir(base_path: Path, scope: str) -> Path | None:
    """Create the agent memory store this scope's agents will be pointed at.

    Install rewrites every agent's `memory:` to match the scope, but nothing
    created the directory that rewrite names. The one real local install on
    record had 23 agents each declaring a store that did not exist.

    Args:
        base_path: The scope's .claude directory
        scope: Installation scope

    Returns:
        The directory, or None for a scope with no documented location
    """
    name = _AGENT_MEMORY_DIRS.get(scope)
    if not name:
        return None
    directory = base_path / name
    # OSError propagates on purpose. Swallowing it returned the same None as an
    # unsupported scope, and the caller could not tell "no store by design" from
    # "the store could not be created" — so agents were rewritten to point at a
    # directory that did not exist while the install reported success.
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _safe_target_path(target: Path, base_path: Path) -> bool:
    """Check that a target path is safe (not a symlink to outside base_path).

    Args:
        target: Target path to validate
        base_path: Expected base directory

    Returns:
        True if the path is safe, False if it's a symlink to an unexpected location
    """
    if not target.exists():
        return True
    resolved = target.resolve()
    base_resolved = base_path.resolve()
    return resolved == base_resolved or base_resolved in resolved.parents


def install_component(
    component: str, base_path: Path = None, force: bool = False, scope: str = "user"
) -> Tuple[int, int, int, List[str]]:
    """
    Install a single component.

    Args:
        component: Component name
        base_path: Base installation path
        force: Force reinstall

    Returns:
        Tuple of (installed_count, skipped_count, failed_count, failed_names)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    source_dir = _get_source_dir(component)
    target_dir = _get_target_dir(component, base_path)

    if not source_dir.exists():
        return 0, 0, 1, [f"Source not found: {source_dir}"]

    target_dir.mkdir(parents=True, exist_ok=True)

    installed = 0
    skipped = 0
    failed = 0
    failed_names = []

    # Copy .md files (excluding README.md and filtered MCP docs)
    for source_file in source_dir.glob("*.md"):
        # Skip README files
        if source_file.stem.upper() == "README":
            continue

        # Skip redundant MCP docs (MCP auto-mode provides tool descriptions)
        if component == "mcp" and source_file.name in MCP_DOCS_SKIP:
            skipped += 1
            continue

        target_file = target_dir / source_file.name
        if target_file.exists() and not force:
            skipped += 1
            continue
        try:
            if component == "agents":
                content = source_file.read_text(encoding="utf-8")
                target_file.write_text(
                    _rewrite_agent_memory_scope(content, scope),
                    encoding="utf-8",
                )
            else:
                shutil.copy2(source_file, target_file)
            installed += 1
        except Exception as e:
            failed += 1
            failed_names.append(f"{source_file.name}: {e}")

    # core/rules/ holds on-demand rule modules (Phase 2-1 core-lite split)
    # routed by context_loader — copy nested .md preserving layout.
    if component == "core":
        for source_file in source_dir.glob("rules/*.md"):
            if source_file.stem.upper() == "README":
                continue
            target_file = target_dir / "rules" / source_file.name
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if target_file.exists() and not force:
                skipped += 1
                continue
            try:
                shutil.copy2(source_file, target_file)
                installed += 1
            except Exception as e:
                failed += 1
                failed_names.append(f"rules/{source_file.name}: {e}")

    # templates/ holds nested doc-scaffold directories consumed by
    # /sc:init (not slash commands). Copy each subdirectory verbatim.
    if component == "templates":
        for sub_dir in source_dir.iterdir():
            if not sub_dir.is_dir():
                continue
            if sub_dir.name.startswith(("_", ".")):
                continue
            target_sub = target_dir / sub_dir.name
            if target_sub.exists() and not force:
                skipped += 1
                continue
            try:
                if target_sub.exists():
                    if not _safe_target_path(target_sub, target_dir):
                        failed += 1
                        failed_names.append(f"{sub_dir.name}: symlink outside target")
                        continue
                    shutil.rmtree(target_sub)
                shutil.copytree(
                    sub_dir,
                    target_sub,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
                )
                installed += 1
            except Exception as e:
                failed += 1
                failed_names.append(f"{sub_dir.name}: {e}")

    return installed, skipped, failed, failed_names


def install_claude_sc_md(
    base_path: Path = None, force: bool = False
) -> Tuple[bool, str]:
    """
    Install CLAUDE_SC.md to ~/.claude/superclaude/

    Args:
        base_path: Base installation path
        force: Force reinstall

    Returns:
        Tuple of (success, message)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    package_root = _get_package_root()
    source_file = package_root / "CLAUDE_SC.md"
    target_dir = base_path / "superclaude"
    target_file = target_dir / "CLAUDE_SC.md"

    if not source_file.exists():
        return False, f"CLAUDE_SC.md not found at {source_file}"

    target_dir.mkdir(parents=True, exist_ok=True)

    if target_file.exists() and not force:
        return True, "CLAUDE_SC.md already exists (use --force to reinstall)"

    try:
        shutil.copy2(source_file, target_file)
        return True, "CLAUDE_SC.md installed"
    except Exception as e:
        return False, f"Failed to install CLAUDE_SC.md: {e}"


def install_hooks(
    base_path: Path = None, force: bool = False, scope: str = "user"
) -> Tuple[int, int, int, List[str]]:
    """
    Install the hook registration.

    This function:
    1. Copies hooks/hooks.json to <base>/hooks/hooks.json, verbatim
    2. Merges its hooks into this scope's settings file

    Every command is ``superclaude hook <name>``. The console script resolves
    its own interpreter and its own copy of the package, so nothing here is
    rewritten per machine and a project-scope settings.json is the same bytes on
    every teammate's checkout. Earlier releases copied the scripts to
    ``<base>/superclaude/scripts/`` and baked the installer's interpreter and
    that directory into each command; a hook command no longer carries a path
    at any scope, so the worktree anchor question (which directory the command
    should name) no longer arises.

    Args:
        base_path: Base installation path (default: ~/.claude)
        force: Replace this scope's SuperClaude hook registrations
        scope: Installation scope ("user", "project", or "local")

    Returns:
        Tuple of (installed_count, skipped_count, failed_count, messages)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    package_root = _get_package_root()
    hooks_source = package_root / "hooks"
    hooks_target = base_path / "hooks"

    installed = 0
    skipped = 0
    failed = 0
    messages = []

    messages.extend(_console_script_warnings())

    hooks_json_file = hooks_source / "hooks.json"
    if not hooks_json_file.exists():
        messages.append("hooks.json not found, skipping hooks configuration")
        return installed, skipped, failed, messages

    try:
        hooks_content = hooks_json_file.read_text(encoding="utf-8")
    except OSError as e:
        failed += 1
        messages.append(f"Failed to read hooks.json: {e}")
        return installed, skipped, failed, messages

    # 1. Copy hooks.json to <base>/hooks/hooks.json. Build output, not user
    # content: rewritten regardless of --force so the file on disk describes
    # the release that is installed. newline pinned: text mode would write CRLF
    # on Windows into a file project scope commits (atomic_write_json pins the
    # same for settings.json).
    try:
        hooks_target.mkdir(parents=True, exist_ok=True)
        with open(
            hooks_target / "hooks.json", "w", encoding="utf-8", newline="\n"
        ) as f:
            f.write(hooks_content)
        installed += 1
        messages.append("hooks.json installed")
    except OSError as e:
        failed += 1
        messages.append(f"Failed to install hooks.json: {e}")

    # 2. Merge hooks into the settings file (what Claude Code actually reads)
    try:
        hooks_config = json.loads(hooks_content)
        merge_success, merge_msg = merge_hooks_to_settings(
            base_path=base_path, hooks_config=hooks_config, scope=scope, force=force
        )

        if merge_success:
            installed += 1
            messages.append(f"✓ {merge_msg}")
        else:
            failed += 1
            messages.append(f"✗ {merge_msg}")
    except json.JSONDecodeError as e:
        failed += 1
        messages.append(f"Failed to parse hooks.json for merge: {e}")
    except OSError as e:
        failed += 1
        messages.append(f"Failed to merge hooks to settings.json: {e}")

    legacy_scripts = base_path / "superclaude" / "scripts"
    if legacy_scripts.is_dir():
        messages.append(
            _legacy_scripts_notice(legacy_scripts, base_path / settings_filename(scope))
        )

    return installed, skipped, failed, messages


def _console_script_warnings() -> List[str]:
    """Warn when the `superclaude` Claude Code's hook shell will find cannot run hooks.

    Every registration is `superclaude hook <name>`, so the hooks work only where
    that shell resolves a console script of this release. The probe
    (install_paths.probe_console_script) searches this process's PATH minus the
    running interpreter's own bin — under `uv run` that is the project venv,
    which the user's shell sees only while activated — and asks the script it
    finds whether it has the `hook` subcommand and which version it is. Still a
    proxy: the hook shell inherits the launching shell's PATH (measured
    2026-09-05 on macOS; Windows unmeasured), not this process's.
    """
    probe = probe_console_script()
    where = probe["path"]
    fix = (
        "put this release's console script on PATH "
        "(uv: `uv tool update-shell`; pipx: `pipx ensurepath`)"
    )
    if where is None:
        excluded = (
            f" `{probe['excluded']}` was left out of the search: Claude Code's shell "
            "sees it only while that environment is active there."
            if probe["excluded"]
            else ""
        )
        return [
            "⚠️  `superclaude` is not on PATH. Every hook runs `superclaude hook "
            f"<name>` and exits 127 where Claude Code cannot find it — {fix}.{excluded}"
        ]
    if not probe["has_hook"]:
        return [
            f"⚠️  PATH resolves `superclaude` to {where}, which has no `hook` "
            f"subcommand ({probe['version'] or 'unknown version'}); every hook exits "
            f"2 there, the blocking code. Upgrade that install or {fix}."
        ]
    if probe["version"] and probe["version"] != __version__:
        return [
            f"⚠️  PATH resolves `superclaude` to {where} (version {probe['version']}), "
            f"not this install ({__version__}); Claude Code runs that version's hooks."
        ]
    return []


def _registered_sc_commands(settings_file: Path) -> List[str]:
    """Commands of every SuperClaude-owned inner hook in a settings file."""
    hooks = _load_settings(settings_file).get("hooks", {})
    if not isinstance(hooks, dict):
        return []
    return [
        hook.get("command", "")
        for array in hooks.values()
        if isinstance(array, list)
        for entry in array
        if isinstance(entry, dict) and _is_superclaude_hook(entry)
        for hook in _split_entry(entry)[0]
    ]


def _legacy_scripts_notice(legacy_scripts: Path, settings_file: Path) -> str:
    """What to tell the user about script copies a previous release installed.

    Never removed by the installer: Claude Code snapshots hook commands at
    session start, so a session already running — this project's, or on a
    user-scope install any project's — keeps executing the OLD registration
    against these files, and python's "can't open file" is exit 2, the blocking
    code on PreToolUse and Stop. Which advice is right depends on the settings
    file just written: while any registration still names the copies (a hook
    this release no longer ships, kept by a non-force install), telling the
    user to delete them would turn a working install into a blocked one.
    """
    still_used = sum(
        1
        for cmd in _registered_sc_commands(settings_file)
        if is_legacy_hook_command(cmd)
    )
    if still_used:
        return (
            f"ℹ️  {still_used} registration(s) in {settings_file.name} still run the "
            f"script copies under {legacy_scripts} — do not remove that directory; "
            "`superclaude install --force` rewrites every registration to "
            "`superclaude hook <name>`."
        )
    return (
        f"ℹ️  {legacy_scripts} holds script copies from a release whose hooks ran "
        "them directly; hooks now run `superclaude hook <name>`. Left in place for "
        "sessions still on the previous registration — remove it after restarting "
        "Claude Code."
    )


def install_all(
    base_path: Path = None, force: bool = False, scope: str = "user"
) -> Tuple[bool, str]:
    """
    Install all SuperClaude components.

    Args:
        base_path: Base installation path (default: ~/.claude)
        force: Force reinstall if components exist
        scope: Installation scope ("user", "project", or "target")

    Returns:
        Tuple of (success: bool, message: str)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    messages = []
    total_installed = 0
    total_skipped = 0
    total_failed = 0

    # Agents are rewritten to this scope's `memory:` value below; the store that
    # rewrite names has to exist for it to mean anything.
    try:
        ensure_agent_memory_dir(base_path, scope)
    except OSError as e:
        total_failed += 1
        messages.append(f"❌ Agent memory store: {e}")

    # Upgrade path: drop skills a pre-removal release installed. Uninstall prunes
    # them too, but nobody upgrading runs uninstall, and leaving them means the
    # auto-invocable ones keep firing with no source left to explain them.
    stale_skills = find_legacy_skills(base_path)
    if stale_skills:
        try:
            for d in stale_skills:
                shutil.rmtree(d)
            messages.append(
                f"🧹 Removed {len(stale_skills)} skill(s) from a pre-removal release"
            )
        except OSError as e:
            total_failed += 1
            messages.append(f"❌ Legacy skill cleanup: {e}")

    # Install each component
    for component, (_, _, description) in COMPONENTS.items():
        installed, skipped, failed, failed_names = install_component(
            component, base_path, force, scope
        )

        total_installed += installed
        total_skipped += skipped
        total_failed += failed

        if installed > 0:
            messages.append(f"✅ {description}: {installed} installed")
        if skipped > 0:
            messages.append(f"⏭️  {description}: {skipped} skipped")
        if failed > 0:
            messages.append(f"❌ {description}: {failed} failed")
            for name in failed_names:
                messages.append(f"   - {name}")

    # Install the hook registration
    hooks_installed, hooks_skipped, hooks_failed, hooks_messages = install_hooks(
        base_path, force, scope
    )
    total_installed += hooks_installed
    total_skipped += hooks_skipped
    total_failed += hooks_failed

    if hooks_installed > 0:
        messages.append(f"✅ Hook registration: {hooks_installed} installed")
    if hooks_skipped > 0:
        messages.append(f"⏭️  Hook registration: {hooks_skipped} skipped")
    if hooks_failed > 0:
        messages.append(f"❌ Hook registration: {hooks_failed} failed")
    for msg in hooks_messages:
        messages.append(f"   {msg}")

    # Install CLAUDE_SC.md
    success, msg = install_claude_sc_md(base_path, force)
    messages.append(f"{'✅' if success else '❌'} {msg}")
    if not success:
        total_failed += 1

    # Check and update CLAUDE.md import (CLAUDE.local.md for local scope)
    messages.append("")
    has_import, check_msg = check_claude_md_import(base_path, scope=scope)
    if has_import:
        messages.append(f"✅ {check_msg}")
    else:
        update_success, update_msg = update_claude_md_import(
            base_path, force=False, scope=scope
        )
        if update_success:
            messages.append(f"✅ {update_msg}")
        else:
            # Counted, not merely warned: without the import the framework is
            # installed and inert, which is the state the summary would
            # otherwise call a success.
            total_failed += 1
            messages.append(f"⚠️  {update_msg}")
            messages.append(f"   Add manually: {CLAUDE_SC_IMPORT}")

    # Add the .git/info/exclude block (per-clone, not shared via the team
    # .gitignore). CC doesn't auto-ignore agents/skills/etc., so we manage the
    # per-clone exclude ourselves. Local scope excludes everything it installs;
    # project scope only the files that cannot be shared — see
    # install_git_exclude._collect_entries.
    if scope in ("local", "project"):
        project_root = base_path.parent
        gi_ok, gi_msg = add_git_exclude(project_root, scope)
        messages.append(f"{'✅' if gi_ok else '⚠️ '} {gi_msg}")
        # Project scope stopped excluding the registration so the team can
        # commit it, but a team-level .gitignore (this very repository carries
        # `.claude/settings.json`) or a global excludes file can still hide it —
        # silently, with install reporting success. Tracked files are never
        # reported, so an already-committed registration stays quiet.
        if scope == "project":
            for source, line, path in find_team_ignores(
                project_root, [".claude/settings.json", ".claude/hooks/hooks.json"]
            ):
                messages.append(
                    f"⚠️  {source}:{line} ignores {path} — project scope commits the "
                    "hook registration, and this rule keeps it out of the team's "
                    "history; remove the rule, or use --scope local for a personal "
                    "install"
                )
        if not gi_ok:
            total_failed += 1

    # Summary
    messages.append("")
    messages.append(
        f"📊 Summary: {total_installed} installed, {total_skipped} skipped, {total_failed} failed"
    )
    messages.append(f"📁 Installation directory: {base_path}")

    if total_skipped > 0:
        messages.append("\n💡 Tip: Use --force to reinstall existing files")

    messages.append("\n🔄 Restart Claude Code to use the new components")

    overall_success = total_failed == 0
    return overall_success, "\n".join(messages)


def install_commands(target_path: Path = None, force: bool = False) -> Tuple[bool, str]:
    """
    Install all SuperClaude commands to Claude Code (legacy function).

    Now installs ALL components, not just commands.

    Args:
        target_path: Base installation path (default: ~/.claude)
                     Note: Commands are installed to {base_path}/commands/sc/
        force: Force reinstall if commands exist

    Returns:
        Tuple of (success: bool, message: str)
    """
    # If target_path is provided, use its parent as base_path
    # (legacy behavior expected commands in target_path directly)
    if target_path is not None:
        base_path = (
            target_path.parent if target_path.name == "commands" else target_path
        )
    else:
        base_path = None
    return install_all(base_path=base_path, force=force)
