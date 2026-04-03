"""
SuperClaude Content Integrity Audit

Combines drift detection, cross-reference checking, and content usage validation
into a single audit report.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

from .verify_drift import verify_drift


def _get_src_root() -> Path:
    """Get the superclaude source root."""
    return Path(__file__).resolve().parent.parent


def _check_cross_refs(src: Path) -> Dict[str, Any]:
    """Run cross-reference integrity checks.

    Returns dict with handoff and mcp results.
    """
    commands_dir = src / "commands"
    agents_dir = src / "agents"
    modes_dir = src / "modes"
    mcp_dir = src / "mcp"
    MCP_ABBREV_MAP = {
        "seq": "MCP_Sequential.md",
        "c7": "MCP_Context7.md",
        "play": "MCP_Playwright.md",
        "perf": "MCP_Chrome-DevTools.md",
        "morph": "MCP_Morphllm.md",
        "magic": "MCP_Magic.md",
        "serena": "MCP_Serena.md",
        "tavily": "MCP_Tavily.md",
    }

    HANDOFF_SKIP = {"/sc:[command]"}

    # Available commands
    available_commands = set()
    if commands_dir.exists():
        available_commands = {
            f.stem for f in commands_dir.glob("*.md")
            if f.stem.upper() != "README"
        }

    # Scan all content files
    issues = {"handoff": [], "mcp": [], "triggers": []}

    content_files = []
    for d in (commands_dir, agents_dir, modes_dir):
        if d.exists():
            content_files.extend(
                f for f in d.glob("*.md") if f.stem.upper() != "README"
            )

    for f in sorted(content_files):
        content = f.read_text(encoding="utf-8")
        file_id = f"{f.parent.name}/{f.stem}"

        # Handoff checks
        handoff_match = re.search(r'<handoff\s+next="([^"]*)"', content)
        if handoff_match:
            targets = re.findall(r"/sc:([\w-]+)", handoff_match.group(1))
            for t in targets:
                if f"/sc:{t}" not in HANDOFF_SKIP and t not in available_commands:
                    issues["handoff"].append(f"{file_id}: /sc:{t}")

        # MCP checks
        mcp_match = re.search(r'<mcp\s+servers="([^"]*)"', content)
        if mcp_match:
            for ref in mcp_match.group(1).split("|"):
                ref = ref.strip()
                if not ref:
                    continue
                if ref not in MCP_ABBREV_MAP:
                    issues["mcp"].append(f"{file_id}: unknown '{ref}'")
                elif not (mcp_dir / MCP_ABBREV_MAP[ref]).exists():
                    issues["mcp"].append(f"{file_id}: {ref} → {MCP_ABBREV_MAP[ref]} missing")

    # Trigger uniqueness
    trigger_owners = defaultdict(list)
    if agents_dir.exists():
        for agent_file in sorted(agents_dir.glob("*.md")):
            if agent_file.stem.upper() == "README":
                continue
            content = agent_file.read_text(encoding="utf-8")
            fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if not fm_match:
                continue
            for line in fm_match.group(1).splitlines():
                if line.strip().startswith("description:"):
                    desc = line.partition(":")[2].strip()
                    t_match = re.search(r"triggers?\s*[-–—]\s*(.+?)(?:\)|$)", desc, re.IGNORECASE)
                    if t_match:
                        triggers = [t.strip().lower() for t in t_match.group(1).split(",") if t.strip()]
                        for trigger in triggers:
                            trigger_owners[trigger].append(agent_file.stem)

    for trigger, owners in sorted(trigger_owners.items()):
        if len(owners) > 1:
            issues["triggers"].append(f"'{trigger}': {owners}")

    total_issues = sum(len(v) for v in issues.values())
    return {
        "issues": issues,
        "total_issues": total_issues,
        "clean": total_issues == 0,
    }


def _check_usage(src: Path) -> Dict[str, Any]:
    """Run content usage checks (mode/MCP mapping to TRIGGER_MAP)."""
    try:
        from superclaude.scripts.context_loader import COMPOSITE_FLAGS, TRIGGER_MAP
    except ImportError:
        return {"issues": ["Cannot import context_loader"], "clean": False}

    trigger_paths = {entry[1] for entry in TRIGGER_MAP}
    composite_paths = set()
    for files in COMPOSITE_FLAGS.values():
        for fp, _ in files:
            composite_paths.add(fp)
    all_mapped = trigger_paths | composite_paths

    issues = []

    # Check modes
    modes_dir = src / "modes"
    if modes_dir.exists():
        for mode_file in sorted(modes_dir.glob("MODE_*.md")):
            relative = f"modes/{mode_file.name}"
            if relative not in all_mapped:
                issues.append(f"Unmapped mode: {mode_file.name}")

    # Check MCP docs
    mcp_dir = src / "mcp"
    if mcp_dir.exists():
        for mcp_file in sorted(mcp_dir.glob("MCP_*.md")):
            relative = f"mcp/{mcp_file.name}"
            if relative not in all_mapped:
                issues.append(f"Unmapped MCP: {mcp_file.name}")

    # Check TRIGGER_MAP references exist
    for _, file_path, _ in TRIGGER_MAP:
        parts = file_path.split("/", 1)
        if len(parts) == 2:
            source_file = src / parts[0] / parts[1]
            if not source_file.exists():
                issues.append(f"TRIGGER_MAP dangling: {file_path}")

    # Check COMPOSITE_FLAGS references exist
    for flag, files in COMPOSITE_FLAGS.items():
        for file_path, _ in files:
            parts = file_path.split("/", 1)
            if len(parts) == 2:
                source_file = src / parts[0] / parts[1]
                if not source_file.exists():
                    issues.append(f"COMPOSITE_FLAGS[{flag}] dangling: {file_path}")

    return {
        "issues": issues,
        "total_issues": len(issues),
        "clean": len(issues) == 0,
    }


def run_audit(
    base_path: Path,
    verbose: bool = False,
    check: str = "all",
) -> Dict[str, Any]:
    """
    Run all harness integrity checks.

    Args:
        base_path: Installation base path
        verbose: Include detailed output
        check: Which check to run ("drift", "cross-refs", "usage", "all")

    Returns:
        Dict with results per check category and overall clean status.
    """
    src = _get_src_root()
    results = {}

    if check in ("drift", "all"):
        results["drift"] = verify_drift(base_path, verbose=verbose)

    if check in ("cross-refs", "all"):
        results["cross_refs"] = _check_cross_refs(src)

    if check in ("usage", "all"):
        results["usage"] = _check_usage(src)

    clean = all(r.get("clean", True) for r in results.values())
    results["clean"] = clean
    return results
