"""Unit tests for Serena-recommended hook integration in install_components.

Covers PR-C plan Phase 4: gate behavior, merge coexistence, idempotency.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def base_path(tmp_path: Path) -> Path:
    """Create a base .claude directory for testing."""
    base = tmp_path / ".claude"
    base.mkdir()
    return base


@pytest.fixture
def stub_serena_registered(monkeypatch):
    """Stub check_mcp_server_installed to control Serena presence."""

    def _make(registered: bool):
        from superclaude.cli import install_mcp

        def _stub(server_name, scope=None, project_root=None):
            if server_name == "serena":
                return registered
            return False

        monkeypatch.setattr(install_mcp, "check_mcp_server_installed", _stub)

    return _make


@pytest.fixture
def package_root_with_only_serena_hooks(tmp_path: Path, monkeypatch):
    """Build a minimal fake package_root containing ONLY serena-hooks.json.

    Removes the normal hooks.json + scripts to keep the test focused on the
    Serena gate path; install_hooks_and_scripts handles missing files gracefully.
    """
    fake_pkg = tmp_path / "pkg"
    (fake_pkg / "hooks").mkdir(parents=True)
    (fake_pkg / "scripts").mkdir()

    # Real serena-hooks.json content (mirrors src/superclaude/hooks/serena-hooks.json)
    serena_hooks = {
        "_meta": {"source": "serena-recommended", "snapshot": "2026-04-27"},
        "hooks": {
            "PreToolUse": [
                {
                    "_comment": "[superclaude] serena-recommended (snapshot 2026-04-27)",
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "serena-hooks remind --client=claude-code",
                        }
                    ],
                }
            ],
            "SessionStart": [
                {
                    "_comment": "[superclaude] serena-recommended (snapshot 2026-04-27)",
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "serena-hooks activate --client=claude-code",
                        }
                    ],
                }
            ],
        },
    }
    (fake_pkg / "hooks" / "serena-hooks.json").write_text(json.dumps(serena_hooks))

    from superclaude.cli import install_components

    monkeypatch.setattr(install_components, "_get_package_root", lambda: fake_pkg)
    return fake_pkg


class TestSerenaHooksGate:
    """Phase 3 gate behavior: Serena MCP presence → hooks installed; absent → skipped."""

    def test_serena_absent_skips_hooks_and_emits_message(
        self,
        base_path: Path,
        stub_serena_registered,
        package_root_with_only_serena_hooks,
    ):
        """When Serena MCP not registered, hooks NOT written, info message present."""
        stub_serena_registered(False)

        from superclaude.cli.install_components import install_hooks_and_scripts

        installed, _, failed, messages = install_hooks_and_scripts(
            base_path=base_path, scope="user"
        )

        assert failed == 0
        assert any("Serena MCP not registered" in m for m in messages)

        settings_file = base_path / "settings.json"
        if settings_file.exists():
            settings = json.loads(settings_file.read_text())
            hooks = settings.get("hooks", {})
            # No Serena hooks should be merged
            for hook_type in hooks.values():
                for entry in hook_type:
                    cmd_str = json.dumps(entry)
                    assert "serena-hooks" not in cmd_str

    def test_serena_present_installs_hooks(
        self,
        base_path: Path,
        stub_serena_registered,
        package_root_with_only_serena_hooks,
    ):
        """When Serena MCP registered, recommended hooks land in settings.json."""
        stub_serena_registered(True)

        from superclaude.cli.install_components import install_hooks_and_scripts

        _, _, failed, messages = install_hooks_and_scripts(
            base_path=base_path, scope="user"
        )

        assert failed == 0
        assert any("serena-hooks" in m for m in messages)

        settings = json.loads((base_path / "settings.json").read_text())
        assert "PreToolUse" in settings["hooks"]
        assert "SessionStart" in settings["hooks"]
        # Snapshot marker present in _comment
        all_entries = (
            settings["hooks"]["PreToolUse"] + settings["hooks"]["SessionStart"]
        )
        assert any("serena-recommended" in e.get("_comment", "") for e in all_entries)


class TestSerenaHooksCoexistence:
    """Phase 4 invariant: Serena hooks coexist with user-authored and core SC hooks."""

    def test_preserves_user_authored_hooks_in_other_event(
        self,
        base_path: Path,
        stub_serena_registered,
        package_root_with_only_serena_hooks,
    ):
        """User PostToolUse hook untouched when Serena adds PreToolUse/SessionStart."""
        stub_serena_registered(True)

        existing = {
            "hooks": {
                "PostToolUse": [
                    {"hooks": [{"command": "echo my-user-hook"}]},
                ]
            }
        }
        (base_path / "settings.json").write_text(json.dumps(existing))

        from superclaude.cli.install_components import install_hooks_and_scripts

        install_hooks_and_scripts(base_path=base_path, scope="user")

        settings = json.loads((base_path / "settings.json").read_text())
        # User PostToolUse preserved
        assert any(
            "my-user-hook" in h.get("command", "")
            for entry in settings["hooks"]["PostToolUse"]
            for h in entry.get("hooks", [])
        )
        # Serena hooks added
        assert "PreToolUse" in settings["hooks"]
        assert "SessionStart" in settings["hooks"]

    def test_user_authored_serena_hook_preserved_alongside_sc_version(
        self,
        base_path: Path,
        stub_serena_registered,
        package_root_with_only_serena_hooks,
    ):
        """User-authored unmarked Serena hook survives merge; SC adds its marked version separately.

        This documents the existing per-event-type marker-based merger semantics:
        unmarked user entries do not trigger the per-type skip — they are preserved as
        "user_hooks" while new SC-marked entries are appended. Both coexist in the array.
        """
        stub_serena_registered(True)

        existing = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "serena-hooks remind --client=claude-code --my-flag",
                            }
                        ],
                    }
                ]
            }
        }
        (base_path / "settings.json").write_text(json.dumps(existing))

        from superclaude.cli.install_components import install_hooks_and_scripts

        install_hooks_and_scripts(base_path=base_path, scope="user", force=False)

        settings = json.loads((base_path / "settings.json").read_text())
        pre_entries = settings["hooks"]["PreToolUse"]

        # User's customized command preserved verbatim (--my-flag retained).
        assert any(
            "--my-flag" in h.get("command", "")
            for entry in pre_entries
            for h in entry.get("hooks", [])
        )
        # SC's marked recommendation also added as a separate entry.
        assert any(
            "serena-recommended" in entry.get("_comment", "") for entry in pre_entries
        )


class TestSerenaHooksIdempotency:
    """Re-running install does not duplicate Serena hook entries."""

    def test_reinstall_no_duplicates(
        self,
        base_path: Path,
        stub_serena_registered,
        package_root_with_only_serena_hooks,
    ):
        stub_serena_registered(True)

        from superclaude.cli.install_components import install_hooks_and_scripts

        install_hooks_and_scripts(base_path=base_path, scope="user")
        install_hooks_and_scripts(base_path=base_path, scope="user")

        settings = json.loads((base_path / "settings.json").read_text())
        pre = settings["hooks"]["PreToolUse"]
        sc_marked = [
            e for e in pre if "serena-recommended" in e.get("_comment", "")
        ]
        assert len(sc_marked) == 1

    def test_reinstall_with_force_replaces_cleanly(
        self,
        base_path: Path,
        stub_serena_registered,
        package_root_with_only_serena_hooks,
    ):
        stub_serena_registered(True)

        from superclaude.cli.install_components import install_hooks_and_scripts

        install_hooks_and_scripts(base_path=base_path, scope="user")
        install_hooks_and_scripts(base_path=base_path, scope="user", force=True)

        settings = json.loads((base_path / "settings.json").read_text())
        pre = settings["hooks"]["PreToolUse"]
        sc_marked = [
            e for e in pre if "serena-recommended" in e.get("_comment", "")
        ]
        assert len(sc_marked) == 1
