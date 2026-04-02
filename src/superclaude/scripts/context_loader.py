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

import difflib
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
    # Core supplementary
    "core/BUSINESS_SYMBOLS.md": (
        "Business symbols + expert selection: 🎯target 📈growth 💰financial ⚖️tradeoffs 🏆competitive 🌊blue-ocean. "
        "Includes expert domain mapping, discussion templates, and abbreviations."
    ),
    # Behavioral MCPs — longer instructions (these need workflow + decision rules)
    "mcp/MCP_Serena.md": (
        "Serena: symbol-level code operations (find_symbol, replace_symbol_body, get_symbols_overview, "
        "insert_before/after_symbol, find_referencing_symbols, rename_symbol). "
        "Workflow: get_symbols_overview → find_symbol(name_path, include_body=True) → edit. "
        "Use search_for_pattern when symbol name is unknown. "
        "Decision: symbol meaning (references, types, rename) → Serena; text patterns (strings, regex) → native Grep/Edit. "
        "Memory: activate_project → list_memories → read_memory for cross-session context. "
        "Prioritize symbolic tools over full file reads."
    ),
    "mcp/MCP_Tavily.md": (
        "Tavily MCP: tavily_search (web search with domain/time filtering), tavily_extract (full-text from URLs), "
        "tavily_research (multi-source synthesis), tavily_crawl (site-wide extraction), tavily_map (URL discovery). "
        "Use for current info post-knowledge-cutoff, multi-source research, fact-checking. "
        "Fallback: native WebSearch for simple queries, WebFetch for single pages."
    ),
    # Tool MCPs — shorter instructions (Claude already has tool descriptions from MCP servers)
    "mcp/MCP_Context7.md": (
        "Context7: 2-step library docs lookup. "
        "Step 1: resolve-library-id (name → ID). Step 2: query-docs (ID + query → docs). "
        "Never skip step 1. Default 10K tokens/query. Pin version: /org/project/version."
    ),
    "mcp/MCP_Sequential.md": (
        "Sequential: multi-step reasoning chain (thought, thoughtNumber, totalThoughts, nextThoughtNeeded). "
        "Branch with branchFromThought+branchId. Revise with isRevision+revisesThought. "
        "Use for: 3+ component problems, root cause analysis, trade-off evaluation."
    ),
    "mcp/MCP_Playwright.md": (
        "Playwright: browser E2E automation. Pattern: navigate → interact → assert. "
        "Prefer CSS selectors, waitForSelector for async. Screenshot on failure. "
        "Combine with DevTools for performance + visual testing."
    ),
    "mcp/MCP_Chrome-DevTools.md": (
        "Chrome DevTools: performance profiling and Core Web Vitals (CLS, LCP, INP). "
        "Workflow: start trace → reproduce → stop trace → analyze insights. "
        "Use lighthouse_audit for scores, take_screenshot for visual validation."
    ),
    "mcp/MCP_Magic.md": (
        "Magic 21st.dev: UI component library. Search → preview → customize → integrate. "
        "Focus on React components, design system tokens, responsive patterns."
    ),
    "mcp/MCP_Morphllm.md": (
        "Morphllm: bulk code transforms via pattern matching. Multi-file edits for: "
        "rename across codebase, pattern migration, API signature updates."
    ),
}

# v3.2: Tier 0 — 1-line summaries for tool MCPs (Claude already has tool descriptions)
# Behavioral MCPs (Serena, Tavily) are NOT here — they use INSTRUCTION_MAP (Tier 1)
TIER_0_MAP = {
    "mcp/MCP_Context7.md": "Context7: resolve-library-id first, then query-docs. Never skip step 1.",
    "mcp/MCP_Sequential.md": "Sequential: multi-step reasoning chain. Use for 3+ component problems.",
    "mcp/MCP_Playwright.md": "Playwright: browser E2E automation. navigate → interact → assert.",
    "mcp/MCP_Chrome-DevTools.md": "DevTools: performance profiling. trace → reproduce → analyze Core Web Vitals.",
    "mcp/MCP_Magic.md": "Magic 21st.dev: UI component search → customize → integrate.",
    "mcp/MCP_Morphllm.md": "Morphllm: bulk pattern-based multi-file code transforms.",
    "core/BUSINESS_SYMBOLS.md": "Business symbols + expert selection. 🎯📈💰⚖️🏆🌊 domain mapping.",
}

