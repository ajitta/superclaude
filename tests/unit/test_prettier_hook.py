"""Tests for the PostToolUse prettier_hook.

Regression for the Windows no-op: `node_modules/.bin/prettier` is a POSIX shell
script, and CreateProcess rejects it (WinError 193, or WinError 2 once `.exe` is
appended to the extension-less relative name). The hook must resolve the
project-local shim through ``shutil.which`` — ``prettier.cmd`` on Windows, the
script elsewhere — anchored on the project root, not the hook's CWD.
"""

from __future__ import annotations

import io
import json
import os
import sys

import pytest

from superclaude.scripts import prettier_hook as hook

POSIX_SHIM = (
    "#!/bin/sh\n"
    'basedir=$(dirname "$(echo "$0" | sed -e \'s,\\\\,/,g\')")\n'
    'exec node "$basedir/../prettier/bin/prettier.cjs" "$@"\n'
)


def _layout(tmp_path, monkeypatch, *, with_cmd: bool):
    """A project with an npm-style .bin: POSIX script always, .cmd shim optional.

    CWD is moved to an unrelated directory so a CWD-relative lookup cannot pass.
    PATH holds only an empty directory so a global prettier on the dev box
    cannot leak into the assertions.
    """
    project = tmp_path / "proj"
    bin_dir = project / "node_modules" / ".bin"
    bin_dir.mkdir(parents=True)
    script = bin_dir / "prettier"
    script.write_text(POSIX_SHIM, newline="\n")
    script.chmod(0o755)
    if with_cmd:
        (bin_dir / "prettier.cmd").write_text(
            '@ECHO off\r\nnode "%~dp0\\..\\prettier\\bin\\prettier.cjs" %*\r\n'
        )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project, bin_dir


class TestFindPrettier:
    def test_windows_picks_cmd_shim_not_posix_script(self, tmp_path, monkeypatch):
        _, bin_dir = _layout(tmp_path, monkeypatch, with_cmd=True)
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv(
            "PATHEXT", ".com;.exe;.bat;.cmd"
        )  # lowercase: exact match on case-sensitive FS too

        found = hook._find_prettier()

        assert found == str(bin_dir / "prettier.cmd")
        assert os.path.isabs(found)

    def test_windows_ignores_posix_script_when_no_cmd_shim(self, tmp_path, monkeypatch):
        _layout(tmp_path, monkeypatch, with_cmd=False)
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv(
            "PATHEXT", ".com;.exe;.bat;.cmd"
        )  # lowercase: exact match on case-sensitive FS too

        assert hook._find_prettier() is None

    def test_posix_picks_script(self, tmp_path, monkeypatch):
        _, bin_dir = _layout(tmp_path, monkeypatch, with_cmd=True)
        monkeypatch.setattr(sys, "platform", "linux")

        found = hook._find_prettier()

        assert found == str(bin_dir / "prettier")
        assert os.path.isabs(found)

    def test_none_when_prettier_absent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        empty_bin = tmp_path / "empty-bin"
        empty_bin.mkdir()
        monkeypatch.setenv("PATH", str(empty_bin))

        assert hook._find_prettier() is None


def _feed(monkeypatch, file_path: str) -> None:
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": file_path}})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))


class TestMain:
    def test_silent_when_prettier_absent(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        empty_bin = tmp_path / "empty-bin"
        empty_bin.mkdir()
        monkeypatch.setenv("PATH", str(empty_bin))

        def _no_spawn(*a, **k):
            raise AssertionError(f"hook spawned a process without prettier: {a}")

        monkeypatch.setattr(hook.subprocess, "run", _no_spawn)
        _feed(monkeypatch, str(tmp_path / "app.ts"))

        hook.main()

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    def test_runs_local_shim_with_path_containing_spaces(
        self, tmp_path, monkeypatch, capsys
    ):
        """End-to-end on the real OS: a fake shim records its argv."""
        project, bin_dir = _layout(tmp_path, monkeypatch, with_cmd=False)
        log = bin_dir / "args.log"
        if sys.platform == "win32":
            (bin_dir / "prettier.cmd").write_text(
                f'@ECHO off\r\n(ECHO %*)>>"{log}"\r\n', newline=""
            )
            # CreateProcess runs .cmd via %COMSPEC%; keep System32 reachable.
            monkeypatch.setenv(
                "PATH",
                os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32"),
            )
        else:
            (bin_dir / "prettier").write_text(
                f"#!/bin/sh\nprintf '%s\\n' \"$@\" >> '{log}'\n", newline="\n"
            )
            (bin_dir / "prettier").chmod(0o755)
        target = project / "src dir" / "my component.tsx"
        _feed(monkeypatch, str(target))

        hook.main()

        out = capsys.readouterr().out.strip()
        assert json.loads(out) == {
            "systemMessage": "Formatted my component.tsx with prettier"
        }
        recorded = log.read_text()
        assert "--write" in recorded
        assert str(target) in recorded


@pytest.mark.parametrize("ext", [".md", ".py", ""])
def test_main_ignores_unsupported_extensions(tmp_path, monkeypatch, capsys, ext):
    monkeypatch.setattr(
        hook, "_find_prettier", lambda: pytest.fail("looked up prettier")
    )
    _feed(monkeypatch, str(tmp_path / f"notes{ext}"))

    hook.main()

    assert capsys.readouterr().out == ""
