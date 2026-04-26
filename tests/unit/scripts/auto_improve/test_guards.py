"""Tests for the 4-guard suite — design §3.5 Guards."""

import time

import pytest

from superclaude.scripts.auto_improve.guards import (
    BudgetGuard,
    GuardVerdict,
    PlateauDetector,
    RegressionBlock,
    SmokeGate,
)


# --- BudgetGuard ---


def test_budget_guard_passes_before_deadline():
    g = BudgetGuard(deadline_monotonic=time.monotonic() + 60)
    v = g.check()
    assert v.pass_ is True


def test_budget_guard_fails_after_deadline():
    g = BudgetGuard(deadline_monotonic=time.monotonic() - 1)
    v = g.check()
    assert v.pass_ is False
    assert "budget" in v.reason.lower()


# --- PlateauDetector ---


def test_plateau_detector_passes_with_recent_improvement():
    d = PlateauDetector(window=5)
    for score in [1.0, 2.0, 2.0, 2.0, 3.0]:
        d.record(score)
    assert d.check().pass_ is True


def test_plateau_detector_fails_after_5_stale():
    d = PlateauDetector(window=5)
    for score in [1.0, 1.0, 1.0, 1.0, 1.0]:
        d.record(score)
    v = d.check()
    assert v.pass_ is False
    assert "plateau" in v.reason.lower()


def test_plateau_detector_resets_on_new_high():
    d = PlateauDetector(window=5)
    for score in [1.0, 1.0, 1.0, 1.0, 1.0]:
        d.record(score)
    assert d.check().pass_ is False
    d.record(2.0)
    assert d.check().pass_ is True


def test_plateau_detector_pre_window_passes():
    d = PlateauDetector(window=5)
    d.record(1.0)
    d.record(1.0)
    assert d.check().pass_ is True


# --- RegressionBlock ---


def test_regression_block_passes_when_score_ge_baseline():
    g = RegressionBlock(baseline=10.0)
    assert g.check_score(10.0).pass_ is True
    assert g.check_score(11.0).pass_ is True


def test_regression_block_fails_when_score_lt_baseline():
    g = RegressionBlock(baseline=10.0)
    v = g.check_score(9.0)
    assert v.pass_ is False
    assert "regress" in v.reason.lower()


def test_regression_block_handles_none_score():
    g = RegressionBlock(baseline=10.0)
    v = g.check_score(None)
    assert v.pass_ is False


# --- SmokeGate ---


def test_smoke_gate_uses_explicit_smoke_cmd(tmp_path):
    script = tmp_path / "ok.py"
    script.write_text("import sys; sys.exit(0)", encoding="utf-8")
    import sys

    cmd = f'"{sys.executable}" "{script}"'
    g = SmokeGate(smoke_cmd=cmd, eval_cmd="should-not-run", timeout=5)
    assert g.check().pass_ is True


def test_smoke_gate_falls_back_to_eval_cmd(tmp_path):
    import sys

    script = tmp_path / "ok.py"
    script.write_text("import sys; sys.exit(0)", encoding="utf-8")
    cmd = f'"{sys.executable}" "{script}"'
    g = SmokeGate(smoke_cmd=None, eval_cmd=cmd, timeout=5)
    assert g.check().pass_ is True


def test_smoke_gate_fails_on_nonzero_exit(tmp_path):
    import sys

    script = tmp_path / "fail.py"
    script.write_text("import sys; sys.exit(1)", encoding="utf-8")
    cmd = f'"{sys.executable}" "{script}"'
    g = SmokeGate(smoke_cmd=cmd, eval_cmd="x", timeout=5)
    v = g.check()
    assert v.pass_ is False
    assert "smoke" in v.reason.lower()


# --- Common interface ---


def test_guard_verdict_uniform_shape():
    v = GuardVerdict(pass_=True, reason="ok")
    assert v.pass_ is True
    assert v.reason == "ok"
