"""
Component Installation & Orchestration for SuperClaude

Handles installing individual components, hooks/scripts, CLAUDE_SC.md,
and the top-level install_all orchestration.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

from .install_paths import (
    COMPONENTS,
    _get_package_root,
    _get_source_dir,
    _get_target_dir,
)
from .install_gitignore import add_local_gitignore
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


def _resolve_template_paths(base_path: Path, scope: str = "user") -> dict:
    """Compute resolved template variable values for a given scope."""
    if scope in ("project", "local"):
        scripts = ".claude/superclaude/scripts"
        skills = ".claude/skills"
    else:
        # Use as_posix() to avoid Windows backslashes breaking YAML parsing
        scripts = (base_path / "superclaude" / "scripts").resolve().as_posix()
        skills = (base_path / "skills").resolve().as_posix()
    return {"{{SCRIPTS_PATH}}": scripts, "{{SKILLS_PATH}}": skills}


def _resolve_skill_templates(skill_dir: Path, template_vars: dict) -> None:
    """Replace template variables in SKILL.md files within a copied skill directory."""
    for manifest in ("SKILL.md", "skill.md"):
        skill_md = skill_dir / manifest
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            changed = False
            for placeholder, value in template_vars.items():
                if placeholder in content:
                    content = content.replace(placeholder, value)
                    changed = True
            if changed:
                skill_md.write_text(content, encoding="utf-8")


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
    component: str,
    base_path: Path = None,
    force: bool = False,
    scope: str = "user"
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
    source_dir = _get_source_dir(component)
    target_dir = _get_target_dir(component, base_path)

    if not source_dir.exists():
        return 0, 0, 1, [f"Source not found: {source_dir}"]

    target_dir.mkdir(parents=True, exist_ok=True)

    installed = 0
    skipped = 0
    failed = 0
    failed_names = []

    # Handle skills directory specially (has subdirectories)
    if component == "skills":
        for skill_dir in source_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith(("_", ".")):
                target_skill_dir = target_dir / skill_dir.name
                if target_skill_dir.exists() and not force:
                    skipped += 1
                    continue
                try:
                    if target_skill_dir.exists():
                        if not _safe_target_path(target_skill_dir, target_dir):
                            failed += 1
                            failed_names.append(f"{skill_dir.name}: symlink outside target")
                            continue
                        shutil.rmtree(target_skill_dir)
                    shutil.copytree(
                        skill_dir,
                        target_skill_dir,
                        ignore=shutil.ignore_patterns(
                            "__pycache__", "*.pyc", ".DS_Store"
                        ),
                    )
                    # Resolve template variables in SKILL.md
                    template_vars = _resolve_template_paths(base_path, scope)
                    _resolve_skill_templates(target_skill_dir, template_vars)
                    installed += 1
                except Exception as e:
                    failed += 1
                    failed_names.append(f"{skill_dir.name}: {e}")

    else:
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
                            failed_names.append(
                                f"{sub_dir.name}: symlink outside target"
                            )
                            continue
                        shutil.rmtree(target_sub)
                    shutil.copytree(
                        sub_dir,
                        target_sub,
                        ignore=shutil.ignore_patterns(
                            "__pycache__", "*.pyc", ".DS_Store"
                        ),
                    )
                    installed += 1
                except Exception as e:
                    failed += 1
                    failed_names.append(f"{sub_dir.name}: {e}")

    return installed, skipped, failed, failed_names


def install_claude_sc_md(base_path: Path = None, force: bool = False) -> Tuple[bool, str]:
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


def install_hooks_and_scripts(
    base_path: Path = None,
    force: bool = False,
    scope: str = "user"
) -> Tuple[int, int, int, List[str]]:
    """
    Install hooks configuration and scripts.

    This function:
    1. Copies scripts from src/superclaude/scripts/ to .claude/superclaude/scripts/
    2. Transforms hooks/hooks.json with correct paths and copies to .claude/hooks/hooks.json

    Args:
        base_path: Base installation path (default: ~/.claude)
        force: Force reinstall
        scope: Installation scope ("user", "project", or "target")

    Returns:
        Tuple of (installed_count, skipped_count, failed_count, messages)
    """
    if base_path is None:
        base_path = Path.home() / ".claude"

    package_root = _get_package_root()
    scripts_source = package_root / "scripts"
    hooks_source = package_root / "hooks"
    scripts_target = base_path / "superclaude" / "scripts"
    hooks_target = base_path / "hooks"

    installed = 0
    skipped = 0
    failed = 0
    messages = []

    # Determine scripts path based on scope
    # - project/local scope: $CLAUDE_PROJECT_DIR-based path (portable, CWD-independent)
    #   Docs: https://code.claude.com/docs/en/hooks — hook CWD is NOT guaranteed project root;
    #   $CLAUDE_PROJECT_DIR is the official env var for project-root-relative paths.
    # - user/target scope: absolute path (works from anywhere)
    if scope in ("project", "local"):
        scripts_path_for_hooks = "$CLAUDE_PROJECT_DIR/.claude/superclaude/scripts"
    else:
        scripts_path_for_hooks = str(scripts_target.resolve())

    # 1. Copy scripts to .claude/superclaude/scripts/
    if scripts_source.exists():
        scripts_target.mkdir(parents=True, exist_ok=True)

        patterns = ["*.sh", "*.py"]
        for pattern in patterns:
            for source_file in scripts_source.glob(pattern):
                # Skip __init__.py and README files
                if source_file.name == "__init__.py" or source_file.stem.upper() == "README":
                    continue

                target_file = scripts_target / source_file.name
                if target_file.exists() and not force:
                    skipped += 1
                    continue

                try:
                    shutil.copy2(source_file, target_file)
                    installed += 1
                except Exception as e:
                    failed += 1
                    messages.append(f"Failed to copy {source_file.name}: {e}")

    # 2. Read and transform hooks.json once (reused for copy + merge)
    hooks_json_file = hooks_source / "hooks.json"
    hooks_content_transformed = None

    if hooks_json_file.exists():
        try:
            raw_content = hooks_json_file.read_text(encoding="utf-8")
            # Use forward slashes for JSON compatibility (works on all platforms)
            scripts_path_json_safe = scripts_path_for_hooks.replace("\\", "/")
            # Python binary: bake absolute path to the Python running the installer.
            # Avoids Windows `python3` absence (legacy installer), Store Python edge cases,
            # and cross-shell $PATH differences. Matches pipx/uv/pre-commit pattern.
            # Forward slashes for JSON compatibility; escape inner quotes if path has spaces
            # (e.g., "C:/Program Files/Python/python.exe" → \"C:/Program Files/...\" for JSON).
            python_bin_json_safe = sys.executable.replace("\\", "/")
            if " " in python_bin_json_safe:
                python_bin_json_safe = f'\\"{python_bin_json_safe}\\"'
            hooks_content_transformed = (
                raw_content
                .replace("{{SCRIPTS_PATH}}", scripts_path_json_safe)
                .replace("{{PYTHON_BIN}}", python_bin_json_safe)
            )
        except OSError as e:
            failed += 1
            messages.append(f"Failed to read hooks.json: {e}")
    else:
        messages.append("hooks.json not found, skipping hooks configuration")

    # 2a. Copy transformed hooks.json to .claude/hooks/hooks.json
    if hooks_content_transformed is not None:
        hooks_target.mkdir(parents=True, exist_ok=True)
        target_hooks_json = hooks_target / "hooks.json"

        if target_hooks_json.exists() and not force:
            messages.append("hooks.json already exists (use --force to update)")
            skipped += 1
        else:
            try:
                target_hooks_json.write_text(hooks_content_transformed, encoding="utf-8")
                installed += 1
                messages.append(f"hooks.json installed (scripts path: {scripts_path_for_hooks})")
            except OSError as e:
                failed += 1
                messages.append(f"Failed to install hooks.json: {e}")

    # 2b. Merge hooks to settings.json (ensures Claude Code recognizes hooks)
    if hooks_content_transformed is not None:
        try:
            hooks_config = json.loads(hooks_content_transformed)
            merge_success, merge_msg = merge_hooks_to_settings(
                base_path=base_path,
                hooks_config=hooks_config,
                scope=scope,
                force=force
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
    base_path: Path = None,
    force: bool = False,
    scope: str = "user"
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

    # Install hooks and scripts
    hooks_installed, hooks_skipped, hooks_failed, hooks_messages = install_hooks_and_scripts(
        base_path, force, scope
    )
    total_installed += hooks_installed
    total_skipped += hooks_skipped
    total_failed += hooks_failed

    if hooks_installed > 0:
        messages.append(f"✅ Hooks and scripts: {hooks_installed} installed")
    if hooks_skipped > 0:
        messages.append(f"⏭️  Hooks and scripts: {hooks_skipped} skipped")
    if hooks_failed > 0:
        messages.append(f"❌ Hooks and scripts: {hooks_failed} failed")
    for msg in hooks_messages:
        messages.append(f"   {msg}")

    # Install CLAUDE_SC.md
    success, msg = install_claude_sc_md(base_path, force)
    messages.append(f"{'✅' if success else '❌'} {msg}")

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
            messages.append(f"⚠️  {update_msg}")
            messages.append(f"   Add manually: {CLAUDE_SC_IMPORT}")

    # For local scope: add .gitignore block (CC doesn't auto-ignore agents/skills/etc.)
    if scope == "local":
        project_root = base_path.parent
        gi_ok, gi_msg = add_local_gitignore(project_root)
        messages.append(f"{'✅' if gi_ok else '⚠️ '} {gi_msg}")

    # Summary
    messages.append("")
    messages.append(f"📊 Summary: {total_installed} installed, {total_skipped} skipped, {total_failed} failed")
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
        base_path = target_path.parent if target_path.name == "commands" else target_path
    else:
        base_path = None
    return install_all(base_path=base_path, force=force)
