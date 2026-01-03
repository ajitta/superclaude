#!/usr/bin/env python3
"""Skill Activator Hook (Python)
Evaluates user prompt against skill triggers for reliable activation
Cross-platform compatible (Windows/macOS/Linux)
"""
import re
import sys


def check_skill_triggers(prompt: str) -> list[str]:
    """Check prompt against skill triggers and return activation hints."""
    hints = []
    prompt_lower = prompt.lower()

    # Confidence check triggers (aligned with SKILL.md)
    confidence_patterns = [
        r"(implement|build|create|add feature|fix bug|refactor)",  # Action triggers
        r"(check confidence|confidence check)",  # Direct triggers
        r"(am i ready|ready to start)",  # Readiness triggers
        r"(verify before|before implementing|pre-implementation)",  # Pre-check triggers
        r"(readiness check|readiness-check)",  # Explicit check triggers
        r"(확인해줘|검증해줘|준비됐|시작하기 전)",  # Korean triggers
    ]
    if any(re.search(p, prompt_lower) for p in confidence_patterns):
        hints.append(
            "INSTRUCTION: Use /confidence-check skill before implementation. "
            "Assess: duplicates, architecture, docs, OSS refs, root cause."
        )

    # Research triggers
    research_pattern = (
        r"(research|investigate|find out|what is|how does|latest|current)"
    )
    if re.search(research_pattern, prompt_lower):
        hints.append("INSTRUCTION: Consider using /sc:research skill for web research")

    # Business panel triggers
    business_pattern = r"(business|strategy|market|competitive|porter|christensen)"
    if re.search(business_pattern, prompt_lower):
        hints.append(
            "INSTRUCTION: Consider using /sc:business-panel skill for expert analysis"
        )

    return hints


def main():
    # Read prompt from stdin (passed by Claude Code)
    prompt = sys.stdin.read() if not sys.stdin.isatty() else ""

    # Execute check and print hints
    hints = check_skill_triggers(prompt)
    for hint in hints:
        print(hint)


if __name__ == "__main__":
    main()
    sys.exit(0)
