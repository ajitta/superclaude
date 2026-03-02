#!/usr/bin/env python3
"""Hybrid injection engine: full .md, compact instruction, or skill hint.

Takes matched triggers and outputs appropriate context format to stdout.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from superclaude.scripts.context_session import (
    BASE_PATH,
    MAX_TOKENS_ESTIMATE,
    SHOW_SKILLS_SUMMARY,
    USE_INSTRUCTIONS,
    estimate_tokens,
)
from superclaude.scripts.context_trigger_map import MatchedTrigger, TriggerCategory

if TYPE_CHECKING:
    from superclaude.scripts.token_estimator import TokenEstimate

# MCP fallback support
try:
    from superclaude.hooks.mcp_fallback import MCP_FALLBACKS, check_mcp_and_notify
    MCP_FALLBACK_AVAILABLE = True
except ImportError:
    MCP_FALLBACK_AVAILABLE = False
    MCP_FALLBACKS = {}

# --- Injection maps ---

# MCP files → short instructions (Claude already has tool descriptions from MCP servers)
MCP_INSTRUCTION_MAP: dict[str, str] = {
    "mcp/MCP_Context7.md": (
        "Context7 MCP: resolve-library-id → query-docs for official library documentation. "
        "Version-specific. Use for imports, framework patterns, API compliance."
    ),
    "mcp/MCP_Sequential.md": (
        "Sequential Thinking MCP: sequentialthinking tool for multi-step reasoning. "
        "Numbered thoughts, revision, branching. Use for debug, architecture, security, "
        "complex analysis with 3+ interconnected components."
    ),
    "mcp/MCP_Playwright.md": (
        "Playwright MCP: Browser automation and E2E testing. Real rendering, screenshots, "
        "user journeys, WCAG accessibility. Use for login flows, forms, visual validation."
    ),
    "mcp/MCP_Morphllm.md": (
        "Morphllm MCP: Pattern-based bulk code transformations. Style enforcement, "
        "framework updates. Fast Apply with 30-50% token savings. Best for <10 files, "
        "straightforward transforms. Not for semantic ops."
    ),
    "mcp/MCP_Magic.md": (
        "Magic MCP (21st.dev): Modern UI component generation. Accessible, design-system "
        "consistent. React/Vue/Angular. Use for production-ready buttons, forms, modals, cards."
    ),
    "mcp/MCP_Chrome-DevTools.md": (
        "Chrome DevTools MCP: Core Web Vitals — CLS, LCP, FID, TTFB. CPU/memory profiling, "
        "layout shift detection, render blocking analysis."
    ),
    # Serena, Tavily: NOT in map → full .md injection (behavioral patterns, integration flows)
}

# Mode files → compact instructions for NL triggers
MODE_COMPACT_MAP: dict[str, str] = {
    "modes/brainstorming.md": (
        "Brainstorming mode: Socratic probing questions, non-presumptive collaborative "
        "discovery. Synthesize insights into structured briefs. Never prescribe solutions "
        "before fully exploring the problem space."
    ),
    "modes/deep-research.md": (
        "Deep Research mode: Systematic investigation with evidence chains and inline citations. "
        "Activates deep-research-agent + Tavily search. Progressive: broad first, then drill. "
        "Every claim needs verification."
    ),
    "modes/introspection.md": (
        "Introspection mode: Self-analysis and reasoning transparency. Expose thinking chain, "
        "identify biases, track error patterns."
    ),
    "modes/orchestration.md": (
        "Orchestration mode: Multi-tool coordination and parallel execution. Batch independent "
        "operations, optimize tool selection matrix."
    ),
    "modes/task-management.md": (
        "Task Management mode: Progressive enhancement with delegation. Use TaskCreate/TaskUpdate "
        "for tracking. Delegate when >3 steps, >2 dirs, or >3 files."
    ),
    "modes/business-panel.md": (
        "Business Panel mode: Multi-expert synthesis (Christensen/disruption, Porter/competitive, "
        "Drucker/management, Godin/marketing, Taleb/risk). Use business symbols for analysis."
    ),
    # token-efficiency: NOT in compact map → always full .md (symbol/abbreviation table is essential)
}

# Core supplementary instructions
CORE_INSTRUCTION_MAP: dict[str, str] = {
    "core/BUSINESS_SYMBOLS.md": (
        "Business symbols + expert selection: 🎯target 📈growth 💰financial ⚖️tradeoffs 🏆competitive 🌊blue-ocean. "
        "Includes expert domain mapping, discussion templates, and abbreviations."
    ),
}

# Skill hints
SKILL_HINT_MAP: dict[str, str] = {
    "skills/hint:sc-confidence-check": (
        "INSTRUCTION: Use /sc-confidence-check skill before implementation. "
        "Assess: duplicates, architecture, docs, OSS refs, root cause."
    ),
}


def _resolve_injection_mode(trigger: MatchedTrigger) -> str:
    """Determine injection mode for a matched trigger.

    Returns: "full" | "compact" | "instruction" | "hint"

    Rules:
    - SKILL → "hint" (always)
    - MODE + explicit flag → "full"
    - MODE + NL + in MODE_COMPACT_MAP → "compact"
    - MODE + NL + not in MODE_COMPACT_MAP → "full" (token-efficiency etc.)
    - MCP + in MCP_INSTRUCTION_MAP → "instruction"
    - MCP + not in map → "full" (Serena, Tavily)
    - CORE → "instruction"
    """
    if trigger.category == TriggerCategory.SKILL:
        return "hint"

    if trigger.category == TriggerCategory.MODE:
        if trigger.is_explicit_flag:
            return "full"
        if trigger.context_file in MODE_COMPACT_MAP:
            return "compact"
        return "full"

    if trigger.category == TriggerCategory.MCP:
        if USE_INSTRUCTIONS and trigger.context_file in MCP_INSTRUCTION_MAP:
            return "instruction"
        return "full"

    if trigger.category == TriggerCategory.CORE:
        if trigger.context_file in CORE_INSTRUCTION_MAP:
            return "instruction"
        return "full"

    return "full"


def _check_mcp_fallbacks(matches: list[MatchedTrigger]) -> list[str]:
    """Check for MCP fallback notifications."""
    if not MCP_FALLBACK_AVAILABLE:
        return []

    notifications = []
    for trigger in matches:
        if trigger.context_file.startswith("mcp/MCP_"):
            mcp_name = trigger.context_file.replace("mcp/MCP_", "").replace(".md", "").lower()
            name_map = {"chrome-devtools": "devtools"}
            mcp_name = name_map.get(mcp_name, mcp_name)
            if mcp_name in MCP_FALLBACKS:
                notification = check_mcp_and_notify(mcp_name)
                if notification:
                    notifications.append(notification)
    return notifications


def get_skill_estimates() -> list["TokenEstimate"]:
    """Get token estimates for all installed skills."""
    try:
        from superclaude.scripts.token_estimator import get_all_skill_estimates
        return get_all_skill_estimates()
    except ImportError:
        return []


def format_skills_summary(skills: list["TokenEstimate"]) -> str:
    """Format skills summary for context output.

    Compact single-line format to minimize attention budget dilution.
    """
    if not skills:
        return ""
    skill_names = ", ".join(s.name for s in skills)
    total_full = sum(s.full_tokens for s in skills)
    return f"<!-- {len(skills)} skills installed ({skill_names}). ~{total_full} tokens full load. Use /sc:help for details. -->"


def generate_output(matches: list[MatchedTrigger], prompt: str = "") -> None:
    """Generate context injection output to stdout.

    Output formats by injection mode:
    - hint: plain text (skill hints)
    - instruction: <sc-context src="...">instruction</sc-context>
    - compact: <sc-context src="..." mode="compact">instruction</sc-context>
    - full: <context-inject file="..." tokens="~N">full content</context-inject>

    Token budget: skips lowest priority triggers when MAX_TOKENS exceeded.
    """
    total_tokens = 0
    loaded_files = []
    skipped_files = []

    # Skills summary (once per prompt)
    if SHOW_SKILLS_SUMMARY:
        skills = get_skill_estimates()
        if skills:
            summary = format_skills_summary(skills)
            if summary:
                print(summary)
                print()

    # MCP fallback notifications
    fallback_notifications = _check_mcp_fallbacks(matches)
    for notification in fallback_notifications:
        print(f"<!-- {notification} -->")
    if fallback_notifications:
        print()

    # --no-mcp notification
    if "--no-mcp" in prompt.lower():
        print("<!-- --no-mcp: MCP contexts suppressed. Using native tools + WebSearch. -->")
        print()

    for trigger in matches:
        mode = _resolve_injection_mode(trigger)

        if mode == "hint":
            hint = SKILL_HINT_MAP.get(trigger.context_file, "")
            if hint:
                tokens = estimate_tokens(hint)
                total_tokens += tokens
                loaded_files.append((trigger.context_file, tokens))
                print(hint)
            continue

        if mode == "instruction":
            instruction = (
                MCP_INSTRUCTION_MAP.get(trigger.context_file)
                or CORE_INSTRUCTION_MAP.get(trigger.context_file, "")
            )
            if instruction:
                tokens = estimate_tokens(instruction)
                total_tokens += tokens
                loaded_files.append((trigger.context_file, tokens))
                print(f'<sc-context src="{trigger.context_file}">')
                print(instruction)
                print("</sc-context>")
                print()
            continue

        if mode == "compact":
            instruction = MODE_COMPACT_MAP.get(trigger.context_file, "")
            if instruction:
                tokens = estimate_tokens(instruction)
                total_tokens += tokens
                loaded_files.append((trigger.context_file, tokens))
                print(f'<sc-context src="{trigger.context_file}" mode="compact">')
                print(instruction)
                print("</sc-context>")
                print()
            continue

        # mode == "full": read and inject full .md content
        file_path = BASE_PATH / trigger.context_file
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        tokens = estimate_tokens(content)

        if total_tokens + tokens > MAX_TOKENS_ESTIMATE:
            skipped_files.append((trigger.context_file, tokens, trigger.category.value))
            continue

        total_tokens += tokens
        loaded_files.append((trigger.context_file, tokens))
        print(f'<context-inject file="{trigger.context_file}" tokens="~{tokens}">')
        print(content)
        print("</context-inject>")
        print()

    # Summary
    if loaded_files or skipped_files:
        print(f"<!-- Context loaded: {len(loaded_files)} files (~{total_tokens} tokens) -->")
        if skipped_files:
            skipped_info = ", ".join(f"{f}(p{p})" for f, _, p in skipped_files)
            print(f"<!-- Skipped (budget): {skipped_info} -->")
