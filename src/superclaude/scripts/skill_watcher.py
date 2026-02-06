"""Skill Hot-Reload Watcher for SuperClaude v2.1.0

Monitors skill directories for changes and triggers reload.
Supports two modes:
  - Poll mode (default): Periodic stat-based change detection
  - Watch mode: Real-time filesystem events (requires watchdog)

Cross-platform compatible (Windows/macOS/Linux).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

# Configuration
POLL_INTERVAL = float(os.environ.get("CLAUDE_SKILL_POLL_INTERVAL", "2.0"))
SKILL_EXTENSIONS = {".md", ".ts", ".py", ".json", ".yaml", ".yml"}

# State file for tracking changes
STATE_DIR = Path.home() / ".claude" / ".superclaude_skills"
STATE_FILE = STATE_DIR / "skill_state.json"


@dataclass
class SkillState:
    """State of a single skill for change detection."""

    name: str
    path: Path
    last_modified: float
    file_hash: str
    file_count: int


@dataclass
class WatcherState:
    """Overall watcher state."""

    skills: dict[str, SkillState] = field(default_factory=dict)
    last_scan: float = 0.0


def get_skill_directories() -> list[Path]:
    """Get all skill directories to monitor.

    Returns:
        List of skill base directories
    """
    return [
        Path.home() / ".claude" / "skills",
        Path.home() / ".claude" / "superclaude" / "skills",
        Path.cwd() / ".claude" / "skills",
    ]


def hash_file(file_path: Path) -> str:
    """Generate hash of file content.

    Args:
        file_path: Path to file

    Returns:
        SHA256 hash (truncated to 12 chars)
    """
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:12]
    except (OSError, IOError):
        return ""


def scan_skill(skill_dir: Path) -> SkillState | None:
    """Scan a skill directory and generate state.

    Args:
        skill_dir: Path to skill directory

    Returns:
        SkillState or None if invalid skill
    """
    if not skill_dir.is_dir():
        return None

    # Find manifest
    manifest = None
    for name in ["SKILL.md", "skill.md"]:
        candidate = skill_dir / name
        if candidate.exists():
            manifest = candidate
            break

    if not manifest:
        return None

    # Collect file info
    latest_mtime = 0.0
    file_hashes = []
    file_count = 0

    for file in skill_dir.glob("**/*"):
        if file.is_file() and file.suffix in SKILL_EXTENSIONS:
            try:
                mtime = file.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
                file_hashes.append(hash_file(file))
                file_count += 1
            except (OSError, IOError):
                pass

    # Combined hash of all files
    combined = "".join(sorted(file_hashes))
    combined_hash = hashlib.sha256(combined.encode()).hexdigest()[:12]

    return SkillState(
        name=skill_dir.name,
        path=skill_dir,
        last_modified=latest_mtime,
        file_hash=combined_hash,
        file_count=file_count,
    )


def load_watcher_state() -> WatcherState:
    """Load watcher state from file.

    Returns:
        WatcherState object
    """
    if not STATE_FILE.exists():
        return WatcherState()

    try:
        data = json.loads(STATE_FILE.read_text())
        state = WatcherState(last_scan=data.get("last_scan", 0.0))

        for name, skill_data in data.get("skills", {}).items():
            state.skills[name] = SkillState(
                name=skill_data["name"],
                path=Path(skill_data["path"]),
                last_modified=skill_data["last_modified"],
                file_hash=skill_data["file_hash"],
                file_count=skill_data["file_count"],
            )

        return state
    except (json.JSONDecodeError, KeyError, TypeError):
        return WatcherState()


def save_watcher_state(state: WatcherState) -> None:
    """Save watcher state to file.

    Args:
        state: WatcherState to save
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "last_scan": state.last_scan,
        "skills": {
            name: {
                "name": skill.name,
                "path": str(skill.path),
                "last_modified": skill.last_modified,
                "file_hash": skill.file_hash,
                "file_count": skill.file_count,
            }
            for name, skill in state.skills.items()
        },
    }

    try:
        STATE_FILE.write_text(json.dumps(data, indent=2))
    except OSError:
        pass


