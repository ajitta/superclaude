"""Tests for Reporter — morning summary + status mode output."""

from __future__ import annotations

import os
import time
from unittest.mock import patch

import pytest

from superclaude.scripts.auto_improve.reporter import _is_pid_alive, morning_summary
from superclaude.scripts.auto_improve.results_tsv import ResultRow, ResultsTsv


@pytest.fixture
def empty_tsv(tmp_path):
    p = tmp_path / "results.tsv"
    ResultsTsv(p).init()
    return p


@pytest.fixture
def populated_tsv(tmp_path):
    p = tmp_path / "results.tsv"
    tsv = ResultsTsv(p)
    tsv.init()
    tsv.append(
        ResultRow(
            cycle_id=0,
            timestamp="t0",
            commit_hash="-",
            metric_value=1.0,
            status="baseline",
            desc="dry run",
            tokens_used=0,
            wall_seconds=1,
        )
    )
    tsv.append(
        ResultRow(
            cycle_id=1,
            timestamp="t1",
            commit_hash="a" * 40,
            metric_value=1.5,
            status="improved",
            desc="x",
            tokens_used=100,
            wall_seconds=2,
        )
    )
    tsv.append(
        ResultRow(
            cycle_id=2,
            timestamp="t2",
            commit_hash="b" * 40,
            metric_value=2.0,
            status="improved",
            desc="y",
            tokens_used=200,
            wall_seconds=3,
        )
    )
    return p


def test_morning_summary_from_empty_tsv(empty_tsv, tmp_path):
    pid = tmp_path / "auto_improve.pid"
    out = morning_summary(empty_tsv, pid)
    assert "no history" in out.lower() or "no cycles" in out.lower()


def test_morning_summary_with_n_cycles_shows_best_and_delta(populated_tsv, tmp_path):
    pid = tmp_path / "auto_improve.pid"
    out = morning_summary(populated_tsv, pid)
    assert "3" in out  # cycle count
    assert "2.0" in out  # best metric
    assert "1.0" in out  # baseline
    # delta = 1.0
    assert "+1.0" in out or "1.0" in out


def test_status_mode_uses_pid_file_to_detect_active_run(populated_tsv, tmp_path):
    pid_file = tmp_path / "auto_improve.pid"
    pid_file.write_text(str(os.getpid()), encoding="utf-8")
    out = morning_summary(populated_tsv, pid_file)
    assert "active" in out.lower() or "running" in out.lower()
    assert str(os.getpid()) in out


def test_status_mode_without_pid_says_not_running(populated_tsv, tmp_path):
    pid_file = tmp_path / "absent.pid"
    out = morning_summary(populated_tsv, pid_file)
    assert "not running" in out.lower() or "complete" in out.lower()


def test_summary_includes_total_tokens(populated_tsv, tmp_path):
    pid = tmp_path / "auto_improve.pid"
    out = morning_summary(populated_tsv, pid)
    assert "300" in out  # 100 + 200 (baseline tokens=0)


def test_is_pid_alive_returns_false_when_process_is_gone(tmp_path):
    pid_file = tmp_path / "auto_improve.pid"
    pid_file.write_text("99999", encoding="utf-8")
    with patch("os.kill", side_effect=ProcessLookupError):
        assert _is_pid_alive(99999, pid_file=pid_file) is False


def test_is_pid_alive_windows_treats_fresh_pid_file_as_alive(tmp_path, monkeypatch):
    """On Windows, kill(0) errors are ambiguous — a freshly-touched PID file
    is the disambiguator. Regression guard for the Windows always-True stub.
    """
    pid_file = tmp_path / "auto_improve.pid"
    pid_file.write_text("99999", encoding="utf-8")
    monkeypatch.setattr(os, "name", "nt")
    with patch("os.kill", side_effect=OSError("ambiguous on win")):
        assert _is_pid_alive(99999, pid_file=pid_file) is True


def test_is_pid_alive_windows_treats_stale_pid_file_as_dead(tmp_path, monkeypatch):
    pid_file = tmp_path / "auto_improve.pid"
    pid_file.write_text("99999", encoding="utf-8")
    stale = time.time() - 25 * 3600  # > 24h threshold
    os.utime(pid_file, (stale, stale))
    monkeypatch.setattr(os, "name", "nt")
    with patch("os.kill", side_effect=OSError("ambiguous on win")):
        assert _is_pid_alive(99999, pid_file=pid_file) is False
