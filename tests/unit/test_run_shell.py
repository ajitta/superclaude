"""run_shell: a shell command whose timeout stops the whole process tree.

``subprocess.run(cmd, shell=True, timeout=...)`` kills only the shell. On
Windows the command the shell started keeps the output pipes open, so ``run``
waited for it to finish (cmd.exe never execs its command): the auto-improve eval
and smoke timeouts and the test-runner hook's cap bounded nothing there
(2026-10-21: a 1 s timeout on a 6 s child returned after 6.1 s). On POSIX
``run`` returned, but the forked command kept running in the background.

run_shell gives the command its own session on POSIX, so a signal to the
caller's process group no longer reaches it; the interrupt tests check that
the caller kills the tree then instead (independent verification 06a, #1).
"""

import os
import signal
import subprocess
import sys
import textwrap
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


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX signals")
@pytest.mark.parametrize("signame", ["SIGINT", "SIGTERM", "SIGHUP"])
def test_a_signal_to_the_callers_group_stops_the_command_tree(
    tmp_path: Path, signame: str
) -> None:
    # The caller runs in its own group, as a terminal job or a supervised
    # process does; the signal goes to that group (Ctrl-C, `kill -TERM -pgid`).
    started = tmp_path / "started"
    marker = tmp_path / "survived"
    cmd = _command(
        tmp_path,
        f"import time; open({str(started)!r}, 'w').close(); time.sleep(2); "
        f"open({str(marker)!r}, 'w').close()",
    )
    driver = tmp_path / "driver.py"
    driver.write_text(
        textwrap.dedent(
            f"""
            from superclaude.utils import run_shell
            run_shell({cmd!r}, timeout=30)
            """
        ),
        encoding="utf-8",
    )
    caller = subprocess.Popen([sys.executable, str(driver)], start_new_session=True)
    try:
        deadline = time.monotonic() + 15
        while not started.exists():
            assert time.monotonic() < deadline, "the command never started"
            assert caller.poll() is None, "the caller ended before the command ran"
            time.sleep(0.05)
        os.killpg(caller.pid, getattr(signal, signame))
        caller.wait(timeout=10)
    finally:
        if caller.poll() is None:
            caller.kill()
    time.sleep(2.5)
    assert not marker.exists(), f"{signame} to the caller left the command running"
