"""Tests for EvalRunner — shell exec + jmespath extraction + timeout.

Uses temp script files to bypass platform-specific shell quoting issues
(esp. cmd.exe on Windows mangles inner double-quotes for `python -c`).
"""

import sys

import pytest

from superclaude.scripts.auto_improve.eval_runner import EvalResult, run_eval


@pytest.fixture
def script_factory(tmp_path):
    counter = {"n": 0}

    def make(body: str) -> str:
        counter["n"] += 1
        path = tmp_path / f"eval_{counter['n']}.py"
        path.write_text(body, encoding="utf-8")
        return f'"{sys.executable}" "{path}"'

    return make


def test_extracts_jmespath_from_json_stdout(script_factory):
    cmd = script_factory(
        'import sys, json; sys.stdout.write(json.dumps({"summary": {"passed": 42}}))'
    )
    result = run_eval(cmd, "summary.passed", timeout=10)
    assert result.metric_value == 42
    assert result.exit_code == 0
    assert result.timed_out is False


def test_returns_none_value_on_extraction_failure(script_factory):
    cmd = script_factory('import sys; sys.stdout.write("not json at all")')
    result = run_eval(cmd, "anything", timeout=10)
    assert result.metric_value is None
    assert result.exit_code == 0


def test_returns_none_when_key_missing(script_factory):
    cmd = script_factory(
        'import sys, json; sys.stdout.write(json.dumps({"present": 1}))'
    )
    result = run_eval(cmd, "missing", timeout=10)
    assert result.metric_value is None


def test_enforces_timeout_kills_subprocess(script_factory):
    cmd = script_factory("import time; time.sleep(30)")
    result = run_eval(cmd, "x", timeout=1)
    assert result.timed_out is True
    assert result.metric_value is None


def test_captures_exit_code_and_wall_seconds(script_factory):
    cmd = script_factory("import sys; sys.exit(7)")
    result = run_eval(cmd, "x", timeout=10)
    assert result.exit_code == 7
    assert result.wall_seconds >= 0
    assert isinstance(result, EvalResult)


def test_coerces_numeric_string_to_float(script_factory):
    cmd = script_factory(
        'import sys, json; sys.stdout.write(json.dumps({"score": "3.14"}))'
    )
    result = run_eval(cmd, "score", timeout=10)
    assert result.metric_value == pytest.approx(3.14)


def test_extraction_handles_nested_path(script_factory):
    cmd = script_factory(
        'import sys, json; sys.stdout.write(json.dumps({"a": {"b": {"c": 9}}}))'
    )
    result = run_eval(cmd, "a.b.c", timeout=10)
    assert result.metric_value == 9


def test_runs_in_specified_cwd(tmp_path):
    """Mutator edits the worktree; eval-cmd MUST run there too. Without
    cwd= passed through, the metric measures the wrong files (regression
    guard for the baseline-pinning bug).
    """
    (tmp_path / "marker.py").write_text(
        'import sys, json; sys.stdout.write(json.dumps({"score": 0.99}))',
        encoding="utf-8",
    )
    cmd = f'"{sys.executable}" marker.py'
    result = run_eval(cmd, "score", timeout=10, cwd=str(tmp_path))
    assert result.exit_code == 0
    assert result.metric_value == pytest.approx(0.99)
