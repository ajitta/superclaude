#!/usr/bin/env python3
"""Dynamic Context Loader Hook (Python)

Detects triggers in user prompts and injects relevant context on-demand.
Runs as a UserPromptSubmit hook via stdin.

Modes:
  - Inject mode (default): Outputs context directly to stdout
  - Directive mode: Outputs <context-load/> for Claude to Read

v3.1 Features:
- Hybrid injection: Mode files → full .md, MCP files → short instructions
  (Serena + Tavily get Tier 1 INSTRUCTION_MAP strings due to behavioral patterns)
- Composite flags: --frontend-verify (3 MCP), --all-mcp (6 MCP)
- --no-mcp: suppresses all mcp/ context loading
- Tightened TRIGGER_MAP regex (no generic single words)
- Session dedup via cache file, cross-platform compatible

v2.2.0: MCP fallback notification support
v2.1.0: Skills discovery and token estimation
"""

import difflib
import json
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superclaude.scripts.token_estimator import TokenEstimate

# Scope-aware path resolution. Imported unconditionally: superclaude.utils is
# stdlib-only, and hooks.json runs these scripts with the installer's own
# interpreter ({{PYTHON_BIN}} = sys.executable), which has the package. Silently
# degrading here would put state and content lookups in the wrong scope.
from superclaude.utils import claude_base, context_cache_file

# v2.2.0: MCP fallback notification support
try:
    from superclaude.hooks.mcp_fallback import MCP_FALLBACKS, check_mcp_and_notify

    MCP_FALLBACK_AVAILABLE = True
except ImportError:
    MCP_FALLBACK_AVAILABLE = False
    MCP_FALLBACKS = {}

# Configuration
INJECT_MODE = os.environ.get("CLAUDE_CONTEXT_INJECT", "1").lower() in (
    "1",
    "true",
    "yes",
)  # Default: inject
MAX_TOKENS_ESTIMATE = int(
    os.environ.get("CLAUDE_CONTEXT_MAX_TOKENS", "8000")
)  # ~8K tokens
CHARS_PER_TOKEN = 4  # Rough estimate

# Dedup cache file, keyed on (project, Claude Code session) and stored in the
# active install's own .claude — see superclaude.utils.hook_state_dir.
#
# The project half is keyed on project_root(), not the CWD: a hook firing from a
# subdirectory would otherwise read a different cache file and silently
# re-inject every context. The session half stops two windows open on one
# repository from starving each other — whichever triggered a context first used
# to mark it loaded for both, leaving the second window with nothing. A session
# id only arrives on stdin, so the file is resolved once per run in main(); the
# project-only name stays as the fallback for callers holding no session id.
_ACTIVE_CACHE_FILE: Path | None = None


def resolve_cache_file(session_id: str | None) -> Path:
    """Pin the dedup cache to one (project, session) for the rest of the run."""
    global _ACTIVE_CACHE_FILE
    _ACTIVE_CACHE_FILE = context_cache_file(session_id)
    return _ACTIVE_CACHE_FILE


def cache_file() -> Path:
    """Cache file resolved for this run, or the project-only fallback."""
    if _ACTIVE_CACHE_FILE is not None:
        return _ACTIVE_CACHE_FILE
    return context_cache_file()


# Base path for context files
def _get_base_path() -> Path:
    """
    Get base path for context files.

    Priority:
    1. SUPERCLAUDE_PATH environment variable (explicit override)
    2. Project-local: $CLAUDE_PROJECT_DIR/.claude/superclaude (if exists)
    3. User scope: ~/.claude/superclaude (default)

    Anchored on $CLAUDE_PROJECT_DIR rather than the CWD: hook CWD is not
    guaranteed to be the project root, and a CWD-based check silently loaded
    user-scope content when Claude Code started in a subdirectory.
    """
    if os.environ.get("SUPERCLAUDE_PATH"):
        return Path(os.environ["SUPERCLAUDE_PATH"])

    return claude_base() / "superclaude"


BASE_PATH = _get_base_path()

