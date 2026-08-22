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
        """SC hook detected via resolved superclaude scripts path (user scope)."""
        hook = {
            "hooks": [
                {"command": "python ~/.claude/superclaude/scripts/session_init.py"}
            ]
        }
        assert self.is_sc_hook(hook) is True

    def test_detects_prettier_hook_command(self):
        """SC hook detected via project-scope superclaude scripts path."""
        hook = {
            "hooks": [
                {
                    "command": "python $CLAUDE_PROJECT_DIR/.claude/superclaude/scripts/prettier_hook.py"
                }
            ]
        }
        assert self.is_sc_hook(hook) is True

    def test_detects_test_runner_hook_command(self):
        """SC hook detected via Windows backslash superclaude scripts path."""
        hook = {
            "hooks": [
                {
                    "command": "python C:\\Users\\x\\.claude\\superclaude\\scripts\\test_runner_hook.py"
                }
            ]
        }
        assert self.is_sc_hook(hook) is True

    def test_detects_unresolved_template_command(self):
        """SC hook detected via unresolved {{SCRIPTS_PATH}} template form."""
        hook = {"hooks": [{"command": "python {{SCRIPTS_PATH}}/session_init.py"}]}
        assert self.is_sc_hook(hook) is True

    def test_user_hook_with_sc_script_name_not_detected(self):
        """User hook whose command merely contains an SC script name is NOT SC-owned."""
        hook = {"hooks": [{"command": "python ~/dotfiles/session_init.py"}]}
        assert self.is_sc_hook(hook) is False

    def test_user_hook_mentioning_superclaude_not_detected(self):
        """Bare 'superclaude' word (no scripts path, no bracket tag) is NOT SC-owned."""
        hook = {"hooks": [{"command": "superclaude doctor --quiet"}]}
        assert self.is_sc_hook(hook) is False

    def test_detects_superclaude_comment(self):
        """SC hook detected via [superclaude] prefix in _comment field."""
        hook = {"_comment": "[superclaude] session init hook", "hooks": []}
        assert self.is_sc_hook(hook) is True

    def test_plain_experimental_comment_not_detected(self):
        """Plain [experimental] comment without superclaude marker is NOT detected."""
        hook = {
            "_comment": "[experimental] Requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1",
            "hooks": [{"command": "echo team-hook"}],
        }
        assert self.is_sc_hook(hook) is False

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

    def test_detects_serena_recommended_via_comment(self):
        """SC-managed Serena hook detected via [superclaude] _comment prefix."""
        hook = {
            "_comment": "[superclaude] serena-recommended (snapshot 2026-04-27)",
            "hooks": [{"command": "serena-hooks remind --client=claude-code"}],
        }
        assert self.is_sc_hook(hook) is True

    def test_user_authored_serena_hook_not_detected(self):
        """User-authored Serena hook (no marker) treated as user hook, not SC."""
        hook = {
            "matcher": "",
            "hooks": [{"command": "serena-hooks remind --client=claude-code"}],
        }
        assert self.is_sc_hook(hook) is False


