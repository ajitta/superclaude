"""A read-only session must end without a blocking Stop.

The unit tests cover each link — the status filter, the session baseline, the
exclude list. This one runs the chain the way Claude Code does: a real
committed repository, `context_loader` invoked as a UserPromptSubmit hook with
a prompt that asks for nothing, then `insight_writer` invoked as the Stop hook.

The failure it pins was invisible to every script-level test. `context_loader`
creates its cache directory inside `<project>/.claude` on import, project scope
never received a git-exclude block, and the Stop gate asked only whether
`git status` printed anything — so the framework's own cache answered "the
session changed code" and every read-only session ended on an extra turn.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent.parent / "src" / "superclaude" / "scripts"


def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A committed repository carrying a project-scope install marker."""
    repo = tmp_path / "repo"
    (repo / ".claude" / "superclaude").mkdir(parents=True)
    (repo / ".claude" / "superclaude" / "CLAUDE_SC.md").write_text(
        "# marker\n", encoding="utf-8"
    )
    (repo / "app.py").write_text("print('hi')\n", encoding="utf-8")

    _git("init", "-q", cwd=repo)
    _git("config", "user.email", "test@example.com", cwd=repo)
    _git("config", "user.name", "test", cwd=repo)
    _git("add", "-A", cwd=repo)
    _git("commit", "-qm", "baseline", cwd=repo)

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
    return repo


def _run(script, argv, payload, cwd, env_home):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *argv],
        cwd=cwd,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
        env={
            "PATH": __import__("os").environ.get("PATH", ""),
            "HOME": str(env_home),
            "USERPROFILE": str(env_home),
            "CLAUDE_PROJECT_DIR": str(cwd),
            "PYTHONPATH": str(Path(__file__).parent.parent.parent / "src"),
        },
    )


def _status(repo):
    result = subprocess.run(
        ["git", "status", "--porcelain", "-uall"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _user_visible_status(repo):
    """Status lines the user did not cause.

    Project scope receives no git-exclude block, by design — the block is a
    per-clone `.git/info/exclude` written only for local scope. So the
    guarantee is not an empty `git status`, it is that everything left is a
    framework-owned path the exclude list names and the Stop gate filters.
    """
    from superclaude.scripts.insight_writer import _FRAMEWORK_OWNED_PATHS

    lines = []
    for raw in _status(repo).splitlines():
        path = raw[3:].strip().strip('"')
        if any(path.startswith(owned) for owned in _FRAMEWORK_OWNED_PATHS):
            continue
        lines.append(raw)
    return "\n".join(lines)


def test_read_only_session_leaves_a_clean_tree_and_a_silent_stop(
    project, tmp_path, sandbox_home
):
    session = {"session_id": "e2e-readonly", "cwd": str(project)}

    start = _run(
        "insight_writer.py", ["pending-count-from-hook"], session, project, sandbox_home
    )
    assert start.returncode == 0, start.stderr

    prompt = _run(
        "context_loader.py",
        [],
        {**session, "prompt": "what does app.py print?"},
        project,
        sandbox_home,
    )
    assert prompt.returncode == 0, prompt.stderr

    assert _user_visible_status(project) == "", (
        "the framework dirtied the user's worktree outside its own state paths"
    )

    stop = _run(
        "insight_writer.py",
        ["request-from-hook"],
        {**session, "stop_hook_active": False},
        project,
        sandbox_home,
    )
    assert stop.returncode == 0, stop.stderr
    assert stop.stdout.strip() == "", (
        f"a read-only session was blocked at Stop: {stop.stdout}"
    )


def test_a_session_that_edits_code_is_still_asked(project, tmp_path, sandbox_home):
    session = {"session_id": "e2e-edit", "cwd": str(project)}

    _run("insight_writer.py", ["pending-count-from-hook"], session, project, sandbox_home)
    (project / "app.py").write_text("print('changed')\n", encoding="utf-8")

    stop = _run(
        "insight_writer.py",
        ["request-from-hook"],
        {**session, "stop_hook_active": False},
        project,
        sandbox_home,
    )

    assert stop.returncode == 0, stop.stderr
    assert json.loads(stop.stdout)["decision"] == "block"
