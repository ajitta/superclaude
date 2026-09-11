"""
Unit tests for CLI install command

Tests the command installation functionality.
"""

from pathlib import Path

import pytest

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
    """hooks.json is a build output, so an upgrade must refresh it.

    The scripts a hook runs ship inside the package now — every command is
    `superclaude hook <name>` — so the version skew that motivated this class
    (a release registering `insight_writer request-from-hook` against an
    installed script copy that did not implement it: argparse exit 2, the
    blocking code on `Stop`, on every turn) cannot recur: the script and the
    registration come from the same install. What is still on disk per
    install, hooks.json, is SuperClaude-owned output, not user-editable content,
    so `--force` keeps its meaning for settings, commands, agents and core only.
    """

    def test_no_script_copies_are_installed(self, tmp_path):
        from superclaude.cli.install_components import install_hooks

        base = tmp_path / ".claude"
        _installed, _skipped, failed, messages = install_hooks(
            base_path=base, force=True, scope="user"
        )

        assert failed == 0, messages
        assert not (base / "superclaude" / "scripts").exists()

    def test_legacy_script_copies_are_left_in_place_and_named(self, tmp_path):
        """A previous release's copies are NOT deleted on upgrade.

        A session on an older Claude Code, or a registration a non-force
        install left in legacy form, still runs these files; python's "can't
        open file" is exit 2, the blocking code, and deleting them under such a
        session blocks every tool call until restart. The install says what
        they are and when to remove them.
        """
        from superclaude.cli.install_components import install_hooks

        base = tmp_path / ".claude"
        legacy = base / "superclaude" / "scripts"
        legacy.mkdir(parents=True)
        (legacy / "loop_guard.py").write_text("# previous release\n", encoding="utf-8")

        _installed, _skipped, failed, messages = install_hooks(
            base_path=base, force=True, scope="user"
        )

        assert failed == 0, messages
        assert (legacy / "loop_guard.py").exists()
        notice = [m for m in messages if str(legacy) in m]
        assert notice and "restart" in notice[0].lower(), messages

    def test_stale_hooks_json_is_replaced_without_force(self, tmp_path):
        from superclaude.cli.install_components import install_hooks

        base = tmp_path / ".claude"
        hooks_target = base / "hooks"
        hooks_target.mkdir(parents=True)
        stale = hooks_target / "hooks.json"
        stale.write_text('{"hooks": {}}\n', encoding="utf-8")

        _installed, _skipped, failed, messages = install_hooks(
            base_path=base, force=False, scope="user"
        )

        assert failed == 0, messages
        assert "Stop" in stale.read_text(encoding="utf-8"), (
            "the on-disk hooks.json still describes a previous release"
        )

    def test_every_registered_command_is_supported_by_its_script(self):
        """The invariant that would have caught the version skew at authoring time.

        Each `command` in hooks.json is `superclaude hook <name> [subcommand]`.
        The name has to be in the dispatcher's registry, arguments may only go
        to a hook that forwards them, and a subcommand has to be one the shipped
        script's own parser accepts.
        """
        import json
        import re
        from pathlib import Path

        from superclaude.cli.hook_dispatch import HOOKS

        package_root = Path(__file__).parent.parent.parent / "src" / "superclaude"
        config = json.loads(
            (package_root / "hooks" / "hooks.json").read_text(encoding="utf-8")
        )

        unsupported = []
        for event, entries in config.get("hooks", {}).items():
            for entry in entries:
                for hook in entry.get("hooks", []):
                    command = hook.get("command", "")
                    match = re.fullmatch(
                        r"superclaude hook ([A-Za-z0-9_]+)(.*)", command
                    )
                    assert match, f"{event}: cannot parse command {command!r}"

                    name = match.group(1)
                    if name not in HOOKS:
                        unsupported.append(f"{event}: {name} is not a registered hook")
                        continue
                    _module, forwards_argv = HOOKS[name]
                    tokens = match.group(2).split()
                    if tokens and not forwards_argv:
                        unsupported.append(
                            f"{event}: {name} takes no arguments but is given {tokens}"
                        )
                        continue

                    source = (package_root / "scripts" / f"{name}.py").read_text(
                        encoding="utf-8"
                    )
                    for token in tokens:
                        if token.startswith("-"):
                            continue
                        if f'"{token}"' not in source and f"'{token}'" not in source:
                            unsupported.append(
                                f"{event}: {name} does not accept {token!r}"
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


class TestListingResolvesTheInstallInEffect:
    """--list/--list-all report on an install, so they walk up to it.

    Following the write path's user-scope default instead printed [0/23] on
    every row inside a project with a local install, while `superclaude doctor`
    called that same install healthy. Writing still follows the shell — only
    reporting walks up.
    """

    def _run(self, args, home, cwd, monkeypatch):
        from click.testing import CliRunner

        from superclaude.cli.main import main

        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        monkeypatch.chdir(cwd)
        return CliRunner().invoke(main, args)

    def _make_local_install(self, project: Path) -> None:
        (project / ".claude" / "superclaude").mkdir(parents=True)
        (project / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )

    def test_list_all_reports_the_local_install(self, tmp_path, monkeypatch):
        home = tmp_path / "home"
        home.mkdir()
        project = home / "project"
        project.mkdir()
        self._make_local_install(project)

        result = self._run(["install", "--list-all"], home, project, monkeypatch)

        assert "(scope: local)" in result.output
        assert str(project / ".claude") in result.output

    def test_list_reports_the_local_install(self, tmp_path, monkeypatch):
        home = tmp_path / "home"
        home.mkdir()
        project = home / "project"
        project.mkdir()
        self._make_local_install(project)

        result = self._run(["install", "--list"], home, project, monkeypatch)

        assert "(scope: local)" in result.output

    def test_explicit_scope_still_wins(self, tmp_path, monkeypatch):
        home = tmp_path / "home"
        home.mkdir()
        project = home / "project"
        project.mkdir()
        self._make_local_install(project)

        result = self._run(
            ["install", "--list-all", "--scope", "user"], home, project, monkeypatch
        )

        assert "(scope: user)" in result.output

    def test_falls_back_to_user_scope_with_no_install_above(
        self, tmp_path, monkeypatch
    ):
        home = tmp_path / "home"
        home.mkdir()
        elsewhere = home / "elsewhere"
        elsewhere.mkdir()

        result = self._run(["install", "--list-all"], home, elsewhere, monkeypatch)

        assert "(scope: user)" in result.output

    def test_home_install_is_not_reported_as_project(self, tmp_path, monkeypatch):
        """The walk-up skips $HOME, so a user install stays named user scope."""
        home = tmp_path / "home"
        (home / ".claude" / "superclaude").mkdir(parents=True)
        (home / ".claude" / "CLAUDE.md").write_text(
            "@superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        elsewhere = home / "elsewhere"
        elsewhere.mkdir()

        result = self._run(["install", "--list-all"], home, elsewhere, monkeypatch)

        assert "(scope: user)" in result.output


class TestWritePathKeepsTheShellAnchor:
    """Rebinding scope for the listing branches must not reach the install path.

    Both listing branches return, so it cannot today — this pins that, because
    the rebinding sits in the same function as the write path a few lines below.
    """

    def test_plain_install_still_targets_user_scope(self, tmp_path, monkeypatch):
        from click.testing import CliRunner

        from superclaude.cli.main import main

        home = tmp_path / "home"
        home.mkdir()
        project = home / "project"
        (project / ".claude" / "superclaude").mkdir(parents=True)
        (project / "CLAUDE.local.md").write_text(
            "@.claude/superclaude/CLAUDE_SC.md\n", encoding="utf-8"
        )
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        monkeypatch.setenv("HOME", str(home))
        monkeypatch.chdir(project)

        result = CliRunner().invoke(main, ["install", "--force"])

        assert "(scope: user)" in result.output
        assert (home / ".claude" / "superclaude" / "CLAUDE_SC.md").exists()


class TestLegacySkillsArePrunedOnUpgrade:
    """Skills from a pre-removal release must not survive an upgrade.

    The layer was deleted, so there is no source dir to diff an install against.
    Without an explicit prune the directories stay forever: the two
    auto-invocable ones (confidence-check, verbalized-sampling) keep firing with
    no source left to explain them, and a local-scope install no longer
    git-excludes them, so they surface as untracked files in a team repo.
    """

    LEGACY = (
        "confidence-check",
        "finishing-a-development-branch",
        "ship",
        "simplicity-coach",
        "verbalized-sampling",
    )

    def _seed(self, base_path: Path, names) -> None:
        for name in names:
            d = base_path / "skills" / name
            d.mkdir(parents=True, exist_ok=True)
            (d / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")

    def test_install_removes_them(self, tmp_path):
        from superclaude.cli.install_components import install_all

        self._seed(tmp_path, self.LEGACY)

        success, _ = install_all(base_path=tmp_path, force=True, scope="project")

        assert success is True
        for name in self.LEGACY:
            assert not (tmp_path / "skills" / name).exists(), (
                f"{name} survived the install — an upgrade leaves it firing forever"
            )

    def test_install_preserves_skills_superclaude_never_shipped(self, tmp_path):
        """.claude/skills is shared; only the exact shipped names may be touched."""
        from superclaude.cli.install_components import install_all

        self._seed(tmp_path, [*self.LEGACY, "someone-elses-skill"])

        install_all(base_path=tmp_path, force=True, scope="project")

        assert (tmp_path / "skills" / "someone-elses-skill" / "SKILL.md").exists()

    def test_uninstall_removes_them_too(self, tmp_path):
        from superclaude.cli.install_inventory import uninstall_all

        self._seed(tmp_path, [*self.LEGACY, "someone-elses-skill"])

        uninstall_all(base_path=tmp_path, dry_run=False)

        for name in self.LEGACY:
            assert not (tmp_path / "skills" / name).exists()
        assert (tmp_path / "skills" / "someone-elses-skill").exists()

    def test_a_clean_install_says_nothing_about_them(self, tmp_path):
        """No legacy dirs present -> no cleanup line in the summary."""
        from superclaude.cli.install_components import install_all

        _success, message = install_all(base_path=tmp_path, force=True, scope="project")

        assert "pre-removal" not in message


class TestHookCommandsCarryNoMachineBytes:
    """The registration is the same bytes on every machine, at every scope.

    Releases before the console entry baked two machine-specific halves into
    each command: the installer's interpreter and the directory holding a copy
    of the script. Project scope's committed settings.json was therefore
    rewritten by every teammate's install, and a linked git worktree — where
    Claude Code reads settings from the MAIN worktree but expands
    ``$CLAUDE_PROJECT_DIR`` to the linked one — broke every hook that named a
    directory through that variable. `superclaude hook <name>` names neither.
    """

    @staticmethod
    def _hook_commands(base, scope):
        """Commands as Claude Code will read them: from the settings file.

        Deliberately NOT ``.claude/hooks/hooks.json``. Both are written from the
        same content today, but the settings file is the one CC actually loads;
        asserting on the intermediate artifact would keep this test green
        through a regression in the merge path.
        """
        import json

        from superclaude.utils import settings_filename

        config = json.loads(
            (base / settings_filename(scope)).read_text(encoding="utf-8")
        )
        return [
            hook["command"]
            for event in config["hooks"].values()
            for group in event
            for hook in group["hooks"]
            if "superclaude" in hook.get("command", "")
        ]

    @pytest.mark.parametrize("scope", ["user", "project", "local"])
    def test_every_command_is_the_bare_console_entry(self, tmp_path, scope):
        import sys

        from superclaude.cli.install_components import install_hooks

        base = tmp_path / ".claude"
        _installed, _skipped, failed, messages = install_hooks(
            base_path=base, force=True, scope=scope
        )

        assert failed == 0, messages
        commands = self._hook_commands(base, scope)
        assert commands
        for command in commands:
            assert command.startswith("superclaude hook "), command
            assert str(tmp_path) not in command, "install directory baked in"
            assert sys.executable not in command, "interpreter baked in"
            assert "$CLAUDE_PROJECT_DIR" not in command, "worktree-fragile anchor"
            assert ".py" not in command, "script path baked in"

    def test_two_machines_write_byte_identical_settings(self, tmp_path, monkeypatch):
        """Project scope's whole promise: two developers, two interpreters, two
        checkout paths, one committed settings.json with no diff between them."""
        import sys

        from superclaude.cli.install_components import install_hooks

        written = []
        for machine, interpreter in (
            ("alice", "/opt/homebrew/bin/python3.13"),
            ("bob", "C:/Users/bob/AppData/Local/Programs/Python/python.exe"),
        ):
            base = tmp_path / machine / "checkout" / ".claude"
            monkeypatch.setattr(sys, "executable", interpreter)
            _installed, _skipped, failed, messages = install_hooks(
                base_path=base, force=True, scope="project"
            )
            assert failed == 0, messages
            written.append(
                (
                    (base / "settings.json").read_bytes(),
                    (base / "hooks" / "hooks.json").read_bytes(),
                )
            )

        assert written[0] == written[1]

    def test_the_installed_hooks_json_is_the_shipped_one_verbatim(self, tmp_path):
        from superclaude.cli.install_components import install_hooks
        from superclaude.cli.install_paths import _get_package_root

        base = tmp_path / ".claude"
        install_hooks(base_path=base, force=True, scope="project")

        shipped = (_get_package_root() / "hooks" / "hooks.json").read_bytes()
        assert (base / "hooks" / "hooks.json").read_bytes() == shipped


def _legacy_registration(base: Path, names: list[str], interpreter: str) -> None:
    """A settings.json the previous release would have written: resolved
    interpreter plus a script copy under <base>/superclaude/scripts/."""
    import json

    scripts = base / "superclaude" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    entries = []
    for name in names:
        (scripts / f"{name}.py").write_text("# previous release\n", encoding="utf-8")
        entries.append(
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "_comment": f"[superclaude] {name}",
                        "type": "command",
                        "command": f"{interpreter} {scripts}/{name}.py",
                        "timeout": 5,
                    }
                ],
            }
        )
    (base / "settings.json").write_text(
        json.dumps({"hooks": {"PreToolUse": entries}}), encoding="utf-8"
    )


