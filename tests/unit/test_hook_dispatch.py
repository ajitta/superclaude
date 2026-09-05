"""`superclaude hook <name>` — the console entry every hooks.json command runs.

Two things break silently here and these tests pin both. The registry has to
cover exactly what hooks.json ships: a name registered in hooks.json but not in
``HOOKS`` exits 2 — the blocking code on PreToolUse and Stop — on the first
tool call of every session. And the fast path has to stay fast: ``entry.py``
dispatches ``hook`` before importing click because the click import alone
(~40ms) costs more than a whole hook run (~20ms, measured 2026-09-05) and hooks
fire three times per Bash tool call; one stray import of ``superclaude.cli.main``
from the dispatch path doubles every hook's cost without failing anything.

Filed at tests/unit/ top level on purpose: pyproject addopts carries
``--ignore=tests/unit/scripts``, so a guard under tests/unit/scripts/ never runs.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG = REPO_ROOT / "src" / "superclaude"


def _shipped_commands() -> list[str]:
    config = json.loads((PKG / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    return [
        hook["command"]
        for array in config["hooks"].values()
        for entry in array
        for hook in entry["hooks"]
    ]


def _shipped_names() -> set[str]:
    names = set()
    for command in _shipped_commands():
        tokens = command.split()
        assert tokens[:2] == ["superclaude", "hook"], command
        names.add(tokens[2])
    return names


class TestRegistry:
    """hooks.json, the registry and scripts/ name the same ten hooks."""

    def test_every_shipped_command_dispatches(self):
        from superclaude.cli.hook_dispatch import HOOKS

        assert _shipped_names() == set(HOOKS)

    def test_every_registered_hook_is_a_shipped_script_with_main(self):
        from superclaude.cli.hook_dispatch import HOOKS

        for name, (module_name, _forwards_argv) in HOOKS.items():
            assert (PKG / "scripts" / f"{name}.py").is_file(), name
            assert module_name == f"superclaude.scripts.{name}", name
            assert callable(importlib.import_module(module_name).main), name

    def test_only_insight_writer_takes_arguments(self):
        """The one script with subcommands is the one hooks.json passes them to."""
        from superclaude.cli.hook_dispatch import HOOKS

        with_args = {
            command.split()[2]
            for command in _shipped_commands()
            if len(command.split()) > 3
        }
        assert with_args == {name for name, (_m, fwd) in HOOKS.items() if fwd}


@pytest.fixture
def fake_hook(monkeypatch):
    """Register a throwaway module as hook `fake`; returns a setter for main()."""
    from superclaude.cli import hook_dispatch

    module = types.ModuleType("superclaude_test_fake_hook")
    monkeypatch.setitem(sys.modules, module.__name__, module)

    def register(main, forwards_argv=False):
        module.main = main
        monkeypatch.setitem(
            hook_dispatch.HOOKS, "fake", (module.__name__, forwards_argv)
        )
        return module

    return register


class TestRunHook:
    def test_no_name_is_a_usage_error(self, capsys):
        from superclaude.cli.hook_dispatch import run_hook

        assert run_hook([]) == 2
        assert "usage: superclaude hook" in capsys.readouterr().err

    def test_help_lists_every_hook(self, capsys):
        from superclaude.cli.hook_dispatch import HOOKS, run_hook

        assert run_hook(["--help"]) == 0
        out = capsys.readouterr().out
        for name in HOOKS:
            assert name in out

    def test_unknown_name_exits_2_and_names_it(self, capsys):
        from superclaude.cli.hook_dispatch import run_hook

        assert run_hook(["no_such_hook"]) == 2
        assert "no_such_hook" in capsys.readouterr().err

    def test_arguments_to_a_stdin_only_hook_are_refused(self, fake_hook, capsys):
        """A stray token on a no-argument hook is a hooks.json typo, not noise."""
        calls = []
        fake_hook(lambda: calls.append("ran"))
        from superclaude.cli.hook_dispatch import run_hook

        assert run_hook(["fake", "harvest-from-hook"]) == 2
        assert calls == [], "the script ran despite the refused argument"
        assert "takes no arguments" in capsys.readouterr().err

    def test_none_return_is_exit_0(self, fake_hook):
        fake_hook(lambda: None)
        from superclaude.cli.hook_dispatch import run_hook

        assert run_hook(["fake"]) == 0

    def test_int_return_is_the_exit_code(self, fake_hook):
        fake_hook(lambda: 3)
        from superclaude.cli.hook_dispatch import run_hook

        assert run_hook(["fake"]) == 3

    def test_a_guards_system_exit_propagates(self, fake_hook):
        """The guards block with sys.exit(2) from inside main(); that must
        reach the process exit code exactly as under `python guard.py`."""

        def blocking():
            sys.exit(2)

        fake_hook(blocking)
        from superclaude.cli.hook_dispatch import run_hook

        with pytest.raises(SystemExit) as raised:
            run_hook(["fake"])
        assert raised.value.code == 2

    def test_argv_and_prog_are_forwarded(self, fake_hook):
        seen = {}

        def main(argv, prog):
            seen["argv"], seen["prog"] = argv, prog
            return 0

        fake_hook(main, forwards_argv=True)
        from superclaude.cli.hook_dispatch import run_hook

        assert run_hook(["fake", "sub", "--flag", "x"]) == 0
        assert seen == {"argv": ["sub", "--flag", "x"], "prog": "superclaude hook fake"}

    def test_insight_writer_help_names_the_console_entry(self, capsys):
        from superclaude.cli.hook_dispatch import run_hook

        with pytest.raises(SystemExit) as raised:
            run_hook(["insight_writer", "--help"])
        assert raised.value.code == 0
        assert "usage: superclaude hook insight_writer" in capsys.readouterr().out


def _run_entry(code: str, tmp_path: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    env.pop("CLAUDE_CODE_SESSION_ID", None)
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        stdin=subprocess.DEVNULL,
        timeout=60,
    )


_NO_CLICK = (
    "import sys\n"
    "for name in ('click', 'yaml', 'superclaude.cli.main'):\n"
    "    assert name not in sys.modules, name + ' imported on the hook fast path'\n"
)


class TestEntryFastPath:
    """The console script reaches a hook without paying for the click app."""

    def test_the_console_script_targets_entry(self):
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'superclaude = "superclaude.cli.entry:main"' in pyproject

    def test_importing_the_dispatch_path_does_not_import_click(self, tmp_path):
        result = _run_entry(
            "import superclaude.cli.entry, superclaude.cli.hook_dispatch\n" + _NO_CLICK,
            tmp_path,
        )
        assert result.returncode == 0, result.stderr

    def test_a_shipped_hook_runs_through_entry_without_click(self, tmp_path):
        """memory_staleness: read-only, and for a fresh project root it has
        nothing to report — a clean exit 0 with click never imported."""
        result = _run_entry(
            "import sys\n"
            "sys.argv = ['superclaude', 'hook', 'memory_staleness']\n"
            "from superclaude.cli.entry import main\n"
            "rc = main()\n" + _NO_CLICK + "raise SystemExit(rc)\n",
            tmp_path,
        )
        assert result.returncode == 0, result.stderr

    def test_an_unknown_hook_exits_2_through_entry(self, tmp_path):
        result = _run_entry(
            "import sys\n"
            "sys.argv = ['superclaude', 'hook', 'no_such_hook']\n"
            "from superclaude.cli.entry import main\n"
            "raise SystemExit(main())\n",
            tmp_path,
        )
        assert result.returncode == 2
        assert "no_such_hook" in result.stderr

    def test_everything_else_reaches_the_click_app(self, tmp_path):
        result = _run_entry(
            "import sys\n"
            "sys.argv = ['superclaude', 'version']\n"
            "from superclaude.cli.entry import main\n"
            "main()\n",
            tmp_path,
        )
        assert result.returncode == 0, result.stderr
        assert "SuperClaude version" in result.stdout


class TestClickRegistration:
    """`hook` is also a click command: the --help listing, and the path a
    console script generated by a previous release still takes."""

    def test_hook_subcommand_registered(self):
        from superclaude.cli.main import main as cli

        assert "hook" in cli.commands

    def test_help_via_click_lists_the_hooks(self):
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(cli, ["hook", "--help"])

        assert result.exit_code == 0, result.output
        assert "context_loader" in result.output

    def test_unknown_hook_via_click_exits_2(self):
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(cli, ["hook", "no_such_hook"])

        assert result.exit_code == 2
