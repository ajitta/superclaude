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

v2.2.0 Features (Claude Code 2.1.20 Integration):
- Multi-directory CLAUDE.md support via --add-dir flag
- CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD environment variable
- Tech stack detection from multiple project directories
"""

import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, List

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
INJECT_MODE = os.environ.get("CLAUDE_CONTEXT_INJECT", "1") == "1"  # Default: inject
MAX_TOKENS_ESTIMATE = int(
    os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS", "8000")
)  # ~8K tokens
CHARS_PER_TOKEN = 4  # Rough estimate

# v2.2.0: Multi-directory CLAUDE.md support
ADDITIONAL_DIRS_ENABLED = (
    os.environ.get("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "0") == "1"
)

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
        r"(sequential|seq|--effort\s*(medium|high)|--think|--think-hard|--ultrathink|debug|architecture|analysis|reasoning|multi.?step|reasoning chain|--seq|--sequential)",
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
    # Note: PRINCIPLES.md removed - now loaded via CLAUDE_SC.md @-reference
]

# Pre-compile regex patterns for performance (P2)
TRIGGER_MAP = [
    (re.compile(pattern, re.IGNORECASE), path, priority)
    for pattern, path, priority in TRIGGER_MAP
]

# v3.0: Instruction Injection Map
# Short instruction strings (~25-80 tokens) replace full .md file injection (~500-750 tokens each)
# Claude already has MCP tool descriptions from servers; these provide behavioral guidance only.
# Full .md files remain source of truth; instructions are derived summaries.
INSTRUCTION_MAP = {
    # Modes - behavioral directives
    "modes/MODE_Brainstorming.md": (
        "Brainstorm mode: Socratic dialogue, probe assumptions, divergent→convergent thinking. "
        "Present alternatives before committing. No implementation until user confirms direction. "
        "Ask probing questions, challenge premises, explore edge cases."
    ),
    "modes/MODE_DeepResearch.md": (
        "Deep research mode: Plan→Search→Analyze→Synthesize. Multi-source triangulation. "
        "Every claim needs verification. Progressive drilling. Confidence scoring per finding. "
        "Citation-ready output. Question biases."
    ),
    "modes/MODE_Introspection.md": (
        "Introspection mode: Expose reasoning with markers — "
        "🤔thinking 🎯target ⚡action 📊metrics 💡insight. "
        "Show confidence levels, alternatives considered, and tradeoffs at each decision point."
    ),
    "modes/MODE_Orchestration.md": (
        "Orchestration mode: Choose most powerful tool per task. "
        "Identify independent ops for parallel execution. Wave→Checkpoint→Wave pattern. "
        "Resource-aware batching. Maximize concurrent operations."
    ),
    "modes/MODE_Task_Management.md": (
        "Task management mode: Plan→Phase→Task→Todo hierarchy. "
        "Use TaskCreate for 3+ steps. Persistent cross-session tracking via write_memory. "
        "Progressive enhancement. Dependency-aware sequencing."
    ),
    "modes/MODE_Token_Efficiency.md": (
        "Token efficiency mode: Symbol-enhanced communication. "
        "Context-aware abbreviation. Target 30-50% token reduction at ≥95% information quality. "
        "Compressed formatting, tables over prose, code over explanation."
    ),
    "modes/MODE_Business_Panel.md": (
        "Business panel mode: Multi-expert analysis with frameworks — "
        "Christensen(disruption) Porter(competition) Drucker(management) Godin(marketing) Taleb(risk). "
        "Adaptive interaction: strategic, innovation, risk debate, socratic."
    ),
    # MCP servers - tool awareness (Claude already has tool descriptions from MCP servers)
    "mcp/MCP_Context7.md": (
        "Context7 MCP: resolve-library-id → query-docs for official library documentation. "
        "Version-specific. Use for imports, framework patterns, API compliance."
    ),
    "mcp/MCP_Sequential.md": (
        "Sequential Thinking MCP: sequentialthinking tool for multi-step reasoning. "
        "Numbered thoughts, revision, branching. Use for debug, architecture, security, "
        "complex analysis with 3+ interconnected components."
    ),
    "mcp/MCP_Tavily.md": (
        "Tavily MCP: tavily_search (web queries), tavily_research (multi-source synthesis), "
        "tavily_extract (URL content), tavily_crawl (site crawling), tavily_map (URL discovery). "
        "Use for current info, news, fact-checking."
    ),
    "mcp/MCP_Playwright.md": (
        "Playwright MCP: Browser automation and E2E testing. Real rendering, screenshots, "
        "user journeys, WCAG accessibility. Use for login flows, forms, visual validation."
    ),
    "mcp/MCP_Serena.md": (
        "Serena MCP: Semantic code understanding — symbol ops, LSP, rename across codebase, "
        "dependency tracking, project memory. Use for large projects, architectural understanding."
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
    "mcp/MCP_Mindbase.md": (
        "Mindbase MCP: Semantic memory with pgvector. Auto-embedding, conversation persistence, "
        "cross-session memory, semantic search."
    ),
    "mcp/MCP_Airis-Agent.md": (
        "Airis MCP: airis_confidence_check (pre-implementation validation), "
        "airis_deep_research (comprehensive research), airis_repo_index (structure indexing)."
    ),
    # Core supplementary
    "core/BUSINESS_SYMBOLS.md": (
        "Business symbols: 🎯target 📈growth 💰financial ⚖️tradeoffs 🏆competitive 🌊blue-ocean. "
        "Use in business panel discussions for visual strategic communication."
    ),
    "core/BUSINESS_PANEL_EXAMPLES.md": (
        "Business panel examples: /sc:business-panel @file with modes — "
        "strategic, innovation, risk debate, socratic. Multi-perspective analysis patterns."
    ),
    # Note: PRINCIPLES.md removed - now loaded via CLAUDE_SC.md @-reference
}

# Environment variable to control instruction mode (default: enabled)
USE_INSTRUCTIONS = os.environ.get("CLAUDE_CONTEXT_USE_INSTRUCTIONS", "1") == "1"

# v2.1.0: Skills configuration
SHOW_SKILLS_SUMMARY = os.environ.get("CLAUDE_SHOW_SKILLS", "1") == "1"


def get_additional_claude_dirs() -> List[Path]:
    """
    Get additional directories containing CLAUDE.md files.

    Supports Claude Code 2.1.20's --add-dir flag feature.
    Requires CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 to be set.

    Returns:
        List of Path objects to additional directories with CLAUDE.md
    """
    if not ADDITIONAL_DIRS_ENABLED:
        return []

    additional_dirs: List[Path] = []

    # Check for CLAUDE_ADD_DIRS environment variable (comma-separated paths)
    add_dirs_env = os.environ.get("CLAUDE_ADD_DIRS", "")
    if add_dirs_env:
        for dir_path in add_dirs_env.split(","):
            dir_path = dir_path.strip()
            if dir_path:
                path = Path(dir_path).expanduser().resolve()
                if path.exists() and (path / "CLAUDE.md").exists():
                    additional_dirs.append(path)

    # Check for common monorepo patterns
    cwd = Path.cwd()

    # Look for workspace packages (monorepo pattern)
    for pattern in ["packages/*", "apps/*", "libs/*", "services/*"]:
        for subdir in cwd.glob(pattern):
            if subdir.is_dir() and (subdir / "CLAUDE.md").exists():
                additional_dirs.append(subdir)

    # Deduplicate while preserving order
    seen = set()
    unique_dirs = []
    for d in additional_dirs:
        if d not in seen:
            seen.add(d)
            unique_dirs.append(d)

    return unique_dirs


def load_additional_claude_md_content() -> str:
    """
    Load and combine CLAUDE.md content from additional directories.

    Returns:
        Combined content from all additional CLAUDE.md files
    """
    additional_dirs = get_additional_claude_dirs()
    if not additional_dirs:
        return ""

    contents = []
    for dir_path in additional_dirs:
        claude_md = dir_path / "CLAUDE.md"
        if claude_md.exists():
            try:
                content = claude_md.read_text(encoding="utf-8")
                contents.append(f"<!-- From {dir_path.name}/CLAUDE.md -->\n{content}")
            except (OSError, UnicodeDecodeError):
                continue

    if contents:
        header = f"<!-- Additional CLAUDE.md files loaded ({len(contents)} dirs) -->\n"
        return header + "\n\n".join(contents)
    return ""


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
        if pattern.search(prompt_lower):
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
    """Output context for triggered files.

    v3.0: Instruction injection mode (default) outputs short instruction strings
    instead of full file contents. ~86% token reduction for heavy sessions.
    Set CLAUDE_CONTEXT_USE_INSTRUCTIONS=0 to revert to full file injection.
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
        # v3.0: Try instruction injection first
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
