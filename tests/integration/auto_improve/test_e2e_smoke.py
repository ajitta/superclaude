"""End-to-end smoke test for the auto-improve worker.

Spins up a temp git repo, runs `python -m superclaude.scripts.auto_improve`
in --dry-run mode, asserts results.tsv contains a baseline row.

Mutator is NOT invoked (dry-run skips Phase 1), so this test does not
require the `claude` CLI to be installed or authenticated.
"""

from __future__ import annotations

import subprocess
import sys


def test_e2e_dry_run_baseline(git_repo, tmp_path):
    eval_script = tmp_path / "eval.py"
    eval_script.write_text(
        'import sys, json; sys.stdout.write(json.dumps({"passed": 1}))',
        encoding="utf-8",
    )
    eval_cmd = f'"{sys.executable}" "{eval_script}"'

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "superclaude.scripts.auto_improve",
            "--project",
            str(git_repo),
            "--eval-cmd",
            eval_cmd,
            "--metric",
            "passed",
            "--budget",
            "1m",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, f"stderr: {proc.stderr}"

    worktrees = sorted((git_repo / ".worktrees").iterdir())
    assert len(worktrees) == 1
    tsv = (worktrees[0] / "results.tsv").read_text(encoding="utf-8").splitlines()
    assert tsv[0].startswith("# cycle_id")
    assert len(tsv) == 2  # header + baseline row
    fields = tsv[1].split("\t")
    assert fields[0] == "0"  # cycle_id
    assert fields[4] == "baseline"  # status
    assert float(fields[3]) == 1.0  # metric_value
    # The summary printed afterwards should mention baseline.
    assert "baseline" in proc.stdout.lower()


def test_status_mode_after_no_run(git_repo):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "superclaude.scripts.auto_improve",
            "--project",
            str(git_repo),
            "--status",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "no prior runs" in proc.stdout.lower() or "no history" in proc.stdout.lower()
