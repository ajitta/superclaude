#!/usr/bin/env python3
"""Dynamic Context Loader Hook (Python)

Detects triggers in user prompts and injects relevant context on-demand.
Runs as a UserPromptSubmit hook via stdin.

Modes:
  - Inject mode (default): Outputs context directly to stdout
  - Directive mode: Outputs <context-load/> for Claude to Read

v3.1 Features:
- Hybrid injection: Mode files → full .md, MCP files → short instructions
  (Serena + Tavily get full .md due to behavioral patterns)
- Composite flags: --frontend-verify (3 MCP), --all-mcp (8 MCP)
- --no-mcp: suppresses all mcp/ context loading
- Tightened TRIGGER_MAP regex (no generic single words)
- Session dedup via cache file, cross-platform compatible

v2.2.0: MCP fallback notification support
v2.1.0: Skills discovery and token estimation
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superclaude.scripts.token_estimator import TokenEstimate

# v2.2.0: MCP fallback notification support
try:
    from superclaude.hooks.mcp_fallback import MCP_FALLBACKS, check_mcp_and_notify

    MCP_FALLBACK_AVAILABLE = True
except ImportError:
    MCP_FALLBACK_AVAILABLE = False
    MCP_FALLBACKS = {}

# Configuration
INJECT_MODE = os.environ.get("CLAUDE_CONTEXT_INJECT", "1").lower() in ("1", "true", "yes")  # Default: inject
MAX_TOKENS_ESTIMATE = int(
    os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS", "8000")
)  # ~8K tokens
CHARS_PER_TOKEN = 4  # Rough estimate

# Session tracking file (unique per working directory, stored in user-private dir)
SESSION_ID = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
_CACHE_DIR = Path.home() / ".claude" / ".superclaude_hooks"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = _CACHE_DIR / f"claude_context_{SESSION_ID}.txt"


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
# NOTE: Avoid generic single words (edit, test, search, task, docs, debug, ui, etc.)
#       that cause false positives on normal coding prompts.
#       Use compound terms (e.g. "browser test" not "test") or explicit flags (--play).
TRIGGER_MAP = [
    # MCP servers - Priority 2 (operational guides: workflows, decision rules, integration patterns)
    (
        r"(serena|symbol ops|rename.?symbol|lsp|--serena|/sc:load|/sc:save)",
        "mcp/MCP_Serena.md",
        2,
    ),
    (
        r"(tavily|web search|news|fact.?check|/sc:research|--tavily)",
        "mcp/MCP_Tavily.md",
        1,
    ),
    (r"(--c7|--context7)", "mcp/MCP_Context7.md", 2),
    (r"(--seq|--sequential)", "mcp/MCP_Sequential.md", 2),
    (r"(--play|--playwright)", "mcp/MCP_Playwright.md", 2),
    (r"(--perf|--devtools)", "mcp/MCP_Chrome-DevTools.md", 2),
    (r"(--magic)", "mcp/MCP_Magic.md", 2),
    (r"(--morph|--morphllm)", "mcp/MCP_Morphllm.md", 2),
    # Business symbols - Priority 3
    (r"(business.?symbol|strategic.?symbol|business.?example|panel.?example|--structured)", "core/BUSINESS_SYMBOLS.md", 3),
    # Modes — retained where content provides unique behavioral/reference value
    (r"(--brainstorm|--bs)", "modes/MODE_Brainstorming.md", 1),
    (r"(--introspect|self.?analysis|analyze reasoning)", "modes/MODE_Introspection.md", 2),
    (r"(--task-manage)", "modes/MODE_Task_Management.md", 2),
    (r"(--uc|--ultracompressed|token.?efficient|--token-efficient|--safe-mode)", "modes/MODE_Token_Efficiency.md", 1),
    (r"(--orchestrate|multi.?tool|tool.?select|/sc:select-tool)", "modes/MODE_Orchestration.md", 2),
    (r"(--research|deep.?research|systematic.?investigation|/sc:research)", "modes/MODE_DeepResearch.md", 1),
    (r"(--business-panel|business.?panel|multi.?expert|strategic.?analysis|/sc:business-panel)", "modes/MODE_Business_Panel.md", 1),
]

# Pre-compile regex patterns for performance (P2)
TRIGGER_MAP = [
    (re.compile(pattern, re.IGNORECASE), path, priority)
    for pattern, path, priority in TRIGGER_MAP
]

# Composite flags: one flag → multiple context files
COMPOSITE_FLAGS = {
    "--frontend-verify": [
        ("mcp/MCP_Playwright.md", 1),
        ("mcp/MCP_Chrome-DevTools.md", 1),
        ("mcp/MCP_Serena.md", 2),
    ],
    "--all-mcp": [
        ("mcp/MCP_Serena.md", 1),
        ("mcp/MCP_Tavily.md", 1),
        ("mcp/MCP_Context7.md", 2),
        ("mcp/MCP_Sequential.md", 2),
        ("mcp/MCP_Playwright.md", 2),
        ("mcp/MCP_Chrome-DevTools.md", 2),
        ("mcp/MCP_Magic.md", 2),
        ("mcp/MCP_Morphllm.md", 2),
    ],
}

# v3.1: Hybrid Injection Map
# MCP files → short instructions (Claude already gets tool descriptions from MCP servers)
# Mode files → full .md injection (behavioral rules, symbol tables, tool matrices need complete content)
# Core files → short instructions (supplementary reference)
INSTRUCTION_MAP = {
    # All MCP docs use full .md injection (operational guides with workflows, decision rules, integration patterns)
    # Core supplementary
    "core/BUSINESS_SYMBOLS.md": (
        "Business symbols + expert selection: 🎯target 📈growth 💰financial ⚖️tradeoffs 🏆competitive 🌊blue-ocean. "
        "Includes expert domain mapping, discussion templates, and abbreviations."
    ),
}

# Environment variable to control instruction mode (default: enabled)
USE_INSTRUCTIONS = os.environ.get("CLAUDE_CONTEXT_USE_INSTRUCTIONS", "1") == "1"

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

    Compact single-line format to minimize attention budget dilution.
    Full skill details available via /sc:help.

    Args:
        skills: List of TokenEstimate objects

    Returns:
        Formatted skills summary string
    """
    if not skills:
        return ""

    skill_names = ", ".join(s.name for s in skills)
    total_full = sum(s.full_tokens for s in skills)
    return f"<!-- {len(skills)} skills installed ({skill_names}). ~{total_full} tokens full load. Use /sc:help for details. -->"


