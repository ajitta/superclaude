"""Unit tests for SuperClaude install_settings module.

Tests hook identification, merge logic, and settings management.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestIsSuperclaudeHook:
    """Tests for _is_superclaude_hook identification logic."""

    @pytest.fixture(autouse=True)
    def _import(self):
        from superclaude.cli.install_settings import _is_superclaude_hook

        self.is_sc_hook = _is_superclaude_hook

    def test_detects_session_init_command(self):
        """SC hook detected via session_init in command path."""
        hook = {"hooks": [{"command": "python ~/.claude/scripts/session_init.py"}]}
        assert self.is_sc_hook(hook) is True

    def test_detects_prettier_hook_command(self):
        """SC hook detected via prettier_hook in command path."""
        hook = {"hooks": [{"command": "python ~/.claude/scripts/prettier_hook.py"}]}
        assert self.is_sc_hook(hook) is True

    def test_detects_test_runner_hook_command(self):
        """SC hook detected via test_runner_hook in command path."""
        hook = {"hooks": [{"command": "python ~/.claude/scripts/test_runner_hook.py"}]}
        assert self.is_sc_hook(hook) is True

    def test_detects_superclaude_comment(self):
        """SC hook detected via [superclaude] prefix in _comment field."""
        hook = {"_comment": "[superclaude] session init hook", "hooks": []}
        assert self.is_sc_hook(hook) is True

    def test_detects_experimental_comment(self):
        """Legacy [experimental] comment detected after marker addition."""
        hook = {
            "_comment": "[experimental] Requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1",
            "hooks": [{"command": "echo team-hook"}],
        }
        assert self.is_sc_hook(hook) is True

    def test_user_hook_not_detected(self):
        """User hooks with npm/echo commands are NOT falsely detected."""
        hook = {"hooks": [{"command": "npm run lint"}]}
        assert self.is_sc_hook(hook) is False

    def test_user_hook_with_custom_comment(self):
        """User hooks with custom _comment are NOT falsely detected."""
        hook = {"_comment": "My custom linter hook", "hooks": [{"command": "eslint ."}]}
        assert self.is_sc_hook(hook) is False

    def test_empty_hook_entry(self):
        """Empty hook entry returns False."""
        assert self.is_sc_hook({}) is False

    def test_hook_with_empty_hooks_array(self):
        """Hook with empty hooks array and no markers returns False."""
        assert self.is_sc_hook({"hooks": []}) is False


class TestMergeHookArrays:
    """Tests for _merge_hook_arrays merge logic."""

    @pytest.fixture(autouse=True)
    def _import(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        self.merge = _merge_hook_arrays

    def _sc_hook(self, cmd="python session_init.py"):
        return {"hooks": [{"command": cmd}]}

    def _user_hook(self, cmd="npm run lint"):
        return {"hooks": [{"command": cmd}]}

    def test_merge_into_empty(self):
        """Merging SC hooks into empty array returns only SC hooks."""
        new = [self._sc_hook()]
        result = self.merge([], new)
        assert len(result) == 1
        assert result[0]["hooks"][0]["command"] == "python session_init.py"

    def test_preserves_user_hooks(self):
        """User hooks preserved alongside new SC hooks."""
        existing = [self._user_hook()]
        new = [self._sc_hook()]
        result = self.merge(existing, new)
        assert len(result) == 2
        commands = [h["hooks"][0]["command"] for h in result]
        assert "npm run lint" in commands
        assert "python session_init.py" in commands

    def test_skips_when_sc_hooks_exist_no_force(self):
        """When SC hooks exist and force=False, returns existing unchanged."""
        existing = [self._user_hook(), self._sc_hook("python session_init_v1.py")]
        new = [self._sc_hook("python session_init_v2.py")]
        result = self.merge(existing, new, force=False)
        assert len(result) == 2
        commands = [h["hooks"][0]["command"] for h in result]
        assert "python session_init_v1.py" in commands
        assert "python session_init_v2.py" not in commands

    def test_force_replaces_sc_hooks(self):
        """Force=True replaces SC hooks while preserving user hooks."""
        existing = [self._user_hook(), self._sc_hook("python session_init_v1.py")]
        new = [self._sc_hook("python session_init_v2.py")]
        result = self.merge(existing, new, force=True)
        assert len(result) == 2
        commands = [h["hooks"][0]["command"] for h in result]
        assert "npm run lint" in commands
        assert "python session_init_v2.py" in commands
        assert "python session_init_v1.py" not in commands

    def test_no_duplicates_on_reinstall(self):
        """Force reinstall doesn't create duplicate SC hooks."""
        sc1 = self._sc_hook("python session_init.py")
        sc2 = {"hooks": [{"command": "python prettier_hook.py"}]}
        existing = [self._user_hook(), sc1, sc2]
        new = [self._sc_hook("python session_init.py"), {"hooks": [{"command": "python prettier_hook.py"}]}]
        result = self.merge(existing, new, force=True)
        # User hook + 2 new SC hooks (old ones removed)
        sc_commands = [
            h["hooks"][0]["command"]
            for h in result
            if "session_init" in h["hooks"][0]["command"]
            or "prettier_hook" in h["hooks"][0]["command"]
        ]
        assert len(sc_commands) == 2


