---
feature: reframing-anchoring
status: reviewed-synthesis
revised: 2026-10-17
---

# 03. Audit synthesis and evidence limits

This is the orchestrator's synthesis of six content classifications and two ponytail reports. It supersedes their severity and deletion recommendations where it disagrees. The leaf reports are evidence inventories, not approved change lists. No framework source files have been changed by this synthesis.

## 1. What the evidence supports

The user's objective is recognizing the unstated purpose behind an action request. The existing framework records the request, propagates it, and checks completion, but does not consistently distinguish the requested means from a hypothesized end. This is a candidate intervention point, not permission to replace the user's goal.

On the code fixture, sonnet often names the actual cause but changes only the requested retry mechanism. Opus vanilla repairs the cause, while opus sc-full asks before editing. On the reply fixture, outputs often omit available fix-date/workaround facts. The mechanisms causing these outcomes are not isolated. Full baseline results and corrections: [02a-measurement.md](./02a-measurement.md).

Do not repeat the earlier conclusions that R3 decision bias was proven, that sc-full had no positive cells, or that R12 alone caused the opus stops. The first-line R3 check conflicts with an explicit format request. Both substantive R3 checks pass in every retained binary and open run. Total session input is higher under sc-full, but the difference is not the same as the static prompt size.

## 2. Coverage and confidence

| Input | Read scope | Status |
|---|---|---|
| 03a | core kernel and four on-demand rule modules | Source-based classification; sampled key claims verified below |
| 03b | modes, sc-author and sc-prompt skills/references | Classification; no intervention ablation |
| 03c / 03d | agents split in two groups | Classification; delivery-boundary recommendations require correction |
| 03e / 03f | commands split in two groups | Classification; common flow is not proof of duplication |
| 04 | Python implementation, prior lean-report verification | Key safety/loader findings source-checked and reproduced below; other findings remain individual candidates |
| 04b | content routing, repeated sections and size map | Structural evidence; raw Must-fix grouping is too broad |

Not fully covered: semantic content of MCP docs and output styles, templates, repo-local authoring rules as a new audit target, a current literature update, and actual intervention efficacy. The skills were covered by 03b, although 04b did not audit their bodies. The six classifications do not amount to an exhaustive all-directory semantic audit.

The briefs supplied the failure taxonomy and preliminary interpretation to the auditors. Isolation from installed files was requested, but the resulting judgments are not blind experimental evidence. Some A classifications were made from reviewer confidence rather than the plan's required vanilla measurement. Treat those as A-candidates, not demonstrated redundancies. C is not automatically irreducible: framework interfaces can themselves be simplified. D includes useful maintainer-only documentation; non-delivery is not a reason to delete it.

Do not combine the reports' approximate byte allocations into a precise savings percentage: section accounting and README inclusion differ. Several raw reports also exceed the repo's documentation size target; split them before committing, without cutting their evidence to make room.

## 3. Verified implementation findings: fix before another content experiment

### 3.1 Normal guard output authorizes tools instead of abstaining

Sources: `scripts/destructive_guard.py:101,107,131,135`, `scripts/loop_guard.py:34-35`, `scripts/file_size_guard.py:110`, all under `src/superclaude/`; registrations in `hooks/hooks.json` PreToolUse.

Normal or disabled paths print `{"decision":"approve"}`. The current official hooks reference says deprecated `approve` maps to `allow`, which skips the normal permission prompt. Explicit deny/ask rules and other documented exceptions still apply: this is not total removal of Claude Code security.

Verified by source and the official reference, not by running a dangerous command. Smallest intended fix: emit no decision for an allowed-by-this-guard path, preserving block/ask behavior. Pin normal, opt-out and malformed-input paths in each hook's tests. Do not change the user's installed config during this audit.

Reference: https://code.claude.com/docs/en/hooks#pretooluse-decision-control . Exact sentence in the retrieved reference: “The deprecated values `"approve"` and `"block"` map to `"allow"` and `"deny"` respectively.”

### 3.2 Invalid settings can be overwritten

Sources: `src/superclaude/cli/install_settings.py:40-57,357,411`.