def get_loaded_contexts() -> set:
    """Read already-loaded contexts from session cache."""
    if CACHE_FILE.exists():
        return set(CACHE_FILE.read_text().strip().split("\n"))
    return set()


def mark_as_loaded(contexts: str | list[str]) -> None:
    """Mark context(s) as loaded in session cache. Accepts single or batch."""
    loaded = get_loaded_contexts()
    if isinstance(contexts, str):
        loaded.add(contexts)
    else:
        loaded.update(contexts)
    CACHE_FILE.write_text("\n".join(loaded))


def estimate_tokens(content: str) -> int:
    """Estimate token count from character count."""
    return len(content) // CHARS_PER_TOKEN


def check_triggers(prompt: str) -> list[tuple[str, int]]:
    """Check prompt against triggers and return contexts to load with priorities."""
    contexts_to_load = []
    loaded = get_loaded_contexts()
    prompt_lower = prompt.lower()

    # --no-mcp: suppress all MCP context loading
    no_mcp = bool(re.search(r"--no-mcp", prompt_lower))

    def _add_context(context_file: str, priority: int) -> None:
        if context_file in loaded:
            return
        if no_mcp and context_file.startswith("mcp/"):
            return
        contexts_to_load.append((context_file, priority))
        loaded.add(context_file)

    # Composite flags (one flag → multiple files)
    for flag, files in COMPOSITE_FLAGS.items():
        if flag in prompt_lower:
            for context_file, priority in files:
                _add_context(context_file, priority)

    # Standard trigger matching
    for pattern, context_file, priority in TRIGGER_MAP:
        if pattern.search(prompt_lower):
            _add_context(context_file, priority)

    # Batch write to cache (single I/O instead of per-context)
    if contexts_to_load:
        mark_as_loaded([ctx for ctx, _ in contexts_to_load])

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
    """Output context for triggered files.

    v3.1: Hybrid injection — MCP files use short instruction strings (Claude already
    has tool descriptions from MCP servers), Mode files inject full .md content
    (behavioral rules, symbol tables, tool matrices need complete content).
    Set CLAUDE_CONTEXT_USE_INSTRUCTIONS=0 to inject full .md files for everything.
    """
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
        # v3.1: Try instruction injection first (MCP + core only)
        if USE_INSTRUCTIONS and context_file in INSTRUCTION_MAP:
            instruction = INSTRUCTION_MAP[context_file]
            tokens = estimate_tokens(instruction)
            total_tokens += tokens
            loaded_files.append((context_file, tokens))
            print(f"<sc-context src=\"{context_file}\">")
            print(instruction)
            print("</sc-context>")
            print()
            continue

        # Fallback: full file injection for unmapped files
        file_path = BASE_PATH / context_file
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
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


# Execution flag patterns and their behavioral directives
_EXECUTION_DIRECTIVES = {
    re.compile(r"--iterations\s+(\d+)", re.IGNORECASE): (
        lambda m: f"<sc-directive flag=\"--iterations {m.group(1)}\">"
        f"Execute exactly {m.group(1)} improvement iterations. "
        f"After each iteration: state what changed. Do not stop early."
        f"</sc-directive>"
    ),
    re.compile(r"--loop\b", re.IGNORECASE): (
        lambda m: "<sc-directive flag=\"--loop\">"
        "Iterative improvement mode: execute → self-evaluate → identify gaps → re-execute. "
        "Repeat until no meaningful improvement. Report total iteration count when done."
        "</sc-directive>"
    ),
    re.compile(r"--concurrency\s+(\d+)", re.IGNORECASE): (
        lambda m: f"<sc-directive flag=\"--concurrency {m.group(1)}\">"
        f"Batch up to {m.group(1)} independent tool calls per message. "
        f"Group reads, searches, and other non-dependent operations together."
        f"</sc-directive>"
    ),
}


def _emit_execution_directives(prompt: str) -> None:
    """Emit inline behavioral directives for execution flags."""
    for pattern, directive_fn in _EXECUTION_DIRECTIVES.items():
        match = pattern.search(prompt)
        if match:
            print(directive_fn(match))
            print()


def _extract_prompt(stdin_data: str) -> str:
    """Extract prompt from UserPromptSubmit JSON input, with raw text fallback."""
    try:
        data = json.loads(stdin_data)
        return data.get("prompt", stdin_data)
    except (json.JSONDecodeError, TypeError):
        return stdin_data


def main() -> None:
    # Read and parse JSON input from Claude Code
    stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
    prompt = _extract_prompt(stdin_data)

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

    # Execution flag directives (inline behavioral hints — no file injection)
    _emit_execution_directives(prompt)

    # Check triggers and get contexts to load
    contexts = check_triggers(prompt)

    # --no-mcp notification
    if "--no-mcp" in prompt.lower():
        print("<!-- --no-mcp: MCP contexts suppressed. Using native tools + WebSearch. -->")
        print()

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
