"""Unit tests for the memory_staleness SessionStart hook.

The hook scans the current project's CC memory directory and emits a stderr
warning for any entry whose `verified: <YYYY-MM-DD>` frontmatter is older than
a threshold (default 90 days, configurable via SUPERCLAUDE_MEMORY_STALE_DAYS).

Source: docs/specs/retrospective-followups-discovery-ajitta-2026-04-25.md (A2).
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


def test_encode_project_path_drive_letter(tmp_path: Path) -> None:
    mod = _load_module()
    # CC encodes: drive colon -> '--', path separators -> '-'
    assert (
        mod.encode_project_path("C:\\Users\\ajitta\\Repos\\ajitta\\superclaude")
        == "C--Users-ajitta-Repos-ajitta-superclaude"
    )
    # Posix-style normalization
    assert mod.encode_project_path("/home/user/repos/proj") == "-home-user-repos-proj"


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