Sandbox reproduction: an invalid settings file containing a dummy permissions entry and model, with one trailing comma, is replaced with hooks only; merge reports success. No real settings or credentials were read. Repair must fail without changing the existing bytes, and handle valid JSON with a non-object root too. Missing-file creation is a separate legitimate case.

### 3.3 Undelivered contexts consume the session dedup cache

Sources: `src/superclaude/scripts/context_loader.py:637-658,791-804`.

Sandbox reproduction with a 300-token limit: quality, delegation, docs and interaction contexts are matched and recorded as loaded; output reports the budget skip; repeating the request returns no contexts. The default-size quality/delegation/docs trio is also above the configured 8,000-character-estimated-token budget. The bug is committing delivery state before delivery, not merely oversized files.

Repair the state transition, not just the current 72-token overrun. A later file growth or read failure would reproduce the bug after a cosmetic trim. Directive mode must distinguish “directive emitted” from proof that the model actually read a file.

### 3.4 Quoted flags load live modes

Sources: `src/superclaude/scripts/context_loader.py:302-322,628-654,1198-1200`.

Sandbox reproduction: a fenced example containing `sc --brainstorm` matches MODE_Brainstorming; passing the same text through the existing scannable filter yields no match. Repair the trigger layer and its explanation path together. Add positive, fenced, inline-code, quoted and external-runner cases, including Korean prompts. An undocumented natural-language trigger is not necessarily dead; test realistic inputs before deleting alternatives.

Parent reproduction command: `uv run python C:/Users/ajitta/AppData/Local/hermes/cache/scratch/reframing_verify.py`. It writes only throwaway sandbox data under Hermes scratch and removes that data. Final output included `reported_success: true, keys_after: [hooks]`, `budget_warning: true, second_matches: []`, and a raw quoted-mode match versus no filtered match. No model sessions were used.

Other implementation findings were re-checked by a second read-only pass against source (no execution):

| Finding | Verdict | Boundary |
|---|---|---|
| 5 smoke fallback (`auto_improve/guards.py:82,96-109`, `coordinator.py:95-110,164-171`) | Confirmed: fixed 30 s ignores the cycle timeout; repeated `smoke_fail` never stops | Fix both the timeout policy and a consecutive-failure stop; a longer timeout alone is not enough |
| 6 project-dir encoders (`memory_staleness.py:32-43`, `insight_writer.py:102-124`) | Partially confirmed: both keep `.`/`_`; the upstream mapping was not established from source | Do not adopt a universal regex as the fix without checking the current Claude Code encoding; `insight_writer` prefers a supplied `transcript_path` (`:298-305,906-907`), so not every harvest fails |
| 7 prettier shim (`prettier_hook.py:19-31,54-55,66-67`) | Conditionally confirmed: an extension-less POSIX shim is chosen over `prettier.cmd` and errors are swallowed; WinError 193 not reproduced | `shutil.which` alone is not a verified fix — batch-file invocation and argument quoting need a test |
| 8 test runner cwd (`test_runner_hook.py:149-168,220-226`) | Confirmed for pytest/npm; the Makefile branch already uses `make -C` | Return the detected root with the command and pass it as `cwd` |
| 9 stale A/B observations (`parallel_ab/aggregator.py:22-36,87-104`, `orchestrator.py:80-89`) | Confirmed: a leftover `obs-*.json` can be the "winner" | Pass the current run's observation list; do not unconditionally delete prior files |

Paths in the table are relative to `src/superclaude/scripts/`. A separate passing scripts-test run does not establish that the native crash in the combined suite has been fixed. Keep the existing separate-run policy until the combined failure is understood.

## 4. Verified content gaps and their proper interpretation

