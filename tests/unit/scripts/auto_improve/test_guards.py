"""Tests for the 4-guard suite — design §3.5 Guards."""

import sys
import time
from unittest.mock import MagicMock, patch

from superclaude.scripts.auto_improve.guards import (
    BudgetGuard,
    PlateauDetector,
    RegressionBlock,
    SmokeGate,
)

# --- BudgetGuard ---


def test_budget_guard_passes_before_deadline():
    g = BudgetGuard(deadline_monotonic=time.monotonic() + 60)
    assert g.check() is True


def test_budget_guard_fails_after_deadline():
    g = BudgetGuard(deadline_monotonic=time.monotonic() - 1)
    assert g.check() is False


# --- PlateauDetector ---


def test_plateau_detector_passes_with_recent_improvement():
    d = PlateauDetector(window=5)
    for score in [1.0, 2.0, 2.0, 2.0, 3.0]:
        d.record(score)
    assert d.check() is True


def test_plateau_detector_fails_after_5_stale():
    d = PlateauDetector(window=5)
    for score in [1.0, 1.0, 1.0, 1.0, 1.0]:
        d.record(score)
    assert d.check() is False


def test_plateau_detector_resets_on_new_high():
    d = PlateauDetector(window=5)
    for score in [1.0, 1.0, 1.0, 1.0, 1.0]:
        d.record(score)
    assert d.check() is False
    d.record(2.0)
    assert d.check() is True


def test_plateau_detector_pre_window_passes():
    d = PlateauDetector(window=5)
    d.record(1.0)
    d.record(1.0)
    assert d.check() is True


# --- RegressionBlock ---


def test_regression_block_passes_when_score_ge_baseline():
    g = RegressionBlock(baseline=10.0)
    assert g.check_score(10.0) is True
    assert g.check_score(11.0) is True


def test_regression_block_fails_when_score_lt_baseline():
    g = RegressionBlock(baseline=10.0)
    assert g.check_score(9.0) is False


def test_regression_block_handles_none_score():
    g = RegressionBlock(baseline=10.0)
    assert g.check_score(None) is False


# --- SmokeGate ---


def test_smoke_gate_uses_explicit_smoke_cmd(tmp_path):
    script = tmp_path / "ok.py"
    script.write_text("import sys; sys.exit(0)", encoding="utf-8")
    cmd = f'"{sys.executable}" "{script}"'
    g = SmokeGate(smoke_cmd=cmd, eval_cmd="should-not-run", timeout=5)
    assert g.check() is True


def test_smoke_gate_falls_back_to_eval_cmd(tmp_path):
    script = tmp_path / "ok.py"
    script.write_text("import sys; sys.exit(0)", encoding="utf-8")
    cmd = f'"{sys.executable}" "{script}"'
    g = SmokeGate(smoke_cmd=None, eval_cmd=cmd, timeout=5)
    assert g.check() is True


def test_smoke_gate_fallback_uses_configured_timeout():
    """Without --smoke-cmd the gate runs eval_cmd; it must honour the
    configured (cycle) timeout. A fixed 30 s cap made every cycle of a 45 s
    eval time out -> smoke_fail, even though the baseline had passed under
    the 600 s cycle timeout.
    """
    g = SmokeGate(smoke_cmd=None, eval_cmd="eval", timeout=45)
    with patch(
        "superclaude.scripts.auto_improve.guards.subprocess.run",
        return_value=MagicMock(returncode=0),
    ) as run:
        assert g.check() is True
    assert run.call_args.kwargs["timeout"] == 45


def test_smoke_gate_runs_in_specified_cwd(tmp_path):
    """SmokeGate must run in the worktree, not the worker's launch dir.
    Regression guard: a misconfigured cwd previously produced thousands
    of fast smoke_fail cycles per minute (eval.py not found in worker dir).
    """
    (tmp_path / "marker.py").write_text("import sys; sys.exit(0)", encoding="utf-8")
    cmd = f'"{sys.executable}" marker.py'
    g = SmokeGate(smoke_cmd=None, eval_cmd=cmd, timeout=5, cwd=str(tmp_path))
    assert g.check() is True


def test_smoke_gate_fails_on_nonzero_exit(tmp_path):
    script = tmp_path / "fail.py"
    script.write_text("import sys; sys.exit(1)", encoding="utf-8")
    cmd = f'"{sys.executable}" "{script}"'
    g = SmokeGate(smoke_cmd=cmd, eval_cmd="x", timeout=5)
    assert g.check() is False