def _sc_commands(base: Path, scope: str) -> list[str]:
    import json

    from superclaude.utils import settings_filename

    config = json.loads((base / settings_filename(scope)).read_text(encoding="utf-8"))
    return [
        hook["command"]
        for event in config["hooks"].values()
        for group in event
        for hook in group["hooks"]
    ]


class TestUpgradeFromALegacyRegistration:
    """The default (non-force) install over a previous release's registration.

    That release's commands named the installing machine's interpreter and
    checkout. Project scope now commits the file, so leaving those commands
    in place on the default upgrade exposed them for commit — while the
    legacy-scripts notice told the user to delete the directory those very
    commands still ran.
    """

    def test_non_force_rewrites_every_legacy_command(self, tmp_path):
        from superclaude.cli.install_components import install_hooks

        base = tmp_path / ".claude"
        _legacy_registration(
            base, ["destructive_guard", "loop_guard"], "/opt/py/bin/python3"
        )

        _i, _s, failed, messages = install_hooks(
            base_path=base, force=False, scope="user"
        )

        assert failed == 0, messages
        commands = _sc_commands(base, "user")
        assert commands and all(c.startswith("superclaude hook ") for c in commands), (
            commands
        )
        assert any("2 legacy command(s) rewritten" in m for m in messages), messages

    def test_notice_says_remove_after_restart_once_nothing_runs_the_copies(
        self, tmp_path
    ):
        from superclaude.cli.install_components import install_hooks

        base = tmp_path / ".claude"
        _legacy_registration(base, ["loop_guard"], "/opt/py/bin/python3")

        _i, _s, _f, messages = install_hooks(base_path=base, force=False, scope="user")

        notice = [m for m in messages if m.startswith("ℹ️")]
        assert len(notice) == 1, messages
        assert "remove it after restarting" in notice[0]
        assert "do not remove" not in notice[0]

    def test_notice_forbids_removal_while_a_registration_still_runs_the_copies(
        self, tmp_path
    ):
        """A hook this release no longer ships stays in its legacy form on a
        non-force install, so the copies it runs must stay too."""
        from superclaude.cli.install_components import install_hooks

        base = tmp_path / ".claude"
        _legacy_registration(base, ["retired_thing"], "/opt/py/bin/python3")

        _i, _s, _f, messages = install_hooks(base_path=base, force=False, scope="user")

        notice = [m for m in messages if m.startswith("ℹ️")]
        assert len(notice) == 1, messages
        assert "do not remove" in notice[0]
        assert "--force" in notice[0]
        assert (base / "superclaude" / "scripts" / "retired_thing.py").exists()