# Trigger → File mapping with priority (lower = higher priority)
# Format: (regex_pattern, relative_path, priority)
# NOTE: Avoid generic single words (edit, test, search, task, docs, debug, ui, etc.)
#       that cause false positives on normal coding prompts.
#       Use compound terms (e.g. "browser test" not "test") or explicit flags (--play).
TRIGGER_MAP = [
    # Priority scheme:
    #   1 = behavioral (complex decision rules, workflow patterns) — survives token budget cuts
    #   2 = operational (tool hints, standard modes) — standard injection
    #   3 = supplementary (reference data) — dropped first on budget pressure
    #
    # MCP servers — behavioral MCPs at P1, tool MCPs at P2
    (
        r"(serena|symbol ops|rename.?symbol|safe.?delete|lsp|--serena|/sc:load|/sc:save)",
        "mcp/MCP_Serena.md",
        1,
    ),
    (
        r"(tavily|fact.?check|/sc:research|--tavily)",
        "mcp/MCP_Tavily.md",
        1,
    ),
    (
        r"(--c7|--context7|library.?docs|framework.?docs|resolve.?library)",
        "mcp/MCP_Context7.md",
        2,
    ),
    (
        r"(--play|--playwright|browser.?test|e2e.?test|network.?mock|mock.?api|browser.?automat)",
        "mcp/MCP_Playwright.md",
        2,
    ),
    (
        r"(--perf|--devtools|lighthouse|memory.?leak|core.?web.?vital|cwv|a11y.?audit|accessibility.?audit)",
        "mcp/MCP_Chrome-DevTools.md",
        2,
    ),
    # Business symbols - supplementary reference
    (
        r"(business.?symbol|strategic.?symbol|business.?example|panel.?example|--structured)",
        "core/BUSINESS_SYMBOLS.md",
        3,
    ),
    # Modes — behavioral at P1, operational at P2
    (r"(--brainstorm|--bs)", "modes/MODE_Brainstorming.md", 1),
    (
        r"(--introspect|self.?analysis|analyze reasoning)",
        "modes/MODE_Introspection.md",
        2,
    ),
    (r"(--task-manage)", "modes/MODE_Task_Management.md", 2),
    (
        r"(--uc|--ultracompressed|token.?efficient|--token-efficient|--safe-mode)",
        "modes/MODE_Token_Efficiency.md",
        1,
    ),
    (r"(--orchestrate|tool.?select|/sc:select-tool)", "modes/MODE_Orchestration.md", 2),
    (
        r"(--research|deep.?research|systematic.?investigation|/sc:research)",
        "modes/MODE_DeepResearch.md",
        1,
    ),
    (
        r"(--business-panel|business.?panel|multi.?expert|strategic.?analysis|/sc:business-panel)",
        "modes/MODE_Business_Panel.md",
        1,
    ),
    # Core rule modules (Phase 2-1 core-lite split): core/RULES.md is the
    # always-loaded kernel; detail modules inject on matching context.
    # Unmapped in INSTRUCTION_MAP/TIER_0_MAP by design → Tier 2 full .md
    # (behavioral rule content needs complete text, same as modes).
    (
        r"(/sc:(implement|improve|test|build|review|cleanup|troubleshoot|analyze|task|reflect|git)|--validate|--loop\b|--iterations)",
        "core/rules/RULES_QUALITY.md",
        1,
    ),
    (
        r"(--delegate|--concurrency|/sc:(pm|agent|task)|sub.?agent|worktree)",
        "core/rules/RULES_DELEGATION.md",
        1,
    ),
    (
        r"(/sc:(document|plan|design|brainstorm|roadmap|index|index-repo|estimate|save|research|promote-feature)|implementation plan|design spec|write.{0,12}(plan|spec))",
        "core/rules/RULES_DOCS.md",
        1,
    ),
    (r"/sc:\w+", "core/rules/RULES_INTERACTION.md", 2),
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
        ("mcp/MCP_Playwright.md", 2),
        ("mcp/MCP_Chrome-DevTools.md", 2),
    ],  # Note: Playwright/DevTools are plugin-install-only (docs still loaded)
}

