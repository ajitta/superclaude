#!/usr/bin/env python3
"""Circuit-breaker hook: stop runaway loops of identical errors.

Contract:
- PostToolUse(Edit|Write|Bash): record an error signature when tool_response
  indicates failure. Successful calls clear counters for the same signature.
- PreToolUse(Edit|Write|Bash): if a matching signature has accumulated
  >=5 error entries within a 15-minute window, block and prompt for a
  change of approach.

State lives at $CLAUDE_PROJECT_DIR/.claude/loop_guard_state.json (or cwd
fallback). Fail-open on any error. Opt out with SUPERCLAUDE_LOOP_GUARD=0.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

BLOCK_THRESHOLD = 5
WINDOW_SECONDS = 15 * 60


def _state_path() -> Path:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(root) / ".claude" / "loop_guard_state.json"


def _approve() -> None:
    print(json.dumps({"decision": "approve"}))


def _block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def _load_state(path: Path) -> dict:
    try:
        if not path.is_file():
            return {"entries": []}
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "entries" not in data:
            return {"entries": []}
        if not isinstance(data["entries"], list):
            return {"entries": []}
        return data
    except (OSError, json.JSONDecodeError):
        return {"entries": []}


def _save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(state, f)
    except OSError:
        # Fail open — don't crash the hook on write failure
        pass


def _input_fingerprint(tool_name: str, tool_input: dict) -> str:
    """Build a stable fingerprint from the tool's primary input field."""
    if not isinstance(tool_input, dict):
        return ""
    if tool_name == "Bash":
        primary = str(tool_input.get("command", ""))
    elif tool_name in ("Edit", "Write", "NotebookEdit"):
        primary = str(tool_input.get("file_path", ""))
    else:
        primary = str(next(iter(tool_input.values()), ""))
    return primary.strip()[:120]


def _signature(tool_name: str, tool_input: dict) -> str:
    return f"{tool_name}::{_input_fingerprint(tool_name, tool_input)}"


def _is_error(tool_response) -> bool:
    """Detect whether a tool_response indicates failure.

    Heuristics across tools: non-zero exit_code (Bash), or explicit 'error'
    field with content (Edit/Write/generic), or 'is_error' flag.
    """
    if not isinstance(tool_response, dict):
        return False
    if tool_response.get("is_error") is True:
        return True
    exit_code = tool_response.get("exit_code")
    if isinstance(exit_code, int) and exit_code != 0:
        return True
    error = tool_response.get("error")
    if isinstance(error, str) and error.strip():
        return True
    return False


def _prune(entries: list, now: float) -> list:
    cutoff = now - WINDOW_SECONDS
    out = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        ts = e.get("ts")
        if not isinstance(ts, (int, float)):
            continue
        if ts < cutoff:
            continue
        out.append(e)
    return out


def _handle_post(data: dict) -> None:
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}
    tool_response = data.get("tool_response", {})
    sig = _signature(tool_name, tool_input)
    path = _state_path()
    state = _load_state(path)
    now = time.time()
    entries = _prune(state.get("entries", []), now)
    if _is_error(tool_response):
        entries.append({"signature": sig, "ts": now, "kind": "error"})
    else:
        # Successful call on this signature clears its error entries
        entries = [e for e in entries if e.get("signature") != sig]
    state["entries"] = entries
    _save_state(path, state)
    _approve()


def _handle_pre(data: dict) -> None:
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}
    sig = _signature(tool_name, tool_input)
    path = _state_path()
    state = _load_state(path)
    now = time.time()
    entries = _prune(state.get("entries", []), now)
    count = sum(
        1
        for e in entries
        if e.get("signature") == sig and e.get("kind") == "error"
    )
    if count >= BLOCK_THRESHOLD:
        _block(
            f"Circuit breaker: same tool call signature failed {count} times "
            f"in the last 15 min. Change your approach — try a different "
            f"tool, a different file/command, or ask the user for guidance "
            f"before retrying. (Set SUPERCLAUDE_LOOP_GUARD=0 to disable.)"
        )
        return
    _approve()


def main() -> None:
    try:
        if os.environ.get("SUPERCLAUDE_LOOP_GUARD", "1") == "0":
            _approve()
            return

        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data.strip():
            _approve()
            return

        try:
            data = json.loads(stdin_data)
        except json.JSONDecodeError:
            _approve()
            return

        event = data.get("hook_event_name", "")
        if event == "PreToolUse":
            _handle_pre(data)
        elif event == "PostToolUse":
            _handle_post(data)
        else:
            _approve()
    except Exception:
        # Catch-all fail-open — never break the user's flow
        _approve()


if __name__ == "__main__":
    main()
