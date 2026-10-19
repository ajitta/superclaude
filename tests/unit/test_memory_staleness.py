"""Unit tests for the memory_staleness SessionStart hook.

The hook scans the current project's CC memory directory and emits a stderr
warning for any entry whose `verified: <YYYY-MM-DD>` frontmatter is older than
a threshold (default 90 days, configurable via SUPERCLAUDE_MEMORY_STALE_DAYS).

Source: docs/archive/specs/retrospective-followups-discovery-ajitta-2026-04-25.md (A2).
"""

from __future__ import annotations

import importlib.util
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "src" / "superclaude" / "scripts" / "memory_staleness.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("memory_staleness", SCRIPT_PATH)
    assert spec and spec.loader, f"could not load module from {SCRIPT_PATH}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_memory(dir_: Path, name: str, verified_iso: str | None) -> Path:
    path = dir_ / f"{name}.md"
    if verified_iso is None:
        body = "---\nname: x\n---\n\nbody\n"
    else:
        body = f"---\nname: x\nverified: {verified_iso}\n---\n\nbody\n"
    path.write_text(body, encoding="utf-8")
    return path


def test_scan_returns_only_stale_entries(tmp_path: Path) -> None:
    mod = _load_module()
    today = date.today()
    _write_memory(tmp_path, "fresh", today.isoformat())
    stale = _write_memory(tmp_path, "stale", (today - timedelta(days=120)).isoformat())
    _write_memory(tmp_path, "no_verified", None)
    results = mod.scan_stale_entries(tmp_path, threshold_days=90)
    names = sorted(p.name for p in results)
    assert names == ["stale.md"], (
        f"expected only stale.md, got {names}; fresh and no_verified should be excluded"
    )
    assert stale.name in names


def test_scan_respects_threshold(tmp_path: Path) -> None:
    mod = _load_module()
    today = date.today()
    _write_memory(tmp_path, "old", (today - timedelta(days=60)).isoformat())
    # threshold 30 -> "old" (60d) is stale; threshold 90 -> not stale
    assert len(mod.scan_stale_entries(tmp_path, threshold_days=30)) == 1
    assert len(mod.scan_stale_entries(tmp_path, threshold_days=90)) == 0


def test_scan_handles_missing_directory(tmp_path: Path) -> None:
    mod = _load_module()
    nonexistent = tmp_path / "no_such_dir"
    # Hook must not crash when the project has no memory dir yet
    assert mod.scan_stale_entries(nonexistent, threshold_days=90) == []


def test_scan_handles_malformed_frontmatter(tmp_path: Path) -> None:
    mod = _load_module()
    (tmp_path / "broken.md").write_text(
        "---\nverified: not-a-date\n---\n", encoding="utf-8"
    )
    # Malformed entries are skipped (not stale, not crashed)
    assert mod.scan_stale_entries(tmp_path, threshold_days=90) == []


# Real (cwd → folder) pairs read from ~/.claude/projects/ on the author's
# machine (98 folders, 2026-10-18) and from the installed CLI's own encoder
# (`replace(/[^a-zA-Z0-9]/g,"-")`). Each row pins one property of the rule.
@pytest.mark.parametrize(
    "cwd,expected",
    [
        # drive colon and both separators → '-', letters keep their case
        (
            "C:\\Users\\ajitta\\Repos\\ajitta\\superclaude",
            "C--Users-ajitta-Repos-ajitta-superclaude",
        ),
        # '.' → '-'  (the defect: `.claude` used to survive, naming a folder
        # Claude Code never creates)
        (
            "C:\\Users\\ajitta\\.claude\\mem-observer\\sessions",
            "C--Users-ajitta--claude-mem-observer-sessions",
        ),
        # lowercase drive letter is kept as given; dotted path inside a repo
        (
            "c:\\Users\\ajitta\\Repos\\ajitta\\superclaude\\.claude\\worktrees\\authoring-skill",
            "c--Users-ajitta-Repos-ajitta-superclaude--claude-worktrees-authoring-skill",
        ),
        # '_' → '-'  (mkdtemp suffixes draw from [a-z0-9_]; the stored names
        # show '-' where '_' was)
        (
            "C:\\Users\\ajitta\\.claude\\tmp\\unknowns-eval-_f5kuegd",
            "C--Users-ajitta--claude-tmp-unknowns-eval--f5kuegd",
        ),
        # POSIX root → leading '-'
        ("/home/user/repos/proj", "-home-user-repos-proj"),
    ],
)
def test_claude_projects_dir_name_matches_observed_folders(
    cwd: str, expected: str
) -> None:
    from superclaude.utils import claude_projects_dir_name

    assert claude_projects_dir_name(cwd) == expected


def test_claude_projects_dir_name_replaces_every_non_alphanumeric() -> None:
    from superclaude.utils import claude_projects_dir_name

    # No coalescing, no truncation, no case folding: one '-' per character.
    assert claude_projects_dir_name("a b.c_d-e@f") == "a-b-c-d-e-f"
    assert claude_projects_dir_name("MiXeD") == "MiXeD"


def test_memory_dir_uses_shared_encoder_for_dotted_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from superclaude.utils import claude_projects_dir_name

    mod = _load_module()
    project = tmp_path / ".dot_ted.proj"
    project.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    resolved = mod.project_memory_dir()
    assert (
        resolved
        == mod.home_projects() / claude_projects_dir_name(str(project)) / "memory"
    )
    assert "." not in resolved.parent.name and "_" not in resolved.parent.name, (
        f"memory dir keeps characters Claude Code encodes: {resolved.parent.name}"
    )
    assert not hasattr(mod, "encode_project_path"), (
        "memory_staleness must not keep its own copy of the encoder"
    )


def test_memory_dir_anchored_on_project_root_not_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from superclaude.utils import claude_projects_dir_name

    mod = _load_module()
    subdir = tmp_path / "src" / "pkg"
    subdir.mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.chdir(subdir)
    # CC encodes the project root into the memory dir name. Anchoring on CWD
    # would encode ...-src-pkg, a directory CC never creates, and the scan
    # would silently find nothing.
    expected = claude_projects_dir_name(str(tmp_path))
    resolved = mod.project_memory_dir()
    assert resolved == mod.home_projects() / expected / "memory"
    assert not resolved.parent.name.endswith("-src-pkg"), (
        f"memory dir followed CWD into the subdirectory: {resolved.parent.name}"
    )


@pytest.mark.parametrize(
    "env_value,expected",
    [
        (None, 90),
        ("30", 30),
        ("0", 90),  # zero falls back to default; never disable silently
        ("not-a-number", 90),  # malformed env falls back to default
    ],
)
def test_threshold_from_env(
    monkeypatch: pytest.MonkeyPatch, env_value, expected
) -> None:
    mod = _load_module()
    if env_value is None:
        monkeypatch.delenv("SUPERCLAUDE_MEMORY_STALE_DAYS", raising=False)
    else:
        monkeypatch.setenv("SUPERCLAUDE_MEMORY_STALE_DAYS", env_value)
    assert mod.resolve_threshold() == expected