class TestConsoleScriptWarning:
    """The installer's only signal for the PATH blocker the request named.

    It reads the probe rather than a bare `shutil.which`: under `uv run` — every
    `make sync-*` target — which() found the venv shim the user's shell never
    sees, so the warning could not fire from the documented install path.
    """

    @staticmethod
    def _messages(monkeypatch, tmp_path, probe: dict) -> list[str]:
        from superclaude.cli import install_components

        monkeypatch.setattr(install_components, "probe_console_script", lambda: probe)
        _i, _s, _f, messages = install_components.install_hooks(
            base_path=tmp_path / ".claude", force=True, scope="user"
        )
        return [m for m in messages if m.startswith("⚠️")]

    def test_missing_script_names_path_and_the_exit_code(self, tmp_path, monkeypatch):
        warnings = self._messages(
            monkeypatch,
            tmp_path,
            {"path": None, "excluded": None, "has_hook": None, "version": None},
        )

        assert len(warnings) == 1, warnings
        assert "PATH" in warnings[0] and "127" in warnings[0]

    def test_an_excluded_own_bin_is_named(self, tmp_path, monkeypatch):
        warnings = self._messages(
            monkeypatch,
            tmp_path,
            {
                "path": None,
                "excluded": "/repo/.venv/bin",
                "has_hook": None,
                "version": None,
            },
        )

        assert "/repo/.venv/bin" in warnings[0]

    def test_a_script_without_the_hook_subcommand_is_reported(
        self, tmp_path, monkeypatch
    ):
        warnings = self._messages(
            monkeypatch,
            tmp_path,
            {
                "path": "/usr/local/bin/superclaude",
                "excluded": None,
                "has_hook": False,
                "version": "4.8.0",
            },
        )

        assert len(warnings) == 1, warnings
        assert "no `hook` subcommand" in warnings[0] and "4.8.0" in warnings[0]

    def test_a_different_version_on_path_is_reported(self, tmp_path, monkeypatch):
        warnings = self._messages(
            monkeypatch,
            tmp_path,
            {
                "path": "/usr/local/bin/superclaude",
                "excluded": None,
                "has_hook": True,
                "version": "0.0.1",
            },
        )

        assert len(warnings) == 1, warnings
        assert "0.0.1" in warnings[0]

    def test_a_matching_script_warns_about_nothing(self, tmp_path, monkeypatch):
        from superclaude import __version__

        warnings = self._messages(
            monkeypatch,
            tmp_path,
            {
                "path": "/usr/local/bin/superclaude",
                "excluded": None,
                "has_hook": True,
                "version": __version__,
            },
        )

        assert warnings == []


