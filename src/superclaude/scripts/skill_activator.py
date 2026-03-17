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

import json
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
    "project-manager",
    "performance-engineer",
    "refactoring-expert",
    "root-cause-analyst",
    "python-expert",
    "technical-writer",
    "deep-researcher",
    "requirements-analyst",
    "socratic-mentor",
    "learning-guide",
    "self-review",
    "repo-index",
}


def get_skill_directories() -> list[Path]:
    """Get skill directories to search."""
    from superclaude.utils import get_skill_directories as _get
    return _get()


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
    """Check prompt against skill triggers and return activation hints.

    Only fires on explicit triggers to avoid noise on normal coding prompts.
    Research/business context injection is handled by context_loader.py.
    """
    hints = []
    prompt_lower = prompt.lower()

    # Confidence check — explicit triggers only (no generic "implement"/"build")
    confidence_patterns = [
        r"(check confidence|confidence check|/confidence-check|--confidence)",
        r"(am i ready|ready to start)",
        r"(verify before|before implementing|pre-implementation)",
        r"(readiness check|readiness-check)",
        r"(확인해줘|검증해줘|준비됐|시작하기 전)",
    ]
    if any(re.search(p, prompt_lower) for p in confidence_patterns):
        hints.append(
            "INSTRUCTION: Use /confidence-check skill before implementation. "
            "Assess: duplicates, architecture, docs, OSS refs, root cause."
        )

    return hints


def _extract_prompt(stdin_data: str) -> str:
    """Extract prompt from UserPromptSubmit JSON input, with raw text fallback."""
    try:
        data = json.loads(stdin_data)
        return data.get("prompt", stdin_data)
    except (json.JSONDecodeError, TypeError):
        return stdin_data


def main() -> None:
    # Read and parse JSON input from Claude Code
    stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
    prompt = _extract_prompt(stdin_data)

    # Execute check and print hints
    hints = check_skill_triggers(prompt)
    for hint in hints:
        print(hint)


if __name__ == "__main__":
    main()
    sys.exit(0)
