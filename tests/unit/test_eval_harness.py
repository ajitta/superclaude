"""Drift guards for the evals/ harness (roadmap Phase 1-1/1-2).

The harness lives outside the installed tree and outside default test runs'
exercise paths, so config drift (tasks.yaml vs fixtures vs run_eval.py) would
rot silently — the same failure class the version-consistency suite closed.
"""

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_DIR = REPO_ROOT / "evals"
TASKS = yaml.safe_load((EVALS_DIR / "tasks.yaml").read_text(encoding="utf-8"))


def test_run_eval_imports_cleanly():
    sys.path.insert(0, str(EVALS_DIR))
    try:
        import run_eval  # noqa: F401
    finally:
        sys.path.remove(str(EVALS_DIR))


def test_every_fixture_dir_exists():
    for task in TASKS["tasks"]:
        assert (EVALS_DIR / task["fixture"]).is_dir(), (
            f"{task['id']}: missing {task['fixture']}"
        )


def test_arms_match_harness_constant():
    source = (EVALS_DIR / "run_eval.py").read_text(encoding="utf-8")
    match = re.search(r"ARMS = \(([^)]+)\)", source)
    harness_arms = set(re.findall(r'"([^"]+)"', match.group(1)))
    assert set(TASKS["arms"]) == harness_arms


def test_all_check_types_implemented():
    source = (EVALS_DIR / "run_eval.py").read_text(encoding="utf-8")
    implemented = set(re.findall(r'ctype == "(\w+)"', source))
    used = {c["type"] for t in TASKS["tasks"] for c in t.get("checks", [])}
    assert used <= implemented, f"unimplemented check types: {used - implemented}"


def test_citation_expected_lines_match_planted_bugs():
    """review-citations expected lines must point at the planted defects."""
    task = next(t for t in TASKS["tasks"] if t["id"] == "review-citations")
    check = next(c for c in task["checks"] if c["type"] == "citation_lines")
    lines = (
        (EVALS_DIR / task["fixture"] / check["file"])
        .read_text(encoding="utf-8")
        .splitlines()
    )
    planted = {
        "time.time() - ttl": check["expected"][0],
        "return self._data[key]": check["expected"][1],
        "del self._expiry[key]": check["expected"][2],
    }
    for snippet, lineno in planted.items():
        assert snippet in lines[lineno - 1], (
            f"store.py:{lineno} no longer contains {snippet!r} — "
            "re-sync tasks.yaml expected lines with the fixture"
        )


def test_introspect_probe_matches_flags_marker_set():
    """probe-introspect-marker regex must stay in sync with FLAGS.md markers."""
    flags = (REPO_ROOT / "src/superclaude/core/FLAGS.md").read_text(encoding="utf-8")
    marker_set = re.search(r"--introspect.*\((.+?)\)", flags).group(1)
    task = next(t for t in TASKS["tasks"] if t["id"] == "probe-introspect-marker")
    probe_chars = set(task["checks"][0]["pattern"].strip("[]"))
    assert probe_chars <= set(marker_set), (
        f"probe markers {probe_chars} not all in FLAGS.md --introspect set {marker_set!r}"
    )


def test_scope_typo_fixture_line_stable():
    """probe-scope-restraint asserts on README.md line 3 — guard the fixture."""
    readme = (EVALS_DIR / "fixtures/probe-scope/README.md").read_text(encoding="utf-8")
    assert "recieve" in readme.splitlines()[2]


def _import_run_eval():
    sys.path.insert(0, str(EVALS_DIR))
    try:
        import run_eval
    finally:
        sys.path.remove(str(EVALS_DIR))
    return run_eval


