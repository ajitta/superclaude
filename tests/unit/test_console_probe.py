"""install_paths.probe_console_script — which `superclaude` Claude Code's hook
shell will find, and whether that one can run this release's hooks.

A bare `shutil.which("superclaude")` was the installer's and doctor's only guard
for the PATH dependence the console entry introduced, and under `uv run` (every
`make sync-*` target) it always found the project venv's shim — a directory the
user's shell, the one Claude Code inherits PATH from, sees only while that venv
is active. The probe leaves the running interpreter's own bin out of the search
and asks the script it finds what it is.
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace

import pytest

from superclaude.cli import install_paths


@pytest.fixture(autouse=True)
def _fresh_probe():
    install_paths.probe_console_script.cache_clear()
    yield
    install_paths.probe_console_script.cache_clear()


def _fake_run(has_hook: bool, version: str | None):
    def run(argv):
        if argv[1:] == ["hook", "--help"]:
            return SimpleNamespace(returncode=0 if has_hook else 2, stdout="")
        if argv[1:] == ["--version"]:
            return SimpleNamespace(
                returncode=0,
                stdout=f"SuperClaude, version {version}\n" if version else "",
            )
        raise AssertionError(argv)

    return run


class TestOwnBinIsLeftOutOfTheSearch:
    """Only a virtual environment's bin is transient. A base interpreter's
    scripts directory (`/usr/bin` after a system pip install, `C:\\PythonXY\\Scripts`,
    a conda base) is the user's permanent PATH entry and stays in the search —
    excluding it made a working layout warn 127 and fail doctor."""

    def test_a_virtualenvs_bin_is_excluded_and_named(self, tmp_path, monkeypatch):
        prefix = tmp_path / "venv"
        own_bin = prefix / ("Scripts" if os.name == "nt" else "bin")
        own_bin.mkdir(parents=True)
        elsewhere = tmp_path / "usr-bin"
        elsewhere.mkdir()
        monkeypatch.setattr(sys, "prefix", str(prefix))
        monkeypatch.setattr(sys, "base_prefix", str(tmp_path / "base"))
        monkeypatch.setenv("PATH", os.pathsep.join([str(own_bin), str(elsewhere)]))
        searched = {}

        def which(name, path=None):
            searched["path"] = path
            return None

        monkeypatch.setattr(install_paths.shutil, "which", which)

        probe = install_paths.probe_console_script()

        assert probe["path"] is None
        assert probe["excluded"] == str(own_bin)
        assert str(own_bin) not in searched["path"].split(os.pathsep)
        assert str(elsewhere) in searched["path"].split(os.pathsep)

    def test_nothing_excluded_when_own_bin_is_not_on_path(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "prefix", str(tmp_path / "venv"))
        monkeypatch.setattr(sys, "base_prefix", str(tmp_path / "base"))
        monkeypatch.setenv("PATH", str(tmp_path / "usr-bin"))
        monkeypatch.setattr(install_paths.shutil, "which", lambda name, path=None: None)

        assert install_paths.probe_console_script()["excluded"] is None

    def test_a_base_interpreters_bin_stays_in_the_search(self, tmp_path, monkeypatch):
        prefix = tmp_path / "usr"
        own_bin = prefix / ("Scripts" if os.name == "nt" else "bin")
        own_bin.mkdir(parents=True)
        monkeypatch.setattr(sys, "prefix", str(prefix))
        monkeypatch.setattr(sys, "base_prefix", str(prefix))
        monkeypatch.setenv("PATH", str(own_bin))
        searched = {}

        def which(name, path=None):
            searched["path"] = path
            return str(own_bin / "superclaude")

        monkeypatch.setattr(install_paths.shutil, "which", which)
        monkeypatch.setattr(install_paths, "_run", _fake_run(True, "4.9.0"))

        probe = install_paths.probe_console_script()

        assert probe["excluded"] is None
        assert str(own_bin) in searched["path"].split(os.pathsep)
        assert probe["path"] == str(own_bin / "superclaude")


class TestTheFoundScriptIsInterrogated:
    def test_hook_subcommand_and_version_are_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "prefix", str(tmp_path / "venv"))
        monkeypatch.setenv("PATH", str(tmp_path / "usr-bin"))
        monkeypatch.setattr(
            install_paths.shutil,
            "which",
            lambda name, path=None: "/usr/bin/superclaude",
        )
        monkeypatch.setattr(install_paths, "_run", _fake_run(True, "4.9.0"))

        probe = install_paths.probe_console_script()

        assert probe == {
            "path": "/usr/bin/superclaude",
            "excluded": None,
            "has_hook": True,
            "version": "4.9.0",
        }

    def test_a_script_without_hook_is_reported_as_such(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "prefix", str(tmp_path / "venv"))
        monkeypatch.setenv("PATH", str(tmp_path / "usr-bin"))
        monkeypatch.setattr(
            install_paths.shutil,
            "which",
            lambda name, path=None: "/usr/bin/superclaude",
        )
        monkeypatch.setattr(install_paths, "_run", _fake_run(False, "4.8.0"))

        probe = install_paths.probe_console_script()

        assert probe["has_hook"] is False
        assert probe["version"] == "4.8.0"

    def test_a_failing_subprocess_does_not_raise(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "prefix", str(tmp_path / "venv"))
        monkeypatch.setenv("PATH", str(tmp_path / "usr-bin"))
        monkeypatch.setattr(
            install_paths.shutil,
            "which",
            lambda name, path=None: "/usr/bin/superclaude",
        )
        monkeypatch.setattr(install_paths, "_run", lambda argv: None)

        probe = install_paths.probe_console_script()

        assert probe["has_hook"] is False
        assert probe["version"] is None


def test_the_real_probe_finds_this_releases_console_script_answering_hook_help():
    """Not mocked: when this machine's PATH resolves THIS release's console
    script, it must answer `hook --help`. A different release on PATH (a dev who
    has not run `make deploy`, an unrelated install) is that machine's state,
    not a regression in this tree, so it skips rather than fails."""
    from superclaude import __version__

    probe = install_paths.probe_console_script()

    if probe["path"] is None:
        pytest.skip("no superclaude console script on PATH")
    if probe["version"] != __version__:
        pytest.skip(
            f"PATH resolves superclaude {probe['version']} at {probe['path']}, not "
            f"this tree's {__version__} (run `make deploy`)"
        )
    assert probe["has_hook"] is True, probe