# v3.1: Hybrid Injection Map
# Only entries reachable by _get_injection_tier() belong here:
#   - Behavioral MCPs (Serena, Tavily) → Tier 1 via _BEHAVIORAL_MCPS check
#   - Tool MCPs and core files use TIER_0_MAP (Tier 0) instead — do NOT duplicate here
# Mode files → always Tier 2 (full .md injection)
INSTRUCTION_MAP = {
    # Behavioral MCPs — complex decision rules and workflow patterns
    "mcp/MCP_Serena.md": (
        "Serena (17 tools): symbol ops (find_symbol, replace_symbol_body, get_symbols_overview, "
        "insert_before/after_symbol, find_referencing_symbols, rename_symbol, safe_delete_symbol). "
        "Workflow: get_symbols_overview → find_symbol(name_path, include_body=True) → edit. "
        "Decision: symbol meaning (references, types, rename, delete) → Serena; text patterns → native Grep/Edit. "
        "Memory (6): list_memories → read/write/edit/rename/delete_memory. Project auto-active via --project-from-cwd; verify with check_onboarding_performed if uncertain. "
        "Note: thinking tools (think_about_*, summarize_changes) NOT active in claude-code context. "
        "Prioritize symbolic tools over full file reads."
    ),
    "mcp/MCP_Tavily.md": (
        "Tavily web access — primary path is the Tavily Agent Skills (install: Tavily CLI + "
        "`npx skills add tavily-ai/skills`): tavily-search (web search), tavily-extract (URL→markdown), "
        "tavily-crawl (multi-page site extraction), tavily-map (URL discovery), tavily-research "
        "(cited multi-source report), tavily-best-practices (integration reference). Auto-invoked by task "
        "or explicit slash commands (/tavily-search, /tavily-crawl, /tavily-research, …). "
        "Optional Tavily MCP exposes only tavily_search + tavily_extract as in-conversation tools "
        "(search_depth: basic/advanced/fast/ultra-fast, time_range, start_date/end_date, "
        "include_domains/exclude_domains, country). "
        "Use for current info post-knowledge-cutoff, multi-source research, fact-checking. "
        "Fallback: native WebSearch/WebFetch when neither skills nor MCP available."
    ),
}

# v3.2: Tier 0 — 1-line summaries for tool MCPs (Claude already has tool descriptions)
# Behavioral MCPs (Serena, Tavily) are NOT here — they use INSTRUCTION_MAP (Tier 1)
TIER_0_MAP = {
    "mcp/MCP_Context7.md": "Context7: resolve-library-id first, then query-docs. Never skip step 1.",
    "mcp/MCP_Playwright.md": "Playwright: browser E2E + network mocking (--caps=network,storage). navigate → assert.",
    "mcp/MCP_Chrome-DevTools.md": "DevTools: 26 tools. Lighthouse audits, CWV, a11y, memory. trace → analyze → optimize.",
    "core/BUSINESS_SYMBOLS.md": "Business symbols + expert selection. 🎯📈💰⚖️🏆🌊 domain mapping.",
}

# Behavioral MCPs that need Tier 1 (INSTRUCTION_MAP), not Tier 0
_BEHAVIORAL_MCPS = {"mcp/MCP_Serena.md", "mcp/MCP_Tavily.md"}

# Environment variable to control instruction mode (default: enabled)
USE_INSTRUCTIONS = os.environ.get("CLAUDE_CONTEXT_USE_INSTRUCTIONS", "1") == "1"

# Where a flag is being *used* rather than *mentioned*.
#
# Every `--name` in the payload used to be a candidate, so a pasted shell
# command, a quoted option in a review, or a sub-agent report listing flag names
# produced advice about flags nobody typed. That half is noise. The other half
# is not: `--verbose-context` forces full .md injection at 5-10x the token cost
# and the execution flags inject behavioural directives, so quoted text could
# change how the session runs. Both were reproduced from a report that only
# quoted the names.
#
# Two rules, each matching how the strings actually appear. Code formatting —
# fences, inline spans, blockquotes — marks a name being talked about. And an
# option on a line that starts with an external runner belongs to that runner:
# `cargo test --parallel` is cargo's flag, not this framework's.
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_BLOCKQUOTE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)
_WORD_RE = re.compile(r"[A-Za-z][\w.-]*")