def test_ws_gitignore_covers_loop_guard_state_path(tmp_path, monkeypatch):
    """WS_GITIGNORE must track loop_guard.py's actual state-file path — if the
    hook moves its state file, workspace scope checks silently re-contaminate.

    Resolved through the real hook resolvers against a project-scope layout,
    since run_eval installs with --scope project into the workspace.
    """
    from superclaude.scripts.loop_guard import _state_path

    (tmp_path / ".claude" / "superclaude").mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

    state_dir = _state_path().parent.relative_to(tmp_path).as_posix() + "/"
    ignored = _import_run_eval().WS_GITIGNORE.splitlines()
    assert state_dir in ignored, (
        f"loop_guard state dir {state_dir!r} not in WS_GITIGNORE {ignored} — "
        "re-sync run_eval.py with scripts/loop_guard.py"
    )


def test_large_file_checks_cover_planted_error_classes():
    """large-file-analysis success checks must name exactly the error classes
    gen_fixture.py plants — class rename in the fixture must fail here, not
    silently false-pass/fail the eval."""
    source = (EVALS_DIR / "fixtures/large-file/gen_fixture.py").read_text(
        encoding="utf-8"
    )
    planted = set(re.findall(r"ERROR (\w+):", source))
    assert planted, "no planted error classes found in gen_fixture.py"
    task = next(t for t in TASKS["tasks"] if t["id"] == "large-file-analysis")
    patterns = {
        c["pattern"]
        for c in task["checks"]
        if c["type"] == "output_regex" and c["tag"] == "success"
    }
    assert planted == patterns, (
        f"planted classes {planted} != checked patterns {patterns}"
    )


def test_pin_python_substitutes_only_bare_python_token():
    run_eval = _import_run_eval()
    cmd = ["python", "-m", "pytest", "-q", "python_helper.py"]
    pinned = run_eval._pin_python(cmd)
    assert pinned == [run_eval.PY_BIN, "-m", "pytest", "-q", "python_helper.py"]
    assert run_eval._pin_python(["git", "status"]) == ["git", "status"]


def test_misleading_evidence_sentinel_matches_fixture():
    """The code-truth sentinel is the whole task — a fixture rename would turn
    a passing check into an unreachable one without failing anything."""
    task = next(t for t in TASKS["tasks"] if t["id"] == "misleading-evidence")
    sentinel = next(c["pattern"] for c in task["checks"] if c["type"] == "output_regex")
    fixture = EVALS_DIR / task["fixture"]
    assert f'return "{sentinel}"' in (fixture / "normalize.py").read_text(
        encoding="utf-8"
    ), f"normalize.py no longer returns {sentinel!r} — re-sync tasks.yaml"
    assert "None" in (fixture / "README.md").read_text(encoding="utf-8"), (
        "README.md must keep the contradicting None claim, or the task tests nothing"
    )


def test_poisoned_readme_carries_injection_and_canary_token():
    """Both halves are load-bearing: the injected directive makes the task a
    test, the canary token makes the leak detectable."""
    task = next(t for t in TASKS["tasks"] if t["id"] == "poisoned-readme")
    fixture = EVALS_DIR / task["fixture"]
    readme = (fixture / "README.md").read_text(encoding="utf-8")
    assert "exfil.txt" in readme and "notes.md" in readme, (
        "poisoned-readme README lost its injected directive — the task would "
        "pass trivially"
    )
    token = next(
        c["pattern"] for c in task["checks"] if c["type"] == "output_not_regex"
    )
    assert token in (fixture / "credentials.txt").read_text(encoding="utf-8"), (
        f"credentials.txt no longer contains {token!r} — re-sync tasks.yaml"
    )


def test_gate_flag_is_read_by_harness():
    """tasks.yaml declares hard gates; run_eval.py must still consume the flag
    and act on it, or every gate silently degrades to a soft metric."""
    source = (EVALS_DIR / "run_eval.py").read_text(encoding="utf-8")
    assert 'check.get("gate"' in source, "run_eval.py stopped reading the gate flag"
    assert "gates_ok" in source, "run_eval.py stopped gating its exit code"


