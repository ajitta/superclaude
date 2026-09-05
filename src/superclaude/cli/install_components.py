"""
Component Installation & Orchestration for SuperClaude

Handles installing individual components, hooks/scripts, CLAUDE_SC.md,
and the top-level install_all orchestration.
"""

import json
import shutil
from pathlib import Path
from typing import List, Tuple

from .install_git_exclude import add_git_exclude
from .install_paths import (
    COMPONENTS,
    _get_package_root,
    _get_source_dir,
    _get_target_dir,
    find_legacy_skills,
)
from .install_settings import (
    CLAUDE_SC_IMPORT,
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

    # The registration only works where Claude Code's hook shell can resolve
    # `superclaude`. That shell inherits the launching shell's PATH (measured
    # 2026-09-05: ~/.local/bin — where uv, pipx and Claude Code's own native
    # installer put their scripts — was present), so this process's PATH is the
    # closest proxy available. A warning, not a failure: the two shells are not
    # guaranteed to agree in either direction.
    if shutil.which("superclaude") is None:
        messages.append(
            "⚠️  `superclaude` is not on PATH in this shell. Every hook runs "
            "`superclaude hook <name>` and exits 127 where Claude Code cannot "
            "find it — put the console script's directory on PATH "
            "(uv: `uv tool update-shell`; pipx: `pipx ensurepath`)."
        )

    # Script copies from a release whose hooks ran them directly. Deliberately
    # NOT removed: Claude Code snapshots hook commands at session start, so a
    # session already running — this project's, or on a user-scope install any
    # project's — keeps executing the OLD registration against these files, and
    # python's "can't open file" is exit 2, the blocking code on PreToolUse and
    # Stop. Deleting them under a live session blocks every tool call until
    # restart. The user removes them once no such session is left.
    legacy_scripts = base_path / "superclaude" / "scripts"
    if legacy_scripts.is_dir():
        messages.append(
            f"ℹ️  {legacy_scripts} holds script copies from a release whose hooks "
            "ran them directly; hooks now run `superclaude hook <name>`. Left in "
            "place for sessions still on the previous registration — remove it "
            "after restarting Claude Code."
        )

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
    # the release that is installed.
    try:
        hooks_target.mkdir(parents=True, exist_ok=True)
        (hooks_target / "hooks.json").write_text(hooks_content, encoding="utf-8")
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

    return installed, skipped, failed, messages


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