# Behavioral MCPs that need Tier 1 (INSTRUCTION_MAP), not Tier 0
_BEHAVIORAL_MCPS = {"mcp/MCP_Serena.md", "mcp/MCP_Tavily.md"}

# Environment variable to control instruction mode (default: enabled)
USE_INSTRUCTIONS = os.environ.get("CLAUDE_CONTEXT_USE_INSTRUCTIONS", "1") == "1"

# Flag alias/fuzzy matching system
# Maps common typos, conceptual aliases, and truncations to valid flags
FLAG_ALIASES: dict[str, list[str]] = {
    # Conceptual aliases
    "ultrathink": ["seq"],
    "think": ["seq"],
    "think-hard": ["seq"],
    "parallel": ["delegate"],
    "agent": ["delegate"],
    # Typo corrections
    "parellel": ["delegate"],
    "conccurrency": ["concurrency"],
    "confidenc-check": ["validate"],
    "confidence-check": ["validate"],
    "iteration": ["iterations"],
    "loo": ["loop"],
    "sea": ["serena"],
    "sampling": ["vs"],
    "verbalized": ["vs"],
}

# All valid flags for fuzzy matching fallback
VALID_FLAGS = {
    "brainstorm", "business-panel", "research", "introspect", "task-manage",
    "orchestrate", "token-efficient", "c7", "context7", "seq", "sequential",
    "magic", "morph", "morphllm", "serena", "play", "playwright", "perf",
    "devtools", "tavily", "tvly", "frontend-verify", "all-mcp", "no-mcp",
    "delegate", "concurrency", "loop", "iterations", "validate", "safe-mode",
    "fast", "plan", "uc", "ultracompressed", "scope", "focus",
    "bs", "verbose-context", "vs",
}


def resolve_flags(prompt: str) -> tuple[str, list[str]]:
    """Resolve flag aliases and typos in a prompt.

    Returns:
        Tuple of (corrected_prompt, list of notification messages)
    """
    notifications: list[str] = []
    corrected = prompt

    # Find all --flag patterns (flags may have values after them)
    flag_pattern = re.compile(r"--([a-zA-Z][\w-]*)")
    for match in flag_pattern.finditer(prompt):
        flag = match.group(1).lower()

        # Skip already-valid flags
        if flag in VALID_FLAGS:
            continue

        # Check alias table
        if flag in FLAG_ALIASES:
            replacements = FLAG_ALIASES[flag]
            replacement_str = " ".join(f"--{r}" for r in replacements)
            corrected = corrected.replace(f"--{match.group(1)}", replacement_str, 1)
            notifications.append(
                f"--{flag} → auto-corrected to {replacement_str} (alias)"
            )
            continue

        # Fuzzy match fallback (Levenshtein distance ≤ 2)
        close = difflib.get_close_matches(flag, VALID_FLAGS, n=3, cutoff=0.6)
        if close:
            suggestions = ", ".join(f"--{c}" for c in close)
            notifications.append(
                f"--{flag} is not a recognized flag. Did you mean: {suggestions}?"
            )

    return corrected, notifications

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


def _get_injection_tier(context_file: str, verbose: bool) -> int:
    """Determine injection tier for a context file.

    Returns:
        0 = 1-line hint (tool MCPs, core)
        1 = compact instruction (behavioral MCPs via INSTRUCTION_MAP)
        2 = full .md (modes, --verbose-context, unmapped)
    """
    if verbose or not USE_INSTRUCTIONS:
        return 2
    if context_file.startswith("modes/"):
        return 2  # Modes always need full behavioral content
    if context_file in _BEHAVIORAL_MCPS:
        return 1  # Serena, Tavily need operational instructions
    if context_file in TIER_0_MAP:
        return 0  # Tool MCPs get 1-line hints
    if context_file in INSTRUCTION_MAP:
        return 1  # Anything else in INSTRUCTION_MAP gets Tier 1
    return 2  # Unmapped files get full injection