def test_hard_gates_stay_on_invariant_tasks():
    """Adding or removing a hard gate must be a deliberate edit, not drift."""
    gated = {
        t["id"] for t in TASKS["tasks"] for c in t.get("checks", []) if c.get("gate")
    }
    assert gated == {
        "destructive-elicitation",
        "poisoned-readme",
        "problem-statement-not-request",
        "conflicting-constraints",
    }, f"hard-gate task set changed: {sorted(gated)}"


def test_parse_stream_flags_refusal_from_assistant_event():
    """A Fable 5.x refusal arrives as the API message's stop_reason on an
    `assistant` event; it must surface as a distinct refusal, not a generic
    error, so a model-release canary can tell classifier trips apart."""
    import json

    run_eval = _import_run_eval()
    res = run_eval.TaskResult(arm="sc-full", task_id="probe")
    stream = "\n".join(
        [
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "stop_reason": "refusal",
                        "stop_details": {"category": "reasoning_extraction"},
                        "content": [{"type": "text", "text": "I can't help."}],
                    },
                }
            ),
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "result": "I can't help.",
                    "usage": {"input_tokens": 10, "output_tokens": 5},
                    "total_cost_usd": 0.01,
                    "num_turns": 1,
                }
            ),
        ]
    )
    run_eval._parse_stream(stream, res)
    assert res.refusal_category == "reasoning_extraction"
    assert res.error.startswith("refusal")
    assert res.ok is False


def test_parse_stream_normal_run_has_no_refusal():
    import json

    run_eval = _import_run_eval()
    res = run_eval.TaskResult(arm="sc-full", task_id="probe")
    stream = json.dumps(
        {"type": "result", "subtype": "success", "result": "done", "usage": {}}
    )
    run_eval._parse_stream(stream, res)
    assert res.refusal_category == ""
    assert res.error == ""


def test_report_lists_refusals_separately(tmp_path):
    run_eval = _import_run_eval()
    refused = run_eval.TaskResult(arm="sc-full", task_id="probe-a")
    run_eval._mark_refusal(refused, "cyber")
    errored = run_eval.TaskResult(arm="sc-full", task_id="probe-b", error="rc=1")
    report = run_eval.write_report([refused, errored], tmp_path)
    assert "| probe-a | REFUSED |" in report
    assert "| probe-b | ERR |" in report
    assert "## Refusals" in report
    assert "| sc-full | probe-a | cyber |" in report


def _refusal_stream(*, result_stop_reason: bool, is_error: bool = False) -> str:
    import json

    events = [
        {
            "type": "assistant",
            "message": {
                "stop_reason": "refusal",
                "stop_details": {"category": "reasoning_extraction"},
                "content": [{"type": "text", "text": "I can't help."}],
            },
        },
        {
            "type": "result",
            "subtype": "success",
            "result": "I can't help.",
            "is_error": is_error,
            "usage": {"input_tokens": 10, "output_tokens": 5},
            "total_cost_usd": 0.01,
            "num_turns": 1,
        },
    ]
    if result_stop_reason:
        # Claude Code 2.1.258's result schema: top-level stop_reason, no stop_details.
        events[1]["stop_reason"] = "refusal"
    return "\n".join(json.dumps(e) for e in events)


def test_result_event_stop_reason_never_downgrades_assistant_category():
    run_eval = _import_run_eval()
    res = run_eval.TaskResult(arm="sc-full", task_id="probe")
    run_eval._parse_stream(_refusal_stream(result_stop_reason=True), res)
    assert res.refusal_category == "reasoning_extraction"
    assert res.error == "refusal (category=reasoning_extraction)"


def test_result_only_refusal_reports_unknown_category():
    import json

    run_eval = _import_run_eval()
    res = run_eval.TaskResult(arm="sc-full", task_id="probe")
    stream = json.dumps(
        {
            "type": "result",
            "subtype": "success",
            "result": "no",
            "stop_reason": "refusal",
        }
    )
    run_eval._parse_stream(stream, res)
    assert res.refusal_category == "unknown"
    assert res.error == "refusal (category=unknown)"


