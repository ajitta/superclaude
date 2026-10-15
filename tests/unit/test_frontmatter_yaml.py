"""Every shipped markdown frontmatter block must be valid YAML.

md_helpers.parse_frontmatter splits lines on the first colon, so it accepts a
description containing ": " that Claude Code's YAML parser rejects
("mapping values are not allowed here"). A rejected block drops the agent or
command from the listing, so the structure tests would stay green while the
file stops routing.
"""

from pathlib import Path

import pytest
import yaml

SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
FILES = sorted(
    p for p in SRC.rglob("*.md") if p.read_text(encoding="utf-8").startswith("---\n")
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(SRC)))
def test_frontmatter_is_valid_yaml(path):
    text = path.read_text(encoding="utf-8")
    block = text.split("---\n", 2)[1]
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        pytest.fail(f"{path.relative_to(SRC)}: frontmatter is not valid YAML: {exc}")
    assert isinstance(data, dict), (
        f"{path.relative_to(SRC)}: frontmatter is not a mapping"
    )
