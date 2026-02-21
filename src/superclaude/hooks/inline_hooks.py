"""Inline Hooks Parser for SuperClaude v2.1.0 Compatibility

Parses inline hooks from skill/agent/command frontmatter.
Supports PreToolUse, PostToolUse, and Stop hook types.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# Try to import yaml, fallback to basic parsing if unavailable
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class InlineHook:
    """Represents a single inline hook definition."""

    type: Literal["command", "prompt"]
    command: str
    matcher: str | None = None
    timeout: int = 30
    once: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "type": self.type,
            "command": self.command,
            "timeout": self.timeout,
        }
        if self.matcher:
            result["matcher"] = self.matcher
        if self.once:
            result["once"] = self.once
        return result


@dataclass
class InlineHooks:
    """Container for all inline hooks from a frontmatter."""

    pre_tool_use: list[InlineHook] = field(default_factory=list)
    post_tool_use: list[InlineHook] = field(default_factory=list)
    stop: list[InlineHook] = field(default_factory=list)

    def has_hooks(self) -> bool:
        """Check if any hooks are defined."""
        return bool(self.pre_tool_use or self.post_tool_use or self.stop)

    def to_claude_code_format(self) -> dict:
        """Convert hooks to Claude Code's native nested format.

        Groups hooks by matcher and outputs the structure Claude Code expects:
            PreToolUse:
              - matcher: "pattern"
                hooks:
                  - type: command
                    command: ...
        """
        result: dict = {}
        for key, hooks in [
            ("PreToolUse", self.pre_tool_use),
            ("PostToolUse", self.post_tool_use),
            ("Stop", self.stop),
        ]:
            if not hooks:
                continue
            groups: dict[str | None, list[dict]] = {}
            for hook in hooks:
                groups.setdefault(hook.matcher, []).append(hook.to_dict())
            entries = []
            for matcher, hook_dicts in groups.items():
                # Strip matcher from inner hook dicts (it belongs at the outer level)
                cleaned = [{k: v for k, v in d.items() if k != "matcher"} for d in hook_dicts]
                entry: dict = {}
                if matcher:
                    entry["matcher"] = matcher
                entry["hooks"] = cleaned
                entries.append(entry)
            result[key] = entries
        return result


def parse_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Parsed frontmatter as dictionary, empty dict if not found
    """
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)

    if HAS_YAML:
        try:
            return yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            return {}

    # Basic fallback parsing for simple key: value pairs
    result: dict = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _get_meta_value(frontmatter: dict, key: str, default=None):
    """Get a value from frontmatter, checking metadata first then root.

    Claude Code skill schema only supports a fixed set of top-level attributes.
    Custom attributes (context, agent, allowed-tools, hooks, etc.) are stored
    under the ``metadata`` key. This helper checks ``metadata`` first, then
    falls back to root-level for backward compatibility with older manifests.

    Args:
        frontmatter: Parsed frontmatter dictionary
        key: The attribute key to look up
        default: Default value if not found

    Returns:
        The value from metadata or root, or default
    """
    metadata = frontmatter.get("metadata")
    if isinstance(metadata, dict) and key in metadata:
        return metadata[key]
    return frontmatter.get(key, default)


def parse_inline_hooks(frontmatter: dict) -> InlineHooks:
    """Parse inline hooks from frontmatter dictionary.

    Args:
        frontmatter: Parsed frontmatter dictionary

    Returns:
        InlineHooks container with parsed hooks
    """
    hooks_data = _get_meta_value(frontmatter, "hooks", {})
    if not hooks_data or not isinstance(hooks_data, dict):
        return InlineHooks()

    result = InlineHooks()

    # Parse PreToolUse hooks
    if "PreToolUse" in hooks_data:
        result.pre_tool_use = _parse_hook_list(hooks_data["PreToolUse"])

    # Parse PostToolUse hooks
    if "PostToolUse" in hooks_data:
        result.post_tool_use = _parse_hook_list(hooks_data["PostToolUse"])

    # Parse Stop hooks
    if "Stop" in hooks_data:
        result.stop = _parse_hook_list(hooks_data["Stop"])

    return result


def _parse_hook_list(hooks_list: list) -> list[InlineHook]:
    """Parse a list of hook definitions.

    Supports two formats:
    - Nested (Claude Code native): entry has 'matcher' + 'hooks' array
    - Flat (legacy): entry has 'command' directly

    Args:
        hooks_list: List of hook dictionaries

    Returns:
        List of InlineHook objects
    """
    if not isinstance(hooks_list, list):
        return []

    result = []
    for entry in hooks_list:
        if not isinstance(entry, dict):
            continue

        # Nested format: entry has 'hooks' key with a list value
        if "hooks" in entry and isinstance(entry["hooks"], list):
            outer_matcher = entry.get("matcher")
            for hook_dict in entry["hooks"]:
                if not isinstance(hook_dict, dict):
                    continue
                command = hook_dict.get("command", "")
                if not command:
                    continue
                result.append(
                    InlineHook(
                        type=hook_dict.get("type", "command"),
                        command=command,
                        matcher=outer_matcher,
                        timeout=hook_dict.get("timeout", 30),
                        once=hook_dict.get("once", False),
                    )
                )
        else:
            # Flat format (legacy): command is at the same level
            command = entry.get("command", "")
            if not command:
                continue
            result.append(
                InlineHook(
                    type=entry.get("type", "command"),
                    command=command,
                    matcher=entry.get("matcher"),
                    timeout=entry.get("timeout", 30),
                    once=entry.get("once", False),
                )
            )

    return result


def parse_skill_frontmatter(skill_path: Path) -> dict:
    """Parse frontmatter from a skill file.

    Args:
        skill_path: Path to SKILL.md or similar file

    Returns:
        Parsed frontmatter dictionary
    """
    if not skill_path.exists():
        return {}

    content = skill_path.read_text(encoding="utf-8")
    return parse_frontmatter(content)


def get_skill_context(frontmatter: dict) -> Literal["inline", "fork"]:
    """Get the execution context for a skill.

    Args:
        frontmatter: Parsed frontmatter dictionary

    Returns:
        'inline' (default) or 'fork' for sub-agent execution
    """
    context: str = _get_meta_value(frontmatter, "context", "inline")
    if context in ("inline", "fork"):
        return context  # type: ignore[return-value]
    return "inline"


def get_skill_agent(frontmatter: dict) -> str | None:
    """Get the agent type for skill execution.

    Args:
        frontmatter: Parsed frontmatter dictionary

    Returns:
        Agent name or None if not specified
    """
    return _get_meta_value(frontmatter, "agent")


