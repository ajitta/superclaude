#!/usr/bin/env python3
"""PreToolUse hook for confidence-check skill web tool validation.

Provides lightweight guardrails for WebSearch/WebFetch calls during
confidence-check runs. The hook is non-blocking by default and injects
additional context to keep evidence collection focused.
"""

from __future__ import annotations

import json
import sys


def _build_additional_context(tool_name: str, tool_input: dict) -> str | None:
    """Build context guidance for confidence-check web lookups."""
    if tool_name == "WebSearch":
        query = str(tool_input.get("query", "")).strip()
        if not query:
            return (
                "Confidence-check: provide a specific WebSearch query. "
                "Target official docs or credible implementation references."
            )
        return (
            "Confidence-check: prioritize official documentation and working "
            "reference implementations. Capture source URLs for validation."
        )

    if tool_name == "WebFetch":
        url = str(tool_input.get("url", "")).strip()
        if not url:
            return (
                "Confidence-check: provide a URL to fetch. Prefer official "
                "docs, standards, or authoritative technical sources."
            )
        return (
            "Confidence-check: verify fetched content relevance and extract "
            "evidence that supports implementation decisions."
        )

    return None


def main() -> None:
    """Read hook input and emit optional PreToolUse response JSON."""
    try:
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
        if not stdin_data:
            return

        payload = json.loads(stdin_data)
        tool_name = str(payload.get("tool_name", "")).strip()
        tool_input = payload.get("tool_input", {})
        if not isinstance(tool_input, dict):
            tool_input = {}

        additional_context = _build_additional_context(tool_name, tool_input)
        if not additional_context:
            return

        print(
            json.dumps(
                {"decision": "allow", "additionalContext": additional_context},
                ensure_ascii=True,
            )
        )
    except (json.JSONDecodeError, OSError):
        # Non-blocking by design.
        return


if __name__ == "__main__":
    main()
    sys.exit(0)
