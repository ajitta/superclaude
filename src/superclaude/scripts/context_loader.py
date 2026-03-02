#!/usr/bin/env python3
"""UserPromptSubmit hook entrypoint.

Parses stdin, orchestrates trigger matching + injection.
Delegates to context_trigger_map (matching) and context_injection (output).

v4.0: Refactored from 495-line monolith into 4-module system:
  - context_session.py    — session state, paths, config constants
  - context_trigger_map.py — unified trigger matching (SKILL > MODE > MCP > CORE)
  - context_injection.py  — hybrid injection engine (full/compact/instruction/hint)
  - context_loader.py     — this file, entrypoint only (~50 lines)
"""

import json
import sys

from superclaude.scripts.context_injection import generate_output
from superclaude.scripts.context_session import INJECT_MODE
from superclaude.scripts.context_trigger_map import match_triggers


def _extract_prompt(stdin_data: str) -> str:
    """Extract prompt from UserPromptSubmit JSON input, with raw text fallback."""
    try:
        data = json.loads(stdin_data)
        return data.get("prompt", stdin_data)
    except (json.JSONDecodeError, TypeError):
        return stdin_data


def main() -> None:
    """Entrypoint: read stdin → match triggers → generate output."""
    stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
    prompt = _extract_prompt(stdin_data)

    if not prompt.strip():
        return

    if not INJECT_MODE:
        return

    matches = match_triggers(prompt)
    if not matches:
        # Still output skills summary even with no matches
        generate_output([], prompt)
        return

    generate_output(matches, prompt)


if __name__ == "__main__":
    main()
    sys.exit(0)
