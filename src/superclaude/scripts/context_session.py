#!/usr/bin/env python3
"""Session state, path resolution, and configuration constants.

Leaf dependency for the context loader system. All session state, path resolution,
and configuration constants live here. Other modules (context_trigger_map,
context_injection, context_loader) import from this module.
"""

import hashlib
import os
from pathlib import Path

# --- Configuration constants (read from environment) ---
INJECT_MODE: bool = os.environ.get("CLAUDE_CONTEXT_INJECT", "1").lower() in ("1", "true", "yes")
MAX_TOKENS_ESTIMATE: int = int(os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS", "8000"))
USE_INSTRUCTIONS: bool = os.environ.get("CLAUDE_CONTEXT_USE_INSTRUCTIONS", "1") == "1"
SHOW_SKILLS_SUMMARY: bool = os.environ.get("CLAUDE_SHOW_SKILLS", "1") == "1"
CHARS_PER_TOKEN: int = 4

# --- Path resolution ---

def get_base_path() -> Path:
    """Get base path for context files.

    Priority:
    1. SUPERCLAUDE_PATH environment variable (explicit override)
    2. Project-local: ./.claude/superclaude (if exists)
    3. User scope: ~/.claude/superclaude (default)
    """
    if os.environ.get("SUPERCLAUDE_PATH"):
        return Path(os.environ["SUPERCLAUDE_PATH"])

    project_path = Path.cwd() / ".claude" / "superclaude"
    if project_path.exists():
        return project_path

    return Path.home() / ".claude" / "superclaude"


BASE_PATH: Path = get_base_path()

# --- Session cache ---
SESSION_ID: str = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
_CACHE_DIR: Path = Path.home() / ".claude" / ".superclaude_hooks"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE: Path = _CACHE_DIR / f"claude_context_{SESSION_ID}.txt"


def get_loaded_contexts() -> set[str]:
    """Read already-loaded contexts from session cache."""
    if CACHE_FILE.exists():
        return set(CACHE_FILE.read_text().strip().split("\n"))
    return set()


def mark_as_loaded(contexts: str | list[str]) -> None:
    """Mark context(s) as loaded in session cache. Accepts single or batch."""
    loaded = get_loaded_contexts()
    if isinstance(contexts, str):
        loaded.add(contexts)
    else:
        loaded.update(contexts)
    CACHE_FILE.write_text("\n".join(loaded))


def estimate_tokens(content: str) -> int:
    """Estimate token count from character count."""
    return len(content) // CHARS_PER_TOKEN