class TestRegistrationFilesAreWrittenWithLF:
    """Project scope commits settings.json and hooks/hooks.json. Text mode with
    no newline argument writes CRLF on Windows, which would make every Windows
    teammate's install dirty both files. Windows is not available here, so the
    write sites are checked for the argument that pins the newline."""

    def test_settings_json_writer_pins_newline_and_encoding(
        self, tmp_path, monkeypatch
    ):
        import os

        from superclaude import utils

        seen = {}
        real_fdopen = os.fdopen

        def recording_fdopen(fd, *args, **kwargs):
            seen.update(kwargs)
            return real_fdopen(fd, *args, **kwargs)

        monkeypatch.setattr(utils.os, "fdopen", recording_fdopen)
        utils.atomic_write_json(tmp_path / "settings.json", {"hooks": {}})

        assert seen.get("newline") == "\n", seen
        assert seen.get("encoding") == "utf-8", seen

    def test_hooks_json_copy_pins_newline_and_encoding(self, tmp_path, monkeypatch):
        import builtins

        from superclaude.cli import install_components

        seen = {}

        def recording_open(path, *args, **kwargs):
            if str(path).endswith("hooks.json") and args and "w" in args[0]:
                seen.update(kwargs)
            return builtins.open(path, *args, **kwargs)

        monkeypatch.setattr(install_components, "open", recording_open, raising=False)
        install_components.install_hooks(
            base_path=tmp_path / ".claude", force=True, scope="user"
        )

        assert seen.get("newline") == "\n", seen
        assert seen.get("encoding") == "utf-8", seen


