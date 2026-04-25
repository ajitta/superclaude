"""SessionStart hook: warn about stale Claude Code memory entries.

Scans the current project's CC memory directory and prints a stderr summary
of any entry whose `verified: <YYYY-MM-DD>` frontmatter is older than the
threshold (default 90 days; configurable via SUPERCLAUDE_MEMORY_STALE_DAYS).

Non-blocking: exits 0 even when stale entries are found. The warning's only
purpose is to convert silent memory degradation into a visible signal.

Source: docs/specs/retrospective-followups-discovery-ajitta-2026-04-25.md (A2).
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULT_THRESHOLD_DAYS = 90
ENV_THRESHOLD = "SUPERCLAUDE_MEMORY_STALE_DAYS"
HOME_PROJECTS = Path.home() / ".claude" / "projects"
VERIFIED_RE = re.compile(r"^verified:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def encode_project_path(cwd: str) -> str:
    """Encode an absolute path the way CC names project memory directories.

    CC collapses the drive-letter `:\\` (or `:/`) into `--`, then replaces
    remaining path separators with `-`. Example:
    ``C:\\Users\\ajitta\\Repos\\ajitta\\superclaude``
        → ``C--Users-ajitta-Repos-ajitta-superclaude``
    """
    normalized = cwd.replace("\\", "/")
    normalized = normalized.replace(":/", "--")
    normalized = normalized.replace("/", "-")
    return normalized


def resolve_threshold() -> int:
    """Read the threshold from env, falling back to the default on bad input.

    Zero / negative values fall back too — we never silently disable the scan.
    """
    raw = os.environ.get(ENV_THRESHOLD)
    if not raw:
        return DEFAULT_THRESHOLD_DAYS
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_THRESHOLD_DAYS
    if value <= 0:
        return DEFAULT_THRESHOLD_DAYS
    return value


def _parse_verified(text: str) -> date | None:
    match = VERIFIED_RE.search(text)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def scan_stale_entries(memory_dir: Path, threshold_days: int) -> list[Path]:
    """Return memory files whose `verified:` is older than `threshold_days`."""
    if not memory_dir.is_dir():
        return []
    today = date.today()
    stale: list[Path] = []
    for path in sorted(memory_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        verified = _parse_verified(text)
        if verified is None:
            continue
        if (today - verified).days > threshold_days:
            stale.append(path)
    return stale


def project_memory_dir() -> Path:
    return HOME_PROJECTS / encode_project_path(os.getcwd()) / "memory"


def main() -> int:
    threshold = resolve_threshold()
    stale = scan_stale_entries(project_memory_dir(), threshold)
    if stale:
        names = ", ".join(p.name for p in stale)
        sys.stderr.write(
            f"⚠️  {len(stale)} memory entries verified > {threshold} days ago: [{names}]\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
