"""`make help` is generated from `## ` comments, so every target must carry one.

The hand-written help list drifted: three `sync-*` targets were in `.PHONY`
with no help line and nothing failed. With help generated from the rule-line
comments, this test is what keeps the listing complete — a target added
without a `## ` comment, or a commented rule left out of `.PHONY`, turns it red.
"""

import re
from pathlib import Path

MAKEFILE = Path(__file__).resolve().parents[2] / "Makefile"

_PHONY_RE = re.compile(r"^\.PHONY:(.*)$", re.M)
_RULE_RE = re.compile(r"^([a-zA-Z_-]+):(?!=)[^\n]*$", re.M)
_DOCUMENTED_RULE_RE = re.compile(r"^([a-zA-Z_-]+):[^\n#]*## +\S", re.M)
_SECTION_RE = re.compile(r"^##@ \S", re.M)


def _text() -> str:
    return MAKEFILE.read_text(encoding="utf-8")


def test_every_phony_target_has_a_help_comment():
    text = _text()
    phony = set(_PHONY_RE.search(text).group(1).split())
    documented = set(_DOCUMENTED_RULE_RE.findall(text))
    assert phony - documented == set(), (
        f"targets in .PHONY without a `## description` on their rule line: "
        f"{sorted(phony - documented)}"
    )
    assert documented - phony == set(), (
        f"documented rules missing from .PHONY: {sorted(documented - phony)}"
    )


def test_every_rule_is_phony_and_documented():
    """No rule line escapes both the listing and `.PHONY`."""
    text = _text()
    rules = set(_RULE_RE.findall(text)) - {"PHONY"}
    phony = set(_PHONY_RE.search(text).group(1).split())
    assert rules == phony, sorted(rules ^ phony)


def test_help_has_sections_and_no_hand_written_list():
    text = _text()
    assert len(_SECTION_RE.findall(text)) >= 3, "help needs `##@ Section` headers"
    help_recipe = text.split("\nhelp:", 1)[1]
    assert '@echo "  make ' not in help_recipe, (
        "help lists targets by hand again — use `## ` comments on the rule lines"
    )
