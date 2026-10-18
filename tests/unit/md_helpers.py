"""Markdown parsers the content-structure tests share.

Not a test module (pytest's default ``python_files`` skips it) — a helper the
agent, command, mode, content and cross-reference tests import so each parser has
one definition site instead of a byte-identical copy per test file.
"""

import re
from pathlib import Path

import yaml

# ``---`` on the first line, the closing ``---`` on its own line; the body (if
# any) follows the match.
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Split markdown into (raw frontmatter, body); frontmatter is None if absent."""
    match = _FRONTMATTER.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end() :]


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter from markdown text as ``key: value`` lines."""
    raw, _ = split_frontmatter(text)
    if raw is None:
        return {}
    fields = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def load_frontmatter(path: Path) -> dict:
    """Frontmatter of ``path`` parsed as YAML; fails the test when there is none."""
    raw, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    assert raw is not None, f"{path.name} has no frontmatter"
    return yaml.safe_load(raw) or {}


def markdown_body(path: Path) -> str:
    """Text of ``path`` after its frontmatter (the whole file when there is none)."""
    return split_frontmatter(path.read_text(encoding="utf-8"))[1]


def extract_xml_attr(text: str, tag: str, attr: str) -> str | None:
    """Extract an attribute value from the first occurrence of an XML tag."""
    pattern = rf"<{tag}\b[^>]*\b{attr}=[\"']([^\"']*)[\"']"
    match = re.search(pattern, text)
    return match.group(1) if match else None


def extract_xml_content(text: str, tag: str) -> str | None:
    """Extract text content from the first occurrence of an XML tag."""
    pattern = rf"<{tag}\b[^>]*>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None
