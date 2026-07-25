"""Shared utility functions for SuperClaude."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_json(path: Path, data: Any, indent: int = 2) -> None:
    """Write JSON data atomically using temp file + os.replace.

    Prevents data corruption from crashes during write by writing to
    a temporary file first, then atomically replacing the target.

    Args:
        path: Target file path
        data: JSON-serializable data
        indent: JSON indentation level
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=indent)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def get_skill_directories() -> list[Path]:
    """Get all skill directories to scan.

    Project-local skills are found via project_root(), not the CWD: a hook
    running from a subdirectory used to see only user-scope skills, so the
    installed-skill count under-reported project and local scope installs.

    Returns:
        List of skill base directories (global, project-local)
    """
    return [
        Path.home() / ".claude" / "skills",
        project_root() / ".claude" / "skills",
    ]


def project_root() -> Path:
    """Project root for hook-relative paths.

    Hook CWD is not guaranteed to be the project root, so $CLAUDE_PROJECT_DIR is
    the anchor whenever Claude Code provides it. See the hooks reference at
    'https://code.claude.com/docs/en/hooks'.

    Returns:
        $CLAUDE_PROJECT_DIR if set, else the current working directory
    """
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


def claude_base() -> Path:
    """Resolve the .claude directory of the install whose hooks are running.

    Project and local scope keep framework content under
    ``<project>/.claude/superclaude``, so its presence identifies the active
    scope. User scope is the fallback.

    Returns:
        Project-local .claude when a scoped install is present, else ~/.claude
    """
    root = project_root() / ".claude"
    if (root / "superclaude").exists():
        return root
    return Path.home() / ".claude"


def hook_state_dir() -> Path:
    """Runtime state directory for hook scripts, scoped to the active install.

    Keeping state under the install's own .claude means a local-scope install
    leaves no footprint in ~/.claude, and ``superclaude uninstall`` can remove it
    with the rest of the scope.

    Returns:
        <claude_base>/.superclaude_hooks
    """
    return claude_base() / ".superclaude_hooks"
