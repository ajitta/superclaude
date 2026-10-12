"""Registry shape and the interactive picker in cli/install_mcp.py.

The picker lists every registry server by number and pre-selects nothing:
empty input installs nothing, and only the entered numbers are installed.
"""

from __future__ import annotations

import click

from superclaude.cli import install_mcp


def test_registry_has_no_category_split():
    assert [
        name for name, info in install_mcp.MCP_SERVERS.items() if "category" in info
    ] == []


def test_registry_has_no_removed_server():
    assert "serena" not in install_mcp.MCP_SERVERS


def test_interactive_menu_lists_every_server_without_default(monkeypatch, capsys):
    prompt_kwargs = {}

    def fake_prompt(text, **kwargs):
        prompt_kwargs.update(kwargs)
        return ""

    monkeypatch.setattr(click, "prompt", fake_prompt)

    result = install_mcp.install_mcp_servers(selected_servers=None, dry_run=True)

    assert result == (False, "No servers selected")
    assert prompt_kwargs.get("default") == ""
    out = capsys.readouterr().out
    for info in install_mcp.MCP_SERVERS.values():
        assert info["name"] in out


def test_interactive_selection_installs_only_chosen_numbers(monkeypatch):
    installed = []

    monkeypatch.setattr(click, "prompt", lambda text, **kwargs: "1")
    monkeypatch.setattr(
        install_mcp, "check_prerequisites", lambda selected_servers: (True, [])
    )

    def fake_install(server_info, scope="user", dry_run=False):
        installed.append(server_info["name"])
        return True

    monkeypatch.setattr(install_mcp, "install_mcp_server", fake_install)

    ok, _ = install_mcp.install_mcp_servers(selected_servers=None, dry_run=True)

    assert ok is True
    assert installed == [next(iter(install_mcp.MCP_SERVERS.values()))["name"]]
