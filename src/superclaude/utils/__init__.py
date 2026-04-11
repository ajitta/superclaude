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

    Returns:
        List of skill base directories (global, superclaude, project-local)
    """
    return [
        Path.home() / ".claude" / "skills",
        Path.home() / ".claude" / "superclaude" / "skills",
        Path.cwd() / ".claude" / "skills",
    ]
