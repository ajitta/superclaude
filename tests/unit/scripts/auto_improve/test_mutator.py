"""Tests for Mutator wrapper around `claude -p` headless CLI."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from superclaude.scripts.auto_improve.mutator import (
    DEFAULT_MODEL,
    MutationResult,
    Mutator,
)


def _fake_claude_response(rationale: str, tokens: int = 1234) -> str:
    """Mimic `claude -p --output-format json` output payload shape."""
    return json.dumps(
        {
            "type": "result",
            "result": rationale,
            "usage": {"input_tokens": tokens // 2, "output_tokens": tokens // 2},
        }
    )


def _completed(stdout: str, returncode: int = 0):
    proc = MagicMock()
    proc.stdout = stdout
    proc.stderr = ""
    proc.returncode = returncode
    return proc


def test_mutator_calls_claude_cli_with_sonnet_default(tmp_path):
    with patch("subprocess.run") as run:
        run.return_value = _completed(_fake_claude_response("reduced lr"))
        m = Mutator()
        result = m.mutate(worktree_path=tmp_path)
    args, kwargs = run.call_args
    cmd = args[0]
    binary = cmd[0].lower()
    assert binary.endswith("claude") or binary.endswith("claude.exe")
    assert "-p" in cmd
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == DEFAULT_MODEL
    assert isinstance(result, MutationResult)
    assert result.rationale == "reduced lr"


def test_mutator_strips_bash_from_tools(tmp_path):
    with patch("subprocess.run") as run:
        run.return_value = _completed(_fake_claude_response("x"))
        Mutator().mutate(worktree_path=tmp_path)
    cmd = run.call_args.args[0]
    assert "--allowed-tools" in cmd
    tools_arg = cmd[cmd.index("--allowed-tools") + 1]
    assert "Bash" not in tools_arg
    assert "Edit" in tools_arg
    assert "Write" in tools_arg


def test_mutator_passes_worktree_as_cwd(tmp_path):
    with patch("subprocess.run") as run:
        run.return_value = _completed(_fake_claude_response("x"))
        Mutator().mutate(worktree_path=tmp_path)
    assert run.call_args.kwargs.get("cwd") == str(tmp_path)


def test_mutator_returns_rationale_files_tokens(tmp_path):
    payload = json.dumps(
        {
            "type": "result",
            "result": "tweaked dropout",
            "usage": {"input_tokens": 100, "output_tokens": 200},
        }
    )
    with patch("subprocess.run") as run:
        run.return_value = _completed(payload)
        result = Mutator().mutate(worktree_path=tmp_path)
    assert result.rationale == "tweaked dropout"
    assert result.tokens_used == 300
    assert result.error is None


def test_mutator_returns_error_on_empty_rationale(tmp_path):
    payload = json.dumps(
        {
            "type": "result",
            "result": "   ",
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
    )
    with patch("subprocess.run") as run:
        run.return_value = _completed(payload)
        result = Mutator().mutate(worktree_path=tmp_path)
    assert result.error is not None
    assert "rationale" in result.error.lower()


def test_mutator_model_override_via_arg(tmp_path):
    with patch("subprocess.run") as run:
        run.return_value = _completed(_fake_claude_response("x"))
        Mutator(model="opus").mutate(worktree_path=tmp_path)
    cmd = run.call_args.args[0]
    assert cmd[cmd.index("--model") + 1] == "opus"


def test_mutator_returns_error_on_nonzero_exit(tmp_path):
    with patch("subprocess.run") as run:
        run.return_value = _completed("", returncode=2)
        result = Mutator().mutate(worktree_path=tmp_path)
    assert result.error is not None
    assert "exit" in result.error.lower() or "claude" in result.error.lower()


def test_mutator_handles_malformed_json(tmp_path):
    with patch("subprocess.run") as run:
        run.return_value = _completed("not json", returncode=0)
        result = Mutator().mutate(worktree_path=tmp_path)
    assert result.error is not None


def test_mutator_passes_timeout_to_subprocess(tmp_path):
    with patch("subprocess.run") as run:
        run.return_value = _completed(_fake_claude_response("x"))
        Mutator(timeout=120).mutate(worktree_path=tmp_path)
    assert run.call_args.kwargs.get("timeout") == 120


def test_mutator_returns_error_on_timeout(tmp_path):
    import subprocess as _sp

    with patch("subprocess.run", side_effect=_sp.TimeoutExpired("claude", 5)):
        result = Mutator(timeout=5).mutate(worktree_path=tmp_path)
    assert result.error is not None
    assert "timeout" in result.error.lower()


def test_mutator_pipes_prompt_via_stdin(tmp_path):
    """claude CLI flags --allowed-tools and --add-dir are variadic and absorb
    a trailing positional prompt. Mutator must pass prompt via stdin instead.
    Regression guard for the "Input must be provided" failure observed in
    actual mutation runs.
    """
    with patch("subprocess.run") as run:
        run.return_value = _completed(_fake_claude_response("x"))
        Mutator(prompt="optimize the metric").mutate(worktree_path=tmp_path)
    cmd = run.call_args.args[0]
    assert "optimize the metric" not in cmd  # prompt NOT in argv
    assert run.call_args.kwargs.get("input") == "optimize the metric"