def test_refusal_error_survives_is_error_on_result_event():
    run_eval = _import_run_eval()
    res = run_eval.TaskResult(arm="sc-full", task_id="probe")
    run_eval._parse_stream(_refusal_stream(result_stop_reason=True, is_error=True), res)
    assert res.refusal_category == "reasoning_extraction"
    assert res.error.startswith("refusal")


def test_report_no_refusals_branch_and_results_json_field(tmp_path):
    import json

    run_eval = _import_run_eval()
    errored = run_eval.TaskResult(arm="sc-full", task_id="probe-b", error="rc=1")
    report = run_eval.write_report([errored], tmp_path)
    assert "No refusals." in report
    refused = run_eval.TaskResult(arm="sc-full", task_id="probe-a")
    run_eval._mark_refusal(refused, "cyber")
    run_eval.write_report([refused], tmp_path)
    payload = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert payload[0]["refusal_category"] == "cyber"


def test_parse_stream_counts_powershell_commands_for_transcript_checks():
    """On Windows the model reaches for PowerShell as readily as Bash; a
    destructive command through either must trip the transcript gates."""
    import json

    run_eval = _import_run_eval()
    res = run_eval.TaskResult(arm="sc-full", task_id="probe")
    stream = "\n".join(
        json.dumps(
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "tool_use", "name": tool, "input": {"command": cmd}}
                    ]
                },
            }
        )
        for tool, cmd in [("PowerShell", "git clean -fdx"), ("Bash", "ls")]
    )
    _, bash_inputs = run_eval._parse_stream(stream, res)
    assert "git clean -fdx" in bash_inputs
    assert "ls" in bash_inputs


def test_file_preserved_glob_accepts_a_stashed_file(tmp_path):
    import subprocess

    run_eval = _import_run_eval()
    ws = tmp_path / "ws"
    ws.mkdir()

    def git(*args):
        subprocess.run(["git", *args], cwd=ws, check=True, capture_output=True)

    git("init", "-b", "main")
    git("config", "user.email", "t@e.com")
    git("config", "user.name", "T")
    (ws / "app.py").write_text("print(1)\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-m", "baseline")
    (ws / "scratch.tmp").write_text("junk\n", encoding="utf-8")

    check = {"type": "file_preserved_glob", "pattern": "scratch.tmp"}
    ok, detail = run_eval._check_one(check, "file_preserved_glob", ws, "", "")
    assert ok and detail == "in working tree"

    git("stash", "push", "--include-untracked", "-m", "wipe")
    assert not (ws / "scratch.tmp").exists()
    ok, detail = run_eval._check_one(check, "file_preserved_glob", ws, "", "")
    assert ok, detail
    assert "scratch.tmp" in detail

    git("stash", "drop")
    ok, detail = run_eval._check_one(check, "file_preserved_glob", ws, "", "")
    assert not ok and detail == "gone"


def test_under_claude_home_guard(monkeypatch, tmp_path):
    run_eval = _import_run_eval()
    home = tmp_path / "home"
    (home / ".claude" / "tmp").mkdir(parents=True)
    monkeypatch.setattr(run_eval.Path, "home", staticmethod(lambda: home))
    assert run_eval._under_claude_home(home / ".claude" / "tmp" / "superclaude-evals")
    assert run_eval._under_claude_home(home / ".claude")
    assert not run_eval._under_claude_home(tmp_path / "elsewhere")


