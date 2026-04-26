"""
Unit tests for the Serena MCP migration logic in install_mcp.py.

Covers PR-A scope only (Item #3 from the Serena follow-ups queue):
  - `_is_serena_stale_entry()` detection across stale/fresh/edge shapes
  - `_handle_stale_serena()` interactive vs non-TTY vs dry-run paths
  - `install_mcp_server()` early-return integration for the Serena case
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from superclaude.cli import install_mcp
from superclaude.cli.install_mcp import (
    MCP_SERVERS,
    _handle_stale_serena,
    _is_serena_stale_entry,
    install_mcp_server,
)

# -----------------------
# _is_serena_stale_entry
# -----------------------


class TestIsSerenaStaleEntry:
    """Detection unit: structured-entry inspection (no CLI calls)."""

    def test_fresh_entry_is_not_stale(self):
        entry = {
            "command": "serena",
            "args": ["start-mcp-server", "--context=claude-code", "--project-from-cwd"],
        }
        assert _is_serena_stale_entry(entry) is False

    def test_missing_project_from_cwd_is_stale(self):
        entry = {
            "command": "serena",
            "args": ["start-mcp-server", "--context=claude-code"],
        }
        assert _is_serena_stale_entry(entry) is True

    def test_enable_web_dashboard_is_stale(self):
        entry = {
            "command": "serena",
            "args": [
                "start-mcp-server",
                "--context=claude-code",
                "--project-from-cwd",
                "--enable-web-dashboard",
                "false",
            ],
        }
        assert _is_serena_stale_entry(entry) is True

    def test_enable_gui_log_window_is_stale(self):
        entry = {
            "command": "serena",
            "args": [
                "start-mcp-server",
                "--context=claude-code",
                "--enable-gui-log-window",
                "false",
            ],
        }
        assert _is_serena_stale_entry(entry) is True

    def test_string_form_command_with_args_is_parsed(self):
        # Some entries may store the full invocation in `command` rather than `args`
        entry = {
            "command": "serena start-mcp-server --context=claude-code --project-from-cwd",
            "args": [],
        }
        assert _is_serena_stale_entry(entry) is False

    def test_string_form_command_missing_flag_is_stale(self):
        entry = {
            "command": "serena start-mcp-server --context=claude-code",
            "args": [],
        }
        assert _is_serena_stale_entry(entry) is True

    def test_empty_entry_is_not_stale(self):
        # Avoid false-positive migration on a malformed/empty entry
        assert _is_serena_stale_entry({}) is False
        assert _is_serena_stale_entry({"command": None, "args": None}) is False

    def test_non_dict_entry_is_not_stale(self):
        assert _is_serena_stale_entry(None) is False  # type: ignore[arg-type]
        assert _is_serena_stale_entry("serena ...") is False  # type: ignore[arg-type]


# -----------------------
# _handle_stale_serena
# -----------------------


class TestHandleStaleSerena:
    """Decision-table coverage for the migration prompt logic."""

    def test_dry_run_short_circuits(self):
        action, should_continue = _handle_stale_serena(scope="user", dry_run=True)
        assert action == "dry-run"
        assert should_continue is False

    def test_non_tty_emits_manual_hint_and_skips(self, capsys):
        with patch.object(install_mcp.sys.stdin, "isatty", return_value=False):
            action, should_continue = _handle_stale_serena(scope="user", dry_run=False)
        assert action == "skip"
        assert should_continue is False
        captured = capsys.readouterr()
        assert "non-interactive" in captured.err.lower()
        assert "claude mcp remove --scope user serena" in captured.err

    def test_interactive_decline_skips(self):
        with (
            patch.object(install_mcp.sys.stdin, "isatty", return_value=True),
            patch.object(install_mcp.click, "confirm", return_value=False),
        ):
            action, should_continue = _handle_stale_serena(scope="user", dry_run=False)
        assert action == "skip"
        assert should_continue is False

    def test_interactive_confirm_runs_remove_and_continues(self):
        with (
            patch.object(install_mcp.sys.stdin, "isatty", return_value=True),
            patch.object(install_mcp.click, "confirm", return_value=True),
            patch.object(
                install_mcp, "_migrate_stale_serena", return_value=(True, "ok")
            ),
        ):
            action, should_continue = _handle_stale_serena(scope="user", dry_run=False)
        assert action == "migrate"
        assert should_continue is True

    def test_interactive_confirm_remove_failure_skips(self):
        with (
            patch.object(install_mcp.sys.stdin, "isatty", return_value=True),
            patch.object(install_mcp.click, "confirm", return_value=True),
            patch.object(
                install_mcp,
                "_migrate_stale_serena",
                return_value=(False, "boom"),
            ),
        ):
            action, should_continue = _handle_stale_serena(scope="user", dry_run=False)
        assert action == "skip"
        assert should_continue is False


# -----------------------
# install_mcp_server() integration
# -----------------------


class TestInstallMcpServerSerenaPath:
    """Verifies the staleness branch is wired into install_mcp_server() correctly."""

    @pytest.fixture
    def serena_info(self):
        return MCP_SERVERS["serena"]

    def _stub_run_command_success(self, *_, **__):
        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        return _R()

    def test_fresh_install_proceeds_to_subprocess(self, serena_info):
        # No existing entry → check_mcp_server_installed returns False → install runs
        with (
            patch.object(install_mcp, "check_mcp_server_installed", return_value=False),
            patch.object(
                install_mcp, "_run_command", side_effect=self._stub_run_command_success
            ),
        ):
            result = install_mcp_server(serena_info, scope="user", dry_run=False)
        assert result is True

    def test_already_installed_fresh_entry_returns_early(self, serena_info):
        # check_mcp_server_installed → True, entry is fresh → early return, no subprocess
        fresh_entry = {
            "command": "serena",
            "args": ["start-mcp-server", "--context=claude-code", "--project-from-cwd"],
        }
        with (
            patch.object(install_mcp, "check_mcp_server_installed", return_value=True),
            patch.object(
                install_mcp,
                "_mcp_servers_in_scope",
                return_value={"serena": fresh_entry},
            ),
            patch.object(install_mcp, "_run_command") as run_cmd,
        ):
            result = install_mcp_server(serena_info, scope="user", dry_run=False)
        assert result is True
        run_cmd.assert_not_called()

    def test_stale_entry_dry_run_skips_install_and_remove(self, serena_info):
        stale_entry = {
            "command": "serena",
            "args": [
                "start-mcp-server",
                "--context=claude-code",
            ],  # missing --project-from-cwd
        }
        with (
            patch.object(install_mcp, "check_mcp_server_installed", return_value=True),
            patch.object(
                install_mcp,
                "_mcp_servers_in_scope",
                return_value={"serena": stale_entry},
            ),
            patch.object(install_mcp, "_run_command") as run_cmd,
        ):
            result = install_mcp_server(serena_info, scope="user", dry_run=True)
        assert result is True
        run_cmd.assert_not_called()

    def test_stale_entry_non_tty_does_not_remove(self, serena_info):
        stale_entry = {
            "command": "serena",
            "args": ["start-mcp-server", "--context=claude-code"],
        }
        with (
            patch.object(install_mcp, "check_mcp_server_installed", return_value=True),
            patch.object(
                install_mcp,
                "_mcp_servers_in_scope",
                return_value={"serena": stale_entry},
            ),
            patch.object(install_mcp.sys.stdin, "isatty", return_value=False),
            patch.object(install_mcp, "_run_command") as run_cmd,
        ):
            result = install_mcp_server(serena_info, scope="user", dry_run=False)
        assert result is True  # no-op exit, leaves existing install alone
        run_cmd.assert_not_called()

    def test_stale_entry_interactive_yes_removes_and_reinstalls(self, serena_info):
        stale_entry = {
            "command": "serena",
            "args": ["start-mcp-server", "--context=claude-code"],
        }

        class _OK:
            returncode = 0
            stdout = ""
            stderr = ""

        with (
            patch.object(install_mcp, "check_mcp_server_installed", return_value=True),
            patch.object(
                install_mcp,
                "_mcp_servers_in_scope",
                return_value={"serena": stale_entry},
            ),
            patch.object(install_mcp.sys.stdin, "isatty", return_value=True),
            patch.object(install_mcp.click, "confirm", return_value=True),
            patch.object(install_mcp, "_run_command", return_value=_OK()) as run_cmd,
        ):
            result = install_mcp_server(serena_info, scope="user", dry_run=False)

        assert result is True
        # Should have run BOTH `claude mcp remove ... serena` AND `claude mcp add ... serena ...`
        commands = [call.args[0] for call in run_cmd.call_args_list]
        assert any("remove" in cmd and "serena" in cmd for cmd in commands), (
            f"Expected a `claude mcp remove ... serena` call; got {commands}"
        )
        assert any("add" in cmd and "serena" in cmd for cmd in commands), (
            f"Expected a `claude mcp add ... serena` call; got {commands}"
        )

    def test_stale_entry_interactive_no_keeps_existing(self, serena_info):
        stale_entry = {
            "command": "serena",
            "args": ["start-mcp-server", "--context=claude-code"],
        }
        with (
            patch.object(install_mcp, "check_mcp_server_installed", return_value=True),
            patch.object(
                install_mcp,
                "_mcp_servers_in_scope",
                return_value={"serena": stale_entry},
            ),
            patch.object(install_mcp.sys.stdin, "isatty", return_value=True),
            patch.object(install_mcp.click, "confirm", return_value=False),
            patch.object(install_mcp, "_run_command") as run_cmd,
        ):
            result = install_mcp_server(serena_info, scope="user", dry_run=False)
        assert result is True
        run_cmd.assert_not_called()
