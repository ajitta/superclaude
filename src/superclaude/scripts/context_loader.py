#!/usr/bin/env python3
"""Dynamic Context Loader Hook (Python)

Detects triggers and loads relevant MD files on-demand.
Supports two modes:
  - Directive mode (default): Outputs <context-load/> for Claude to Read
  - Inject mode: Directly outputs file content (deterministic)

Tracks loaded contexts per session to prevent duplicates.
Cross-platform compatible (Windows/macOS/Linux)

v2.1.0 Features:
- Skills discovery and token estimation
- Skill frontmatter loading for context visualization
"""

import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superclaude.scripts.token_estimator import TokenEstimate

# v2.2.0: MCP fallback notification support
try:
    from superclaude.hooks.mcp_fallback import check_mcp_and_notify, MCP_FALLBACKS
    MCP_FALLBACK_AVAILABLE = True
except ImportError:
    MCP_FALLBACK_AVAILABLE = False
    MCP_FALLBACKS = {}

# Configuration
INJECT_MODE = os.environ.get("CLAUDE_CONTEXT_INJECT", "1") == "1"  # Default: inject
MAX_TOKENS_ESTIMATE = int(
    os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS", "8000")
)  # ~8K tokens
CHARS_PER_TOKEN = 4  # Rough estimate

# Session tracking file (unique per working directory)
SESSION_ID = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
CACHE_FILE = Path(tempfile.gettempdir()) / f"claude_context_{SESSION_ID}.txt"

# Base path for context files
def _get_base_path() -> Path:
    """
    Get base path for context files.

    Priority:
    1. SUPERCLAUDE_PATH environment variable (explicit override)
    2. Project-local: ./.claude/superclaude (if exists)
    3. User scope: ~/.claude/superclaude (default)
    """
    if os.environ.get("SUPERCLAUDE_PATH"):
        return Path(os.environ["SUPERCLAUDE_PATH"])

    # Check project-local first
    project_path = Path.cwd() / ".claude" / "superclaude"
    if project_path.exists():
        return project_path

    # Fall back to user scope
    return Path.home() / ".claude" / "superclaude"

BASE_PATH = _get_base_path()

