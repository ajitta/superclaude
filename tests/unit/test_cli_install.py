"""
Unit tests for CLI install command

Tests the command installation functionality.
"""

from superclaude.cli.install_commands import (
    install_commands,
    list_available_commands,
    list_installed_commands,
)


class TestInstallCommands:
    """Test suite for install commands functionality"""

    def test_list_available_commands(self):
        """Test listing available commands"""
        commands = list_available_commands()

        assert isinstance(commands, list)
        assert len(commands) > 0
        assert "research" in commands
        assert "index-repo" in commands

    def test_install_commands_to_temp_dir(self, tmp_path):
        """Test installing commands to a temporary directory"""
        target_dir = tmp_path / "commands"

        success, message = install_commands(target_path=target_dir, force=False)

        assert success is True
        assert "installed" in message.lower()

        # Commands are installed to commands/sc/ subdirectory
        commands_dir = tmp_path / "commands" / "sc"
        assert commands_dir.exists()

        # Check that command files were copied
        command_files = list(commands_dir.glob("*.md"))
        assert len(command_files) > 0

        # Verify specific commands
        assert (commands_dir / "research.md").exists()
        assert (commands_dir / "index-repo.md").exists()

    def test_install_commands_skip_existing(self, tmp_path):
        """Test that existing commands are skipped without --force"""
        target_dir = tmp_path / "commands"

        # First install
        success1, message1 = install_commands(target_path=target_dir, force=False)
        assert success1 is True

        # Second install without force
        success2, message2 = install_commands(target_path=target_dir, force=False)
        assert success2 is True
        assert "skipped" in message2.lower()

    def test_install_commands_force_reinstall(self, tmp_path):
        """Test force reinstall of existing commands"""
        target_dir = tmp_path / "commands"

        # First install
        success1, message1 = install_commands(target_path=target_dir, force=False)
        assert success1 is True

        # Commands are in commands/sc/ subdirectory
        commands_dir = tmp_path / "commands" / "sc"
        research_file = commands_dir / "research.md"

        # Modify a file
        research_file.write_text("modified")
        assert research_file.read_text() == "modified"

        # Force reinstall
        success2, message2 = install_commands(target_path=target_dir, force=True)
        assert success2 is True
        assert "installed" in message2.lower()

        # Verify file was overwritten
        content = research_file.read_text()
        assert content != "modified"
        assert "research" in content.lower()

    def test_list_installed_commands(self, tmp_path):
        """Test listing installed commands"""
        target_dir = tmp_path / "commands"

        # Note: list_installed_commands checks ~/.claude/commands/sc by default
        # We can't easily test this without mocking, so just verify it returns a list
        installed = list_installed_commands()
        assert isinstance(installed, list)

        # After install to temp dir
        install_commands(target_path=target_dir, force=False)

        # Commands are in commands/sc/ subdirectory
        commands_dir = tmp_path / "commands" / "sc"

        # Verify files exist
        command_files = list(commands_dir.glob("*.md"))
        assert len(command_files) > 0

    def test_install_commands_creates_target_directory(self, tmp_path):
        """Test that target directory is created if it doesn't exist"""
        target_dir = tmp_path / "nested" / "commands"

        assert not target_dir.exists()

        success, message = install_commands(target_path=target_dir, force=False)

        assert success is True
        # Commands are in commands/sc/ subdirectory
        commands_dir = tmp_path / "nested" / "commands" / "sc"
        assert commands_dir.exists()

    def test_available_commands_format(self):
        """Test that available commands have expected format"""
        commands = list_available_commands()

        # Should be list of strings
        assert all(isinstance(cmd, str) for cmd in commands)

        # Should not include file extensions
        assert all(not cmd.endswith(".md") for cmd in commands)

        # Should be sorted
        assert commands == sorted(commands)

    def test_research_command_exists(self, tmp_path):
        """Test that research command specifically gets installed"""
        target_dir = tmp_path / "commands"

        install_commands(target_path=target_dir, force=False)

        # Commands are in commands/sc/ subdirectory
        commands_dir = tmp_path / "commands" / "sc"
        research_file = commands_dir / "research.md"
        assert research_file.exists()

        content = research_file.read_text()
        assert "research" in content.lower()
        assert len(content) > 100  # Should have substantial content

    def test_all_expected_commands_available(self):
        """Test that all expected commands are available"""
        commands = list_available_commands()

        expected = ["agent", "index-repo", "recommend", "research"]

        for expected_cmd in expected:
            assert expected_cmd in commands, (
                f"Expected command '{expected_cmd}' not found"
            )


