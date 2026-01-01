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

    # Confidence check triggers
    confidence_pattern = r"(implement|build|create|add feature|before starting)"
    if re.search(confidence_pattern, prompt_lower):
        hints.append(
            "INSTRUCTION: Consider using /confidence-check skill before implementation"
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