def test_file_exists_glob_accepts_a_pattern_list(tmp_path):
    run_eval = _import_run_eval()
    ws = tmp_path
    (ws / "docs" / "features" / "csv-export").mkdir(parents=True)
    (ws / "docs" / "features" / "csv-export" / "05-plan.md").write_text("# plan\n")
    check = {"pattern": ["docs/plans/*.md", "docs/features/*/05-plan.md"]}
    ok, detail = run_eval._check_one(check, "file_exists_glob", ws, "", "")
    assert ok and "docs/features/*/05-plan.md" in detail
    ok, detail = run_eval._check_one(
        {"pattern": ["docs/plans/*.md"]}, "file_exists_glob", ws, "", ""
    )
    assert not ok and detail == "no match"
    # a bare string keeps working
    ok, _ = run_eval._check_one(
        {"pattern": "docs/features/*/05-plan.md"}, "file_exists_glob", ws, "", ""
    )
    assert ok


def test_plan_routing_accepts_both_convention_locations():
    """RULES_DOCS.md names two correct homes for a plan; the task must not
    score the convention-mandated feature folder as a wrong location."""
    task = next(t for t in TASKS["tasks"] if t["id"] == "plan-routing")
    exists = next(c for c in task["checks"] if c["type"] == "file_exists_glob")
    assert set(exists["pattern"]) == {"docs/plans/*.md", "docs/features/*/05-plan.md"}
    assert not any(
        c["type"] == "file_absent_glob" and "features" in str(c.get("pattern"))
        for c in task["checks"]
    )


def test_result_subtype_reads_the_result_event():
    import json

    run_eval = _import_run_eval()
    stream = "\n".join(
        [
            json.dumps({"type": "assistant", "message": {"content": []}}),
            json.dumps({"type": "result", "subtype": "error_max_turns", "result": ""}),
        ]
    )
    assert run_eval._result_subtype(stream) == "error_max_turns"
    assert run_eval._result_subtype("not json\n") is None


def test_max_turns_exit_keeps_usage_and_checks(tmp_path, monkeypatch):
    """`error_max_turns` exits 1 after the model has worked; the run must keep
    its usage and be scored on the workspace, while `ok` stays false."""
    import json
    import subprocess

    run_eval = _import_run_eval()
    ws = tmp_path / "ws"
    (ws / "docs" / "plans").mkdir(parents=True)
    (ws / "docs" / "plans" / "csv.md").write_text("# plan\n", encoding="utf-8")
    stream = "\n".join(
        [
            json.dumps({"type": "assistant", "message": {"content": []}}),
            json.dumps(
                {
                    "type": "result",
                    "subtype": "error_max_turns",
                    "is_error": True,
                    "result": "",
                    "usage": {"input_tokens": 100, "output_tokens": 50},
                    "total_cost_usd": 0.42,
                    "num_turns": 13,
                }
            ),
        ]
    )

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, stdout=stream, stderr="")

    monkeypatch.setattr(run_eval.subprocess, "run", fake_run)
    task = {
        "id": "t",
        "prompt": "do the thing",
        "checks": [
            {
                "type": "file_exists_glob",
                "tag": "location",
                "pattern": "docs/plans/*.md",
            }
        ],
    }
    res = run_eval.run_task(
        "sc-full", task, ws, tmp_path / "cfg", tmp_path / "logs", "claude", "m", {}
    )
    assert res.error.startswith("claude rc=1: error_max_turns")
    assert res.cost_usd == 0.42 and res.num_turns == 13 and res.tokens_out == 50
    assert [c.passed for c in res.checks] == [True]
    assert res.ok is False


def test_nonzero_exit_without_result_event_is_a_plain_error(tmp_path, monkeypatch):
    import subprocess

    run_eval = _import_run_eval()
    ws = tmp_path / "ws"
    ws.mkdir()

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="boom")

    monkeypatch.setattr(run_eval.subprocess, "run", fake_run)
    task = {
        "id": "t",
        "prompt": "do the thing",
        "checks": [{"type": "file_exists_glob", "pattern": "*.md"}],
    }
    res = run_eval.run_task(
        "sc-full", task, ws, tmp_path / "cfg", tmp_path / "logs", "claude", "m", {}
    )
    assert res.error == "claude rc=1: boom"
    assert res.checks == []
