"""
Pytest configuration and shared fixtures for superclaude tests
"""

import subprocess
from pathlib import Path

import pytest


def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run git, raise on failure, keep its chatter out of the test output."""
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


def init_git_repo(
    path: Path, *, commit: bool = True, files: dict[str, str] | None = None
) -> Path:
    """A real repository at *path* on branch ``main``, by default with one commit.

    Identity and ``commit.gpgsign=false`` go into the repo-local config rather
    than ``-c`` flags so they also cover the git calls the code under test
    makes inside the repo (worktree manager, coordinator, insight writer).
    *files* (name -> text, default ``README.md``) are written and committed
    when *commit* is true.
    """
    path.mkdir(parents=True, exist_ok=True)
    git("init", "-q", "-b", "main", str(path))
    for key, value in (
        ("user.email", "t@t"),
        ("user.name", "t"),
        ("commit.gpgsign", "false"),
    ):
        git("-C", str(path), "config", key, value)
    if commit:
        for name, text in (files or {"README.md": "seed\n"}).items():
            target = path / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        git("-C", str(path), "add", "-A")
        git("-C", str(path), "commit", "-q", "-m", "seed")
    return path


@pytest.fixture
def isolated_git_config(tmp_path_factory, monkeypatch) -> None:
    """Shut out the developer's global git config (templates, excludes file,
    identity) so git's own answers in these tests come from the repo alone."""
    empty = tmp_path_factory.mktemp("gitconfig") / "empty-gitconfig"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


@pytest.fixture
def git_repo(tmp_path: Path, isolated_git_config) -> Path:
    """``tmp_path`` as a committed git repository with global config shut out."""
    return init_git_repo(tmp_path)


@pytest.fixture(autouse=True)
def sandbox_home(tmp_path_factory, monkeypatch):
    """Redirect HOME so a user-scope fallback cannot reach the developer's own.

    claude_base() resolves to Path.home()/".claude" whenever the project has no
    .claude/superclaude marker, and every bare tmp_path lacks one. Under test
    that fallback pointed at the real home, so each run left a fresh
    loop_guard_<md5(tmp_path)>.json behind — 29 had accumulated before this was
    caught. Redirecting HOME moves the fallback into a sandbox without changing
    what any test is asserting.

    USERPROFILE is set alongside HOME because that is what Path.home() consults
    on Windows. The sandbox is deliberately *not* the test's own tmp_path: tests
    that assert state stays outside the home directory need the two to differ.
    """
    home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    # Redirecting HOME fixes every path resolved per call. It does nothing for a
    # path resolved at module import, which happens during collection — before
    # any fixture runs — so those constants still point at the developer's real
    # home. Re-point them here, once, rather than in each test that remembers to.
    import superclaude.hooks.mcp_fallback as mcp_fallback
    from superclaude.utils import hook_state_dir

    state = hook_state_dir()
    monkeypatch.setattr(
        mcp_fallback, "MCP_FALLBACK_FILE", state / "mcp_fallbacks.json", raising=False
    )
    return home
