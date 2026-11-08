"""The repo marketplace (.claude-plugin/marketplace.json) after the socratic plugin was removed.

The file stays so Claude Code can uninstall the plugin from machines that
still have it: a `null` entry in `renames` drops the old name, and
`forceRemoveDeletedPlugins` uninstalls a plugin the marketplace no longer
lists at the next session start (code.claude.com/docs/en/plugins/host-marketplace,
"Rename or remove a plugin"). Without both, an installed copy stays behind
and reports `Plugin "socratic" not found in marketplace`.
"""

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_MARKETPLACE = _ROOT / ".claude-plugin" / "marketplace.json"

# Append-only history: Claude Code follows the chain from the oldest name.
_RETIRED = {
    "socratic-brainstorm": "socratic",
    "socratic-elenchus": "socratic",
    "socratic": None,
}


def _load() -> dict:
    return json.loads(_MARKETPLACE.read_text(encoding="utf-8"))


def test_marketplace_keeps_its_name():
    # Installs are keyed `<plugin>@ajitta-socratic`; a new name would not
    # reach the machines that still have the plugin.
    assert _load()["name"] == "ajitta-socratic"


def test_retired_plugins_are_not_listed():
    listed = {entry["name"] for entry in _load()["plugins"]}
    assert not listed & set(_RETIRED), listed


def test_renames_keep_the_retired_chain():
    renames = _load().get("renames", {})
    assert {k: renames.get(k, "missing") for k in _RETIRED} == _RETIRED


def test_removed_plugins_are_uninstalled():
    assert _load().get("forceRemoveDeletedPlugins") is True


def test_listed_plugin_sources_exist():
    for entry in _load()["plugins"]:
        source = entry["source"]
        if isinstance(source, str) and source.startswith("./"):
            assert (_ROOT / source).is_dir(), source