class TestMergeHookArrays:
    """Tests for _merge_hook_arrays merge logic."""

    @pytest.fixture(autouse=True)
    def _import(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        self.merge = _merge_hook_arrays

    SC_SCRIPTS = "~/.claude/superclaude/scripts"

    def _sc_hook(self, cmd=None):
        cmd = cmd or f"python {self.SC_SCRIPTS}/session_init.py"
        return {"hooks": [{"command": cmd}]}

    def _user_hook(self, cmd="npm run lint"):
        return {"hooks": [{"command": cmd}]}

    def test_merge_into_empty(self):
        """Merging SC hooks into empty array returns only SC hooks."""
        new = [self._sc_hook()]
        result = self.merge([], new)
        assert len(result) == 1
        assert (
            result[0]["hooks"][0]["command"]
            == f"python {self.SC_SCRIPTS}/session_init.py"
        )

    def test_preserves_user_hooks(self):
        """User hooks preserved alongside new SC hooks."""
        existing = [self._user_hook()]
        new = [self._sc_hook()]
        result = self.merge(existing, new)
        assert len(result) == 2
        commands = [h["hooks"][0]["command"] for h in result]
        assert "npm run lint" in commands
        assert f"python {self.SC_SCRIPTS}/session_init.py" in commands

    def test_adds_unregistered_script_without_force(self):
        """A script this release ships and the install lacks is added, not skipped.

        Superseding the old contract, which returned `existing` untouched the
        moment any SuperClaude hook was present. That froze an install's hook set
        while its content kept updating, and is how a shipped hook stayed
        unregistered in a real install for weeks.
        """
        v1 = f"python {self.SC_SCRIPTS}/session_init_v1.py"
        v2 = f"python {self.SC_SCRIPTS}/session_init_v2.py"
        existing = [self._user_hook(), self._sc_hook(v1)]
        new = [self._sc_hook(v2)]
        result = self.merge(existing, new, force=False)
        commands = [h["hooks"][0]["command"] for h in result]
        assert commands[: len(existing)] == [
            "npm run lint",
            v1,
        ], "existing entries must survive a non-force merge verbatim"
        assert v2 in commands

    def test_registered_script_is_not_re_added(self):
        """Same script, drifted command: still one registration, not two."""
        settled = f"python {self.SC_SCRIPTS}/session_init.py"
        reshipped = f"/usr/bin/python3 {self.SC_SCRIPTS}/session_init.py --verbose"
        existing = [self._user_hook(), self._sc_hook(settled)]

        result = self.merge(existing, [self._sc_hook(settled)], force=False)
        assert result == existing, "an identical hook was appended again"

        drifted = self.merge(existing, [self._sc_hook(reshipped)], force=False)
        assert drifted == existing, (
            "a path or flag change re-registered a hook that is already installed"
        )

    def test_one_script_shipped_twice_under_a_matcher(self):
        """Two subcommands of one script are two hooks, not one.

        A set-based presence check would see the first registration and call the
        second shipped hook already installed.
        """
        harvest = f"python {self.SC_SCRIPTS}/insight_writer.py harvest-from-hook"
        pending = f"python {self.SC_SCRIPTS}/insight_writer.py pending-count-from-hook"
        existing = [{"matcher": "", "hooks": [{"command": harvest}]}]
        new = [{"matcher": "", "hooks": [{"command": harvest}, {"command": pending}]}]

        result = self.merge(existing, new, force=False)

        commands = [h["command"] for entry in result for h in entry["hooks"]]
        assert commands.count(harvest) == 1, "already-registered hook was doubled"
        assert pending in commands, "second subcommand never reached the install"

    def test_force_replaces_sc_hooks(self):
        """Force=True replaces SC hooks while preserving user hooks."""
        v1 = f"python {self.SC_SCRIPTS}/session_init_v1.py"
        v2 = f"python {self.SC_SCRIPTS}/session_init_v2.py"
        existing = [self._user_hook(), self._sc_hook(v1)]
        new = [self._sc_hook(v2)]
        result = self.merge(existing, new, force=True)
        assert len(result) == 2
        commands = [h["hooks"][0]["command"] for h in result]
        assert "npm run lint" in commands
        assert v2 in commands
        assert v1 not in commands

    def test_no_duplicates_on_reinstall(self):
        """Force reinstall doesn't create duplicate SC hooks."""
        sc1 = self._sc_hook(f"python {self.SC_SCRIPTS}/session_init.py")
        sc2 = {"hooks": [{"command": f"python {self.SC_SCRIPTS}/prettier_hook.py"}]}
        existing = [self._user_hook(), sc1, sc2]
        new = [
            self._sc_hook(f"python {self.SC_SCRIPTS}/session_init.py"),
            {"hooks": [{"command": f"python {self.SC_SCRIPTS}/prettier_hook.py"}]},
        ]
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

    SC_SCRIPTS = "~/.claude/superclaude/scripts"

    def _sc_hooks_config(self):
        """Sample SC hooks config for testing."""
        return {
            "hooks": {
                "SessionStart": [
                    {
                        "_comment": "[superclaude] session init",
                        "hooks": [
                            {"command": f"python {self.SC_SCRIPTS}/session_init.py"}
                        ],
                    }
                ],
                "PostToolUse": [
                    {
                        "hooks": [
                            {"command": f"python {self.SC_SCRIPTS}/prettier_hook.py"}
                        ],
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
        merge_hooks_to_settings(base_path, self._sc_hooks_config(), scope="user")

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
        post_cmds = [h["hooks"][0]["command"] for h in settings["hooks"]["PostToolUse"]]
        assert "npm run lint" in post_cmds
        assert f"python {self.SC_SCRIPTS}/prettier_hook.py" not in post_cmds
        # SessionStart should be gone entirely (was only SC hooks)
        assert "SessionStart" not in settings["hooks"]

    def _sc_hooks_config_with_echo(self):
        """SC hooks config including echo-only hooks (TeammateIdle, TaskCompleted)."""
        config = self._sc_hooks_config()
        config["hooks"]["TeammateIdle"] = [
            {
                "_comment": "[superclaude] experimental",
                "hooks": [
                    {"command": "echo '[superclaude] Teammate idle — assign next task'"}
                ],
            }
        ]
        config["hooks"]["TaskCompleted"] = [
            {
                "_comment": "[superclaude] experimental",
                "hooks": [
                    {
                        "command": "echo '[superclaude] Task completed — aggregate results'"
                    }
                ],
            }
        ]
        return config

    def test_idempotent_reinstall_no_duplicates(self, base_path: Path):
        """Running merge twice should NOT create duplicate hook entries."""
        from superclaude.cli.install_settings import merge_hooks_to_settings

        config = self._sc_hooks_config_with_echo()

        # First install
        merge_hooks_to_settings(base_path, config, scope="user")
        # Second install (re-install)
        merge_hooks_to_settings(base_path, config, scope="user")

        settings = json.loads((base_path / "settings.json").read_text())
        for hook_type in [
            "SessionStart",
            "PostToolUse",
            "TeammateIdle",
            "TaskCompleted",
        ]:
            entries = settings["hooks"].get(hook_type, [])
            assert len(entries) == len(config["hooks"][hook_type]), (
                f"{hook_type}: expected {len(config['hooks'][hook_type])} entries, got {len(entries)}"
            )

    def test_detection_after_comment_stripping(self, base_path: Path):
        """Hooks remain detectable after _comment fields are stripped (as Claude Code does)."""
        from superclaude.cli.install_settings import merge_hooks_to_settings

        config = self._sc_hooks_config_with_echo()

        # First install
        merge_hooks_to_settings(base_path, config, scope="user")

        # Simulate Claude Code stripping _comment fields
        settings = json.loads((base_path / "settings.json").read_text())
        for hook_type, hook_array in settings["hooks"].items():
            for entry in hook_array:
                entry.pop("_comment", None)
        (base_path / "settings.json").write_text(json.dumps(settings, indent=2))

        # Re-install should NOT duplicate
        merge_hooks_to_settings(base_path, config, scope="user")

        settings = json.loads((base_path / "settings.json").read_text())
        for hook_type in ["TeammateIdle", "TaskCompleted"]:
            entries = settings["hooks"].get(hook_type, [])
            assert len(entries) == 1, (
                f"{hook_type}: expected 1 entry after re-install, got {len(entries)}"
            )

    def test_uninstall_echo_only_hooks_after_comment_stripping(self, base_path: Path):
        """Uninstall removes echo-only hooks even after _comment is stripped."""
        from superclaude.cli.install_settings import (
            merge_hooks_to_settings,
            uninstall_hooks_from_settings,
        )

        config = self._sc_hooks_config_with_echo()
        merge_hooks_to_settings(base_path, config, scope="user")

        # Strip _comment fields (simulating Claude Code behavior)
        settings = json.loads((base_path / "settings.json").read_text())
        for hook_type, hook_array in settings["hooks"].items():
            for entry in hook_array:
                entry.pop("_comment", None)
        (base_path / "settings.json").write_text(json.dumps(settings, indent=2))

        # Uninstall should still remove all SC hooks
        success, _ = uninstall_hooks_from_settings(base_path)
        assert success is True

        settings = json.loads((base_path / "settings.json").read_text())
        # All hook types should be removed (no user hooks mixed in)
        assert "TeammateIdle" not in settings.get("hooks", {}), (
            "TeammateIdle should be removed after uninstall"
        )
        assert "TaskCompleted" not in settings.get("hooks", {}), (
            "TaskCompleted should be removed after uninstall"
        )


class TestHookDedup:
    """Tests for _dedup_hook_array and idempotent merge behavior.

    Regression: third-party installers (e.g., serena-hooks) re-add identical
    entries on each `make sync-user`, accumulating duplicates that
    `_is_superclaude_hook` does not catch (no SC marker). Five real reverts
    were observed in production before this fix.
    """

    @pytest.fixture(autouse=True)
    def _import(self):
        from superclaude.cli.install_settings import (
            _dedup_hook_array,
            _hook_entry_signature,
            merge_hooks_to_settings,
        )

        self.dedup = _dedup_hook_array
        self.signature = _hook_entry_signature
        self.merge = merge_hooks_to_settings

    def test_signature_matches_identical_entries(self):
        a = {
            "matcher": "",
            "hooks": [{"type": "command", "command": "serena-hooks remind"}],
        }
        b = {
            "matcher": "",
            "hooks": [{"type": "command", "command": "serena-hooks remind"}],
        }
        assert self.signature(a) == self.signature(b)

    def test_signature_distinguishes_matcher(self):
        a = {"matcher": "", "hooks": [{"command": "x"}]}
        b = {"matcher": "Bash", "hooks": [{"command": "x"}]}
        assert self.signature(a) != self.signature(b)

    def test_signature_ignores_comment_metadata(self):
        a = {"matcher": "", "hooks": [{"command": "x"}]}
        b = {"_comment": "some note", "matcher": "", "hooks": [{"command": "x"}]}
        assert self.signature(a) == self.signature(b)

    def test_dedup_collapses_triplicate(self):
        entry = {"matcher": "", "hooks": [{"command": "serena-hooks remind"}]}
        result = self.dedup([entry, entry, entry])
        assert len(result) == 1
        assert result[0] == entry

    def test_dedup_preserves_distinct(self):
        a = {"matcher": "", "hooks": [{"command": "cmd-a"}]}
        b = {"matcher": "", "hooks": [{"command": "cmd-b"}]}
        result = self.dedup([a, b, a])
        assert result == [a, b]

    def test_dedup_idempotent_on_clean_array(self):
        a = {"matcher": "", "hooks": [{"command": "cmd-a"}]}
        b = {"matcher": "Bash", "hooks": [{"command": "cmd-b"}]}
        clean = [a, b]
        assert self.dedup(clean) == clean

    def test_dedup_empty_array(self):
        assert self.dedup([]) == []

    def test_merge_cleans_third_party_duplicates_on_skip_path(self, tmp_path):
        """Existing array gets deduped even when SC hooks already present (skip path).

        This is the actual production bug: SC hooks exist (skip merge), but
        third-party entries pile up across reinstalls because no path cleans them.
        """
        base_path = tmp_path / ".claude"
        base_path.mkdir()

        # Pre-existing settings.json: SC hooks present + 3 duplicate serena entries
        sc_entry = {
            "hooks": [
                {"command": "python ~/.claude/superclaude/scripts/session_init.py"}
            ]
        }
        third_party = {
            "matcher": "",
            "hooks": [{"type": "command", "command": "serena-hooks remind"}],
        }
        existing = {
            "hooks": {"PreToolUse": [sc_entry, third_party, third_party, third_party]}
        }
        (base_path / "settings.json").write_text(json.dumps(existing, indent=2))

        # Re-run install with same SC hooks (no force) - should hit skip path
        hooks_config = {"hooks": {"PreToolUse": [sc_entry]}}
        success, _ = self.merge(base_path, hooks_config, scope="user", force=False)
        assert success is True

        result = json.loads((base_path / "settings.json").read_text())
        pretooluse = result["hooks"]["PreToolUse"]
        # 3 serena duplicates collapsed to 1; SC hook preserved
        assert len(pretooluse) == 2
        serena_count = sum(
            1
            for e in pretooluse
            if any(
                "serena-hooks remind" in h.get("command", "")
                for h in e.get("hooks", [])
            )
        )
        assert serena_count == 1, f"Expected 1 serena entry, got {serena_count}"

    def test_merge_idempotent_with_third_party_accumulation(self, tmp_path):
        """Running merge N times with a third-party adding 1 entry each time stays bounded."""
        base_path = tmp_path / ".claude"
        base_path.mkdir()

        sc_entry = {
            "hooks": [
                {"command": "python ~/.claude/superclaude/scripts/session_init.py"}
            ]
        }
        third_party = {
            "matcher": "",
            "hooks": [{"type": "command", "command": "serena-hooks remind"}],
        }

        # Initial install
        hooks_config = {"hooks": {"PreToolUse": [sc_entry]}}
        self.merge(base_path, hooks_config, scope="user", force=False)

        # Simulate third-party installer adding entries across 4 syncs
        for _ in range(4):
            settings = json.loads((base_path / "settings.json").read_text())
            settings["hooks"]["PreToolUse"].append(third_party)
            (base_path / "settings.json").write_text(json.dumps(settings, indent=2))
            # Subsequent SC merge should dedup the accumulated third-party entries
            self.merge(base_path, hooks_config, scope="user", force=False)

        result = json.loads((base_path / "settings.json").read_text())
        pretooluse = result["hooks"]["PreToolUse"]
        serena_count = sum(
            1
            for e in pretooluse
            if any(
                "serena-hooks remind" in h.get("command", "")
                for h in e.get("hooks", [])
            )
        )
        assert serena_count == 1, (
            f"After 4 accumulation rounds, expected 1 serena entry, got {serena_count}"
        )


class TestNewlyShippedHookReachesAnExistingInstall:
    """A hook added in a later release must reach an install that predates it.

    The merge used to skip a whole event type once any SuperClaude hook existed
    under it, so an install updated without --force froze its hook set at
    whatever was written first while its markdown kept updating. That is how
    prettier_hook.py ended up shipped-but-unregistered in a real install with
    twelve of the thirteen hooks present.
    """

    SC = "~/.claude/superclaude/scripts"

    @pytest.fixture
    def base_path(self, tmp_path: Path):
        base = tmp_path / ".claude"
        base.mkdir()
        return base

    def _settled_install(self, base_path: Path, extra: list | None = None) -> Path:
        """An install carrying the previous release's PostToolUse hook only."""
        settings_file = base_path / "settings.json"
        settings = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Edit|Write",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"python {self.SC}/test_runner_hook.py",
                                "timeout": 120,
                            }
                        ],
                    },
                    *(extra or []),
                ]
            }
        }
        settings_file.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        return settings_file

    def _shipped(self) -> dict:
        """This release ships prettier alongside test_runner on the same matcher."""
        return {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Edit|Write",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"python {self.SC}/prettier_hook.py",
                                "timeout": 30,
                            },
                            {
                                "type": "command",
                                "command": f"python {self.SC}/test_runner_hook.py",
                                "timeout": 120,
                            },
                        ],
                    }
                ]
            }
        }

    @staticmethod
    def _registered_scripts(settings_file: Path) -> set:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        return {
            hook["command"].rsplit("/", 1)[-1]
            for entry in settings["hooks"]["PostToolUse"]
            for hook in entry["hooks"]
        }

    def test_missing_hook_is_added_without_force(self, base_path: Path):
        from superclaude.cli.install_settings import merge_hooks_to_settings

        settings_file = self._settled_install(base_path)

        success, msg = merge_hooks_to_settings(
            base_path, self._shipped(), scope="user", force=False
        )

        assert success is True, msg
        assert self._registered_scripts(settings_file) == {
            "prettier_hook.py",
            "test_runner_hook.py",
        }, "a newly shipped hook never reached the install"

    def test_existing_entries_are_left_alone(self, base_path: Path):
        """Only additions. A user's timeout edit survives a non-force merge."""
        from superclaude.cli.install_settings import merge_hooks_to_settings

        settings_file = self._settled_install(base_path)
        before = json.loads(settings_file.read_text(encoding="utf-8"))["hooks"][
            "PostToolUse"
        ]

        merge_hooks_to_settings(base_path, self._shipped(), scope="user", force=False)

        after = json.loads(settings_file.read_text(encoding="utf-8"))["hooks"][
            "PostToolUse"
        ]
        assert after[: len(before)] == before, "an existing entry was rewritten"

    def test_repeat_merge_adds_nothing(self, base_path: Path):
        """Idempotent: the second non-force merge is a no-op."""
        from superclaude.cli.install_settings import merge_hooks_to_settings

        settings_file = self._settled_install(base_path)

        merge_hooks_to_settings(base_path, self._shipped(), scope="user", force=False)
        once = settings_file.read_text(encoding="utf-8")
        merge_hooks_to_settings(base_path, self._shipped(), scope="user", force=False)

        assert settings_file.read_text(encoding="utf-8") == once

    def test_user_hooks_survive(self, base_path: Path):
        """A non-SuperClaude entry under the same event type is untouched."""
        from superclaude.cli.install_settings import merge_hooks_to_settings

        user_entry = {
            "matcher": "Edit",
            "hooks": [{"type": "command", "command": "python /home/me/mine.py"}],
        }
        settings_file = self._settled_install(base_path, extra=[user_entry])

        merge_hooks_to_settings(base_path, self._shipped(), scope="user", force=False)

        entries = json.loads(settings_file.read_text(encoding="utf-8"))["hooks"][
            "PostToolUse"
        ]
        assert user_entry in entries


