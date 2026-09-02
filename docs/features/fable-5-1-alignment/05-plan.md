---
status: implementing
revised: 2026-09-03
---

# Fable 5.1 Alignment — Improvement Plan for `src/superclaude`

**Source:** [03-analysis.md](./03-analysis.md) (delta audit, 2026-09-03) on top of [opus5-fable5-alignment](../opus5-fable5-alignment/README.md).
**Scope (R06):** content edits in `src/superclaude`, one code comment, refusal classification in the three headless runners, and eval-harness instrumentation. No new agents, modes, or commands. No `model:` pins. Root `README.md` and `.claude/rules/agent-authoring.md` are touched only for sediment that would otherwise contradict the edited command.
**Gate:** approved by the user on 2026-09-03; status moved to `implementing`. Open questions in section 4 resolved by their stated defaults unless the user overrides.

**Guiding principle.** Claude Code now injects the Fable 5.1 tuning blocks itself. The framework's job is to say nothing the harness already says, contradict nothing the harness says, and fill only the gaps the harness leaves. Every addition below is one to three sentences in an on-demand module; the always-loaded tier gains zero lines.

---

## 1. Change sets

Ordered by certainty. CS-A and CS-B need no probe (correctness under the framework's own rules). CS-C is code with unit tests. CS-D is behavior and is measurement-gated. CS-E is deferred.

### CS-A — Sediment: Fable 5.1 as the current Fable target

**A1. `commands/prompt.md`** (finding S1–S3). Direction rows only; numbers keep coming from the `claude-api` skill at invocation, which the migration guide confirms is Fable 5.1-aware (`/claude-api migrate this project to claude-fable-5-1`).

| Location | Before | After |
|---|---|---|
| line 2 `description`, line 8 `<mission>` | "Claude Opus 5 or Fable 5" | "Claude Opus 5 or Fable 5.1" |
| line 11 `<syntax>` | `[--model opus5\|fable5]` | `[--model opus5\|fable51]` — accept `fable5` as a legacy alias for the same column, since Fable 5 prompts run unchanged on 5.1 |
| line 15 flow step 2 | `'claude-opus-5' or 'claude-fable-5'` | `'claude-opus-5' or 'claude-fable-5-1'` |
| line 26 `<model_delta>` header | `'claude-fable-5'` | `'claude-fable-5-1'` |
| line 61 `<context_targets>` Reason | `'claude-fable-5'` | `'claude-fable-5-1'` |
| line 86 example | `--model fable5` | `--model fable51` |

Proposed `<model_delta>` table (replaces lines 26–34):

| Axis | `'claude-opus-5'` | `'claude-fable-5-1'` |
|---|---|---|
| Verification instructions | Delete — it self-verifies unprompted, and "double-check" causes over-verification | Keep only claim-grounding (report what a tool result shows); add a fresh-context, read-only verifier with a PASS/FAIL verdict only for long autonomous builds beyond what the model solves reliably alone |
| Subagent delegation | Cap it — this model reaches for subagents readily | Keep it; tell the lead to continue independent work while workers run, and to reuse a long-lived worker for follow-ups, since cache reads are cheap |
| Tool-call batching | Issues parallel calls as expected | In loops where the next reads are implied rather than named it may issue one call per turn; append the one-sentence batching nudge each turn (a turn-scoped system message on `--target api`) |
| Progress updates | Narrates readily; give it a cadence | Writes fewer updates; delete any hold-for-final line first, then add a when-and-what line only if the interface shows text between calls |
| Task completion | Pair scope discipline with "finish the whole task" | The same, and on autonomous workloads add the documented two-block autonomy text; leave it out of human-in-the-loop prompts |
| Prescriptiveness | Add scope discipline; it expands task scope | De-prescribe; state what to leave out (nearby fixes, extra committed test files) |
| Verbosity and formatting | A brief conciseness instruction cuts length; effort is not the lever | Prose runs denser than Fable 5: define mannered prose as the anti-pattern; remove anti-formatting rules, because it under-formats |
| Written deliverables | Calibrate file length explicitly | Lead with the outcome; at `xhigh` or `max` append the single-limit note naming `max_tokens` |
| Native failure modes | Scope expansion, self-correction narration | Early stopping, unrequested adjacent actions, one call per turn in implied loops, whole-file rewrites, over-committed tests, memory answers at `low`, unmarked quotation of sources |
| Intent framing | Full task specification up front in one turn | The reason behind the request, not just the request |

Proposed `<removal_targets>` changes:

| Row | Change |
|---|---|
| Proactivity boosters (line 45) | Signal stays `be thorough`, `do not be lazy`, bare `do not stop early`. Action becomes: "Delete the slogans. Where the prompt drives autonomous multi-step work, replace them with the documented autonomy block (operating autonomously, reversible steps proceed, the assessment exception, check the last paragraph): a mechanism with a stated trigger, not a booster. On `--target cc` the harness already injects it, so add it only for `--target api`." |
| New: Narration suppression | Signal `hold all findings for the final response`, `no commentary between steps`. Action: delete on `'claude-fable-5-1'`; it already under-narrates |
| New: Anti-formatting rules | Signal `no bullet points`, `never use headers`, `avoid bold`. Action: replace with a conditional rule (lists when the content is multifaceted, plain prose when asked) on `'claude-fable-5-1'` |

Proposed additions elsewhere in the file:

- `<context_targets>`: "Compaction contract (`--target api`, client-side compaction only): the six things a summary must keep — problems and their resolutions, options tried or set aside, decisions and constraints stated exactly, current position, open items, and exact specifics."
- `<outputs>` Request-config: "effort, thinking display, `max_tokens` floor, refusal fallback target, and the per-turn batching nudge placement — `--target api` only."
- `<gotchas>`: `booster-vs-mechanism: the autonomy block is not a proactivity booster; deleting it under the booster rule reintroduces early stopping on 'claude-fable-5-1'.`

Durability note: the column header names a release and will re-stale at the next one. The alternative is a neutral `--model opus|fable` alias resolving to "the current release per the `claude-api` skill" with release-specific rows tagged. Recommended: keep the explicit alias (the command is release-specific by construction, and the August research already established that direction rows age slowly).

**A2. Listings** (S4): `commands/help.md:54`, `commands/sc.md:54`, `commands/README.md:80`, root `README.md:684` → "Opus 5 / Fable 5.1". Root `README.md:379` → "Claude 5-family models reason natively between tool calls".

**A3. `scripts/context_loader.py:416`** (S5): comment → "Claude 5-family models already think between tool calls natively."

**A4. `.claude/rules/agent-authoring.md:33`** (S6): the comment `# inherit | sonnet | opus | haiku | full ID (e.g. claude-opus-4-7). Default: inherit` → `# sonnet | opus | haiku | fable | full ID (e.g. claude-fable-5-1). Omit the field to inherit the session model (Claude Code documents no inherit keyword)`. No agent file changes; `schemas.yaml` carries no model enum, so no test pins this.

Verification: Level 0 (docs) plus `uv run pytest` because `test_context_loader.py` pins trigger-map paths and the codex component map counts modules.

### CS-B — Gaps the harness leaves, filled in on-demand modules

**B1. `core/rules/RULES_DELEGATION.md` `<sub_agent_decision>`** (G-a, G-b). Add one line after "Spawn discipline":

> Run-alongside: while a delegate runs, continue main-loop work that does not depend on its result (the Agent tool returns immediately and notifies on completion); never redo the delegated work yourself, and wait only when the next step needs the result. For follow-up work in the same stream, continue the existing delegate with SendMessage rather than spawning a fresh one — its context is intact and cached.

Optional clause on the existing "Never spawn a sub-agent to verify" sentence, for teams that run multi-hour autonomous builds through the framework:

> Exception: a fresh-context, read-only verifier returning PASS or FAIL with evidence, on a multi-hour autonomous build that exceeds what the model solves reliably alone. Ordinary tasks verify inline.

Include the exception only if such builds actually run here; otherwise it is a speculative rule (G9).

**B2. `commands/save.md` `<compaction_strategy>`** (D1, G-c layer 1). Replace the Preserve line:

> Preserve (high signal): (1) problems hit and how they were resolved; (2) approaches tried or set aside, and why; (3) what was asked, decided, ruled out, or set as a constraint — stated exactly; (4) where the work stands; (5) what is open or promised next; (6) exact names, numbers, paths, commands, and wording that would be hard to reconstruct. Session goal status rides on (4).

Keep the Discard, Claim-strength, and Format lines unchanged. This list governs the session record that a later context resumes from; it does not change `MODE_Token_Efficiency`'s response-selectivity example ("the recommendation, and the one option that was close"), which is about what a *reply* includes. State that distinction in the commit body so the two are not read as a contradiction.

**B3. `modes/MODE_Token_Efficiency.md` "## Compaction"** (D1). Replace the Preserve and Discard bullets with a pointer, in the pattern `commands/load.md` already uses for storage:

> Preserve/discard list: SSOT in /sc:save `<compaction_strategy>` (installed sibling commands/sc/save.md).

Keep "When:" and "Safest action:".

Verification: Level 0 plus `uv run pytest` (trigger-map test), then `superclaude install --force --scope user` and a re-read of the installed files to confirm the pointer resolves.

### CS-C — Refusal classification in the headless runners (G-e)

Fable 5.1 keeps `stop_reason: "refusal"` with `stop_details.category`. The runners currently fold refusals into generic errors, which is exactly what stopped the August canary from measuring the `reasoning_extraction` risk it was built to measure. The Claude Code headless reference does not document refusal fields, but the installed CLI binary (2.1.258) does: its result-message schema carries a top-level nullable `stop_reason` and no `stop_details`, and the refusal path sets both fields on the assistant message. So: in `stream-json` the category comes from `assistant` events (the `_parse_stream` loop in `evals/run_eval.py` already reads that object) and the `result` event confirms the refusal without a category; in `--output-format json` (parallel_ab, auto_improve) the refusal is detectable but the category is `unknown` until the CLI adds it. A `subtype` naming a refusal is the fallback; `is_error` stays a generic error.

| File | Change |
|---|---|
| `src/superclaude/scripts/parallel_ab/runner.py` | Parse the refusal signal into `ParsedResult`; a refusal gets its own `exit_status: "refusal"` and carries `refusal_category` in the observation JSON (emitted only when set, so non-refusal observations keep the documented schema shape). Applied: `aggregator.py` renders the category inside the existing `exit` cell (`refusal (cyber)`) rather than adding a column, which keeps the matrix header and its tests unchanged |
| `evals/run_eval.py` | Applied: `TaskResult` gains `refusal_category`; the task matrix shows `REFUSED` in the existing cell and `report.md` gains a `## Refusals` section (arm, task, category); `results.json` carries the field. A result-level refusal never downgrades a category captured from the assistant event, and a refusal keeps precedence over `is_error` text on the same run. Exit code unchanged: an errored or refused task already exits 2 through `gates_ok`, which predates this work |
| `src/superclaude/scripts/auto_improve/mutator.py` | Today it gates only on exit code, JSON parse, and an empty `result` (`:100`, `:108`, `:119`), so a refusal returned with exit 0 is accepted as a mutation rationale. Read the refusal signal from the payload and return `refused=True` with the category. Applied: the coordinator's existing error path records it under the unchanged `mutation_error` TSV status with a `mutator refused (category=…)` description, so `results_tsv.STATUS_VALUES` (a schema) stays put; the real defect, refusal text applied as a rationale, is closed |
| `evals/README.md` | Applied: `claude-fable-5-1` named in the model-release canary instructions plus the `REFUSED` / Refusals explanation. The cross-model probe table lives in the August feature README; its Fable 5.1 column is added with the branch canary run (CS-D gate), not with CS-C |
| `tests/unit/` | Applied: inline refusal payloads, 2–6 tests per runner (detector branches, precedence over `is_error` and non-zero exit, near-miss negative control, aggregator cell and winner exclusion, coordinator row, report branches). No new `.py` under `src/superclaude/`, so the codex module count stays put |
| `docs/specs/parallel-ab-harness-design-ajitta-2026-05-14.md` | Applied: the observation schema block names the four-value `exit_status` enum and the optional `refusal_category` key, so `observation.py`'s "matches the spec" docstring stays true |

Review outcome (adversarial workflow, 3 lenses, 2 refuters per finding, 27 survivors): the one high-severity finding was the result-event downgrade to `unknown`, fixed above with a test that reproduces the real two-event shape. Follow-ups recorded, not applied: a deterministic refusal in `auto_improve` re-runs every cycle until the budget or plateau ends it (the coordinator does not read `refused`); refused cycles, like every `mutation_error`, leave the agent's earlier edits in the worktree (the error text now says "rationale discarded" rather than claiming no mutation); `parallel_ab` would need `stream-json` to learn the category; the detector is three small copies (`parallel_ab`, `auto_improve`, `evals`), kept separate because `evals/` is documented as not importing the package.

Verification: Level 2 (`uv run pytest`), then one live `parallel_ab` smoke with a benign spec on `claude-fable-5-1` to confirm the normal path is unchanged.

### CS-D — Measurement-gated behavior addition (G-d)

**D1. `core/rules/RULES_DOCS.md`**, one sentence at the top of `<doc_output_convention>`:

> Long documents: settle the structure and the hard decisions before writing, then write the document once; drafting it in full while reasoning and again as output doubles the turn without improving it.

The module loads only on doc-producing contexts, so the cost is zero elsewhere. Claude Code does not document exposing the effort level to hooks or the model, so the sentence ships unconditional; the guide reports the note shortens thinking on prose requests, and at `high` it is at worst a no-op.

Gate: run a doc-producing task (`plan-routing` is the closest existing canary task) on `claude-fable-5-1` under `ultracode`, `master` vs branch, and compare duration and output tokens, which the harness already captures. Ship only if duration or tokens drop with no check regressing. Two runs per arm minimum; single runs cannot separate this from noise.

**D2. Claude Code compaction instruction — dropped.** The hooks reference states that Claude Code discards a `PreCompact` hook's `systemMessage` and `continue` fields, so the six-item list cannot be installed into native compaction. The session-save SSOT (B2) is the whole fix; `context_reset.py`'s post-compact re-injection of dynamic contexts remains the mitigation for rule drift. The manual path, `/compact <instructions>`, exists for the user and needs nothing from the framework.

### CS-E — Deferred, with the trigger that would promote each

| Item | Promote when |
|---|---|
| G-f `self-review` verdict `PASS` / `FAIL` (criterion, evidence, repro) / `UNVERIFIED` | A downstream consumer needs to filter verdicts deterministically |
| G-g Feature contracts (`status: fail` until evidence) in `/sc:roadmap` and `/sc:task` output | A premature "done" on a multi-phase roadmap is observed in an eval or a session |
| G-h Low-effort search nudge in `MODE_DeepResearch.md` | A research session at `low`/`medium` answers a fast-moving question from memory |
| G-i One worked example with rationale for quoting in research outputs | A research deliverable reproduces a source passage unmarked |
| G-j Eval check counting committed test files under `scope` | Already covered: `bugfix-scope-creep` carries `git_diff_max_files: 2` under the `scope` tag, so an extra committed test file fails that check today. No new check added; the `quality-engineer` trigger is revisited only if that check starts failing on Fable 5.1 |
| Chatspeak hygiene (`b4`, `u r`, `w/`, `thru`) across 20+ files | Opportunistically, one file at a time when that file is edited for another reason |

---

## 2. Decided non-changes

Recorded in [03-analysis.md Part 4](./03-analysis.md#part-4--decided-non-changes). In one line each: no effort table in `FLAGS.md`; the `>3 files` approval gate stays as the product's listed confirmation point; the scope-discipline assessment sentence stays as a known harness duplicate; batching gains no fourth statement; agents stay `model: inherit`; runner defaults stay `sonnet`; API-level migration items are not applicable; the `quality-engineer` trigger is measured (G-j) before it is touched.

---

## 3. Verification gates and cost

| Gate | Command | Pass condition |
|---|---|---|
| Unit suite | `uv run pytest` | Exit 0. Baseline with these three docs added, 2026-09-03: 2470 passed, 25 skipped. Two scope tests (`test_falls_back_to_user_scope_with_no_install_above`, `test_explicit_local_scope_names_the_cwd_when_no_install_is_found`) are environment-dependent when pytest's tmp root nests under `~/.claude/tmp/`; they passed today and predate this work either way |
| Format | `make format` | Clean |
| Durability lint | part of `uv run pytest` (`test_version_consistency.py`) | It scans `core/**/*.md`, `src/superclaude/*/README.md`, and `.claude/rules/*.md` for expiring phrasing (`as of <date>`, `last reviewed`, `verify quarterly`, pass counts). Every sentence added by CS-A, CS-B, and CS-D must avoid those shapes; the proposed texts above do |
| Harness dry run | `uv run python evals/run_eval.py --dry-run` | Builds and validates, zero API calls |
| Canary, baseline | `uv run python evals/run_eval.py --canary --model claude-fable-5-1` on a `master` worktree | Recorded per task; 7/7 hard gates |
| Canary, branch | Same on the feature branch | No task below its baseline; 7/7 hard gates; `probe-scope-restraint` 3/3 and `probe-introspect-marker` 1/1 (extends the August cross-model table with a Fable 5.1 column) |
| CS-D measurement | `plan-routing` (or a doc-producing probe), 2 runs per arm | Duration or output tokens drop, no check regresses |
| Install sync | `superclaude install --force --scope user`, then `uv run pytest tests/unit/test_context_loader.py` | Trigger-map paths resolve in the installed tree |

Cost estimate, unmeasured: the August canary (10 tasks, `sonnet`) cost $2.51. Fable 5.1 lists at five times Sonnet 5's per-token price, and the suite is now 14 tasks, so one canary run is roughly ~$15 to ~$18, and the baseline-plus-branch pair roughly ~$30 to ~$35. Cheaper cache reads may pull that down. The user decides whether to spend this; without it, CS-A through CS-C still ship on correctness grounds, and only CS-D waits.

---

## 4. Open questions

Resolved on 2026-09-03 against the Claude Code docs (details in [03-analysis.md Part 5](./03-analysis.md#part-5--harness-facts-checked-2026-09-03-against-codeclaudecomdocs)): a `PreCompact` hook cannot add summarizer instructions (D2 dropped); a `fable` alias selects Fable 5.1 (A4 concrete); effort exposure is undocumented (D1 unconditional).

| Question | Blocks | Default if unanswered |
|---|---|---|
| Which `claude -p` JSON fields expose a refusal? (undocumented; no local transcript) | CS-C field names | Detect on assistant `message.stop_reason` and the result `subtype`; fixture from the first captured real refusal |
| Approve roughly ~$30 to ~$35 of canary spend on `claude-fable-5-1`? | Gates for CS-D; confidence for CS-B | CS-A to CS-C ship without it |
| Do multi-hour autonomous builds run through the framework here? | The optional verifier exception in B1 | Omit the exception |
| `prompt.md` alias: explicit `fable51` (recommended) or neutral `fable` resolving to the current release? | CS-A1 syntax line | Explicit `fable51` |

---

## 5. Sequencing and rollback

1. Branch `feature/fable-5-1-alignment` from `integration` (`master ← integration ← feature/*`).
2. One commit per change set: `docs(prompt): …` for CS-A, `feat(rules): …` for CS-B, `feat(evals): …` for CS-C, `feat(rules): …` for CS-D only after its gate passes.
3. After each commit: `uv run pytest`, then `superclaude install --force --scope user` so the next interactive session runs the new content.
4. Canary baseline before CS-B lands, branch run after CS-B and CS-C.
5. Rollback is a plain revert of the change-set commit followed by an install sync; nothing here migrates data or touches user settings.
6. On completion, update this feature's README status table with commit hashes and the canary numbers, in the shape the August README uses.
