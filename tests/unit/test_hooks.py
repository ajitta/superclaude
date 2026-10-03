"""Unit tests for SuperClaude hooks module.

Tests inline_hooks.py functionality.
"""

from __future__ import annotations


class TestInlineHooks:
    """Tests for inline_hooks.py functionality."""

    def test_parse_frontmatter_basic(self):
        """Test basic frontmatter parsing."""
        from superclaude.hooks.inline_hooks import parse_frontmatter

        content = """---
name: test-skill
description: A test skill
---
Content here
"""
        fm = parse_frontmatter(content)
        assert fm["name"] == "test-skill"
        assert fm["description"] == "A test skill"

    def test_parse_frontmatter_with_lists(self):
        """Test frontmatter parsing with YAML lists in metadata."""
        from superclaude.hooks.inline_hooks import parse_frontmatter

        content = """---
name: test-skill
metadata:
  allowed-tools:
    - Read
    - Grep
    - WebFetch
---
"""
        fm = parse_frontmatter(content)
        assert fm["name"] == "test-skill"
        assert fm["metadata"]["allowed-tools"] == ["Read", "Grep", "WebFetch"]

    def test_parse_frontmatter_with_lists_root_compat(self):
        """Test frontmatter parsing with YAML lists at root (backward compat)."""
        from superclaude.hooks.inline_hooks import parse_frontmatter

        content = """---
name: test-skill
allowed-tools:
  - Read
  - Grep
  - WebFetch
---
"""
        fm = parse_frontmatter(content)
        assert fm["name"] == "test-skill"
        assert fm["allowed-tools"] == ["Read", "Grep", "WebFetch"]
