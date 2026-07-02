"""Tests for loop_guard.py circuit breaker hook.

Contract:
- PostToolUse records a signature (tool_name + input_fingerprint) when the
  tool_response indicates an error. Entries outside a 15-min sliding window
  are purged.
- PreToolUse reads the state and blocks if the prospective call's signature
  has accumulated >=5 error entries in the window.
- Env var SUPERCLAUDE_LOOP_GUARD=0 disables the guard (always approve).
- Failure modes (bad stdin, write failure, etc.) fail open (approve).
- State file is scoped to $CLAUDE_PROJECT_DIR/.claude/loop_guard_state.json.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

GUARD_SCRIPT = (
    Path(__file__).parent.parent.parent
    / "src"
    / "superclaude"
    / "scripts"
    / "loop_guard.py"
)

BLOCK_THRESHOLD = 5


def run_guard(
    payload: dict,
    project_dir: Path,
    env_override: dict | None = None,
) -> dict:
    """Invoke loop_guard.py with given hook payload; return parsed JSON output."""
    stdin_data = json.dumps(payload)
    env = os.environ.copy()
    env.pop("SUPERCLAUDE_LOOP_GUARD", None)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    if env_override:
        env.update(env_override)

    result = subprocess.run(
        [sys.executable, str(GUARD_SCRIPT)],
        input=stdin_data,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"guard crashed: {result.stderr}"
    return json.loads(result.stdout.strip() or "{}")


def post_event(tool_name: str, command: str, error: str) -> dict:
    """Build a PostToolUse payload representing a failed Bash/Edit/Write call."""
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": tool_name,
        "tool_input": {"command": command}
        if tool_name == "Bash"
        else {"file_path": command},
        "tool_response": {"error": error, "exit_code": 1},
    }


def pre_event(tool_name: str, command: str) -> dict:
    """Build a PreToolUse payload for a prospective call."""
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"command": command}
        if tool_name == "Bash"
        else {"file_path": command},
    }


@pytest.fixture
def project_dir(tmp_path):
    (tmp_path / ".claude").mkdir()
    return tmp_path


class TestApprove:
    """PreToolUse approves by default."""

    def test_fresh_state_approves(self, project_dir):
        result = run_guard(pre_event("Bash", "ls -la"), project_dir)
        assert result["decision"] == "approve"

    def test_post_event_approves(self, project_dir):
        """PostToolUse never blocks — it only records."""
        result = run_guard(post_event("Bash", "false", "command failed"), project_dir)
        assert result["decision"] == "approve"

    def test_successful_post_does_not_record(self, project_dir):
        """PostToolUse without error signal must not increment counters."""
        good = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "tool_response": {"exit_code": 0, "stdout": "ok"},
        }
        # 10 successes, then a pre-event on the same command → approve
        for _ in range(10):
            run_guard(good, project_dir)
        result = run_guard(pre_event("Bash", "ls"), project_dir)
        assert result["decision"] == "approve"

    def test_unknown_event_approves(self, project_dir):
        result = run_guard(
            {"hook_event_name": "Something", "tool_name": "Bash"},
            project_dir,
        )
        assert result["decision"] == "approve"

    def test_empty_stdin_approves(self, project_dir):
        result = run_guard({}, project_dir)
        assert result["decision"] == "approve"


class TestBlockAfterRepeats:
    """PreToolUse blocks after 5 identical error signatures in window."""

    def test_blocks_at_fifth_repeat(self, project_dir):
        """5 identical errors → 6th PreToolUse for same signature blocked."""
        for _ in range(BLOCK_THRESHOLD):
            run_guard(
                post_event("Bash", "make broken", "undefined symbol xyz"), project_dir
            )
        result = run_guard(pre_event("Bash", "make broken"), project_dir)
        assert result["decision"] == "block"
        assert "circuit breaker" in result["reason"].lower()

    def test_four_errors_do_not_block(self, project_dir):
        for _ in range(BLOCK_THRESHOLD - 1):
            run_guard(
                post_event("Bash", "make broken", "undefined symbol xyz"), project_dir
            )
        result = run_guard(pre_event("Bash", "make broken"), project_dir)
        assert result["decision"] == "approve"

    def test_block_message_is_actionable(self, project_dir):
        for _ in range(BLOCK_THRESHOLD):
            run_guard(
                post_event("Bash", "make broken", "undefined symbol xyz"), project_dir
            )
        result = run_guard(pre_event("Bash", "make broken"), project_dir)
        assert result["decision"] == "block"
        # Should suggest changing approach
        reason = result["reason"].lower()
        assert "approach" in reason or "different" in reason or "change" in reason


class TestStateIsolation:
    """Different signatures accumulate independently; success resets."""

    def test_different_commands_do_not_accumulate(self, project_dir):
        """4 errors of cmd-A + 1 error of cmd-B → neither blocked."""
        for _ in range(4):
            run_guard(post_event("Bash", "cmd-A", "err-A"), project_dir)
        run_guard(post_event("Bash", "cmd-B", "err-B"), project_dir)
        assert (
            run_guard(pre_event("Bash", "cmd-A"), project_dir)["decision"] == "approve"
        )
        assert (
            run_guard(pre_event("Bash", "cmd-B"), project_dir)["decision"] == "approve"
        )

    def test_successful_call_resets_signature(self, project_dir):
        """4 errors, 1 success on same signature, 4 more errors → no block."""
        for _ in range(4):
            run_guard(post_event("Bash", "flaky", "transient error"), project_dir)
        # success clears counter
        good = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "flaky"},
            "tool_response": {"exit_code": 0, "stdout": "ok"},
        }
        run_guard(good, project_dir)
        for _ in range(4):
            run_guard(post_event("Bash", "flaky", "transient error"), project_dir)
        result = run_guard(pre_event("Bash", "flaky"), project_dir)
        assert result["decision"] == "approve"

    def test_different_tools_do_not_cross_pollute(self, project_dir):
        """5 Edit errors on foo.py must not block Bash on foo.py."""
        for _ in range(BLOCK_THRESHOLD):
            run_guard(post_event("Edit", "foo.py", "string not found"), project_dir)
        assert (
            run_guard(pre_event("Bash", "foo.py"), project_dir)["decision"] == "approve"
        )


class TestEnvOptOut:
    def test_env_var_disables_guard(self, project_dir):
        """SUPERCLAUDE_LOOP_GUARD=0 → always approve regardless of state."""
        for _ in range(BLOCK_THRESHOLD):
            run_guard(post_event("Bash", "make broken", "err"), project_dir)
        result = run_guard(
            pre_event("Bash", "make broken"),
            project_dir,
            env_override={"SUPERCLAUDE_LOOP_GUARD": "0"},
        )
        assert result["decision"] == "approve"


class TestSlidingWindow:
    def test_stale_entries_expire(self, project_dir):
        """Entries older than window should not count toward block."""
        # Seed state file directly with 5 old entries
        state_file = project_dir / ".claude" / "loop_guard_state.json"
        old_ts = time.time() - (16 * 60)  # 16 min ago, outside 15-min window
        state = {
            "entries": [
                {
                    "signature": "Bash::make broken",
                    "ts": old_ts,
                    "kind": "error",
                }
                for _ in range(BLOCK_THRESHOLD)
            ]
        }
        state_file.write_text(json.dumps(state))
        result = run_guard(pre_event("Bash", "make broken"), project_dir)
        assert result["decision"] == "approve"

    def test_recent_entries_still_block(self, project_dir):
        state_file = project_dir / ".claude" / "loop_guard_state.json"
        recent_ts = time.time() - 60  # 1 min ago
        state = {
            "entries": [
                {
                    "signature": "Bash::make broken",
                    "ts": recent_ts,
                    "kind": "error",
                }
                for _ in range(BLOCK_THRESHOLD)
            ]
        }
        state_file.write_text(json.dumps(state))
        result = run_guard(pre_event("Bash", "make broken"), project_dir)
        assert result["decision"] == "block"


class TestFailureModes:
    def test_malformed_state_file_approves(self, project_dir):
        """Corrupted state file must not crash the hook (fail open)."""
        state_file = project_dir / ".claude" / "loop_guard_state.json"
        state_file.write_text("not valid json {{{")
        result = run_guard(pre_event("Bash", "ls"), project_dir)
        assert result["decision"] == "approve"

    def test_missing_claude_dir_auto_creates(self, tmp_path):
        """If .claude/ missing, guard should not crash — create on write."""
        result = run_guard(post_event("Bash", "foo", "err"), tmp_path)
        assert result["decision"] == "approve"