# Runners whose own options collide with SuperClaude names. A runner anywhere
# ahead of the option on its line claims it — `run pytest --no-parallel for me`
# is as much pytest's flag as `pytest --no-parallel` is. That over-reaches on a
# line like "explain how python handles --loop", and the trade is deliberate:
# the cost of over-reaching is one missing notice, and the cost of under-
# reaching is a behavioural directive fired by text nobody typed. Not exhaustive
# by design, for the same reason.
_EXTERNAL_RUNNERS = frozenset(
    {
        "bun", "cargo", "curl", "docker", "eslint", "gh", "git", "go", "gradle",
        "jest", "kubectl", "make", "mvn", "node", "npm", "npx", "pip", "pnpm",
        "poetry", "prettier", "pytest", "python", "python3", "ruff", "rustc",
        "terraform", "tsc", "uv", "uvx", "vitest", "wget", "yarn",
    }
)


def scannable_prompt(prompt: str) -> str:
    """The prompt with mentioned-not-used regions blanked out.

    Blanks rather than deletes, so nothing downstream depends on offsets that
    would shift.
    """
    text = _FENCED_CODE_RE.sub(" ", prompt)
    if "```" in text:  # an unterminated fence opens a region that never closes
        text = text[: text.index("```")]
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _BLOCKQUOTE_RE.sub(" ", text)

    kept = []
    for line in text.splitlines():
        head = line.split("--", 1)[0]
        runner = any(
            word.group(0).lower() in _EXTERNAL_RUNNERS for word in _WORD_RE.finditer(head)
        )
        kept.append("" if runner else line)
    return "\n".join(kept)


# How close a mistyped flag has to be to a retired name before we name it.
# difflib.SequenceMatcher similarity, not edit distance: --parellel/--parallel
# scores 0.88, while --link/--think scored 0.67 and produced advice to change a
# valid curl option.
RETIRED_FUZZY_CUTOFF = 0.8

# Flag alias system — empty by design. All canonical flags live in VALID_FLAGS.
# Typos are caught by the fuzzy-match fallback in resolve_flags (difflib ≥ 0.6).
# Conceptual aliases (e.g., --parallel for --delegate) were removed to keep one
# canonical name per concept; update command docs to use canonical flags directly.
FLAG_ALIASES: dict[str, list[str]] = {}

# All valid flags for fuzzy matching fallback
VALID_FLAGS = {
    "brainstorm",
    "business-panel",
    "research",
    "introspect",
    "task-manage",
    "orchestrate",
    "token-efficient",
    "c7",
    "context7",
    "serena",
    "play",
    "playwright",
    "perf",
    "devtools",
    "tavily",
    "frontend-verify",
    "all-mcp",
    "no-mcp",
    "delegate",
    "concurrency",
    "loop",
    "iterations",
    "validate",
    "safe-mode",
    "plan",
    "uc",
    "ultracompressed",
    "scope",
    "focus",
    "bs",
    "verbose-context",
    "vs",
}

# Claude Code native flags / triggers — pass through unchanged, no fuzzy suggestion
CC_NATIVE_PASSTHROUGH: set[str] = {
    "ultrathink",
    "fast",  # CC-native fast mode (/fast toggle) — SC ships no behavior for it
    "effort",  # removed from SC in 06d972b; Claude Code owns /effort now
}

# Flags this framework removed, and where their work went. Typed 479 times
# between them after the removals landed, every one answered in silence: with no
# valid flag inside edit distance 2, the fuzzy fallback had nothing to suggest.
# Per D5 the flags are not restored — the notice carries the redirect.
RETIRED_FLAGS: dict[str, str] = {
    "think": "Use the native /effort control (--ultrathink also still works).",
    "think-hard": "Use the native /effort control (--ultrathink also still works).",
    "think-harder": "Use the native /effort control (--ultrathink also still works).",
    "parallel": "Use --delegate for sub-agent fan-out, --concurrency [n] to batch calls.",
    # Sequential MCP dropped: it is an external scratchpad, not a reasoning
    # engine, and Opus 5 / Fable 5 already think between tool calls natively.
    "seq": "Sequential MCP removed — native reasoning covers it; use /effort for depth.",
    "sequential": "Sequential MCP removed — native reasoning covers it; use /effort for depth.",
}