class TestTeamIgnoreOfTheRegistrationIsReported:
    """Project scope stopped excluding settings.json so the team can commit it,
    but a team-level .gitignore can still hide it — this repository's own
    .gitignore does — and the install used to say nothing."""

    @staticmethod
    def _isolated_repo(tmp_path, monkeypatch):
        """The developer's global excludes file must not decide these tests."""
        import subprocess

        empty = tmp_path / "empty-gitconfig"
        empty.write_text("", encoding="utf-8")
        monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        return repo

    def test_install_all_names_the_rule(self, tmp_path, monkeypatch):
        from superclaude.cli.install_components import install_all

        repo = self._isolated_repo(tmp_path, monkeypatch)
        (repo / ".gitignore").write_text(
            "# team rules\n.claude/settings.json\n", encoding="utf-8"
        )

        _ok, message = install_all(
            base_path=repo / ".claude", force=True, scope="project"
        )

        assert ".gitignore:2 ignores .claude/settings.json" in message, message
        assert "hooks/hooks.json" not in [
            line for line in message.splitlines() if "ignores" in line
        ], "hooks.json is not ignored here and must not be reported"

    def test_a_clean_repo_gets_no_ignore_warning(self, tmp_path, monkeypatch):
        from superclaude.cli.install_components import install_all

        repo = self._isolated_repo(tmp_path, monkeypatch)

        _ok, message = install_all(
            base_path=repo / ".claude", force=True, scope="project"
        )

        assert "ignores .claude/" not in message, message


