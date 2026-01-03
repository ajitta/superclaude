#!/usr/bin/env python3
"""Dynamic Context Loader Hook (Python)
Detects triggers and loads relevant MD files on-demand.
Tracks loaded contexts per session to prevent duplicates.
Cross-platform compatible (Windows/macOS/Linux)
"""
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

# Session tracking file (unique per working directory)
SESSION_ID = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
CACHE_FILE = Path(tempfile.gettempdir()) / f"claude_context_{SESSION_ID}.txt"

# Trigger → File mapping
# Format: (regex_pattern, relative_path_from_.claude/superclaude/)
TRIGGER_MAP = [
    # Modes (detailed)
    (r"(brainstorm|ideate|explore ideas|maybe|thinking about)", "modes/MODE_Brainstorming.md"),
    (r"(deep.?research|investigate thoroughly|comprehensive search)", "modes/MODE_DeepResearch.md"),
    (r"(introspect|reflect|self.?analysis|meta)", "modes/MODE_Introspection.md"),
    (r"(orchestrat|parallel|multi.?tool|batch)", "modes/MODE_Orchestration.md"),
    (r"(task.?manage|delegate|milestone|phase)", "modes/MODE_TaskManagement.md"),
    (r"(--uc|ultracompressed|token.?efficient|compress)", "modes/MODE_TokenEfficiency.md"),
    (r"(business.?panel|expert.?panel|strategy.?panel)", "modes/MODE_BusinessPanel.md"),

    # MCP servers (detailed)
    (r"(context7|c7|library docs|framework docs|--c7)", "mcp/MCP_Context7.md"),
    (r"(sequential|seq|multi.?step|reasoning chain|--seq)", "mcp/MCP_Sequential.md"),
    (r"(playwright|browser test|e2e|screenshot|--play)", "mcp/MCP_Playwright.md"),
    (r"(serena|symbol|rename across|lsp|--serena)", "mcp/MCP_Serena.md"),
    (r"(morphllm|morph|bulk edit|pattern replace|--morph)", "mcp/MCP_Morphllm.md"),
    (r"(magic|21st|ui component|--magic)", "mcp/MCP_Magic.md"),
    (r"(tavily|web search|news search|--tavily)", "mcp/MCP_Tavily.md"),
    (r"(devtools|chrome|performance audit|layout debug|--chrome)", "mcp/MCP_Chrome-DevTools.md"),

    # Agents (loaded via Task tool, but can be pre-loaded for reference)
    (r"(frontend|react|vue|css|accessibility|a11y)", "agents/frontend-architect.md"),
    (r"(backend|api|database|security|auth)", "agents/backend-architect.md"),
    (r"(architect|system design|scalability|boundary)", "agents/system-architect.md"),
    (r"(security|owasp|vulnerability|pentest)", "agents/security-engineer.md"),
    (r"(test|quality|coverage|edge case)", "agents/quality-engineer.md"),
    (r"(devops|ci.?cd|kubernetes|terraform|docker)", "agents/devops-architect.md"),
    (r"(refactor|tech.?debt|solid|clean code)", "agents/refactoring-expert.md"),
    (r"(debug|root cause|hypothesis|bisect)", "agents/root-cause-analyst.md"),
    (r"(performance|optimize|profil|bottleneck)", "agents/performance-engineer.md"),

    # Business
    (r"(business|strategy|market|competitive)", "core/BUSINESS_PANEL.md"),
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


def check_triggers(prompt: str) -> list[str]:
    """Check prompt against triggers and return contexts to load."""
    contexts_to_load = []
    loaded = get_loaded_contexts()
    prompt_lower = prompt.lower()

    for pattern, context_file in TRIGGER_MAP:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            if context_file not in loaded:
                contexts_to_load.append(context_file)
                mark_as_loaded(context_file)

    return contexts_to_load


def main():
    # Read prompt from stdin
    prompt = sys.stdin.read() if not sys.stdin.isatty() else ""

    if not prompt.strip():
        return

    # Check triggers and get contexts to load
    contexts = check_triggers(prompt)

    # Output loading directives
    for context in contexts:
        print(f"<context-load file=\".claude/superclaude/{context}\"/>")

    # If any contexts were loaded, add instruction
    if contexts:
        print()
        print("INSTRUCTION: Use Read tool to load the <context-load> files above.")
        print("These provide detailed guidance for the detected domain.")


if __name__ == "__main__":
    main()
    sys.exit(0)
