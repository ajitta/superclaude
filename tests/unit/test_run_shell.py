"""run_shell: a shell command whose timeout stops the whole process tree.

``subprocess.run(cmd, shell=True, timeout=...)`` kills only the shell. A command
the shell started keeps the output pipes open, so ``run`` waited for it to
finish: on Windows always (cmd.exe never execs its command), on POSIX whenever
the shell forks. The auto-improve eval and smoke timeouts and the test-runner
hook's 120 s cap bounded nothing there (2026-10-21, Windows: a 1 s timeout on a
6 s child returned after 6.1 s).
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest

from superclaude.utils import run_shell


def _command(tmp_path: Path, body: str) -> str:
    script = tmp_path / "child.py"
    script.write_text(body, encoding="utf-8")
    # `&& echo done` makes a POSIX shell fork instead of exec'ing python, so a
    # surviving grandchild is possible on every platform, as with cmd.exe.
    return f'"{sys.executable}" "{script}" && echo done'


def test_returns_the_completed_process(tmp_path: Path) -> None:
    cmd = _command(
        tmp_path,
        "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)",
    )

    proc = run_shell(cmd, timeout=30)

    assert proc.returncode == 3
    assert proc.stdout.strip() == "out"
    assert proc.stderr.strip() == "err"


def test_runs_in_cwd(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    cmd = _command(tmp_path, "import os; print(os.getcwd())")

    proc = run_shell(cmd, timeout=30, cwd=work)

    assert Path(proc.stdout.splitlines()[0]).resolve() == work.resolve()


def test_timeout_stops_the_command_tree(tmp_path: Path) -> None:
    marker = tmp_path / "survived"
    cmd = _command(
        tmp_path, f"import time; time.sleep(3); open({str(marker)!r}, 'w').close()"
    )

    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        run_shell(cmd, timeout=0.5)
    # Returned well before the child would have finished on its own ...
    assert time.monotonic() - start < 2.5
    # ... and the child was killed, not left running in the background.
    time.sleep(3)
    assert not marker.exists()