| Source | Finding | Disposition |
|---|---|---|
| `commands/intent.md:13-18` | Captures the user's wording; unstated fields stay “not stated.” | Keep this provenance contract. Add inferred purpose as a separate labeled hypothesis, never silently rewrite the user's words. |
| `core/RULES.md:21-22` | A concrete completion check is required, but there is no distinction between means and end. | Candidate location for a short purpose-to-observable-result bridge. Preserve verification. |
| `core/rules/RULES_QUALITY.md:13` | Intent verification skips explicit file paths/single-file edits; it checks target ambiguity, not unstated purpose. | Do not rely on this rule to supply I0. Do not remove all scope safeguards. |
| `modes/MODE_Task_Management.md:18,27,32` | Re-entry resumes a checkpoint and forbids work outside an existing list, without an explicit plan-invalidation transition. | Add an evidence-triggered plan revision, if tested; no mandatory re-planning on every turn. |
| `commands/implement.md:14-15` | Approved plan order is followed exactly; departure asks first. | Preserve approval boundaries, but distinguish revising the diagnosis from unauthorized implementation changes. |
| `commands/brainstorm.md:13` | The requester's intent wording is the anchor. | This protects provenance. It should not make user-stated causes or solutions unquestionable facts. Keep source record, distinguish interpretation. |
| `commands/review.md:15-21,44` and `core/RULES.md:10` | Ordinary in-thread review reads the target and context together; delegated review already has a withholding contract. | A default blind independent review is a design choice, not a proven current-model defect; A4 fixtures are at ceiling. Do not claim all review paths lack isolation. |
| `agents/simplicity-guide.md:31-35` | Already restates artifact purpose before simplification and verifies feedback. | Preserve as a partial mechanism; a blanket “no purpose step anywhere” claim is false. |
| `core/rules/RULES_INTERACTION.md:9-11` | Recommends ★ and y/n. | Recommendation formatting is an intentional interface; the current R3 experiment did not test ★ or prove harm. Revisit separately, not as an established bug. |

Paths in the table are relative to `src/superclaude/`.

## 5. Cuts not approved by this audit

1. **Do not hoist agent safety text to a parent-only rule and delete every leaf copy.** Native auto-delegation can invoke an agent without the framework's packet builder. Agents do not inherit the parent's rule modules. A shared source requires a proven delivery route (for example generation/inlining); it is not a free runtime deduplication.
2. **Do not classify git agent/command overlap as a Must fix.** `commands/git.md:21-24` has command flags; `agents/git-workflow.md:40-44` has different authorization semantics and `:76-79` forbids source editing. Shared PR tables are consolidation candidates, but deleting the agent is a public routing change.
3. **Do not add savings across mutually exclusive proposals.** Raw implementation (~5,000 lines) and content (~52 KB) estimates are candidate inventories, not independently verified net cuts. Keep decisions from 2026-10-03 still bind.
4. **Do not describe 14 KB repeated across the catalog as 14 KB saved per agent call.** One agent receives one copy. A catalog-wide saving and per-invocation saving are different quantities.
5. **Do not delete reference files solely because default injection uses a short form.** Verbose/manual loading is a real supported route; show that route is unnecessary before removal.
6. **Do not remove scope restrictions because they appear to oppose reframing.** Observing a broader cause is not permission to expand implementation, send mail, grant credits, change auth or touch production.

## 6. Verification of the current worktree

- `uv run pytest -q`: **3574 passed, 3 skipped** (71.10 s).
- `uv run pytest tests/unit/scripts -o addopts= -q`: **149 passed** (43.14 s), run separately as required.
- `uv run ruff format --check src tests`: **234 files already formatted**.
- `uv run ruff check src tests`: **All checks passed**.
- `git diff --check`: passed. Local links in the synthesis/options/measurement/index resolve; feature Markdown files have LF endings.
- Seven raw leaf reports are over 30 KB. They are retained as uncommitted audit evidence and must be split before integration. The passing suite does not enforce that artifact limit or prove the reported bugs are absent.
- No new headless calls, implementation repairs, installed-config changes, commits or pushes were made during synthesis. Existing harness/fixture changes from the measurement phase remain uncommitted.

## 7. Next decision

Separate correctness/security repairs from the architecture experiment. Compare four alternatives in [05-options.md](./05-options.md); choose an intervention before applying sweeping cuts. Run no more headless sessions until the test allocation and corrected comparison are agreed. Current model-call ledger: 144/180 used, 36 remain. Fresh literature work and intervention validation are not complete.