def detect_changes(
    old_state: WatcherState,
    new_state: WatcherState,
) -> dict[str, list[str]]:
    """Detect changes between two states.

    Args:
        old_state: Previous state
        new_state: Current state

    Returns:
        Dictionary with 'added', 'modified', 'removed' skill lists
    """
    changes: dict[str, list[str]] = {
        "added": [],
        "modified": [],
        "removed": [],
    }

    old_names = set(old_state.skills.keys())
    new_names = set(new_state.skills.keys())

    # Added skills
    for name in new_names - old_names:
        changes["added"].append(name)

    # Removed skills
    for name in old_names - new_names:
        changes["removed"].append(name)

    # Modified skills
    for name in old_names & new_names:
        old_skill = old_state.skills[name]
        new_skill = new_state.skills[name]

        if old_skill.file_hash != new_skill.file_hash:
            changes["modified"].append(name)

    return changes


def scan_all_skills() -> WatcherState:
    """Scan all skill directories and build state.

    Returns:
        WatcherState with all skills
    """
    state = WatcherState(last_scan=time.time())
    seen_names: set[str] = set()

    for base in get_skill_directories():
        if not base.exists():
            continue

        for item in base.iterdir():
            if not item.is_dir() or item.name.startswith("_"):
                continue

            # Normalize name for deduplication
            canonical = item.name.replace("_", "-")
            if canonical in seen_names:
                continue

            skill_state = scan_skill(item)
            if skill_state:
                seen_names.add(canonical)
                state.skills[skill_state.name] = skill_state

    return state


def check_for_changes() -> dict[str, list[str]]:
    """Check for skill changes since last scan.

    Returns:
        Dictionary with changes (added, modified, removed)
    """
    old_state = load_watcher_state()
    new_state = scan_all_skills()
    changes = detect_changes(old_state, new_state)
    save_watcher_state(new_state)
    return changes


def format_changes(changes: dict[str, list[str]]) -> str:
    """Format changes for output.

    Args:
        changes: Changes dictionary

    Returns:
        Formatted string
    """
    lines = []

    if changes["added"]:
        lines.append(f"➕ Added: {', '.join(changes['added'])}")

    if changes["modified"]:
        lines.append(f"✏️  Modified: {', '.join(changes['modified'])}")

    if changes["removed"]:
        lines.append(f"➖ Removed: {', '.join(changes['removed'])}")

    if not lines:
        return ""

    return "\n".join(lines)


class SkillWatcher:
    """Skill watcher with polling-based change detection."""

    def __init__(
        self,
        on_change: Callable[[dict[str, list[str]]], None] | None = None,
        poll_interval: float = POLL_INTERVAL,
    ):
        """Initialize watcher.

        Args:
            on_change: Callback for changes
            poll_interval: Seconds between polls
        """
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._running = False

    def check_once(self) -> dict[str, list[str]]:
        """Check for changes once.

        Returns:
            Changes dictionary
        """
        return check_for_changes()

    def start_polling(self) -> None:
        """Start polling for changes (blocking)."""
        self._running = True

        while self._running:
            changes = check_for_changes()

            if any(changes.values()) and self.on_change:
                self.on_change(changes)

            time.sleep(self.poll_interval)

    def stop(self) -> None:
        """Stop polling."""
        self._running = False


def main() -> None:
    """CLI entry point for skill watcher."""
    import argparse

    parser = argparse.ArgumentParser(description="SuperClaude Skill Watcher")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for changes once and exit",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for changes continuously",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=POLL_INTERVAL,
        help=f"Poll interval in seconds (default: {POLL_INTERVAL})",
    )

    args = parser.parse_args()

    if args.check:
        changes = check_for_changes()
        output = format_changes(changes)
        if output:
            print(output)
        else:
            print("No skill changes detected")
        return

    if args.watch:
        def on_change(changes: dict[str, list[str]]) -> None:
            timestamp = datetime.now().strftime("%H:%M:%S")
            output = format_changes(changes)
            if output:
                print(f"[{timestamp}] {output}")

        print(f"👀 Watching skills (poll interval: {args.interval}s)")
        print("   Press Ctrl+C to stop\n")

        watcher = SkillWatcher(on_change=on_change, poll_interval=args.interval)
        try:
            watcher.start_polling()
        except KeyboardInterrupt:
            watcher.stop()
            print("\n👋 Watcher stopped")
        return

    # Default: show current state
    state = scan_all_skills()
    print(f"📋 Skills ({len(state.skills)}):\n")
    for name, skill in sorted(state.skills.items()):
        print(f"   {name:25} {skill.file_count} files")


if __name__ == "__main__":
    main()
    sys.exit(0)
