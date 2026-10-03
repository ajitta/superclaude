---
status: draft
revised: 2026-10-03
---

# B6: Hook and runtime behavior removals

Item specs for batch B6. Order, preconditions and cross-item constraints are in
[05-plan.md](./05-plan.md#b6). Owner decisions are in [README.md](./README.md#decisions).

Specs are model output from read-only verifiers, rendered verbatim. Treat them as leads to check:

- Line numbers are from base commit `57287b4` and drift after the first edit. Anchor every edit
  on a symbol or a unique string, and re-grep each cited reference before deleting anything.
- No verifier ran pytest, ruff or the `Verify` commands, so every "suite stays green" claim
  below is a prediction.

## F07: token_estimator.py and skills banner

`delete` · verdict **confirmed** · ~115 lines · owner decision: yes (see README)

Holds in both variants. (a) estimate_command_tokens, estimate_agent_tokens, get_context_token_summary and format_token_report have zero callers anywhere (~115 lines). (b) The rest of token_estimator.py (TokenEstimate, extract_frontmatter, estimate_skill_tokens, get_skill_directories wrapper, get_all_skill_estimates) feeds only the once-per-session skills banner; deleting the module needs cli/main.py:1145 repointed to context_loader.estimate_tokens and utils.get_skill_directories deleted with it. The banner's 'full load' figure is char//4 over every .md/.ts/.py/.json in each skill dir, which no Claude Code mechanism loads.

**Batch note:** Variant (a), deleting only the four uncalled functions, is decision-free and can land in B4. Variant (b) removes the module and the banner and needs the owner decision. Skip (a) if (b) is approved.

**Decision:** Variant (b) removes a visible behavior: the once-per-session '&lt;!-- N skills installed (...). ~N tokens full load. Use /sc:help for details. -->' banner (injected into the model's context, with a documented CLAUDE_SHOW_SKILLS opt-out and a disclosure line in `context explain`). It is also the only place a skill full-load token figure appears, and the figure overstates (155381 tokens for 43 skills here). Pick (a) firm: delete only the 4 uncalled functions (~115 lines, zero behavior change, no decision). Or (b) full: delete the module and banner (~420 lines incl. tests, the banner disappears). Variant (b) at ~420 lines is the larger saving.

**Changes**

- `src/superclaude/scripts/token_estimator.py` (edit): (a) FIRM: delete lines 110-159 (estimate_command_tokens + estimate_agent_tokens + trailing blanks) and lines 197-261 (get_context_token_summary + format_token_report); leave two blank lines before EOF cleanup. 261 -> ~145 lines. Imports (re, dataclass, Path, Literal) all stay in use. No test touches this module.
- `src/superclaude/scripts/token_estimator.py` (delete): (b) FULL: delete the whole file (261 lines). Supersedes (a).
- `src/superclaude/scripts/context_loader.py` (edit): (b) delete: line 20 docstring line 'v2.1.0: Skills discovery and token estimation'; lines 28-32 (`from typing import TYPE_CHECKING`, blank, `if TYPE_CHECKING:` block; TYPE_CHECKING is used nowhere else in the file); lines 590-627 (SHOW_SKILLS_SUMMARY, get_skill_estimates, format_skills_summary); lines 1150-1159 (the banner block in main(), up to the blank before '# Execution flag directives'). Keep estimate_tokens at 650.
- `src/superclaude/cli/main.py` (edit): (b) line 1145: change to `from superclaude.scripts.context_loader import estimate_tokens`. Delete line 1121 (`env["CLAUDE_SHOW_SKILLS"] = "0"`). Delete the click.echo at 1335-1338 ('skills:  installed-skills banner suppressed ...'). Trim the docstring clause at ~1297-1299 ('and the once-per-session installed-skills banner is suppressed rather than shown').
- `src/superclaude/utils/__init__.py` (delete): (b) delete get_skill_directories, lines 61-74 plus one blank line.
- `src/superclaude/scripts/README.md` (edit): (b) delete table row at line 19 (`token_estimator.py` | Context window usage estimation).
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` (edit): (b) section 1 row '전체 Python module': recompute the count (57 -> 56 for this cut alone) with `uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"`. Do this once at the end if F07-b, F10 and F14 all land (57 -> 54).

**Tests**

- tests/unit/test_context_loader.py: (b) delete the FakeTokenEstimate dataclass (lines 28-35), the `format_skills_summary` import (line 23), `from dataclasses import dataclass` (line 9) and class TestFormatSkillsSummary (lines 57-97); delete the dead `env["CLAUDE_SHOW_SKILLS"] = "0"` in run_loader (~line 439); update the module docstring line 4 ('Tests: format_skills_summary, ...').
- tests/unit/test_cli_context.py: (b) delete test_the_suppressed_skills_banner_is_disclosed (lines 242-250); delete the dead env line at ~113.
- tests/unit/test_scope_paths.py: (b) delete the `get_skill_directories` import (line 17) and class TestSkillDirectories (lines 250-268).
- tests/manual/test_context_loader_tiers.py (not collected by pytest, no test_ functions): (b) drop the CLAUDE_SHOW_SKILLS env line at 168, verify_session_dedup (192-211) with its call site, and the 'skills installed' filters at ~231 and 263-265.
- No test needs changing for variant (a).

**Doc references**

- src/superclaude/scripts/README.md:19
- docs/codex/prompting_session_raw/02_component_and_delivery_map.md:32 (module count)
- .claude/rules/gotchas/hooks.md:11 names get_skill_directories and the 'skills banner reported 9 skills instead of 22' symptom. It is a dated historical record: leave it, or add a note that the symptom is moot after the cut.
- docs/archive/reports/OPUS_4_8_ALIGNMENT.md mentions token_estimator (archive, ignore).

**Collateral**

- Module-count trap: (b) removes one .py under src/superclaude, so test_codex_component_map.py::test_documented_count_matches_source goes red until section 1 of 02_component_and_delivery_map.md is recomputed. (a) removes no file, so no count change.
- The `superclaude context explain` output loses the 'skills:' line. tests/unit/test_cli_context.py must lose its assertion in the same commit.
- Existing sessions' dedup caches may still contain the '_skills_summary' marker. It is inert and swept by the 7-day state prune.
- tests/unit/scripts/ and `make test-scripts` are not involved: nothing here touches auto_improve or parallel_ab.
- Ruff: (b) leaves unused `dataclass` and `get_skill_directories` imports unless removed as listed.

**Verify**

```bash
uv run pytest   # must exit 0
uv run ruff check src/ tests/
(a): grep -rnE "estimate_command_tokens|estimate_agent_tokens|get_context_token_summary|format_token_report" src tests scripts   # no output
(b): grep -rnE "token_estimator|TokenEstimate|get_skill_estimates|format_skills_summary|SHOW_SKILLS|_skills_summary|get_skill_directories" src tests scripts   # no output (tests/manual cleaned too)
(b): uv run python -c "from pathlib import Path; print(len(list(Path('src/superclaude').rglob('*.py'))))"   # equals the number in 02_component_and_delivery_map.md section 1
(b): uv run superclaude context explain "--serena rename x"   # exits 0, no 'skills:' line
```

<details><summary>Evidence</summary>

- Repo-wide grep (src, tests, scripts/, evals/, Makefile, .github, pyproject, hooks.json, HOOKS registry, install_settings, *.md): estimate_command_tokens / estimate_agent_tokens / get_context_token_summary / format_token_report appear only as defs inside token_estimator.py (110-132, 135-157, 197-227, 230-261).
- The token_estimator module name appears in no test, no hooks.json, no HOOKS registry, no pyproject, no Makefile and no .github. It appears only in cli/main.py:1145, context_loader.py:31 and :601, scripts/README.md:19, and the archived docs/archive/reports/OPUS_4_8_ALIGNMENT.md.
- context_loader.py:28-31 imports TokenEstimate under TYPE_CHECKING only. get_skill_estimates (594-605) is the sole importer of get_all_skill_estimates. format_skills_summary (608-625) builds the '&lt;!-- N skills installed (...). ~N tokens full load. Use /sc:help for details. -->' line. main() emits it at 1150-1158 once per session, marked in the cache as '_skills_summary'.
- estimate_tokens has 3 copies: token_estimator.py:35, context_loader.py:650-652, and the inline `len(content) // 4` in cli/main.py:579 (agents --tokens). Only cli/main.py:1145 imports token_estimator's copy. main.py:1258 already does an in-function `from superclaude.scripts.context_loader import ...`, so the same import for estimate_tokens has precedent.
- utils/__init__.py:61-74 get_skill_directories: callers are token_estimator.py:162 and tests/unit/test_scope_paths.py:17 and 250-267 (class TestSkillDirectories) only.
- The banner is a deliberate surface. CLAUDE_SHOW_SKILLS opt-out at context_loader.py:591. cli/main.py:1121 sets it to 0 inside `context explain`, :1335-1338 prints 'skills: installed-skills banner suppressed', and tests/unit/test_cli_context.py:242-250 pins that line.
- Measured read-only here: get_all_skill_estimates() returned 43 skills, 86 files, 155381 'full load' tokens, in 50 ms. That cost is paid on the first prompt of every session.
- No other surface shows skill token cost. `superclaude agents --tokens` (main.py:565-595) is agents-only and does its own inline math.

</details>

## F12: session-start PR-status line

`native` · verdict **confirmed** · ~355 lines · owner decision: yes (see README)

The PR-status line in session_init.py (get_pr_status + 600s cache, lines 108-249) is a model-visible SessionStart line with one caller (main()). Deleting it drops the PR line from model context, and the Claude Code footer badge (not verified here, see unknowns) is UI-only. The cost argument is weaker than the docstring says: since commit 4cfc0fb the line is cached per branch for 600s (0.05ms on a hit), so only a cold miss pays the 552ms. Offline is the worse case, because the TimeoutExpired path writes no cache and so pays up to 10s every session start. The cut also reverses a recorded decision: the archived hook-performance 05-plan says the call was 'cached rather than removed, so the banner line is unchanged'. The on-demand path survives: /sc:git --pr-status (commands/git.md:29-41) and the git-workflow agent run `gh pr view` themselves.

**Decision:** Delete the model-visible PR-status line at session start? That gives up passive PR awareness (the footer badge is for the human only). /sc:git --pr-status and the git-workflow agent remain as the on-demand path. It reverses the 2026-08-23 'cache it, do not remove it' decision recorded in the archived hook-performance plan. Also confirm F35a (the same banner block) goes in the same change.

**Changes**

- `src/superclaude/scripts/session_init.py` (delete): Delete lines 108-250: PR_STATUS_TTL_SECONDS through the end of get_pr_status().
- `src/superclaude/scripts/session_init.py` (edit): main(): delete the '# 3. Check PR status' block (:293-296, 4 lines + blank) and renumber the remaining step comments. Docstring :12 loses '- PR review status indicator display' (the whole v2.2.0 block goes with F35a). Drop `import json` (:18), which only the PR code used; `import subprocess` stays until F35b lands.
- `src/superclaude/hooks/hooks.json` (edit): Line 10 `_comment`: drop ', PR-review status line' and keep the leading '[superclaude]'. Do not touch the command or timeout.

**Tests**

- tests/unit/test_session_init.py: delete class TestGetPrStatus with its banner comment (lines 198-360, 13 tests plus the _isolated_pr_cache fixture).
- tests/unit/test_session_init.py: delete TestMain.test_main_prints_pr_status_when_present (:461-483) and test_main_omits_pr_status_when_empty (:485-504).
- tests/unit/test_session_init.py: remove the `patch('...get_pr_status', ...)` lines from the remaining TestMain tests (:450, :520, :542). Remove `get_pr_status` from the import list (:19). Remove `import json` (:8) and `import pytest` (:14), which only the deleted class used (recheck after F35a/F35b). Update the module docstring (:4-5).

**Doc references**

- src/superclaude/scripts/session_init.py:12-13 (module docstring v2.2.0 block)
- src/superclaude/hooks/hooks.json:10 (_comment)
- src/superclaude/scripts/README.md:16 (optional: the 'load SuperClaude context at startup' text is already inaccurate; say 'install-status banner + hook-session cleanup')

**Collateral**

- No .py file is added or removed, so the codex 02 §1 module count is untouched. session_init stays registered (it still runs init_hook_tracker and get_install_status), so the hooks.json registration count, test_hook_dispatch and install_settings markers are unaffected.
- Gitignored installed copies (.claude/hooks/hooks.json, .claude/settings.local.json) keep the old _comment until a resync (`make sync-local`, or `superclaude install --force --scope local` per the windows-make-sync-broken gotcha).
- Existing installs keep a stale pr_status_&lt;key>.json in .superclaude_hooks. It is harmless, never pruned, and removed on uninstall.
- Land F12, F35a, F35b and F35m.e as one session_init commit. They all rewrite the same TestMain tests and the same imports, and splitting them forces repeated edits to the same patch lines.

**Verify**

```bash
uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -rnE "get_pr_status|_read_pr_cache|_write_pr_cache|PR_STATUS_TTL|pr_status_\{" src tests (expect no hits) ; echo '{}' | superclaude hook session_init on a feature branch with an open PR prints no 'PR:' line.
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/session_init.py:108-249 holds PR_STATUS_TTL_SECONDS, _pr_cache_path, _read_pr_cache, _write_pr_cache and get_pr_status. Their only caller is main() at :293-296.
- Whole-repo grep for get_pr_status|_read_pr_cache|_write_pr_cache|PR_STATUS_TTL_SECONDS|pr_status_ hits only session_init.py and tests/unit/test_session_init.py. The `pr_status_integration` tag in commands/git.md:29-41 is an unrelated XML tag for the /sc:git command.
- The cache file pr_status_&lt;project_key>.json is not in utils._PRUNABLE_PREFIXES (src/superclaude/utils/__init__.py:411-419), so there is no prune code to edit. `superclaude uninstall` rmtree's .superclaude_hooks (cli/install_inventory.py:473-475).
- src/superclaude/hooks/hooks.json:10 `_comment` says '...PR-review status line'. install_settings._hook_entry_signature ignores `_comment` (cli/install_settings.py:78-83), so editing the text is merge-safe as long as the '[superclaude]' marker prefix stays.
- `git show 4cfc0fb` and docs/archive/features/hook-performance/05-plan.md:98-100 record the 'cache, do not remove' decision (lever 1 'Accepted, implemented').
- No other doc, memory or insight mentions the PR line (grep for 'PR status|PR-review|gh pr view' over md/py/json).

</details>

## F35b: session_init git line

`native` · verdict **confirmed** · ~132 lines · owner decision: yes (see README)

get_git_status (session_init.py:88-105, main :290-291) prints '📊 Git: clean|N files|not a repo'. Claude Code already injects a richer gitStatus block at conversation start (visible in this very session's context), so the line is a strict subset. Cost is one subprocess (~15ms measured in the archived analysis). The /sc:agent command doc (commands/agent.md:20-21 &lt;startup>) reproduces the same banner format but as its own instruction (it tells Claude to run git status itself), so that doc stays valid without the hook.

**Decision:** Small. Confirm Claude Code's gitStatus injection stays enabled for the way you run sessions. If includeGitInstructions is off in some setups, this one-line git summary is the only git signal at session start.

**Changes**

- `src/superclaude/scripts/session_init.py` (delete): Delete get_git_status (:88-106) and the '# 2. Check git status' lines in main() (:290-292). With F12 also gone, `import subprocess` (:19) is unused: delete it, leaving only `import sys`.
- `README.md` (edit): Line 433: change 'SessionStart: git status + memory staleness warning' to 'SessionStart: install-status banner + memory staleness warning'.
- `src/superclaude/commands/agent.md` (edit): Optional, no cut required: lines 20-21 keep working as the command's own startup steps. If tidied, drop 'Remind: 💡 Use /context...' (see F35m.e) and leave the git status check.

**Tests**

- tests/unit/test_session_init.py: delete class TestGetGitStatus with its banner (:111-196).
- Delete TestMain.test_main_prints_git_status (:440-459) and the `patch('...get_git_status', ...)` lines (:446-449, :468-470, :493-495, :517-519, :539-541). Remove `get_git_status` from the import (:18). After F12/F35a/F35b, remove the now-unused FakeCompletedProcess dataclass (:29-35) and the `subprocess`, `dataclass`, `json` and `pytest` imports. Keep `Path`, `MagicMock` and `patch`.
- Keep TestMain.test_main_prints_install_status (:506-530), with only the init_hook_tracker patch.

**Doc references**

- README.md:433
- src/superclaude/commands/agent.md:20-21 (optional)
- src/superclaude/scripts/session_init.py:89 docstring goes with the function

**Collateral**

- No .py added or removed. Same commit as F12, F35a and F35m.e.
- Resulting session_init.py is about 100 lines: get_install_status, init_hook_tracker, main. It still prints one model-visible line, the install status.

**Verify**

```bash
uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -rn "get_git_status\|Git: " src tests (expect only commands/agent.md:20) ; echo '{}' | superclaude hook session_init prints a single 'SuperClaude:' line.
```

<details><summary>Evidence</summary>

- src/superclaude/scripts/session_init.py:88-105 (function), :290-291 (call).
- Only references: tests/unit/test_session_init.py (TestGetGitStatus :111-196, TestMain), commands/agent.md:20 and README.md:433 'SessionStart: git status + memory staleness warning'.
- CC's own gitStatus injection is observable in this session's context ('This is the git status at the start of the conversation'). Whether it can be switched off (includeGitInstructions) was not verified.

</details>

## F20: context_loader dead knobs

`delete` · verdict **confirmed** · ~100 lines · owner decision: yes (see README)

All the dead knobs and branches exist, though the audit's line numbers are off. CLAUDE_CONTEXT_INJECT directive mode: INJECT_MODE at context_loader.py:50-54, output_directive_mode at :692-700, the branch at :1193-1197, plus the _CTX_LOAD_RE consumer in cli/main.py. FLAG_ALIASES = {} at :361-365 with its resolve_flags branch at :453-461. CLAUDE_CONTEXT_USE_INSTRUCTIONS at :265-266 and :744. MCP_FALLBACK_AVAILABLE with its same-package ImportError guard at :40-47 (uses at :716 and :937). A second same-package guard around token_estimator at :600-605. _BEHAVIORAL_MCPS at :262-263 equals set(INSTRUCTION_MAP) (checked by running it), TIER_0_MAP and INSTRUCTION_MAP do not intersect, so _get_injection_tier's :748-749 check is redundant with :752-753. After the cut, resolve_flags's returned `corrected` is always the input prompt (optional follow-up). Three env vars are NOT dead and must stay: CLAUDE_CONTEXT_MAX_TOKENS (cli/main.py:1310, test_cli_context.py:169), CLAUDE_SHOW_SKILLS and SUPERCLAUDE_PATH.

**Decision:** Two env vars (CLAUDE_CONTEXT_INJECT=0 directive mode, CLAUDE_CONTEXT_USE_INSTRUCTIONS=0 full-.md mode) were published as user knobs in the archived 2026-03-22 context-engineering guide. Confirm nobody runs with them set in a shell profile or settings env block. The repo and ~/.claude/settings*.json show no use, but other machines cannot be grepped.

**Changes**

- `src/superclaude/scripts/context_loader.py` (edit): Docstring :7-9 (Modes block) drop the directive-mode line. :40-47 replace the try/except with a plain `from superclaude.hooks.mcp_fallback import MCP_FALLBACKS, check_mcp_and_notify`. Delete :50-54 (INJECT_MODE) and keep the '# Configuration' comment for MAX_TOKENS_ESTIMATE. :223 comment says 'via INSTRUCTION_MAP'. Delete :262-263 (_BEHAVIORAL_MCPS) and :265-266 (USE_INSTRUCTIONS).
- `src/superclaude/scripts/context_loader.py` (edit): Delete :361-365 (FLAG_ALIASES comment and dict). In resolve_flags delete the '# Check alias table' branch :453-461, and reword the docstring :427 and the comment :1143 from 'flag aliases and typos' to 'flag typos'. `corrected = prompt` is now never reassigned: keep the (prompt, notes) signature for the minimal change, or collapse it as the optional follow-up below.
- `src/superclaude/scripts/context_loader.py` (edit): get_skill_estimates :600-605: drop the try/except ImportError and keep the lazy import inside the function. Delete output_directive_mode :692-701. check_mcp_fallbacks: delete :716-717. _get_injection_tier: `if verbose:` only at :744, and delete :748-749 so the order is modes -> TIER_0_MAP -> INSTRUCTION_MAP -> 2. output_inject_mode docstring: delete :768. _emit_execution_directives :937: drop `MCP_FALLBACK_AVAILABLE and`. main() :1193-1197: replace the if/else with `output_inject_mode(contexts, prompt=prompt, session_id=session_id)`.
- `src/superclaude/cli/main.py` (edit): Delete :1027 (_CTX_LOAD_RE) and the `load = _CTX_LOAD_RE.match(line)` block :1204-1210. Optional: since tier/tokens can no longer be None, simplify :1239 (`sum(c['tokens'] for c in contexts)`), :1350 and :1351.
- `.claude/rules/mcp-authoring.md` (edit): Delete step 4 at :102 (the _BEHAVIORAL_MCPS bullet), the trailing 'and `_BEHAVIORAL_MCPS` for behavioral servers' at :120, and the '/ `_BEHAVIORAL_MCPS` if applicable' at :132. Optionally add that an INSTRUCTION_MAP entry is what yields Tier 1.

**Tests**

- tests/unit/test_context_loader.py: remove `_BEHAVIORAL_MCPS` (:14) and `FLAG_ALIASES` (:16) from the imports.
- Delete test_flag_aliases_table_is_empty (:103-105), the '# --- Alias resolution ---' comment (:101), and the '# --- Data integrity ---' pair test_all_alias_targets_are_valid and test_no_alias_is_also_valid (:180-195). They exercise only the empty dict. Keep test_removed_alias_parallel_no_auto_remap.
- test_tier_0_and_instruction_map_no_conflicting_keys (:239-245): iterate `INSTRUCTION_MAP` instead of `_BEHAVIORAL_MCPS`. This assertion is the invariant that makes the cut safe, so keep it.
- TestContext7HasNoDocOnlyAFlag._emit (:691): replace the MCP_FALLBACK_AVAILABLE patch with monkeypatch.setattr(cl, 'check_mcp_and_notify', lambda *a, **k: None) so the directive output stays free of fallback comments.
- Optional collapse of resolve_flags to return only notes: 11 call sites in tests/unit/test_context_loader.py (:109-175) plus :633, and main() :1144.

**Doc references**

- .claude/rules/mcp-authoring.md:102, :120, :132
- src/superclaude/scripts/context_loader.py:7-9, :223, :427, :768, :1143
- docs/archive/guides/2026-03-22-context-engineering-guide-ko.md:254-255 (archived, leave as is)

**Collateral**

- No .py added or removed (codex module count unchanged). No hooks.json change.
- tests/integration/test_readonly_session_is_quiet.py and tests/unit/test_cli_context.py run context_loader as a subprocess, so import-time regressions surface there.
- scripts/validate_instructions.py imports INSTRUCTION_MAP and TRIGGER_MAP only, so it is unaffected.
- output_inject_mode keeps its name: tests/unit/test_context_loader.py:659-667 import it.

**Verify**

```bash
uv run pytest tests/unit/test_context_loader.py tests/unit/test_cli_context.py tests/integration/test_readonly_session_is_quiet.py && uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ ; grep -rnE "CLAUDE_CONTEXT_INJECT|CLAUDE_CONTEXT_USE_INSTRUCTIONS|FLAG_ALIASES|_BEHAVIORAL_MCPS|MCP_FALLBACK_AVAILABLE|output_directive_mode|_CTX_LOAD_RE|context-load" src tests .claude/rules (expect none) ; uv run superclaude context explain "--serena --playwright" still reports tier 1 and tier 0.
```

<details><summary>Evidence</summary>

- Whole-repo grep for CLAUDE_CONTEXT_INJECT, CLAUDE_CONTEXT_USE_INSTRUCTIONS, INJECT_MODE, output_directive_mode and the `context-load` marker: only context_loader.py, the cli/main.py parser (comment at :1204 says 'CLAUDE_CONTEXT_INJECT=0 (directive mode)') and the archived docs/archive/guides/2026-03-22-context-engineering-guide-ko.md:254-255, which documents both env vars as user knobs. No test, eval, hooks.json, settings.local.json or ~/.claude/settings*.json sets them.
- Ran in .venv: _BEHAVIORAL_MCPS == set(INSTRUCTION_MAP) is True, set(TIER_0_MAP) & set(INSTRUCTION_MAP) is empty, FLAG_ALIASES == {}, INJECT_MODE/USE_INSTRUCTIONS/MCP_FALLBACK_AVAILABLE are all True.
- The guarded modules are same-package and import only stdlib or superclaude.*: hooks/mcp_fallback.py:15-20 and scripts/token_estimator.py:7-12. The loader already does `from superclaude.utils import ...` unguarded at :38.
- cli/main.py:1027 (_CTX_LOAD_RE) and the :1204-1210 block exist only to parse directive-mode output. The `tier is None` / `tokens is None` handling at :1239, :1350 and :1351 is reachable only from that block.
- tests/unit/test_context_loader.py:691 does monkeypatch.setattr(cl, 'MCP_FALLBACK_AVAILABLE', False), which raises AttributeError once the name is gone. tests/conftest.py already redirects MCP_FALLBACK_FILE into the sandbox.
- .claude/rules/mcp-authoring.md:102, :120 and :132 instruct authors to add servers to _BEHAVIORAL_MCPS ('force Tier-1 always-on injection'). That is wrong today: INSTRUCTION_MAP membership alone yields Tier 1 and injection still needs a trigger.

</details>

## F14: memory_staleness hook

`delete` · verdict **confirmed** · ~280 lines · owner decision: yes (see README)

The memory_staleness hook scans for a `verified: YYYY-MM-DD` frontmatter key that no shipped command or skill asks anyone to write, and none of the 46 memory files on this machine carries it, so it can never fire. It does not fail open at the settings level: a removed hook still registered in a user's settings.json makes `superclaude hook memory_staleness` exit 1 'unknown hook' on every startup until `install --force` is re-run.

**Decision:** Removes a documented, deliberately chosen opt-in feature: the 'verified:' memory convention with the SUPERCLAUDE_MEMORY_STALE_DAYS env var, advertised in README.md:411 and :433 and locked in the 2026-04-25 retrospective (A2). Two questions for the owner. (1) Cut it (never fires; 0 of 46 memories carry the key) or keep it as a documented convention? (2) If cut, accept that non-force upgraders see an 'unknown hook' exit-1 line each startup until `install --force`, since the installer cannot retire a shipped registration (the rejection recorded in commit c4c6b83)? The alternative is to keep a no-op stub in HOOKS for one release, which defeats most of the cut.

**Changes**

- `src/superclaude/scripts/memory_staleness.py` (delete): Delete the file (115 lines).
- `src/superclaude/hooks/hooks.json` (edit): Delete lines 16-22 (the memory_staleness entry) and change line 15 from `},` to `}` so the JSON stays valid.
- `src/superclaude/cli/hook_dispatch.py` (edit): Delete line 51 (`"memory_staleness": (...)`). The registry then holds 9 hooks.
- `src/superclaude/hooks/README.md` (edit): Delete line 38 (the memory_staleness bullet) and the whole section at lines 212-235 ('## Memory `verified:` convention').
- `src/superclaude/scripts/README.md` (edit): Delete table row at line 17.
- `README.md` (edit): Line 411: delete the bullet '`verified:` convention + SessionStart memory-staleness warning'. Line 433: change 'SessionStart: git status + memory staleness warning' to 'SessionStart: git status'.
- `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` (edit): Section 1 line 31: 'distinct hook entry scripts' 10 -> 9, and the cell text '`hooks.json`의 14개 등록' -> '13개 등록' (test_hook_registration_note_matches_hooks_json pins it). Line 32: module count -1 (57 -> 56 alone; 54 if F07-b and F10 also land).

**Tests**

- tests/unit/test_memory_staleness.py: delete the whole file (126 lines).
- tests/unit/test_hook_dispatch.py:218-228 (test_a_shipped_hook_runs_through_entry_without_click): replace 'memory_staleness' with 'destructive_guard'. With stdin=DEVNULL it prints approve and returns, is read-only, and imports no click or yaml. Update the docstring to match. Line 55 docstring 'the same ten hooks' -> 'nine'.
- test_every_shipped_command_dispatches and test_every_registered_hook_is_a_shipped_script_with_main stay green only if hooks.json, HOOKS and the script file are removed together.

**Doc references**

- README.md:411
- README.md:433
- src/superclaude/hooks/README.md:38,212-235
- src/superclaude/scripts/README.md:17
- docs/codex/prompting_session_raw/02_component_and_delivery_map.md:31-32
- docs/archive/plans/retrospective-followups-ajitta-2026-04-25.md:148 (archive, ignore)

**Collateral**

- Three-place hook trap: hooks.json, HOOKS registry and the script file must go in one commit. install_settings needs no code change.
- Counts: distinct hook scripts 10 -> 9, hooks.json registrations 14 -> 13, module count -1. test_codex_component_map.py asserts all three.
- Existing installs: a non-force `superclaude install` keeps the old registration, so every SessionStart(startup) runs `superclaude hook memory_staleness`, exits 1 with 'unknown hook' plus the usage text on stderr. Non-blocking: SessionStart cannot block and exit 1 is not 2. It clears on `superclaude install --force --scope <scope>` (what make sync-user/project/local use).
- On this dev machine the registration also lives in ~/.claude/settings.json and .claude/settings.local.json:162-171, and `make deploy` is an editable tool, so the working tree is the live hook code (gotcha editable-tool-branch-switch). Run `make sync-local` and `superclaude install --force --scope user` right after the change lands, before opening new sessions, or each one prints the hook error.
- No change to project_root, claude_base or utils; the hook anchored on Path.home()/.claude/projects, which nothing else shares.

**Verify**

```bash
uv run pytest   # must exit 0
uv run ruff check src/ tests/
grep -rnE "memory_staleness|MEMORY_STALE_DAYS|memory-staleness" src tests README.md   # no output
uv run python -c "import json; d=json.load(open('src/superclaude/hooks/hooks.json')); print(sum(len(e['hooks']) for a in d['hooks'].values() for e in a))"   # 13
uv run superclaude hook --help   # lists 9 hooks, no memory_staleness
uv run superclaude hook memory_staleness; echo $?   # prints 'unknown hook', exit 1 (expected fail-open behavior)
```

<details><summary>Evidence</summary>

- `grep -rlE "^verified:" ~/.claude/projects/*/memory/` returned nothing: 0 of 46 memory .md files across 6 memory dirs.
- `grep -rl "verified:" src --include=*.md` hits only src/superclaude/hooks/README.md and src/superclaude/scripts/README.md. No command, agent, skill or mode tells Claude to write the key. (docs/codex/* hits use 'verified:' with other meanings.)
- Registration is in three places: hooks.json:15-22 (SessionStart matcher 'startup', timeout 5, once), hook_dispatch.py:51 (HOOKS entry), and the dev tree's untracked copies .claude/hooks/hooks.json:19 (git-excluded) and .claude/settings.local.json:171 (gitignored). install_settings.py has no per-hook-name logic: it matches by the '[superclaude]' marker and the `superclaude hook` command form.
- Documentation exists, so it is a declared feature: README.md:411 ('`verified:` convention + SessionStart memory-staleness warning'), README.md:433, hooks/README.md:38 and :213-235 (convention section, SUPERCLAUDE_MEMORY_STALE_DAYS), scripts/README.md:17. It was a deliberate 'locked' decision: .claude/insights.jsonl:115 (R06, 2026-04-25, 'minimal stub') and docs/archive/plans/retrospective-followups-ajitta-2026-04-25.md:148.
- hook_dispatch.py:92-96: an unknown name writes to stderr and returns 1, not 2, so it does not block tools. The install_settings.py _merge_hook_arrays docstring says non-force merge leaves existing entries 'authoritative' and never drops a hook the release stopped shipping. Only `--force` strips old SuperClaude entries (the force branch of _merge_hook_arrays).
- Commit c4c6b83's message records that retiring a shipped hook registration was rejected because the installer cannot retire registrations on a non-force upgrade: 'Rejected at this scope, with the reasoning recorded so it is not re-proposed.'
- Only tests that name it: tests/unit/test_memory_staleness.py (126 lines) and tests/unit/test_hook_dispatch.py:218-228 (uses memory_staleness as the sample hook for the no-click fast-path test).

</details>