def resolve_flags(prompt: str) -> tuple[str, list[str]]:
    """Resolve flag aliases and typos in a prompt.

    Returns:
        Tuple of (corrected_prompt, list of notification messages)
    """
    notifications: list[str] = []
    corrected = prompt
    scannable = scannable_prompt(prompt)

    # Find all --flag patterns (flags may have values after them)
    flag_pattern = re.compile(r"--([a-zA-Z][\w-]*)")
    for match in flag_pattern.finditer(scannable):
        flag = match.group(1).lower()

        # Skip already-valid flags
        if flag in VALID_FLAGS:
            continue

        # Skip CC-native triggers (e.g., ultrathink) — pass through silently
        if flag in CC_NATIVE_PASSTHROUGH:
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

        # Retired flags, exact then fuzzy. Fuzzy matters as much as exact here:
        # --parellel was typed 159 times and is a typo *of a flag that no longer
        # exists*, so neither pass alone would have caught it.
        if flag in RETIRED_FLAGS:
            notifications.append(f"--{flag} was retired. {RETIRED_FLAGS[flag]}")
            continue
        # Tighter than the valid-flag pass below: a retired name carries a
        # replacement instruction, so a wrong match tells the user to change
        # something that was right. 0.6 called --link a typo of --think.
        retired_close = difflib.get_close_matches(
            flag, RETIRED_FLAGS, n=1, cutoff=RETIRED_FUZZY_CUTOFF
        )
        if retired_close:
            target = retired_close[0]
            notifications.append(
                f"--{flag} looks like --{target}, which was retired. "
                f"{RETIRED_FLAGS[target]}"
            )
            continue

        # Fuzzy match fallback — difflib similarity, not edit distance
        close = difflib.get_close_matches(flag, VALID_FLAGS, n=3, cutoff=0.6)
        if close:
            suggestions = ", ".join(f"--{c}" for c in close)
            notifications.append(
                f"--{flag} is not a recognized flag. Did you mean: {suggestions}?"
            )

    return corrected, notifications


# Commands renamed out from under their users. /sc:workflow was typed 25 times
# after commands/workflow.md was deleted in 16b89c0 and reborn as roadmap with no
# alias behind it.
RETIRED_COMMANDS: dict[str, str] = {
    "workflow": "roadmap",
}

_COMMAND_TOKEN_RE = re.compile(r"/sc:([a-zA-Z][\w-]*)")


def _known_command_names() -> set[str]:
    """The command names this install actually ships.

    Read off disk rather than hardcoded, so adding a command cannot silently make
    itself a typo. The installed layout keeps them in <claude_base>/commands/sc;
    the source tree keeps them beside the rest of the content. An install with
    neither resolves nothing, and every check below falls open.
    """
    for directory in (claude_base() / "commands" / "sc", BASE_PATH / "commands"):
        try:
            names = {
                f.stem for f in directory.glob("*.md") if f.stem.upper() != "README"
            }
        except OSError:
            continue
        if names:
            return names
    return set()


def resolve_command_name(prompt: str) -> tuple[list[str], set[str]]:
    """Check the /sc: name in a prompt against what is installed.

    Never rewrites the prompt. A wrong name gets one comment naming what it
    probably meant, and when nothing plausible exists the caller suppresses
    command context — injecting it anyway made a command that does not exist look
    to the model exactly like one that does.

    Every token is checked, not just the first: a valid name up front used to let
    every later unknown one through unremarked.

    Returns:
        (notifications, names that resolve to nothing)
    """
    known = _known_command_names()
    if not known:
        return [], set()

    notifications: list[str] = []
    unresolved: set[str] = set()
    for name in dict.fromkeys(
        m.group(1).lower() for m in _COMMAND_TOKEN_RE.finditer(prompt)
    ):
        if name in known:
            continue

        if name in RETIRED_COMMANDS:
            replacement = RETIRED_COMMANDS[name]
            notifications.append(f"/sc:{name} was renamed. Use /sc:{replacement}.")
            if replacement not in known:
                unresolved.add(name)
            continue

        close = difflib.get_close_matches(name, known, n=3, cutoff=0.6)
        if close:
            suggestions = ", ".join(f"/sc:{c}" for c in close)
            notifications.append(
                f"/sc:{name} is not a command. Did you mean: {suggestions}?"
            )
            continue

        notifications.append(f"/sc:{name} is not a command. Run /sc:help for the list.")
        unresolved.add(name)

    return notifications, unresolved


