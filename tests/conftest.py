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


@pytest.fixture(autouse=True)
def sandbox_home(tmp_path_factory, monkeypatch):
    """Redirect HOME so a user-scope fallback cannot reach the developer's own.

    claude_base() resolves to Path.home()/".claude" whenever the project has no
    .claude/superclaude marker, and every bare tmp_path lacks one. Under test
    that fallback pointed at the real home, so each run left a fresh
    loop_guard_<md5(tmp_path)>.json behind — 29 had accumulated before this was
    caught. Redirecting HOME moves the fallback into a sandbox without changing
    what any test is asserting.

    USERPROFILE is set alongside HOME because that is what Path.home() consults
    on Windows. The sandbox is deliberately *not* the test's own tmp_path: tests
    that assert state stays outside the home directory need the two to differ.
    """
    home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    return home