class TestInnerHookOwnership:
    """Ownership is per inner hook, not per outer entry.

    One Claude settings entry carries a single matcher and a list of inner
    hooks, so a user's own command can sit next to a SuperClaude one. Judging
    the whole entry SuperClaude-owned made `--force` and `uninstall` delete the
    user's command with it — silently, and against the docstring's own promise
    to preserve user hooks.
    """

    @staticmethod
    def _mixed_entry(user_first: bool = False):
        sc = {"type": "command", "command": "python .../superclaude/scripts/prettier_hook.py"}
        user = {"type": "command", "command": "npm run user-lint"}
        inner = [user, sc] if user_first else [sc, user]
        return {"matcher": "Edit", "hooks": inner}

    def test_force_keeps_the_user_hook_in_its_entry(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        shipped = [
            {
                "matcher": "Edit",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python /new/superclaude/scripts/prettier_hook.py",
                    }
                ],
            }
        ]

        merged = _merge_hook_arrays([self._mixed_entry()], shipped, force=True)

        commands = [h["command"] for entry in merged for h in entry.get("hooks", [])]
        assert "npm run user-lint" in commands
        assert any("/new/superclaude/scripts/prettier_hook.py" in c for c in commands)
        assert not any(c.startswith("python .../") for c in commands), (
            "the previous SuperClaude command survived a force merge"
        )

    def test_force_keeps_a_leading_user_hook_too(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        merged = _merge_hook_arrays([self._mixed_entry(user_first=True)], [], force=True)

        commands = [h["command"] for entry in merged for h in entry.get("hooks", [])]
        assert commands == ["npm run user-lint"]

    def test_uninstall_keeps_the_user_hook(self, tmp_path):
        import json

        from superclaude.cli.install_settings import uninstall_hooks_from_settings

        base = tmp_path / ".claude"
        base.mkdir()
        settings_file = base / "settings.json"
        settings_file.write_text(
            json.dumps({"hooks": {"PostToolUse": [self._mixed_entry()]}}),
            encoding="utf-8",
        )

        success, message = uninstall_hooks_from_settings(base, scope="user")

        assert success, message
        remaining = json.loads(settings_file.read_text(encoding="utf-8"))
        commands = [
            h["command"]
            for array in remaining.get("hooks", {}).values()
            for entry in array
            for h in entry.get("hooks", [])
        ]
        assert commands == ["npm run user-lint"]

    def test_force_does_not_reorder_user_entries(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        user_entry = {"matcher": "Write", "hooks": [{"type": "command", "command": "user-a"}]}
        sc_entry = {
            "matcher": "Edit",
            "hooks": [
                {"type": "command", "command": "python /old/superclaude/scripts/x.py"}
            ],
        }
        shipped = [
            {
                "matcher": "Edit",
                "hooks": [
                    {"type": "command", "command": "python /new/superclaude/scripts/x.py"}
                ],
            }
        ]

        merged = _merge_hook_arrays([sc_entry, user_entry], shipped, force=True)

        assert merged[-1]["hooks"][0]["command"].startswith("python /new/")
        assert [e["matcher"] for e in merged[:-1]] == ["Write"]


class TestHookIdentityCarriesTheSubcommand:
    """One script, two entry points, is two hooks.

    Identity was the bare `.py` filename, so a release that moved a script to a
    new subcommand could not deliver it: the old registration matched, the new
    subcommand was called already-present, and the wrong entry point kept
    running. The rule has to survive flag drift, though, or every re-shipped
    option appends a duplicate.
    """

    def test_a_different_subcommand_is_a_different_hook(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        existing = [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python /sc/superclaude/scripts/insight_writer.py pending-count-from-hook",
                    }
                ],
            }
        ]
        shipped = [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python /sc/superclaude/scripts/insight_writer.py harvest-from-hook",
                    },
                    {
                        "type": "command",
                        "command": "python /sc/superclaude/scripts/insight_writer.py pending-count-from-hook",
                    },
                ],
            }
        ]

        merged = _merge_hook_arrays(existing, shipped, force=False)
        commands = [h["command"] for entry in merged for h in entry.get("hooks", [])]

        assert sum("harvest-from-hook" in c for c in commands) == 1
        assert sum("pending-count-from-hook" in c for c in commands) == 1

    def test_flag_drift_does_not_append_a_duplicate(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        existing = [
            {
                "matcher": "Edit",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python /sc/superclaude/scripts/loop_guard.py --threshold 5",
                    }
                ],
            }
        ]
        shipped = [
            {
                "matcher": "Edit",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python /sc/superclaude/scripts/loop_guard.py",
                    }
                ],
            }
        ]

        merged = _merge_hook_arrays(existing, shipped, force=False)
        commands = [h["command"] for entry in merged for h in entry.get("hooks", [])]

        assert len(commands) == 1, commands

    def test_a_user_matcher_edit_is_preserved_not_duplicated(self):
        from superclaude.cli.install_settings import _merge_hook_arrays

        existing = [
            {
                "matcher": "clear|startup",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python /sc/superclaude/scripts/context_reset.py",
                    }
                ],
            }
        ]
        shipped = [
            {
                "matcher": "clear|compact|startup",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python /sc/superclaude/scripts/context_reset.py",
                    }
                ],
            }
        ]

        merged = _merge_hook_arrays(existing, shipped, force=False)

        assert len(merged) == 1, merged
        assert merged[0]["matcher"] == "clear|startup"