def strip_unresolved_commands(prompt: str, unresolved: set[str]) -> str:
    """Remove only the tokens that name nothing, leaving valid ones in place.

    Suppression used to run `_COMMAND_TOKEN_RE.sub("", prompt)`, which removed
    every `/sc:` token — so one unresolvable name in a prompt also cost a valid
    command its context.
    """
    if not unresolved:
        return prompt
    return _COMMAND_TOKEN_RE.sub(
        lambda m: "" if m.group(1).lower() in unresolved else m.group(0), prompt
    )


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
    """Read the contexts already injected into this session."""
    if cache_file().exists():
        return set(cache_file().read_text().strip().split("\n"))
    return set()


def mark_as_loaded(contexts: str | list[str]) -> None:
    """Mark context(s) as loaded in session cache. Accepts single or batch."""
    loaded = get_loaded_contexts()
    if isinstance(contexts, str):
        loaded.add(contexts)
    else:
        loaded.update(contexts)
    # Created here rather than at import: importing this module used to mkdir in
    # the developer's real home during pytest collection, before any fixture had
    # redirected HOME.
    path = cache_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(loaded))


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


def check_mcp_fallbacks(
    contexts: list[tuple[str, int]], session_id: str | None = None
) -> list[str]:
    """Check for MCP fallback notifications (first time only per session).

    Args:
        contexts: List of (context_file, priority) tuples
        session_id: CC session id from hook stdin JSON — keys the
            once-per-session dedup so hints re-arm each CC session

    Returns:
        List of notification strings to display
    """
    if not MCP_FALLBACK_AVAILABLE:
        return []

    notifications = []
    for context_file, _ in contexts:
        # Extract MCP name from path like "mcp/MCP_Serena.md"
        if context_file.startswith("mcp/MCP_"):
            mcp_name = context_file.replace("mcp/MCP_", "").replace(".md", "").lower()
            # Map special names
            name_map = {"chrome-devtools": "devtools"}
            mcp_name = name_map.get(mcp_name, mcp_name)

            if mcp_name in MCP_FALLBACKS:
                notification = check_mcp_and_notify(mcp_name, session_id)
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


def output_inject_mode(
    contexts: list[tuple[str, int]],
    prompt: str = "",
    session_id: str | None = None,
) -> None:
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
    verbose = bool(
        re.search(r"--verbose-context", scannable_prompt(prompt), re.IGNORECASE)
    )
    if verbose:
        print(
            "<!-- SuperClaude --verbose-context: forcing full .md injection for "
            f"{len(contexts)} file(s). Expect 5-10x token inflation vs default tiers. -->"
        )
        print()

    # v2.2.0: Check MCP fallbacks first
    fallback_notifications = check_mcp_fallbacks(contexts, session_id)
    for notification in fallback_notifications:
        print(f"<!-- {notification} -->")
    if fallback_notifications:
        print()

    for context_file, priority in contexts:
        tier = _get_injection_tier(context_file, verbose)

        # Tier 0: 1-line hint (tool MCPs, core)
        if tier == 0 and context_file in TIER_0_MAP:
            # Defensive: skip hint if backing file is missing (avoids advertising deleted MCPs)
            if not (BASE_PATH / context_file).exists():
                print(f"<!-- skip {context_file}: backing file not installed -->")
                print()
                continue
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
        lambda m: (
            f'<sc-directive flag="--iterations {m.group(1)}">'
            f"Execute exactly {m.group(1)} improvement iterations. "
            f"After each iteration: state what changed. Do not stop early."
            f"</sc-directive>"
        )
    ),
    re.compile(r"--loop\b", re.IGNORECASE): (
        lambda m: (
            '<sc-directive flag="--loop">'
            "Iterative improvement mode: state verifiable success criteria first, then "
            "execute → self-evaluate vs criteria → identify gaps → re-execute. "
            "Stop when criteria met, no meaningful improvement, or 5-iteration safety cap. "
            "Report total iteration count and criteria status when done."
            "</sc-directive>"
        )
    ),
    re.compile(r"--concurrency\s+(\d+)", re.IGNORECASE): (
        lambda m: (
            f'<sc-directive flag="--concurrency {m.group(1)}">'
            f"Batch up to {m.group(1)} independent tool calls per message. "
            f"Group reads, searches, and other non-dependent operations together."
            f"</sc-directive>"
        )
    ),
    # --serena directive removed: INSTRUCTION_MAP[mcp/MCP_Serena.md] (Tier 1)
    # already provides workflow + decision rules. Avoids ~85 token duplicate.
    re.compile(r"--plan\b", re.IGNORECASE): (
        lambda _: (
            '<sc-directive flag="--plan">'
            "Lightweight planning mode: before implementing, generate a concise 5-line plan "
            "(goal, approach, files to change, risks, verification). "
            "Present the plan and wait for user approval before proceeding with implementation."
            "</sc-directive>"
        )
    ),
}


