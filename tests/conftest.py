"""
Pytest configuration and shared fixtures for SuperClaude tests
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="session")
def rules_schemas() -> dict:
    """Load .claude/rules/schemas.yaml as source of truth for enum rules."""
    path = Path(__file__).parent.parent / ".claude" / "rules" / "schemas.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)
