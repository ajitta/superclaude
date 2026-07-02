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


def test_ws_gitignore_covers_loop_guard_state_path():
    """WS_GITIGNORE must track loop_guard.py's actual state-file path — if the
    hook moves its state file, workspace scope checks silently re-contaminate."""
    source = (REPO_ROOT / "src/superclaude/scripts/loop_guard.py").read_text(
        encoding="utf-8"
    )
    match = re.search(r'Path\(root\)\s*/\s*"([^"]+)"\s*/\s*"([^"]+)"', source)
    state_path = f"{match.group(1)}/{match.group(2)}"
    ignored = _import_run_eval().WS_GITIGNORE.splitlines()
    assert state_path in ignored, (
        f"loop_guard state path {state_path!r} not in WS_GITIGNORE {ignored} — "
        "re-sync run_eval.py with scripts/loop_guard.py"
    )


def test_pin_python_substitutes_only_bare_python_token():
    run_eval = _import_run_eval()
    cmd = ["python", "-m", "pytest", "-q", "python_helper.py"]
    pinned = run_eval._pin_python(cmd)
    assert pinned == [run_eval.PY_BIN, "-m", "pytest", "-q", "python_helper.py"]
    assert run_eval._pin_python(["git", "status"]) == ["git", "status"]
