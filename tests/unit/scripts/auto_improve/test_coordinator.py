"""Tests for Coordinator state machine — design §3.2."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.scripts.auto_improve.coordinator import (
    Coordinator,
    CoordinatorConfig,
    status_mode,
)
from superclaude.scripts.auto_improve.eval_runner import EvalResult
from superclaude.scripts.auto_improve.mutator import MutationResult
from superclaude.scripts.auto_improve.results_tsv import ResultsTsv


def _git(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)


@pytest.fixture
def repo(tmp_path):
    _git(["git", "init", "-b", "main"], cwd=tmp_path)
    _git(["git", "config", "user.email", "t@e.com"], cwd=tmp_path)
    _git(["git", "config", "user.name", "T"], cwd=tmp_path)
    (tmp_path / "README.md").write_text("seed", encoding="utf-8")
    _git(["git", "add", "."], cwd=tmp_path)
    _git(["git", "commit", "-m", "seed"], cwd=tmp_path)
    return tmp_path


def _make_config(repo: Path, **overrides) -> CoordinatorConfig:
    base = dict(
        repo_root=repo,
        eval_cmd="echo {}",
        metric_path="x",
        budget_seconds=60,
        cycle_timeout_seconds=10,
        smoke_cmd=None,
        mutator_model="sonnet",
        plateau_window=5,
    )
    base.update(overrides)
    return CoordinatorConfig(**base)


def _eval_result(value, exit_code=0, timed_out=False):
    return EvalResult(
        metric_value=value,
        exit_code=exit_code,
        wall_seconds=1,
        stderr="",
        timed_out=timed_out,
    )


def test_phase0_dry_run_baseline_records_cycle_id_zero(repo):
    cfg = _make_config(repo)
    with (
        patch(
            "superclaude.scripts.auto_improve.coordinator.run_eval",
            return_value=_eval_result(10.0),
        ),
        patch.object(Coordinator, "_run_smoke", return_value=True),
        patch.object(Coordinator, "_run_mutator_cycle") as mut,
    ):
        # 1 mutation cycle then budget exhausts
        mut.side_effect = [None]
        c = Coordinator(cfg)
        result_path = c.run_baseline_only()
    rows = ResultsTsv(result_path).read_all()
    assert rows[0].cycle_id == 0
    assert rows[0].status == "baseline"


def test_phase0_failure_exits_no_loop_entry(repo):
    cfg = _make_config(repo)
    with patch(
        "superclaude.scripts.auto_improve.coordinator.run_eval",
        return_value=_eval_result(None, exit_code=1),
    ):
        c = Coordinator(cfg)
        with pytest.raises(SystemExit) as exc:
            c.run_baseline_only()
        assert exc.value.code != 0


def test_loop_aborts_on_budget_exceeded(repo):
    cfg = _make_config(repo, budget_seconds=0)  # immediate exhaustion
    with patch(
        "superclaude.scripts.auto_improve.coordinator.run_eval",
        return_value=_eval_result(1.0),
    ):
        c = Coordinator(cfg)
        cycles = c.run()
    # Only baseline cycle (#0) should appear; loop aborts before mutation.
    assert cycles == 1


def test_loop_aborts_on_5_stale_plateau(repo):
    cfg = _make_config(repo, plateau_window=3)
    eval_results = [
        _eval_result(10.0),  # baseline
        _eval_result(10.0),  # stale 1
        _eval_result(10.0),  # stale 2
        _eval_result(10.0),  # stale 3 -> plateau triggers
    ]
    with (
        patch(
            "superclaude.scripts.auto_improve.coordinator.run_eval",
            side_effect=eval_results,
        ),
        patch.object(Coordinator, "_run_smoke", return_value=True),
        patch.object(Coordinator, "_invoke_mutator") as mut,
    ):
        mut.return_value = MutationResult(rationale="step", tokens_used=10)
        c = Coordinator(cfg)
        cycles = c.run()
    assert cycles >= 2  # baseline + at least 1 mutation
    assert cycles <= 5  # plateau should fire within window+small slack


def test_regressed_score_does_not_commit(repo):
    cfg = _make_config(repo, budget_seconds=120)
    eval_results = [
        _eval_result(10.0),  # baseline
        _eval_result(5.0),  # regression
        _eval_result(5.0),  # regression
        _eval_result(5.0),  # regression
        _eval_result(5.0),  # regression
        _eval_result(5.0),  # regression -> plateau or budget
    ]
    with (
        patch(
            "superclaude.scripts.auto_improve.coordinator.run_eval",
            side_effect=eval_results,
        ),
        patch.object(Coordinator, "_run_smoke", return_value=True),
        patch.object(Coordinator, "_invoke_mutator") as mut,
        patch.object(Coordinator, "_git_commit") as commit,
    ):
        mut.return_value = MutationResult(rationale="r", tokens_used=10)
        c = Coordinator(cfg)
        c.run()
    # All mutation cycles regressed -> no commits expected.
    assert commit.call_count == 0


def test_smoke_fail_skips_cycle_no_mutation_attempted(repo):
    cfg = _make_config(repo)
    eval_results = [_eval_result(10.0)]  # baseline only

    with (
        patch(
            "superclaude.scripts.auto_improve.coordinator.run_eval",
            side_effect=eval_results,
        ),
        patch.object(Coordinator, "_run_smoke", return_value=False),
        patch.object(Coordinator, "_invoke_mutator") as mut,
    ):
        c = Coordinator(cfg)
        # Force loop to run at most one mutation iteration
        cfg2 = _make_config(repo, budget_seconds=2)
        c.config = cfg2
        c.run()
    # smoke always fails -> mutator never invoked
    assert mut.call_count == 0


def test_each_cycle_writes_exactly_one_results_tsv_row(repo):
    cfg = _make_config(repo, budget_seconds=120, plateau_window=2)
    eval_results = [
        _eval_result(10.0),  # baseline
        _eval_result(11.0),  # improved
        _eval_result(11.0),  # stale 1
        _eval_result(11.0),  # stale 2 -> plateau
    ]
    with (
        patch(
            "superclaude.scripts.auto_improve.coordinator.run_eval",
            side_effect=eval_results,
        ),
        patch.object(Coordinator, "_run_smoke", return_value=True),
        patch.object(Coordinator, "_invoke_mutator") as mut,
    ):
        mut.return_value = MutationResult(rationale="r", tokens_used=10)
        c = Coordinator(cfg)
        cycles = c.run()
    rows = ResultsTsv(c.tsv_path).read_all()
    assert len(rows) == cycles


def test_status_mode_skips_loop(repo):
    cfg = _make_config(repo)
    # No active worktree -> status should still produce output without raising
    out = status_mode(cfg)
    assert "auto-improve" in out.lower()


def test_pid_file_written_during_setup(repo):
    cfg = _make_config(repo, budget_seconds=0)
    captured: dict = {}

    def _capture_pid(self):
        captured["existed"] = self.pid_path.exists()
        captured["pid_value"] = self.pid_path.read_text(encoding="utf-8").strip()
        # Now act as the original method would (record baseline + raise on failure)
        raise SystemExit(0)  # short-circuit teardown

    with (
        patch.object(Coordinator, "_record_baseline_or_die", _capture_pid),
        patch(
            "superclaude.scripts.auto_improve.coordinator.run_eval",
            return_value=_eval_result(1.0),
        ),
    ):
        c = Coordinator(cfg)
        with pytest.raises(SystemExit):
            c.run()
    assert captured["existed"] is True
    assert captured["pid_value"]  # non-empty PID string


def test_pid_file_removed_on_exit(repo):
    cfg = _make_config(repo, budget_seconds=0)
    with patch(
        "superclaude.scripts.auto_improve.coordinator.run_eval",
        return_value=_eval_result(1.0),
    ):
        c = Coordinator(cfg)
        c.run()
    assert not c.pid_path.exists()
