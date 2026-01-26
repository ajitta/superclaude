"""Shared utility functions for SuperClaude."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def word_overlap_ratio(text1: str, text2: str) -> float:
    """Jaccard similarity coefficient between word sets.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Ratio of shared words to total unique words (0.0-1.0)
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)


def word_overlap_count(text1: str, text2: str) -> int:
    """Count of overlapping words between two texts.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Number of shared words
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    return len(words1 & words2)


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