def _emit_execution_directives(prompt: str) -> None:
    """Emit inline behavioral directives for execution flags.
    Session-deduped: each (pattern, matched-flag) combo emits once per session."""
    loaded = get_loaded_contexts()
    new_marks = []
    scannable = scannable_prompt(prompt)
    for pattern, directive_fn in _EXECUTION_DIRECTIVES.items():
        match = pattern.search(scannable)
        if not match:
            continue
        marker = f"_directive:{pattern.pattern}:{match.group(0).lower()}"
        if marker in loaded:
            continue
        print(directive_fn(match))
        print()
        new_marks.append(marker)
    if new_marks:
        mark_as_loaded(new_marks)


def _extract_prompt(stdin_data: str) -> str:
    """Extract prompt from UserPromptSubmit JSON input, with raw text fallback."""
    try:
        data = json.loads(stdin_data)
        return data.get("prompt", stdin_data)
    except (json.JSONDecodeError, TypeError):
        return stdin_data


def _extract_session_id(stdin_data: str) -> str | None:
    """Extract the CC session_id from hook stdin JSON (None if unavailable).

    Keys mcp_fallback's once-per-session dedup to the real Claude Code
    session, so hints re-arm each session instead of once per machine.
    """
    try:
        data = json.loads(stdin_data)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    session_id = data.get("session_id")
    return session_id if isinstance(session_id, str) and session_id else None


def main() -> None:
    # Read and parse JSON input from Claude Code
    stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
    prompt = _extract_prompt(stdin_data)
    session_id = _extract_session_id(stdin_data)
    # Pin the dedup cache before anything reads it — a concurrent session in the
    # same project must not consume the injections meant for this one.
    resolve_cache_file(session_id)

    if not prompt or not prompt.strip():
        return

    # v3.2: Resolve flag aliases and typos before processing
    prompt, flag_notifications = resolve_flags(prompt)
    if flag_notifications:
        for note in flag_notifications:
            print(f"<!-- SuperClaude flag: {note} -->")
        print()

    # v2.1.0: Output skills summary if enabled — once per session (cache-marked)
    if SHOW_SKILLS_SUMMARY and "_skills_summary" not in get_loaded_contexts():
        skills = get_skill_estimates()
        if skills:
            summary = format_skills_summary(skills)
            if summary:
                print(summary)
                print()
                mark_as_loaded("_skills_summary")

    # Execution flag directives (inline behavioral hints — no file injection)
    _emit_execution_directives(prompt)

    # An unknown /sc: name must not read as a real command
    command_notes, unresolved_commands = resolve_command_name(prompt)
    for note in command_notes:
        print(f"<!-- SuperClaude command: {note} -->")
    if command_notes:
        print()

    # Check triggers and get contexts to load
    trigger_prompt = strip_unresolved_commands(prompt, unresolved_commands)
    contexts = check_triggers(trigger_prompt)

    # --no-mcp notification — once per session
    if (
        "--no-mcp" in scannable_prompt(prompt).lower()
        and "_notice:--no-mcp" not in get_loaded_contexts()
    ):
        print(
            "<!-- --no-mcp: MCP contexts suppressed. Using native tools + WebSearch. -->"
        )
        print()
        mark_as_loaded("_notice:--no-mcp")

    if not contexts:
        return

    # Output based on mode
    if INJECT_MODE:
        output_inject_mode(contexts, prompt=prompt, session_id=session_id)
    else:
        output_directive_mode(contexts)


if __name__ == "__main__":
    main()
    sys.exit(0)
