#!/usr/bin/env python3
"""Dynamic Context Loader Hook (Python)

Detects triggers and loads relevant MD files on-demand.
Supports two modes:
  - Directive mode (default): Outputs <context-load/> for Claude to Read
  - Inject mode: Directly outputs file content (deterministic)

Tracks loaded contexts per session to prevent duplicates.
Cross-platform compatible (Windows/macOS/Linux)
"""
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

# Configuration
INJECT_MODE = os.environ.get("CLAUDE_CONTEXT_INJECT", "1") == "1"  # Default: inject
MAX_TOKENS_ESTIMATE = int(os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS", "8000"))  # ~8K tokens
CHARS_PER_TOKEN = 4  # Rough estimate

# Session tracking file (unique per working directory)
SESSION_ID = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
CACHE_FILE = Path(tempfile.gettempdir()) / f"claude_context_{SESSION_ID}.txt"

# Base path for context files
BASE_PATH = Path(".claude/superclaude")

# Trigger → File mapping with priority (lower = higher priority)
# Format: (regex_pattern, relative_path, priority)
TRIGGER_MAP = [
    # Modes (detailed) - Priority 1-2
    (r"(brainstorm|ideate|explore ideas|maybe|thinking about)", "modes/MODE_Brainstorming.md", 1),
    (r"(deep.?research|investigate thoroughly|comprehensive search)", "modes/MODE_DeepResearch.md", 1),
    (r"(introspect|reflect|self.?analysis|meta)", "modes/MODE_Introspection.md", 2),
    (r"(orchestrat|parallel|multi.?tool|batch)", "modes/MODE_Orchestration.md", 2),
    (r"(task.?manage|delegate|milestone|phase)", "modes/MODE_TaskManagement.md", 2),
    (r"(--uc|ultracompressed|token.?efficient|compress)", "modes/MODE_TokenEfficiency.md", 1),
    (r"(business.?panel|expert.?panel|strategy.?panel)", "modes/MODE_BusinessPanel.md", 1),

    # MCP servers (detailed) - Priority 1-2
    (r"(context7|c7|library docs|framework docs|--c7)", "mcp/MCP_Context7.md", 2),
    (r"(sequential|seq|multi.?step|reasoning chain|--seq)", "mcp/MCP_Sequential.md", 2),
    (r"(playwright|browser test|e2e|screenshot|--play)", "mcp/MCP_Playwright.md", 2),
    (r"(serena|symbol|rename across|lsp|--serena)", "mcp/MCP_Serena.md", 2),
    (r"(morphllm|morph|bulk edit|pattern replace|--morph)", "mcp/MCP_Morphllm.md", 2),
    (r"(magic|21st|ui component|--magic)", "mcp/MCP_Magic.md", 2),
    (r"(tavily|web search|news search|--tavily)", "mcp/MCP_Tavily.md", 1),
    (r"(devtools|chrome|performance audit|layout debug|--chrome)", "mcp/MCP_Chrome-DevTools.md", 2),

    # Agents - Priority 3 (loaded via Task tool typically)
    (r"(frontend|react|vue|css|accessibility|a11y)", "agents/frontend-architect.md", 3),
    (r"(backend|api|database|security|auth)", "agents/backend-architect.md", 3),
    (r"(architect|system design|scalability|boundary)", "agents/system-architect.md", 3),
    (r"(security|owasp|vulnerability|pentest)", "agents/security-engineer.md", 3),
    (r"(test|quality|coverage|edge case)", "agents/quality-engineer.md", 3),
    (r"(devops|ci.?cd|kubernetes|terraform|docker)", "agents/devops-architect.md", 3),
    (r"(refactor|tech.?debt|solid|clean code)", "agents/refactoring-expert.md", 3),
    (r"(debug|root cause|hypothesis|bisect)", "agents/root-cause-analyst.md", 3),
    (r"(performance|optimize|profil|bottleneck)", "agents/performance-engineer.md", 3),

    # Business - Priority 2
    (r"(business|strategy|market|competitive)", "core/BUSINESS_PANEL.md", 2),
]


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


def output_inject_mode(contexts: list[tuple[str, int]]) -> None:
    """Directly output file contents (deterministic, no Read dependency)."""
    total_tokens = 0
    loaded_files = []
    skipped_files = []

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
        print(f"<!-- Context loaded: {len(loaded_files)} files (~{total_tokens} tokens) -->")
        if skipped_files:
            skipped_info = ", ".join(f"{f}(p{p})" for f, _, p in skipped_files)
            print(f"<!-- Skipped (budget): {skipped_info} -->")


def main():
    # Read prompt from stdin
    prompt = sys.stdin.read() if not sys.stdin.isatty() else ""

    if not prompt.strip():
        return

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
