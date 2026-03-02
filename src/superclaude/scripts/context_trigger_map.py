#!/usr/bin/env python3
"""Unified trigger map: skills > modes > MCP > core.

Consolidates trigger matching from context_loader.py TRIGGER_MAP and
skill_activator.py check_skill_triggers into a single priority system.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum

from superclaude.scripts.context_session import get_loaded_contexts, mark_as_loaded


class TriggerCategory(IntEnum):
    """Trigger categories in priority order (lower = higher priority)."""
    SKILL = 0
    MODE = 1
    MCP = 2
    CORE = 3


@dataclass
class MatchedTrigger:
    """A matched trigger with metadata for injection routing."""
    category: TriggerCategory
    context_file: str       # relative path (e.g., "modes/brainstorming.md")
    is_explicit_flag: bool  # --brainstorm (True) vs "brainstorm ideas" (False)

    @property
    def sort_key(self) -> tuple[int, int]:
        return (self.category.value, 0 if self.is_explicit_flag else 1)


# --- Trigger definitions ---
# Format: (regex_pattern, context_file, is_flag_pattern)
# NOTE: Avoid generic single words that cause false positives on normal coding prompts.

SKILL_TRIGGERS: list[tuple[str, str, bool]] = [
    # sc-confidence-check — explicit triggers only
    (r"(check confidence|confidence check|/sc-confidence-check|/confidence-check|--confidence)", "skills/hint:sc-confidence-check", True),
    (r"(am i ready|ready to start|verify before|before implementing|pre-implementation)", "skills/hint:sc-confidence-check", False),
    (r"(readiness check|readiness-check)", "skills/hint:sc-confidence-check", True),
    (r"(확인해줘|검증해줘|준비됐|시작하기 전)", "skills/hint:sc-confidence-check", False),
]

MODE_TRIGGERS: list[tuple[str, str, bool]] = [
    # Explicit flags (is_flag=True) → full .md injection
    (r"--brainstorm|--bs", "modes/brainstorming.md", True),
    (r"--research", "modes/deep-research.md", True),
    (r"--introspect", "modes/introspection.md", True),
    (r"--orchestrate", "modes/orchestration.md", True),
    (r"--task-manage", "modes/task-management.md", True),
    (r"--uc|--ultracompressed|--token-efficient|--safe-mode", "modes/token-efficiency.md", True),
    (r"--business-panel", "modes/business-panel.md", True),
    # Natural language triggers (is_flag=False) → compact injection
    (r"brainstorm|ideate|explore ideas", "modes/brainstorming.md", False),
    (r"deep.?research|investigate thoroughly|comprehensive search|/sc:research", "modes/deep-research.md", False),
    (r"introspect|self.?analysis|analyze reasoning", "modes/introspection.md", False),
    (r"orchestrat|coordinate|multi.?tool", "modes/orchestration.md", False),
    (r"task.?manage", "modes/task-management.md", False),
    (r"business.?panel|expert.?panel|strategy.?panel|christensen|porter|drucker|godin|taleb", "modes/business-panel.md", False),
    # token-efficiency: NL triggers also get full .md (symbol table is essential)
    (r"token.?efficient", "modes/token-efficiency.md", True),  # force is_flag=True
]

MCP_TRIGGERS: list[tuple[str, str, bool]] = [
    # Explicit flags
    (r"--c7|--context7", "mcp/MCP_Context7.md", True),
    (r"--seq|--sequential|--effort\s*(medium|high|max)", "mcp/MCP_Sequential.md", True),
    (r"--play|--playwright", "mcp/MCP_Playwright.md", True),
    (r"--serena|/sc:load|/sc:save", "mcp/MCP_Serena.md", True),
    (r"--morph|--morphllm", "mcp/MCP_Morphllm.md", True),
    (r"--magic|/ui|/21", "mcp/MCP_Magic.md", True),
    (r"--tavily|/sc:research", "mcp/MCP_Tavily.md", True),
    (r"--perf|--devtools", "mcp/MCP_Chrome-DevTools.md", True),
    # Natural language triggers
    (r"context7|c7|library docs|framework docs", "mcp/MCP_Context7.md", False),
    (r"sequential thinking|multi.?step reasoning|reasoning chain", "mcp/MCP_Sequential.md", False),
    (r"playwright|browser test|e2e|screenshot|wcag", "mcp/MCP_Playwright.md", False),
    (r"serena|symbol ops|rename.?symbol|lsp", "mcp/MCP_Serena.md", False),
    (r"morphllm|morph|pattern replace|bulk edit|bulk transform", "mcp/MCP_Morphllm.md", False),
    (r"magic|21st|ui component|design system", "mcp/MCP_Magic.md", False),
    (r"tavily|web search|news|fact.?check", "mcp/MCP_Tavily.md", False),
    (r"devtools|performance audit|layout shift|core web vitals|\bcls\b|\blcp\b|\bfid\b|\bttfb\b", "mcp/MCP_Chrome-DevTools.md", False),
]

CORE_TRIGGERS: list[tuple[str, str, bool]] = [
    (r"business.?symbol|strategic.?symbol|business.?example|panel.?example|--structured", "core/BUSINESS_SYMBOLS.md", False),
    (r"research.?config|hop.?config|research.?depth|deep.?research.?config", "modes/research-config.md", False),
]

# Pre-compile all trigger patterns
_COMPILED_TRIGGERS: list[tuple[re.Pattern, str, bool, TriggerCategory]] = []
for _triggers, _category in [
    (SKILL_TRIGGERS, TriggerCategory.SKILL),
    (MODE_TRIGGERS, TriggerCategory.MODE),
    (MCP_TRIGGERS, TriggerCategory.MCP),
    (CORE_TRIGGERS, TriggerCategory.CORE),
]:
    for _pattern, _file, _is_flag in _triggers:
        _COMPILED_TRIGGERS.append(
            (re.compile(_pattern, re.IGNORECASE), _file, _is_flag, _category)
        )

# Composite flags: one flag → multiple context files
COMPOSITE_FLAGS: dict[str, list[tuple[str, TriggerCategory]]] = {
    "--frontend-verify": [
        ("mcp/MCP_Playwright.md", TriggerCategory.MCP),
        ("mcp/MCP_Chrome-DevTools.md", TriggerCategory.MCP),
        ("mcp/MCP_Serena.md", TriggerCategory.MCP),
    ],
    "--all-mcp": [
        ("mcp/MCP_Context7.md", TriggerCategory.MCP),
        ("mcp/MCP_Sequential.md", TriggerCategory.MCP),
        ("mcp/MCP_Playwright.md", TriggerCategory.MCP),
        ("mcp/MCP_Serena.md", TriggerCategory.MCP),
        ("mcp/MCP_Morphllm.md", TriggerCategory.MCP),
        ("mcp/MCP_Magic.md", TriggerCategory.MCP),
        ("mcp/MCP_Tavily.md", TriggerCategory.MCP),
        ("mcp/MCP_Chrome-DevTools.md", TriggerCategory.MCP),
    ],
}


def match_triggers(prompt: str) -> list[MatchedTrigger]:
    """Unified trigger matching.

    Processing order:
    1. --no-mcp check (suppress entire MCP category)
    2. Composite flag expansion (--frontend-verify, --all-mcp)
    3. SKILL -> MODE -> MCP -> CORE pattern matching
    4. Session cache dedup (context_session.get_loaded_contexts)
    5. Same-file flag+NL dedup (flag wins)
    6. Sort by (category, is_explicit_flag)

    Returns:
        list[MatchedTrigger] sorted by priority
    """
    prompt_lower = prompt.lower()
    no_mcp = bool(re.search(r"--no-mcp", prompt_lower))

    loaded = get_loaded_contexts()
    matches: dict[str, MatchedTrigger] = {}  # context_file -> best match

    def _add_match(context_file: str, category: TriggerCategory, is_flag: bool) -> None:
        if context_file in loaded:
            return
        if no_mcp and category == TriggerCategory.MCP:
            return

        existing = matches.get(context_file)
        if existing is None:
            matches[context_file] = MatchedTrigger(category, context_file, is_flag)
        elif is_flag and not existing.is_explicit_flag:
            # Flag wins over NL for same file
            matches[context_file] = MatchedTrigger(category, context_file, is_flag)

    # Composite flags
    for flag, files in COMPOSITE_FLAGS.items():
        if flag in prompt_lower:
            for context_file, category in files:
                _add_match(context_file, category, is_flag=True)

    # Standard trigger matching
    for pattern, context_file, is_flag, category in _COMPILED_TRIGGERS:
        if pattern.search(prompt_lower):
            _add_match(context_file, category, is_flag)

    result = sorted(matches.values(), key=lambda m: m.sort_key)

    # Batch mark as loaded
    if result:
        mark_as_loaded([m.context_file for m in result])

    return result