class TestForceSweepsRetiredEvents:
    """`--force` means "replace with what this release ships", everywhere.

    The merge walked only the event types present in the new config, so a
    SuperClaude hook left on an event a later release dropped kept firing — and
    kept calling a script that is no longer shipped.
    """

    def test_a_retired_event_is_removed(self, tmp_path):
        import json

        from superclaude.cli.install_settings import merge_hooks_to_settings

        base = tmp_path / ".claude"
        base.mkdir()
        settings_file = base / "settings.json"
        settings_file.write_text(
            json.dumps(
                {
                    "hooks": {
                        "TeammateIdle": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python /sc/superclaude/scripts/gone.py",
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

        shipped = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python /sc/superclaude/scripts/insight_writer.py request-from-hook",
                            }
                        ]
                    }
                ]
            }
        }

        success, message = merge_hooks_to_settings(base, shipped, "user", force=True)

        assert success, message
        events = json.loads(settings_file.read_text(encoding="utf-8"))["hooks"]
        assert "TeammateIdle" not in events
        assert "Stop" in events

    def test_a_user_hook_on_a_retired_event_survives(self, tmp_path):
        import json

        from superclaude.cli.install_settings import merge_hooks_to_settings

        base = tmp_path / ".claude"
        base.mkdir()
        settings_file = base / "settings.json"
        settings_file.write_text(
            json.dumps(
                {
                    "hooks": {
                        "TeammateIdle": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python /sc/superclaude/scripts/gone.py",
                                    },
                                    {"type": "command", "command": "notify-send idle"},
                                ]
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

        success, message = merge_hooks_to_settings(
            base, {"hooks": {"Stop": []}}, "user", force=True
        )

        assert success, message
        events = json.loads(settings_file.read_text(encoding="utf-8"))["hooks"]
        commands = [h["command"] for e in events.get("TeammateIdle", []) for h in e["hooks"]]
        assert commands == ["notify-send idle"]
