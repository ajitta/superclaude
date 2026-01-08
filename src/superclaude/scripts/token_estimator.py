"""Token Estimator for SuperClaude v2.1.0

Provides token estimation for skills, commands, and agents.
Supports frontmatter-only estimation for accurate /context display.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Token estimation ratio (characters per token)
CHARS_PER_TOKEN = 4


@dataclass
class TokenEstimate:
    """Token estimation result."""

    name: str
    type: Literal["skill", "command", "agent", "mode", "mcp"]
    frontmatter_tokens: int
    full_tokens: int
    file_count: int
    path: Path

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        return f"{self.name}: ~{self.frontmatter_tokens} tokens (full: ~{self.full_tokens})"


def estimate_tokens(content: str) -> int:
    """Estimate token count from content.

    Args:
        content: Text content to estimate

    Returns:
        Estimated token count
    """
    return len(content) // CHARS_PER_TOKEN


def extract_frontmatter(content: str) -> str:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Full markdown content

    Returns:
        Frontmatter text (without delimiters) or empty string
    """
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def estimate_skill_tokens(skill_dir: Path) -> TokenEstimate | None:
    """Estimate tokens for a skill directory.

    Args:
        skill_dir: Path to skill directory

    Returns:
        TokenEstimate or None if not a valid skill
    """
    if not skill_dir.is_dir():
        return None

    # Find manifest file
    manifest = None
    for name in ["SKILL.md", "skill.md"]:
        candidate = skill_dir / name
        if candidate.exists():
            manifest = candidate
            break

    if not manifest:
        return None

    # Read manifest
    content = manifest.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)

    # Count all files
    full_tokens = 0
    file_count = 0
    for file in skill_dir.glob("**/*"):
        if file.is_file() and file.suffix in {".md", ".ts", ".py", ".json"}:
            try:
                full_tokens += estimate_tokens(file.read_text(encoding="utf-8"))
                file_count += 1
            except (OSError, UnicodeDecodeError):
                pass

    return TokenEstimate(
        name=skill_dir.name,
        type="skill",
        frontmatter_tokens=estimate_tokens(frontmatter),
        full_tokens=full_tokens,
        file_count=file_count,
        path=skill_dir,
    )


def estimate_command_tokens(command_file: Path) -> TokenEstimate | None:
    """Estimate tokens for a command file.

    Args:
        command_file: Path to command .md file

    Returns:
        TokenEstimate or None if not valid
    """
    if not command_file.exists() or command_file.suffix != ".md":
        return None

    content = command_file.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)

    return TokenEstimate(
        name=command_file.stem,
        type="command",
        frontmatter_tokens=estimate_tokens(frontmatter),
        full_tokens=estimate_tokens(content),
        file_count=1,
        path=command_file,
    )


def estimate_agent_tokens(agent_file: Path) -> TokenEstimate | None:
    """Estimate tokens for an agent file.

    Args:
        agent_file: Path to agent .md file

    Returns:
        TokenEstimate or None if not valid
    """
    if not agent_file.exists() or agent_file.suffix != ".md":
        return None

    content = agent_file.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)

    return TokenEstimate(
        name=agent_file.stem,
        type="agent",
        frontmatter_tokens=estimate_tokens(frontmatter),
        full_tokens=estimate_tokens(content),
        file_count=1,
        path=agent_file,
    )


def get_skill_directories() -> list[Path]:
    """Get all skill directories to scan.

    Returns:
        List of skill base directories
    """
    return [
        Path.home() / ".claude" / "skills",
        Path.home() / ".claude" / "superclaude" / "skills",
        Path.cwd() / ".claude" / "skills",
    ]


def get_all_skill_estimates() -> list[TokenEstimate]:
    """Get token estimates for all installed skills.

    Returns:
        List of TokenEstimate objects for all skills
    """
    estimates = []
    seen_names: set[str] = set()

    for base in get_skill_directories():
        if not base.exists():
            continue

        for item in base.iterdir():
            if not item.is_dir() or item.name.startswith("_"):
                continue

            # Skip duplicates (prefer earlier in path order)
            canonical = item.name.replace("_", "-")
            if canonical in seen_names:
                continue

            estimate = estimate_skill_tokens(item)
            if estimate:
                seen_names.add(canonical)
                estimates.append(estimate)

    return sorted(estimates, key=lambda e: e.name)


def get_context_token_summary() -> dict:
    """Get a summary of token usage for context visualization.

    Returns:
        Dictionary with token summary by category
    """
    skills = get_all_skill_estimates()

    # Calculate totals
    skill_frontmatter = sum(s.frontmatter_tokens for s in skills)
    skill_full = sum(s.full_tokens for s in skills)

    return {
        "skills": {
            "count": len(skills),
            "frontmatter_tokens": skill_frontmatter,
            "full_tokens": skill_full,
            "items": [
                {
                    "name": s.name,
                    "frontmatter_tokens": s.frontmatter_tokens,
                    "full_tokens": s.full_tokens,
                }
                for s in skills
            ],
        },
        "total": {
            "frontmatter_tokens": skill_frontmatter,
            "full_tokens": skill_full,
        },
    }


def format_token_report(summary: dict) -> str:
    """Format token summary as human-readable report.

    Args:
        summary: Token summary dictionary

    Returns:
        Formatted report string
    """
    lines = ["📊 Token Estimation Report", ""]

    # Skills section
    skills = summary.get("skills", {})
    lines.append(f"Skills ({skills.get('count', 0)}):")
    lines.append(
        f"  Frontmatter: ~{skills.get('frontmatter_tokens', 0)} tokens"
    )
    lines.append(f"  Full load:   ~{skills.get('full_tokens', 0)} tokens")

    for item in skills.get("items", []):
        lines.append(
            f"    • {item['name']}: ~{item['frontmatter_tokens']} "
            f"(full: ~{item['full_tokens']})"
        )

    # Total
    lines.append("")
    total = summary.get("total", {})
    lines.append(
        f"Total: ~{total.get('frontmatter_tokens', 0)} tokens "
        f"(full: ~{total.get('full_tokens', 0)})"
    )

    return "\n".join(lines)
