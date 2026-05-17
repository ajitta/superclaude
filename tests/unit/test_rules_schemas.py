"""Tests for .claude/rules/schemas.yaml — single source of truth for enum rules."""
from pathlib import Path

import yaml

SCHEMAS_PATH = Path(__file__).parent.parent.parent / ".claude" / "rules" / "schemas.yaml"

EXPECTED_ROLE_GROUPS = {
    "architecture",
    "engineering",
    "research",
    "documentation",
    "management",
    "indexing",
}


def _load():
    with SCHEMAS_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_schemas_yaml_exists_and_parses():
    assert SCHEMAS_PATH.exists(), f"{SCHEMAS_PATH} must exist"
    data = _load()
    assert isinstance(data, dict)
    for key in ("agent_colors", "effort_values", "forbidden_command_fields"):
        assert key in data, f"schemas.yaml missing top-level key: {key}"


def test_agent_colors_mapping_matches_role_groups():
    data = _load()
    colors = data["agent_colors"]
    assert isinstance(colors, dict), "agent_colors must be a mapping, not a list"
    assert set(colors.keys()) == EXPECTED_ROLE_GROUPS, (
        f"agent_colors keys {set(colors.keys())} != expected {EXPECTED_ROLE_GROUPS}"
    )


def test_red_not_in_agent_colors():
    data = _load()
    assert "red" not in set(data["agent_colors"].values()), (
        "red must not be in agent_colors (drift fix regression guard)"
    )


def test_conftest_fixture_rules_schemas_loads(rules_schemas):
    assert isinstance(rules_schemas, dict)
    for key in ("agent_colors", "effort_values", "forbidden_command_fields"):
        assert key in rules_schemas
