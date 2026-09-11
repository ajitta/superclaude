"""Structural validation for shipped output styles in src/superclaude/output-styles/.

An output style is read natively by Claude Code: the frontmatter fields are
Claude Code's contract (https://code.claude.com/docs/en/output-styles) and the
body is sent verbatim as system-prompt instructions with every request. Two
guarantees matter and nothing else checks them:

* ``keep-coding-instructions: true`` — without it Claude Code drops its own
  software-engineering instructions, so a style shipped by a coding framework
  would silently stop Claude scoping and verifying its work.
* Language-neutral text — the style ships to every user. A Korean example
  phrase in a global style reads as noise to everyone else, so no script other
  than Latin may appear.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pytest

STYLES_DIR = (
    Path(__file__).parent.parent.parent / "src" / "superclaude" / "output-styles"
)
STYLE_FILES = sorted(p for p in STYLES_DIR.glob("*.md") if p.name != "README.md")
STYLE_IDS = [f.stem for f in STYLE_FILES]

# Sent with every request: the budget is a token cost every turn, not a style choice.
MAX_BODY_WORDS = 600

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def _split(text: str) -> tuple[dict[str, str], str]:
    m = _FRONTMATTER.match(text)
    assert m, "no YAML frontmatter"
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, m.group(2)


@pytest.fixture(params=STYLE_FILES, ids=STYLE_IDS)
def style(request) -> tuple[str, dict[str, str], str]:
    path: Path = request.param
    fields, body = _split(path.read_text(encoding="utf-8"))
    return path.name, fields, body


def test_at_least_one_style_ships():
    assert STYLE_FILES, f"no output styles under {STYLES_DIR}"


class TestFrontmatter:
    def test_filename_is_kebab_case(self, style):
        name, _fields, _body = style
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.md", name), name

    def test_name_and_description_present(self, style):
        name, fields, _body = style
        assert fields.get("name"), f"{name}: missing `name`"
        assert fields.get("description"), f"{name}: missing `description`"

    def test_keeps_coding_instructions(self, style):
        name, fields, _body = style
        assert fields.get("keep-coding-instructions") == "true", (
            f"{name}: `keep-coding-instructions: true` is required — without it "
            "Claude Code drops its software-engineering instructions"
        )

    def test_no_unknown_fields(self, style):
        name, fields, _body = style
        allowed = {"name", "description", "keep-coding-instructions"}
        extra = set(fields) - allowed
        assert not extra, f"{name}: fields Claude Code does not read: {sorted(extra)}"


class TestBody:
    def test_is_plain_markdown_not_xml_component(self, style):
        name, _fields, body = style
        assert "<component" not in body, (
            f"{name}: output styles are sent verbatim as prose; "
            "the <component> XML pattern is for SuperClaude-loaded content"
        )

    def test_within_per_request_budget(self, style):
        name, _fields, body = style
        words = len(body.split())
        assert words <= MAX_BODY_WORDS, (
            f"{name}: {words} words > {MAX_BODY_WORDS}; the body is sent with every request"
        )

    def test_language_neutral(self, style):
        """Every letter is Latin: the style is global, not one locale's.

        Letters only — digits, punctuation and symbols carry no language, and
        accented Latin letters (é, ü) are Latin. Any other script, whether an
        example phrase or a single character, fails.
        """
        name, fields, body = style
        text = body + " ".join(fields.values())
        foreign = sorted(
            {
                ch
                for ch in text
                if ch.isalpha() and not unicodedata.name(ch, "").startswith("LATIN")
            }
        )
        assert not foreign, (
            f"{name}: non-Latin characters {foreign[:10]} — the shipped style "
            "must read the same for every user; name the pattern, not one "
            "language's phrase"
        )

    def test_does_not_mention_itself(self, style):
        """A style that names itself invites the model to announce it."""
        name, fields, body = style
        assert f'"{fields["name"]}"' not in body, f"{name}: body quotes its own name"