# Trigger → File mapping with priority (lower = higher priority)
# Format: (regex_pattern, relative_path, priority)
TRIGGER_MAP = [
    # Modes (detailed) - Priority 1-2
    (
        r"(brainstorm|ideate|explore(?: ideas)?|maybe|thinking about|discuss|not sure|--brainstorm|--bs)",
        "modes/MODE_Brainstorming.md",
        1,
    ),
    (
        r"(deep.?research|investigate(?: thoroughly)?|comprehensive search|/sc:research|--research|explore|discover|analyz)",
        "modes/MODE_DeepResearch.md",
        1,
    ),
    (
        r"(introspect|reflect|self.?analysis|meta|analyze reasoning|--introspect)",
        "modes/MODE_Introspection.md",
        2,
    ),
    (
        r"(orchestrat|coordinate|parallel|multi.?tool|batch|resource|efficiency|--orchestrate)",
        "modes/MODE_Orchestration.md",
        2,
    ),
    (
        r"(task|manage|task.?manage|delegate|milestone|phase|--task-manage)",
        "modes/MODE_Task_Management.md",
        2,
    ),
    (
        r"(--uc|--ultracompressed|token.?efficient|compress|brevity|efficient|token)",
        "modes/MODE_Token_Efficiency.md",
        1,
    ),
    (
        r"(business|panel|expert|strategy|business.?panel|expert.?panel|strategy.?panel|christensen|porter|drucker|godin|taleb)",
        "modes/MODE_Business_Panel.md",
        1,
    ),
    # MCP servers (detailed) - Priority 1-2
    (
        r"(context7|c7|library|docs|framework|documentation|import|require|library docs|framework docs|--c7|--context7)",
        "mcp/MCP_Context7.md",
        2,
    ),
    (
        r"(sequential|seq|think|think-hard|ultrathink|debug|architecture|analysis|reasoning|multi.?step|reasoning chain|--seq|--sequential)",
        "mcp/MCP_Sequential.md",
        2,
    ),
    (
        r"(playwright|browser|browser test|e2e|test|screenshot|validation|accessibility|wcag|--play|--playwright)",
        "mcp/MCP_Playwright.md",
        2,
    ),
    (
        r"(serena|symbol|rename|rename across|extract|move|lsp|session|memory|--serena|/sc:load|/sc:save)",
        "mcp/MCP_Serena.md",
        2,
    ),
    (
        r"(morphllm|morph|pattern|pattern replace|bulk|bulk edit|edit|transform|style|framework|text-replacement|--morph|--morphllm)",
        "mcp/MCP_Morphllm.md",
        2,
    ),
    (
        r"(magic|21st|ui component|ui|component|button|form|modal|card|table|nav|responsive|accessible|--magic|/ui|/21)",
        "mcp/MCP_Magic.md",
        2,
    ),
    (
        r"(tavily|search|research|news|current|web|fact-check|/sc:research|web search|news search|--tavily)",
        "mcp/MCP_Tavily.md",
        1,
    ),
    (
        r"(devtools|perf|performance|performance audit|layout|layout debug|cls|lcp|metrics|core web vitals|--perf|--devtools)",
        "mcp/MCP_Chrome-DevTools.md",
        2,
    ),
    (
        r"(mindbase|memory|conversation|conversation.?memory|session|semantic|embedding|pgvector|--mindbase)",
        "mcp/MCP_Mindbase.md",
        2,
    ),
    (
        r"(airis|confidence|confidence.?check|research|index|repo.?index|optimize|sync|--airis)",
        "mcp/MCP_Airis-Agent.md",
        2,
    ),
    # Business symbols/examples - Priority 3 (lower priority, supplementary)
    (r"(business.?symbol|strategic.?symbol)", "core/BUSINESS_SYMBOLS.md", 3),
    (r"(business.?example|panel.?example)", "core/BUSINESS_PANEL_EXAMPLES.md", 3),
]

# v2.1.0: Skills configuration
SHOW_SKILLS_SUMMARY = os.environ.get("CLAUDE_SHOW_SKILLS", "1") == "1"


def get_skill_estimates() -> list["TokenEstimate"]:
    """Get token estimates for all installed skills.

    Returns:
        List of TokenEstimate objects for all skills
    """
    try:
        from superclaude.scripts.token_estimator import get_all_skill_estimates

        return get_all_skill_estimates()
    except ImportError:
        return []


def format_skills_summary(skills: list["TokenEstimate"]) -> str:
    """Format skills summary for context output.

    Args:
        skills: List of TokenEstimate objects

    Returns:
        Formatted skills summary string
    """
    if not skills:
        return ""

    lines = ["<!-- Skills Available -->"]
    total_frontmatter = 0
    total_full = 0

    for skill in skills:
        total_frontmatter += skill.frontmatter_tokens
        total_full += skill.full_tokens
        lines.append(
            f"<!--   {skill.name}: ~{skill.frontmatter_tokens} tokens "
            f"(full: ~{skill.full_tokens}) -->"
        )

    lines.append(
        f"<!-- Skills Total: ~{total_frontmatter} frontmatter, "
        f"~{total_full} full load -->"
    )
    return "\n".join(lines)


def get_loaded_contexts() -> set:
    """Read already-loaded contexts from session cache."""
    if CACHE_FILE.exists():
        return set(CACHE_FILE.read_text().strip().split("\n"))
    return set()


def mark_as_loaded(context: str) -> None:
    """Mark a context as loaded in session cache."""
    loaded = get_loaded_contexts()
    loaded.add(context)
    CACHE_FILE.write_text("\n".join(loaded))


def estimate_tokens(content: str) -> int:
    """Estimate token count from character count."""
    return len(content) // CHARS_PER_TOKEN


