#!/usr/bin/env python3
"""Skill Activator Hook (Python)

Evaluates user prompt against skill triggers for reliable activation.
Cross-platform compatible (Windows/macOS/Linux).

v2.1.0 Features:
- Frontmatter parsing (context, agent, user-invocable, allowed-tools, hooks)
- Agent routing based on skill configuration
- Inline hooks support
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superclaude.hooks.inline_hooks import InlineHooks

# Valid agent types for skill routing
VALID_AGENTS = {
    "system-architect",
    "backend-architect",
    "frontend-architect",
    "security-engineer",
    "quality-engineer",
    "devops-architect",
    "pm-agent",
    "performance-engineer",
    "refactoring-expert",
    "root-cause-analyst",
    "python-expert",
    "technical-writer",
    "deep-research-agent",
    "requirements-analyst",
    "socratic-mentor",
    "learning-guide",
    "self-review",
    "repo-index",
}


def get_skill_directories() -> list[Path]:
    """Get skill directories to search."""
    return [
        Path.home() / ".claude" / "skills",
        Path.home() / ".claude" / "superclaude" / "skills",
        Path.cwd() / ".claude" / "skills",
    ]


def find_skill_manifest(skill_name: str) -> Path | None:
    """Find SKILL.md manifest for a skill.

    Args:
        skill_name: Name of the skill to find

    Returns:
        Path to SKILL.md or None if not found
    """
    for base in get_skill_directories():
        if not base.exists():
            continue

        # Try both kebab-case and snake_case
        for name_variant in [skill_name, skill_name.replace("-", "_")]:
            skill_dir = base / name_variant
            if skill_dir.exists():
                for manifest_name in ["SKILL.md", "skill.md"]:
                    manifest = skill_dir / manifest_name
                    if manifest.exists():
                        return manifest
    return None


def get_agent_for_skill(skill_name: str) -> str | None:
    """Get the agent type configured for a skill.

    Args:
        skill_name: Name of the skill

    Returns:
        Agent name if configured and valid, None otherwise
    """
    try:
        from superclaude.hooks.inline_hooks import (
            get_skill_agent,
            parse_skill_frontmatter,
        )

        manifest = find_skill_manifest(skill_name)
        if not manifest:
            return None

        frontmatter = parse_skill_frontmatter(manifest)
        agent = get_skill_agent(frontmatter)

        if agent and agent in VALID_AGENTS:
            return agent
    except ImportError:
        pass

    return None


def should_fork_context(skill_name: str) -> bool:
    """Check if skill should run in forked sub-agent context.

    Args:
        skill_name: Name of the skill

    Returns:
        True if context is 'fork', False otherwise
    """
    try:
        from superclaude.hooks.inline_hooks import (
            get_skill_context,
            parse_skill_frontmatter,
        )

        manifest = find_skill_manifest(skill_name)
        if not manifest:
            return False

        frontmatter = parse_skill_frontmatter(manifest)
        return get_skill_context(frontmatter) == "fork"
    except ImportError:
        return False


def get_skill_inline_hooks(skill_name: str) -> "InlineHooks | None":
    """Get inline hooks for a skill.

    Args:
        skill_name: Name of the skill

    Returns:
        InlineHooks object or None if not found/no hooks
    """
    try:
        from superclaude.hooks.inline_hooks import (
            parse_inline_hooks,
            parse_skill_frontmatter,
        )

        manifest = find_skill_manifest(skill_name)
        if not manifest:
            return None

        frontmatter = parse_skill_frontmatter(manifest)
        hooks = parse_inline_hooks(frontmatter)

        if hooks.has_hooks():
            return hooks
    except ImportError:
        pass

    return None


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