def output_inject_mode(contexts: list[tuple[str, int]], prompt: str = "") -> None:
    """Output context for triggered files.

    v3.1: Hybrid injection — MCP files use short instruction strings (Claude already
    has tool descriptions from MCP servers), Mode files inject full .md content
    (behavioral rules, symbol tables, tool matrices need complete content).
    v3.2: --verbose-context forces full .md injection for all contexts.
    Set CLAUDE_CONTEXT_USE_INSTRUCTIONS=0 to inject full .md files for everything.
    """
    total_tokens = 0
    loaded_files = []
    skipped_files = []

    # v3.2: --verbose-context overrides INSTRUCTION_MAP (force full .md)
    verbose = bool(re.search(r"--verbose-context", prompt, re.IGNORECASE))

    # v2.2.0: Check MCP fallbacks first
    fallback_notifications = check_mcp_fallbacks(contexts)
    for notification in fallback_notifications:
        print(f"<!-- {notification} -->")
    if fallback_notifications:
        print()

    for context_file, priority in contexts:
        tier = _get_injection_tier(context_file, verbose)

        # Tier 0: 1-line hint (tool MCPs, core)
        if tier == 0 and context_file in TIER_0_MAP:
            hint = TIER_0_MAP[context_file]
            tokens = estimate_tokens(hint)
            total_tokens += tokens
            loaded_files.append((context_file, tokens))
            print(f'<sc-context-hint src="{context_file}">{hint}</sc-context-hint>')
            print()
            continue

        # Tier 1: compact instruction (behavioral MCPs, core with INSTRUCTION_MAP)
        if tier <= 1 and context_file in INSTRUCTION_MAP:
            instruction = INSTRUCTION_MAP[context_file]
            tokens = estimate_tokens(instruction)
            total_tokens += tokens
            loaded_files.append((context_file, tokens))
            print(f'<sc-context src="{context_file}">')
            print(instruction)
            print("</sc-context>")
            print()
            continue

        # Tier 2: full .md injection (modes, --verbose-context, unmapped files)
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
            skipped_names = ", ".join(f for f, _, _ in skipped_files)
            print(f"<!-- ⚠️ Budget exceeded: skipped {skipped_names} -->")


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
    re.compile(r"--tvly\b", re.IGNORECASE): (
        lambda m: "<sc-directive flag=\"--tvly\">"
        "Use Tavily CLI (`tvly` command) via Bash instead of Tavily MCP tools. "
        "Prefer: tvly search, tvly extract, tvly crawl, tvly map, tvly research run. "
        "Use --json for structured output, -o for file output."
        "</sc-directive>"
    ),
    re.compile(r"--serena\b", re.IGNORECASE): (
        lambda _: "<sc-directive flag=\"--serena\">"
        "Serena-first code exploration: prefer symbolic tools over Read/Grep for code files. "
        "1) get_symbols_overview before Read, 2) find_symbol(include_body=True) for specific functions, "
        "3) search_for_pattern instead of Grep, 4) find_referencing_symbols instead of Grep for usage tracing. "
        "Reserve Read for non-code files or when full file context is needed."
        "</sc-directive>"
    ),
    re.compile(r"--plan\b", re.IGNORECASE): (
        lambda _: "<sc-directive flag=\"--plan\">"
        "Lightweight planning mode: before implementing, generate a concise 5-line plan "
        "(goal, approach, files to change, risks, verification). "
        "Present the plan and wait for user approval before proceeding with implementation."
        "</sc-directive>"
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

    if not prompt or not prompt.strip():
        return

    # v3.2: Resolve flag aliases and typos before processing
    prompt, flag_notifications = resolve_flags(prompt)
    if flag_notifications:
        for note in flag_notifications:
            print(f"<!-- SuperClaude flag: {note} -->")
        print()

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
        output_inject_mode(contexts, prompt=prompt)
    else:
        output_directive_mode(contexts)


if __name__ == "__main__":
    main()
    sys.exit(0)