class TestOutputStylesInstallIntoClaudeCodesDirectory:
    """Output styles land where Claude Code reads them and leave the user's own alone.

    `<scope>/output-styles/` is Claude Code's directory, shared with styles the
    user wrote by hand. Install must put the shipped file there (not under
    `superclaude/`, which Claude Code never scans), and uninstall must remove
    only the shipped filenames, so a hand-written style survives.
    """

    SHIPPED = "plain-language.md"

    def test_install_copies_the_style_where_claude_code_scans(self, tmp_path):
        from superclaude.cli.install_components import install_all

        success, message = install_all(base_path=tmp_path, force=True, scope="project")

        assert success is True, message
        installed = tmp_path / "output-styles" / self.SHIPPED
        assert installed.is_file()
        assert "Output styles: 1 installed" in message
        source = (
            Path(__file__).parents[2]
            / "src"
            / "superclaude"
            / "output-styles"
            / self.SHIPPED
        )
        assert installed.read_bytes() == source.read_bytes(), "copied verbatim"

    def test_listing_counts_it(self, tmp_path):
        from superclaude.cli.install_components import install_all
        from superclaude.cli.install_inventory import list_all_components

        install_all(base_path=tmp_path, force=True, scope="project")
        row = list_all_components(base_path=tmp_path, scope="project")["output-styles"]

        assert row["available"] >= 1
        assert row["installed"] == row["available"]

    def test_uninstall_removes_only_the_shipped_style(self, tmp_path):
        from superclaude.cli.install_components import install_all
        from superclaude.cli.install_inventory import uninstall_all

        install_all(base_path=tmp_path, force=True, scope="project")
        own = tmp_path / "output-styles" / "my-team-voice.md"
        own.write_text("---\nname: Team Voice\n---\nBe terse.\n", encoding="utf-8")

        success, message = uninstall_all(base_path=tmp_path, scope="project")

        assert success is True, message
        assert not (tmp_path / "output-styles" / self.SHIPPED).exists()
        assert own.is_file(), "a hand-written style must survive uninstall"
        assert "SC output-styles file(s)" in message

    @pytest.mark.parametrize("component_dir", ["agents", "output-styles"])
    def test_uninstall_leaves_a_user_readme_alone(self, tmp_path, component_dir):
        """README.md is never shipped, so it is never SuperClaude's to remove.

        The agents-only uninstall built its removal set from the source glob
        including README.md, so a hand-written `.claude/agents/README.md` was
        deleted on uninstall. The shared helper excludes it for both directories.
        """
        from superclaude.cli.install_components import install_all
        from superclaude.cli.install_inventory import uninstall_all

        install_all(base_path=tmp_path, force=True, scope="project")
        readme = tmp_path / component_dir / "README.md"
        readme.write_text("# our team's notes\n", encoding="utf-8")

        uninstall_all(base_path=tmp_path, scope="project")

        assert readme.is_file(), f"{component_dir}/README.md was never shipped"

    def test_uninstall_drops_the_directory_once_empty(self, tmp_path):
        from superclaude.cli.install_components import install_all
        from superclaude.cli.install_inventory import uninstall_all

        install_all(base_path=tmp_path, force=True, scope="project")

        uninstall_all(base_path=tmp_path, scope="project")

        assert not (tmp_path / "output-styles").exists()

    def test_dry_run_names_it_without_removing(self, tmp_path):
        from superclaude.cli.install_components import install_all
        from superclaude.cli.install_inventory import uninstall_all

        install_all(base_path=tmp_path, force=True, scope="project")

        _ok, message = uninstall_all(base_path=tmp_path, scope="project", dry_run=True)

        assert "Would remove: 1 SC output-styles file(s)" in message
        assert (tmp_path / "output-styles" / self.SHIPPED).is_file()

    def test_verify_drift_covers_it(self, tmp_path):
        from superclaude.cli.install_components import install_all
        from superclaude.cli.verify_drift import verify_drift

        install_all(base_path=tmp_path, force=True, scope="project")
        result = verify_drift(tmp_path, verbose=True)

        assert result["components"]["output-styles"]["files"][self.SHIPPED] == "OK"
