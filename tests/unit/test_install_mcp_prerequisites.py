"""Prerequisite checks in cli/install_mcp.py.

The Node.js check must run only when an npm-based server is selected, and must
accept exactly the versions the strictest upstream `engines.node` range accepts
(chrome-devtools-mcp: ^20.19.0 || ^22.12.0 || >=23).
"""

from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from superclaude.cli import install_mcp


def _fake_run(node_version: str | None):
    """Build a `_run_command` stand-in: claude/uv/serena succeed, node reports a version."""

    def run(cmd, **kwargs):
        tool = cmd[0]
        if tool == "node":
            if node_version is None:
                raise FileNotFoundError("node")
            return subprocess.CompletedProcess(
                cmd, 0, stdout=f"{node_version}\n", stderr=""
            )
        return subprocess.CompletedProcess(cmd, 0, stdout="ok\n", stderr="")

    return run


@pytest.mark.parametrize(
    ("version", "ok"),
    [
        ("v18.20.0", False),
        ("v20.10.0", False),
        ("v20.19.0", True),
        ("v21.7.0", False),
        ("v22.11.0", False),
        ("v22.12.0", True),
        ("v23.0.0", True),
        ("v24.1.2", True),
    ],
)
def test_node_version_ok_matches_strictest_engines_range(version, ok):
    assert install_mcp._node_version_ok(version) is ok


def test_node_version_ok_returns_none_when_unparseable():
    assert install_mcp._node_version_ok("weird") is None
    assert install_mcp._node_version_ok("") is None


def test_every_registry_server_except_serena_needs_node():
    """Playwright and Tavily run via npx; chrome-devtools is a plugin that does too."""
    needs = {
        name: install_mcp._server_needs_node(name) for name in install_mcp.MCP_SERVERS
    }
    assert needs == {
        "serena": False,
        "tavily": True,
        "playwright": True,
        "chrome-devtools": True,
    }


def test_serena_only_selection_skips_node_check():
    """A Python-only install on old Node must not be blocked by the npm gate."""
    with patch.object(install_mcp, "_run_command", _fake_run("v18.20.0")):
        ok, errors = install_mcp.check_prerequisites(selected_servers=["serena"])
    assert ok is True
    assert errors == []


def test_serena_only_selection_tolerates_missing_node():
    with patch.object(install_mcp, "_run_command", _fake_run(None)):
        ok, errors = install_mcp.check_prerequisites(selected_servers=["serena"])
    assert ok is True
    assert errors == []


@pytest.mark.parametrize("selection", [["playwright"], ["tavily"], ["chrome-devtools"]])
def test_npm_server_selection_rejects_old_node(selection):
    with patch.object(install_mcp, "_run_command", _fake_run("v20.10.0")):
        ok, errors = install_mcp.check_prerequisites(selected_servers=selection)
    assert ok is False
    assert len(errors) == 1
    assert "v20.10.0" in errors[0]
    assert install_mcp.NODE_VERSION_REQUIREMENT in errors[0]


@pytest.mark.parametrize("selection", [["playwright"], ["serena", "chrome-devtools"]])
def test_npm_server_selection_accepts_supported_node(selection):
    with patch.object(install_mcp, "_run_command", _fake_run("v22.12.0")):
        ok, errors = install_mcp.check_prerequisites(selected_servers=selection)
    assert ok is True
    assert errors == []


def test_npm_server_selection_reports_missing_node():
    with patch.object(install_mcp, "_run_command", _fake_run(None)):
        ok, errors = install_mcp.check_prerequisites(selected_servers=["playwright"])
    assert ok is False
    assert errors == ["Node.js not found - required for npm-based MCP servers"]


def test_no_selection_runs_every_check():
    """selected_servers=None is the pre-selection path and keeps the old always-check behaviour."""
    with patch.object(install_mcp, "_run_command", _fake_run("v18.20.0")):
        ok, errors = install_mcp.check_prerequisites(selected_servers=None)
    assert ok is False
    assert any("v18.20.0" in e for e in errors)
