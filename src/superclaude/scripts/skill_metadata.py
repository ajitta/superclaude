#!/usr/bin/env python3
"""Skill metadata utilities.

Provides skill discovery, agent routing, context detection, and inline hooks.
Trigger logic has been consolidated into context_trigger_map.py.

Renamed from skill_activator.py in v4.0 refactoring.
"""

from __future__ import annotations

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
    # Added for completeness — these agents exist in FLAGS.md persona_index
    "business-panel-experts",
    "simplicity-guide",
    # Claude Code built-in agent type (no .md file, used by skills like ship)
    "general-purpose",
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
