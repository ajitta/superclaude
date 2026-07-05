"""Frontmatter parsing for SuperClaude content files.

Provides parse_frontmatter() for extracting YAML frontmatter from
markdown content (consumed by the CLI). Inline-hook parsing machinery
was removed as dead code — frontmatter hooks are handled natively by
Claude Code, not by this module.
"""

from __future__ import annotations

import re

# Try to import yaml, fallback to basic parsing if unavailable
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


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