class TestMergeHooksToSettings:
    """Integration tests for merge_hooks_to_settings with tmp_path."""

    @pytest.fixture
    def base_path(self, tmp_path: Path):
        """Create a base .claude directory for testing."""
        base = tmp_path / ".claude"
        base.mkdir()
        return base

    def _sc_hooks_config(self):
        """Sample SC hooks config for testing."""
        return {
            "hooks": {
                "SessionStart": [
                    {
                        "_comment": "[superclaude] session init",
                        "hooks": [{"command": "python session_init.py"}],
                    }
                ],
                "PostToolUse": [
                    {
                        "hooks": [{"command": "python prettier_hook.py"}],
                    }
                ],
            }
        }

    def test_creates_settings_from_scratch(self, base_path: Path):
        """Creates settings.json when it doesn't exist."""
        from superclaude.cli.install_settings import merge_hooks_to_settings

        success, msg = merge_hooks_to_settings(
            base_path, self._sc_hooks_config(), scope="user"
        )
        assert success is True

        settings = json.loads((base_path / "settings.json").read_text())
        assert "hooks" in settings
        assert "SessionStart" in settings["hooks"]
        assert "PostToolUse" in settings["hooks"]

    def test_preserves_existing_settings(self, base_path: Path):
        """Existing env/other settings preserved during merge."""
        from superclaude.cli.install_settings import merge_hooks_to_settings

        # Pre-existing settings
        existing = {"env": {"FOO": "bar"}, "permissions": {"allow": ["Read"]}}
        (base_path / "settings.json").write_text(json.dumps(existing))

        success, _ = merge_hooks_to_settings(
            base_path, self._sc_hooks_config(), scope="user"
        )
        assert success is True

        settings = json.loads((base_path / "settings.json").read_text())
        assert settings["env"]["FOO"] == "bar"
        assert settings["permissions"]["allow"] == ["Read"]
        assert "hooks" in settings

    def test_uninstall_removes_only_sc_hooks(self, base_path: Path):
        """Uninstall removes SC hooks but preserves user hooks."""
        from superclaude.cli.install_settings import (
            merge_hooks_to_settings,
            uninstall_hooks_from_settings,
        )

        # First install SC hooks
        merge_hooks_to_settings(
            base_path, self._sc_hooks_config(), scope="user"
        )

        # Manually add a user hook
        settings = json.loads((base_path / "settings.json").read_text())
        settings["hooks"]["PostToolUse"].append(
            {"hooks": [{"command": "npm run lint"}]}
        )
        (base_path / "settings.json").write_text(json.dumps(settings))

        # Uninstall
        success, _ = uninstall_hooks_from_settings(base_path)
        assert success is True

        settings = json.loads((base_path / "settings.json").read_text())
        # User hook should remain
        assert "PostToolUse" in settings["hooks"]
        post_cmds = [
            h["hooks"][0]["command"] for h in settings["hooks"]["PostToolUse"]
        ]
        assert "npm run lint" in post_cmds
        assert "python prettier_hook.py" not in post_cmds
        # SessionStart should be gone entirely (was only SC hooks)
        assert "SessionStart" not in settings["hooks"]