class TestInstallCommandsEdgeCases:
    """Test edge cases and error handling"""

    def test_install_to_nonexistent_parent(self, tmp_path):
        """Test installation to path with nonexistent parent directories"""
        target_dir = tmp_path / "a" / "b" / "c" / "commands"

        success, message = install_commands(target_path=target_dir, force=False)

        assert success is True
        # Commands are in commands/sc/ subdirectory
        commands_dir = tmp_path / "a" / "b" / "c" / "commands" / "sc"
        assert commands_dir.exists()

    def test_empty_target_directory_ok(self, tmp_path):
        """Test that installation works with empty target directory"""
        target_dir = tmp_path / "commands"
        target_dir.mkdir()

        success, message = install_commands(target_path=target_dir, force=False)

        assert success is True


def test_cli_integration():
    """
    Integration test: verify CLI can import and use install functions

    This tests that the CLI main.py can successfully import the functions
    """
    from superclaude.cli.install_commands import (
        list_available_commands,
    )

    # Should not raise ImportError
    commands = list_available_commands()
    assert len(commands) > 0


class TestRegisteredHookVisibility:
    """--list-all must show what Claude Code will actually run.

    The "Hook configuration" row only reports that hooks.json arrived. Claude
    Code runs settings.json, and an install whose settings froze reads as fully
    current on that row alone — which is how a shipped hook stayed unregistered
    in a real install for weeks without anything reporting it.
    """

    SC = "~/.claude/superclaude/scripts"

    def _install(self, tmp_path, registered: list[str]):
        import json

        base = tmp_path / ".claude"
        (base / "hooks").mkdir(parents=True)
        (base / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
        (base / "settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "PostToolUse": [
                            {
                                "matcher": "Edit|Write",
                                "hooks": [
                                    {"command": f"python {self.SC}/{name}"}
                                    for name in registered
                                ],
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )
        return base

    def test_shipped_count_comes_from_hooks_json(self):
        """Every inner hook across every event type counts once."""
        from superclaude.cli.install_inventory import _count_shipped_hooks
        from superclaude.cli.install_paths import _get_package_root

        shipped = _count_shipped_hooks(_get_package_root() / "hooks" / "hooks.json")
        assert shipped >= 10, f"expected the full shipped hook set, got {shipped}"

    def test_registered_count_ignores_user_hooks(self, tmp_path):
        from superclaude.cli.install_inventory import _count_registered_hooks

        base = self._install(tmp_path, ["prettier_hook.py", "loop_guard.py"])
        import json

        settings = json.loads((base / "settings.json").read_text(encoding="utf-8"))
        settings["hooks"]["PostToolUse"].append(
            {"matcher": "Edit", "hooks": [{"command": "npm run lint"}]}
        )
        (base / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

        assert _count_registered_hooks(base / "settings.json") == 2

    def test_frozen_install_shows_a_shortfall(self, tmp_path):
        """The row is the signal: fewer registered than shipped."""
        from superclaude.cli.install_inventory import list_all_components

        base = self._install(tmp_path, ["prettier_hook.py"])
        row = list_all_components(base_path=base, scope="user")["hooks_registered"]

        assert row["installed"] == 1
        assert row["available"] > row["installed"], (
            "a frozen install must not read as complete"
        )

    def test_local_scope_reads_settings_local(self, tmp_path):
        from superclaude.cli.install_inventory import list_all_components

        base = self._install(tmp_path, ["prettier_hook.py"])
        (base / "settings.local.json").write_text(
            (base / "settings.json").read_text(encoding="utf-8"), encoding="utf-8"
        )
        (base / "settings.json").unlink()

        row = list_all_components(base_path=base, scope="local")["hooks_registered"]
        assert row["installed"] == 1
        assert row["target_path"].endswith("settings.local.json")


class TestAgentMemoryDirectory:
    """Every agent declares a memory store; nothing created the directory.

    Per .claude/rules/agent-authoring.md a local install rewrites agents to
    `memory: local`, whose files belong at `.claude/agent-memory-local/<agent>/`.
    That path did not exist in the one real local install on record, and nothing
    in the CLI made it — 23 agents each pointing at a store that was not there
    (A11-b).
    """

    def test_each_scope_gets_its_own_root(self, tmp_path):
        from superclaude.cli.install_components import ensure_agent_memory_dir

        base = tmp_path / ".claude"
        assert ensure_agent_memory_dir(base, "user").name == "agent-memory"
        assert ensure_agent_memory_dir(base, "project").name == "agent-memory"
        assert ensure_agent_memory_dir(base, "local").name == "agent-memory-local"

    def test_directory_is_created(self, tmp_path):
        from superclaude.cli.install_components import ensure_agent_memory_dir

        base = tmp_path / ".claude"
        created = ensure_agent_memory_dir(base, "local")

        assert created is not None and created.is_dir()

    def test_unknown_scope_creates_nothing(self, tmp_path):
        """`target` scope has no documented memory location — do not guess one."""
        from superclaude.cli.install_components import ensure_agent_memory_dir

        base = tmp_path / ".claude"
        assert ensure_agent_memory_dir(base, "target") is None
        assert not (base / "agent-memory").exists()
        assert not (base / "agent-memory-local").exists()

    def test_install_makes_it(self, tmp_path):
        """End to end: a local install leaves the store its agents point at."""
        from superclaude.cli.install_components import install_all

        base = tmp_path / ".claude"
        success, message = install_all(base_path=base, force=True, scope="local")

        assert success, message
        assert (base / "agent-memory-local").is_dir()



class TestFrameworkArtifactsAlwaysUpdate:
    """Scripts and hooks.json are build outputs, so an upgrade must refresh them.

    `superclaude install` without `--force` used to skip any script already on
    disk while still merging the *package's* hooks.json into settings.json. A
    release that adds a hook therefore registered a subcommand the installed
    script did not implement: `insight_writer.py request-from-hook` reached
    argparse, exited 2 — the blocking code on `Stop` — and pushed usage text back
    into the model on every turn. The mirror failure is that none of a release's
    script fixes shipped either.

    These files are SuperClaude-owned outputs, not user-editable content, so
    `--force` keeps its meaning for settings, commands, agents and core only.
    """

    def test_stale_script_is_replaced_without_force(self, tmp_path):
        from superclaude.cli.install_components import install_hooks_and_scripts

        base = tmp_path / ".claude"
        scripts_target = base / "superclaude" / "scripts"
        scripts_target.mkdir(parents=True)
        stale = scripts_target / "insight_writer.py"
        stale.write_text("# previous release, no request subcommand\n", encoding="utf-8")

        installed, _skipped, failed, messages = install_hooks_and_scripts(
            base_path=base, force=False, scope="user"
        )

        assert failed == 0, messages
        assert "request-from-hook" in stale.read_text(encoding="utf-8"), (
            "a non-force install left the previous release's script in place while "
            "registering a hook that needs the new one"
        )
        assert installed > 0

    def test_stale_hooks_json_is_replaced_without_force(self, tmp_path):
        from superclaude.cli.install_components import install_hooks_and_scripts

        base = tmp_path / ".claude"
        hooks_target = base / "hooks"
        hooks_target.mkdir(parents=True)
        stale = hooks_target / "hooks.json"
        stale.write_text('{"hooks": {}}\n', encoding="utf-8")

        _installed, _skipped, failed, messages = install_hooks_and_scripts(
            base_path=base, force=False, scope="user"
        )

        assert failed == 0, messages
        assert "Stop" in stale.read_text(encoding="utf-8"), (
            "the on-disk hooks.json still describes a previous release"
        )

    def test_every_registered_command_is_supported_by_its_script(self):
        """The invariant that would have caught the version skew at authoring time.

        Each `command` in hooks.json names a script and, sometimes, a subcommand.
        Both have to exist in the shipped script.
        """
        import json
        import re
        from pathlib import Path

        package_root = Path(__file__).parent.parent.parent / "src" / "superclaude"
        config = json.loads(
            (package_root / "hooks" / "hooks.json").read_text(encoding="utf-8")
        )

        unsupported = []
        for event, entries in config.get("hooks", {}).items():
            for entry in entries:
                for hook in entry.get("hooks", []):
                    command = hook.get("command", "")
                    match = re.search(r"([A-Za-z0-9_]+\.py)(.*)$", command)
                    assert match, f"{event}: cannot parse command {command!r}"

                    script = package_root / "scripts" / match.group(1)
                    if not script.exists():
                        unsupported.append(f"{event}: {match.group(1)} does not ship")
                        continue

                    source = script.read_text(encoding="utf-8")
                    for token in match.group(2).split():
                        if token.startswith("-"):
                            continue
                        if f'"{token}"' not in source and f"'{token}'" not in source:
                            unsupported.append(
                                f"{event}: {match.group(1)} does not accept {token!r}"
                            )

        assert not unsupported, "\n".join(unsupported)


class TestHookRegistrationIsCheckedByIdentity:
    """`N/N ✅` has to mean the shipped hooks are the registered hooks.

    The row compared two integers. Fourteen obsolete SuperClaude hooks and
    fourteen shipped ones read as `14/14 ✅`, certifying an install whose
    settings pointed at scripts this release no longer has — the exact state a
    `--force` install could not clear.
    """

    SC = "~/.claude/superclaude/scripts"

    def _base(self, tmp_path, hooks: dict):
        import json

        base = tmp_path / ".claude"
        (base / "hooks").mkdir(parents=True)
        (base / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
        (base / "settings.json").write_text(
            json.dumps({"hooks": hooks}), encoding="utf-8"
        )
        return base

    def test_obsolete_hooks_do_not_read_as_installed(self, tmp_path):
        from superclaude.cli.install_inventory import (
            _count_shipped_hooks,
            list_all_components,
        )
        from superclaude.cli.install_paths import _get_package_root

        shipped = _count_shipped_hooks(_get_package_root() / "hooks" / "hooks.json")
        base = self._base(
            tmp_path,
            {
                "PostToolUse": [
                    {
                        "matcher": "Edit",
                        "hooks": [
                            {"command": f"python {self.SC}/retired_{i}.py"}
                            for i in range(shipped)
                        ],
                    }
                ]
            },
        )

        row = list_all_components(base_path=base, scope="user")["hooks_registered"]

        assert row["available"] == shipped
        assert row["installed"] == 0, "obsolete registrations counted as installed"
        assert row["obsolete"] == shipped
        assert row["missing"] == shipped

    def test_a_matching_registration_counts(self, tmp_path):
        from superclaude.cli.install_inventory import list_all_components

        base = self._base(
            tmp_path,
            {
                "PostToolUse": [
                    {
                        "matcher": "Edit|Write",
                        "hooks": [{"command": f"python {self.SC}/prettier_hook.py"}],
                    }
                ]
            },
        )

        row = list_all_components(base_path=base, scope="user")["hooks_registered"]

        assert row["installed"] == 1
        assert row["obsolete"] == 0

    def test_a_duplicate_registration_is_named(self, tmp_path):
        from superclaude.cli.install_inventory import list_all_components

        base = self._base(
            tmp_path,
            {
                "PostToolUse": [
                    {
                        "matcher": "Edit|Write",
                        "hooks": [
                            {"command": f"python {self.SC}/prettier_hook.py"},
                            {"command": f"python {self.SC}/prettier_hook.py"},
                        ],
                    }
                ]
            },
        )

        row = list_all_components(base_path=base, scope="user")["hooks_registered"]

        assert row["installed"] == 1
        assert row["duplicate"] == 1

    def test_dry_run_uninstall_counts_inner_hooks(self, tmp_path):
        """`--dry-run` said "N hooks" while counting entries, so it under-reported."""
        from superclaude.cli.install_inventory import uninstall_all

        base = self._base(
            tmp_path,
            {
                "PostToolUse": [
                    {
                        "matcher": "Edit",
                        "hooks": [
                            {"command": f"python {self.SC}/prettier_hook.py"},
                            {"command": f"python {self.SC}/loop_guard.py"},
                        ],
                    }
                ]
            },
        )

        _success, message = uninstall_all(base_path=base, scope="user", dry_run=True)

        assert "2 SuperClaude hooks" in message, message


class TestFailuresReachTheSummary:
    """`0 failed` has to mean nothing failed.

    `ensure_agent_memory_dir` swallowed OSError and returned None, and the caller
    discarded the return value — so agents were rewritten to point at a store
    that could not be created while the install reported success. Three more
    steps printed ❌ or ⚠️ without touching the failure count, which is how
    `overall_success` could be True with a ❌ on screen.
    """

    def test_a_blocked_memory_directory_fails_the_install(self, tmp_path):
        from superclaude.cli.install_components import install_all

        base = tmp_path / ".claude"
        base.mkdir(parents=True)
        # A regular file where the store belongs: mkdir raises FileExistsError.
        (base / "agent-memory-local").write_text("not a directory", encoding="utf-8")

        success, message = install_all(base_path=base, force=True, scope="local")

        assert not success, message
        assert "0 failed" not in message, message

    def test_an_unsupported_scope_is_not_a_failure(self, tmp_path):
        """`target` has no documented store; absence by design is not an error."""
        from superclaude.cli.install_components import ensure_agent_memory_dir

        assert ensure_agent_memory_dir(tmp_path / ".claude", "target") is None

    def test_a_healthy_install_still_reports_success(self, tmp_path):
        from superclaude.cli.install_components import install_all

        success, message = install_all(
            base_path=tmp_path / ".claude", force=True, scope="local"
        )

        assert success, message