def check_triggers(prompt: str) -> list[tuple[str, int]]:
    """Check prompt against triggers and return contexts to load with priorities."""
    contexts_to_load = []
    loaded = get_loaded_contexts()
    prompt_lower = prompt.lower()

    for pattern, context_file, priority in TRIGGER_MAP:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            if context_file not in loaded:
                contexts_to_load.append((context_file, priority))
                mark_as_loaded(context_file)

    # Sort by priority (lower number = higher priority)
    contexts_to_load.sort(key=lambda x: x[1])
    return contexts_to_load


def output_directive_mode(contexts: list[tuple[str, int]]) -> None:
    """Output <context-load/> directives for Claude to Read."""
    for context_file, _ in contexts:
        print(f'<context-load file="{BASE_PATH}/{context_file}"/>')

    if contexts:
        print()
        print("INSTRUCTION: Use Read tool to load the <context-load> files above.")
        print("These provide detailed guidance for the detected domain.")


def check_mcp_fallbacks(contexts: list[tuple[str, int]]) -> list[str]:
    """Check for MCP fallback notifications (first time only per session).

    Args:
        contexts: List of (context_file, priority) tuples

    Returns:
        List of notification strings to display
    """
    if not MCP_FALLBACK_AVAILABLE:
        return []

    notifications = []
    for context_file, _ in contexts:
        # Extract MCP name from path like "mcp/MCP_Morphllm.md"
        if context_file.startswith("mcp/MCP_"):
            mcp_name = context_file.replace("mcp/MCP_", "").replace(".md", "").lower()
            # Map special names
            name_map = {"chrome-devtools": "devtools"}
            mcp_name = name_map.get(mcp_name, mcp_name)

            if mcp_name in MCP_FALLBACKS:
                notification = check_mcp_and_notify(mcp_name)
                if notification:
                    notifications.append(notification)

    return notifications


def output_inject_mode(contexts: list[tuple[str, int]]) -> None:
    """Directly output file contents (deterministic, no Read dependency)."""
    total_tokens = 0
    loaded_files = []
    skipped_files = []

    # v2.2.0: Check MCP fallbacks first
    fallback_notifications = check_mcp_fallbacks(contexts)
    for notification in fallback_notifications:
        print(f"<!-- {notification} -->")
    if fallback_notifications:
        print()

    for context_file, priority in contexts:
        file_path = BASE_PATH / context_file
        if not file_path.exists():
            continue

        content = file_path.read_text(encoding="utf-8")
        tokens = estimate_tokens(content)

        # Check token budget
        if total_tokens + tokens > MAX_TOKENS_ESTIMATE:
            skipped_files.append((context_file, tokens, priority))
            continue

        total_tokens += tokens
        loaded_files.append((context_file, tokens))
        print(f'<context-inject file="{context_file}" tokens="~{tokens}">')
        print(content)
        print("</context-inject>")
        print()

    # Summary
    if loaded_files or skipped_files:
        print(
            f"<!-- Context loaded: {len(loaded_files)} files (~{total_tokens} tokens) -->"
        )
        if skipped_files:
            skipped_info = ", ".join(f"{f}(p{p})" for f, _, p in skipped_files)
            print(f"<!-- Skipped (budget): {skipped_info} -->")


def main():
    # Read prompt from stdin
    prompt = sys.stdin.read() if not sys.stdin.isatty() else ""

    if not prompt.strip():
        return

    # v2.1.0: Output skills summary if enabled
    if SHOW_SKILLS_SUMMARY:
        skills = get_skill_estimates()
        if skills:
            summary = format_skills_summary(skills)
            if summary:
                print(summary)
                print()

    # Check triggers and get contexts to load
    contexts = check_triggers(prompt)

    if not contexts:
        return

    # Output based on mode
    if INJECT_MODE:
        output_inject_mode(contexts)
    else:
        output_directive_mode(contexts)


if __name__ == "__main__":
    main()
    sys.exit(0)
