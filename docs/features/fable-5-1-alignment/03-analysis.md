---
status: complete
revised: 2026-09-03
---

# Fable 5.1 Alignment — Delta Analysis of `src/superclaude`

Audit of the content framework against the Claude Fable 5.1 release, scoped as a delta on top of [opus5-fable5-alignment](../opus5-fable5-alignment/README.md) (2026-08-02). That work derived the G1–G14 authoring guideline and applied five change sets; this document only covers what Fable 5.1 changed and what the surrounding harness now carries.

## Sources

| Source | Read | Role |
|---|---|---|
| `C:\Users\ajitta\ObsidianVault\fable-5-1-obsidian-notes\` (10 notes + verification report, 2026-09-02) | 2026-09-03 | User's curated summary; every factual claim there was verified against official docs on 2026-09-02 (see `Verification_Report_2026-09-02.md`) |
| `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1` | 2026-09-03 (markdown variant, 54 KB) | Primary: 16 behavioral sections with verbatim prompt blocks |
| `https://platform.claude.com/docs/en/models/fable-5-1/migration-guide` | 2026-09-03 | Primary: breaking changes, 3 behavior changes, recommended changes, checklists |
| `https://platform.claude.com/docs/en/models/fable-5-1/overview` | 2026-09-03 | Primary: IDs, pricing, effort default, status "Active (latest)", released 2026-09-01 |
| Claude Code system prompt of this session (Fable 5.1, CC on Windows) | observed 2026-09-03 | Which Fable 5.1 tuning blocks the harness already injects |
| `docs/features/opus5-fable5-alignment/02-research.md`, `03-analysis.md` | 2026-09-03 | Guideline G1–G14, applied change sets CS1–CS8, rejected findings |
| `docs/analysis/opus-fable-handbook-applicability-ajitta-2026-08-12.md` | 2026-09-03 | Later decisions that overlap this delta: the async-delegation quote it recorded as missing from the handbook (§3.3a), the claim-strength line it added to `save.md` (A1), and the deferred `/sc:implement` definition-of-done item (B3) |

The notes' Verification Report found zero factual errors across roughly 40 checkable claims, so the notes are treated as a reliable index into the primary docs, and the primary docs as the authority where wording matters.

## Method

1. Read all ten notes, then the three primary pages (fetched as `.md` from the docs site into the session scratchpad).
2. Inventoried `src/superclaude` with `grep` for: model-name strings, effort, compaction, evaluator vocabulary, API-level parameters, headless `claude -p` call sites, state/handoff guidance, batching guidance, edit-style guidance, refusal handling.
3. Swept for the specific anti-patterns the Fable 5.1 guide names: narration suppression, anti-formatting rules, compile-check phrasing, base64 in tool output, test-creation pushes, blocking approval gates, chatspeak leftovers.
4. Compared every guide section against what the Claude Code system prompt already carries, so the framework neither duplicates nor contradicts the harness.
5. Cross-checked which unit tests pin the affected files (`tests/unit/test_context_loader.py` pins trigger-map paths; nothing pins `commands/prompt.md` strings).
6. Sent the draft to an independent agent instructed to refute it (default REJECTED under uncertainty), then revalidated each correction against the files myself before applying it. Every primary-source claim survived. Corrections applied: one line number (`prompt.md:45`, not `:41`), `mutator.py` reads no status field at all (the refusal finding got stronger), the harness "Delivering work" block is carried in substance rather than verbatim, one mis-cited gotcha under D1 removed, and the harness-design article's evaluator wording quoted from the article instead of from the notes.

Grep note: Bash `grep` was used for content sweeps rather than the Grep tool's content mode, because of the recorded long-line false-negative gotcha on `description:` lines.

## Headline

**Fable 5.1 is a small delta for this framework, and most of it lands in the harness rather than in the content.** Anthropic's own summary is "your existing Claude Fable 5 prompts should perform well on Claude Fable 5.1 without changes." Of the sixteen prompting-guide sections, the Claude Code system prompt in this session already carries four verbatim (the progress-update line, the "only you see that output" note, the per-turn batching nudge, and the autonomy block), carries the "Delivering work" scope block in substance with different wording, and adds its own writing and formatting rules. None of the framework's content contradicts those blocks: sweeps for narration suppression, anti-formatting language, and compile-check phrasing all returned nothing.

What remains is three kinds of work:

1. **Sediment.** `commands/prompt.md` and three command listings still name Fable 5 as the current target, and one `prompt.md` removal rule leaves API-target rewrites without the completion mechanism the Fable 5.1 guide prescribes.
2. **Gaps the harness does not fill.** Continue-while-delegate-runs, long-lived worker reuse, the six-item compaction preservation list, long-output behavior at `xhigh`, and refusal classification in the headless runners.
3. **Decisions to record rather than edits to make.** Effort tables stay out of `FLAGS.md`, the `>3 files` approval gate stays, the scope-discipline "assessment" sentence stays even though the harness now duplicates it.

## Part 1 — What actually changed from Fable 5 to Fable 5.1

Drawn from the migration guide and prompting guide. Items marked "API" cannot affect a content framework that runs inside Claude Code and ships no Messages API code.

| Change | Kind | Relevance to `src/superclaude` |
|---|---|---|
| Model ID `claude-fable-5-1`; Fable 5.1 "Active (latest)", released 2026-09-01; Fable 5 becomes legacy | identity | `commands/prompt.md`, listings, one code comment |
| Cache reads $0.25/MTok (a quarter of Fable 5); input/output unchanged at $10/$50 | economics | Long-lived subagents with cached prefixes become cheaper; later compaction may be the better trade-off |
| Fewer parallel tool calls in long loops where next steps are implied (coding agents, bash-and-editor harnesses) | behavior | Harness carries the per-turn batching nudge; framework already has three batching statements, add none |
| Fewer progress messages between tool calls | behavior | Harness carries the cadence line; framework has no suppression lines |
| Fewer search calls at `low` effort | behavior | Sessions here run `high` or `ultracode`; hold |
| Denser prose than Fable 5; less bold, fewer lists and headers in chat | behavior | Harness carries writing rules; `MODE_Token_Efficiency` already says complete sentences (CS2) |
| Whole-file rewrites more likely | behavior | Claude Code's Edit tool and Serena symbol edits already steer to targeted edits |
| More likely to reproduce source passages unmarked | behavior | Research surfaces only; hold |
| Over-delivers on open-ended features: nearby fixes, extra committed test files | behavior | R06 covers scope; test-file sizing is not covered anywhere |
| "Finish the whole task" nudge recommended for async workloads | behavior | Harness carries the autonomy block verbatim and the scope block in substance; the `prompt.md` removal rule leaves `--target api` rewrites without the mechanism |
| Fresh-context verifier subagents outperform self-critique on long builds; per-criterion `FAIL — <finding>` output (harness-design article) | agent pattern | `self-review` verdict shape; the delegation rule's verifier prohibition needs the long-build exception it already implies |
| Lead agent should keep working while subagents run | agent pattern | Claude Code's Agent tool already returns immediately; no framework line says to continue |
| Long output at `xhigh`/`max`: the model may draft the deliverable in thinking and again in output | behavior | Doc-producing `/sc:` commands under `ultracode` are exactly this case |
| Compaction: tell the model the six things to preserve | harness | The framework's two preservation lists cover three of six |
| Forced `tool_choice` returns 400; thinking blocks bound to the producing model and conversation; append-only history; prefill 400; `thinking: disabled` 400; 30-day retention; no Priority Tier; beta headers for turn-scoped system messages, mid-conversation effort, `thinking.display: updates`, `fallbacks: "default"` | API | Not applicable: no Messages API code in the repo, and `claude -p` runners inherit Claude Code's handling. `commands/prompt.md` `--target api` reads these from the `claude-api` skill at invocation, by design |
| Refusals: `stop_reason: "refusal"` with `stop_details.category` (`cyber`, `bio`, `reasoning_extraction`); Opus 5 as fallback target | API + harness | Headless runners read `is_error` at most (`evals/run_eval.py`, `parallel_ab/runner.py`) or no status field at all (`auto_improve/mutator.py`) |

Unchanged from Fable 5 and therefore already handled by the August work: the reasoning-extraction refusal category (CS1), compression-as-brevity (CS2), the verifier-subagent prohibition for ordinary tasks (CS3), aggressive-language overtriggering (G5), context anxiety (G6), effort ladder names and the `high` default (G13).

## Part 2 — Coverage matrix: harness vs framework

"Harness" means the Claude Code system prompt observed in this Fable 5.1 session. "Framework" means `src/superclaude`. A duplicate is not neutral: the August research recorded that duplicated instructions compound rather than cancel, so the default action on a harness-carried item is *add nothing*.

| # | Guide section | Harness | Framework | Verdict |
|---|---|---|---|---|
| 1 | Consider all effort levels | `/effort` is user-set; CC-native | `commands/help.md:66` "Effort levels are Claude Code native, not managed by SuperClaude" | No change. The August decision to keep effort tables out of `FLAGS.md` stands; 5.1 adds "re-run the sweep, names don't map across models", which is eval guidance, not content |
| 2 | Ask for user-facing progress updates | Verbatim | No suppression lines (sweep A: zero hits for hold-findings / silent / no-narration phrasing) | No change |
| 3 | Batch independent tool calls | Verbatim, per turn | `core/PRINCIPLES.md` Parallel-Thinking, `core/FLAGS.md` `--concurrency`, `modes/MODE_Orchestration.md` Batching | No change. Three pre-existing statements plus the harness copy; August rejected `orchestration-never-sequential` on the same grounds |
| 4 | Keep the conversation history append-only | Claude Code owns the transcript | Not applicable | Record N/A |
| 5 | Writing density | CC "Writing for the user" rules | `MODE_Token_Efficiency.md` post-CS2 | No change |
| 6 | Formatting in chat | CC rules | Sweep B: zero anti-formatting lines | No change |
| 7 | Quoting retrieved sources | Not carried | `agents/deep-researcher.md:17` "Quote brief, only when needed" has no marked-quotation rule | Hold (Tier 3) until a research output shows unmarked reproduction |
| 8 | Finish the whole task | Autonomy block verbatim; the "Delivering work" scope block in substance ("the requested scope is the deliverable — don't quietly narrow, widen, or transform it"), not the guide's wording | `core/RULES.md` `<scope_discipline>` carries the assessment exception (CS6); R12/R13 default to bounded-proceed; `commands/implement.md:15` and `commands/task.md:16` gate `>3 files` on approval | Keep all three. See Part 4 |
| 9 | Tell the model what to preserve in compaction | Claude Code compacts natively; a `PreCompact` hook cannot add summarizer instructions (Part 5) | `commands/save.md:23-28` `<compaction_strategy>` and `modes/MODE_Token_Efficiency.md` "## Compaction": two answer locations, each covering about 3 of the 6 items | Gap plus duplication (finding D1) |
| 10 | Keep changes and tests to what the task asks | "Delivering work" block carries the scope half; the test-sizing half is not carried | R06; `agents/quality-engineer.md:72` "do not add tests for code you did not change"; `quality-engineer.md:3` description arms "immediately after new behavior added needing systematic coverage" | Watch (Tier 3). August deliberately kept that trigger; revisit only if an eval shows over-committed test files |
| 11 | Search triggering at low effort | Not carried | `modes/MODE_DeepResearch.md`, `agents/deep-researcher.md`, `commands/prompt.md` facts-not-memory | Hold (Tier 3); sessions run `high` |
| 12 | Reduce safeguard false positives | n/a | Sweep C: no compile-check phrasing, no base64 | No change |
| 13 | Prefer targeted edits over whole-file rewrites | Edit tool description ("For partial changes, use Edit") | R17 symbolic-first; Serena edit tools | No change |
| 14 | Leave room for long outputs at `xhigh` and `max` | Not carried (Claude Code sets `max_tokens`; the cost is time and tokens, not truncation) | `core/rules/RULES_DOCS.md` loads on every doc-producing context; nothing says "settle structure in reasoning, write once" | Gap (finding G-d), measure-gated |
| 15 | Let the lead agent keep working while subagents run | Mechanism carried: the Agent tool "runs in the background; you'll be notified". Text says "Once you've delegated a search, don't also run it yourself — wait for the result" (about duplication, not idling) | Sweep L: no line anywhere about continuing independent work while a delegate runs | Gap (finding G-a) |
| 16 | Give vision work tools to crop and zoom | n/a | n/a | No change |
| M1 | Migration: fewer parallel tool calls | Same as #3 | Same as #3 | No change |
| M2 | Migration: fewer progress messages | Same as #2 | Same as #2 | No change |
| M3 | Migration: fewer search calls at `low` | Same as #11 | Same as #11 | Hold |
| M4 | Migration: refusals and `fallbacks` | Claude Code surfaces the refusal to the session; runner-visible fields are undocumented (Part 5) | `evals/run_eval.py:269`, `src/superclaude/scripts/parallel_ab/runner.py:178-180`: `is_error` only | Gap (finding G-e) |
| M5 | Migration: cache reads cheaper, long-lived workers | The Agent tool supports `SendMessage` to continue a spawned agent | Sweep M: no reuse guidance | Gap (finding G-b) |

## Part 3 — Findings

Every quote below was read directly from the file at the cited line on 2026-09-03.

### Sediment (model identity)

**S1 — `commands/prompt.md` targets Fable 5 as current.** Lines 2, 8, 11, 15, 26, 61, 86 name `Fable 5` / `'claude-fable-5'` / `--model opus5|fable5`. The overview page lists Fable 5.1 as "Active (latest)" and the verification report records Fable 5 as "Active (legacy)". The command's `<fact_sourcing>` design (numbers from the `claude-api` skill, direction in the table) holds; only the direction rows and the target alias need the 5.1 delta.

**S2 — `commands/prompt.md:45` leaves the rewrite without the documented completion mechanism.** The `<removal_targets>` row reads:

> `| Proactivity boosters | be thorough, do not be lazy, do not stop early | Delete — both targets are proactive by default |`

Deleting slogans is compatible with the guide, which never endorses slogans. The defect is what the row leaves out. The Fable 5.1 "Finish the whole task" section says that on complex asynchronous workloads, without a nudge, "the model sometimes describes what it would do next instead of doing it ('Next, I'll …') or stops to ask permission for a step the original request already covered," and prescribes a specific two-block addition; the rationale "both targets are proactive by default" already sat next to line 33, which lists "Early stopping" as a Fable-native failure mode, so the inconsistency predates 5.1 and 5.1 sharpens it. Scope: for `--target cc` the harness injects the block itself, so the gap bites on `--target api` rewrites of autonomous prompts. The distinction the row must make: generic slogans still go; the documented autonomy block, a mechanism with a stated trigger rather than a booster, gets *added* there.

**S3 — `commands/prompt.md:26-34` `<model_delta>` rows are Fable 5 shaped.** "Verification instructions … Add — long runs need an explicit checking cadence plus fresh-context verifier subagents" overstates the current guidance. The harness-design article (fetched 2026-09-03): an evaluator "is worth the cost when the task sits beyond what the current model does reliably solo," and for tasks inside that boundary it "became unnecessary overhead"; its evaluator output is per-criterion `FAIL — <finding>` rows. The `PASS`/`FAIL` pair and the read-only rule are the notes' rendering of that pattern, not the article's words. "Native failure modes … Early stopping, context anxiety, unrequested adjacent actions" is missing the 5.1 items: one call per turn in implied loops, fewer progress updates, denser prose, whole-file rewrites, over-committed tests, memory answers at `low`, unmarked quotations. No row covers formatting (5.1 under-formats, so anti-formatting rules must be removed), progress updates, or the compaction preservation instruction for API targets that compact client-side.

**S4 — Listings.** `commands/help.md:54` "prompt: rewrite a prompt for Opus 5 / Fable 5", `commands/sc.md:54`, `commands/README.md:80`, and repo-root `README.md:684` say the same. `README.md:379` cites "Opus 5 / Fable 5 reason natively between tool calls" as the Sequential-Thinking removal rationale (still true of 5.1; the wording just ages).

**S5 — `src/superclaude/scripts/context_loader.py:416`** comment: "Opus 5 / Fable 5 already think between tool calls natively." Harmless; version-neutralize when touched.

**S6 — Authoring SSOT alias list.** `.claude/rules/agent-authoring.md:33` enumerates `model: inherit | sonnet | opus | haiku | full ID`. Claude Code documents a `fable` alias that selects Fable 5.1 (Part 5), and does not list `inherit` as a field value (omission inherits). No agent pins a model (commit `8b5d931`), so this is documentation only.

### Duplication

**D1 — Two compaction preservation lists, neither complete.**

- `commands/save.md:24`: "Preserve (high signal): architecture decisions + rationale, unresolved issues, key patterns discovered, session goal status"
- `modes/MODE_Token_Efficiency.md` "## Compaction": "Preserve: Architecture decisions, unresolved issues, impl details, active file paths"

The 5.1 guide's six items: (1) difficulties and how they were resolved, (2) options tried or set aside and why, (3) anything asked, decided, ruled out, or established as a constraint, stated exactly, (4) where things stand, (5) anything open or promised next, (6) hard-to-reconstruct specifics kept exactly. Both framework lists omit (1) and (2); `MODE_Token_Efficiency`'s "impl details, active file paths" is item-6-shaped, `save.md` has nothing for (6). The rubric was written for a compaction summarizer, so the fit is exact for `save.md` (a session record that a later context resumes from) and weak for the mode (in-session pruning advice, where items (1) and (2) have no use). No repo gotcha records a rejected approach being re-tried after context loss; the motivation for (2) is the guide's own claim plus the cost asymmetry, since re-trying a discarded approach is the most expensive thing a resumed session can do. `save.md` already carries the right adjacent rule ("compaction shortens the record, never upgrades it"), so it is the natural SSOT and the mode becomes a pointer. One surface distinction to state when editing: the mode's `<examples>` row "Listing all six options considered before the recommendation → The recommendation, and the one option that was close" governs *responses*; the session record is a different surface and keeps the set-aside options.

**D2 — `core/RULES.md` `<scope_discipline>` assessment sentence.** Added in CS6 because nothing in the framework carried it. The Fable 5.1 harness now injects the same sentence. It costs one always-loaded sentence, holds on any model, and the harness copy is only confirmed for Fable 5.1 sessions. Keep; record as a known duplicate so nobody re-adds a third.

**D3 — Batching.** Three framework statements plus the harness nudge. August already declined to add or remove here. Keep.

### Gaps (neither harness nor framework)

**G-a — Continue while a delegate runs.** `core/rules/RULES_DELEGATION.md` `<sub_agent_decision>` decides whether to spawn and how to pack the prompt, and never says what the main loop does while the delegate runs. The 2026-08-12 applicability analysis already quoted the Fable 5 guide's "prefer asynchronous communication between orchestrator and subagents over blocking" as an item the handbook lacked (§3.3a), and no later commit wrote it into the rule. The Fable 5.1 guide: "letting the lead continue while subagents run lowers average time to completion at similar quality, token usage, and cost … The model still often chooses to wait." Claude Code already returns immediately from Agent, so a one-sentence rule is all that is missing. It must not contradict the harness's "don't also run the delegated search yourself."

**G-b — Reuse a long-lived worker.** Claude Code offers `SendMessage` to continue a spawned agent with its context intact. With cache reads at a quarter of the Fable 5 price, follow-up work in the same stream is cheaper on the existing worker than on a fresh spawn. This is the "long-lived subagents" pattern the August research already endorsed for Fable 5 (G2) but never wrote into the rule.

**G-c — Six-item compaction list.** See D1. One layer only: the framework's own session-save (SSOT in `save.md`). Claude Code's native compaction cannot take instructions from a hook (Part 5), so the framework cannot install the list there.

**G-d — Long deliverables at `xhigh`/`max`.** `ultracode` sends `xhigh` to the model (Claude Code model-config reference, Part 5; the repo recorded the same in `docs/features/ultracode-sc-integration/02-research.md:27`), and `/sc:plan`, `/sc:design`, `/sc:roadmap`, `/sc:research`, `/sc:index` produce multi-section documents. The guide's mitigation is a note that the model should use "the reasoning space to reason and the output space to write" and not draft the deliverable twice; it reports the note "makes the thinking much shorter on prose and code requests." `RULES_DOCS.md` loads on exactly those contexts. Unmeasured here; gate on a before/after run.

**G-e — Refusal classification in headless runners.** `evals/run_eval.py:269` (`if event.get("is_error")`) and `parallel_ab/runner.py:178-180` (`rc == 0 and not parsed.is_error`) treat every non-success alike. `auto_improve/mutator.py` is worse: it reads no status field, gating only on a non-zero exit code (`:100`), JSON parse failure (`:108`), and an empty `result` (`:119`), so a refusal that returns exit 0 with refusal text in `result` is accepted as a valid mutation rationale. The August canary wanted to *measure* `reasoning_extraction` refusals and could not distinguish them from harness errors. Fable 5.1 keeps the same categories, so a refusal row in `report.md` and in the A/B matrix is the instrument the canary lacks. The exact JSON fields available from `claude -p` are checked in Part 5.

**G-f — Verifier verdict vocabulary.** `agents/self-review.md:31` outputs "Checklist: pass/fail per dimension" and its gotcha at `:72` already says "report 'verification not possible: [reason]'". The harness-design article's evaluator emits per-criterion `FAIL — <finding>` rows with the failing location; the notes render that as a `PASS`/`FAIL` verdict and add `UNVERIFIED`. Cosmetic alignment; Tier 3.

**G-g — Feature contracts with fail-until-evidence status.** `commands/roadmap.md` has no status or evidence fields (grep: only "Validate: Quality gates + workflow completeness"). The long-running-harness pattern (a feature list starting `fail`, flipped only with evidence) is a real capability the framework lacks, but no observed failure in this repo motivates it and it is a design addition, not an alignment fix. The 2026-08-12 applicability analysis deferred the adjacent `/sc:implement` definition-of-done block (its B3) for the same reason, pending root-cause isolation of the `bugfix-scope-creep` `verification` 0/1 result. Recorded so it is a deliberate deferral; it fails R18 today.

**G-h / G-i / G-j — Low-effort search nudge, quoting example, over-committed-tests probe.** All hold until observed; G-j is the cheapest to instrument (count committed test files under the existing `scope` tag).

### Hygiene carried forward

Chatspeak leftovers (`b4`, `u r`, `w/`, `thru`) remain in more than 20 files (sweep F: `agents/security-engineer.md` 10, `agents/insight-analyst.md` 10, `modes/MODE_Task_Management.md` 6, and so on). August listed `MODE_Task_Management.md` chatspeak as a PLAUSIBLE ride-along and did not apply it. `.claude/rules/xml-prose-format.md` does not ban abbreviations, so this is not a spec violation. It is instruction-side, not output-side, so the Fable 5.1 writing guidance does not directly apply. Tier 3, opportunistic.

## Part 4 — Decided non-changes

Recorded so the next audit does not re-litigate them.

| Item | Decision | Reason |
|---|---|---|
| Effort guidance in `FLAGS.md` | Do not add | The August verdict stands: the model cannot set its own effort in Claude Code. Fable 5.1's "re-run the effort sweep" is an instruction to the eval harness, and `evals/README.md` already prescribes `--canary --model <new-model>` on each release |
| `>3 files → wait user approval` (`implement.md:15`, `task.md:16`, R12/R13) | Keep | The harness autonomy block explicitly allows "if your product needs the model to stop for specific confirmations, add a sentence after it listing them." The R12 four-class gate is that list. Known cost: headless runs cannot answer it (August `plan-routing` eval) |
| `<scope_discipline>` assessment sentence in `core/RULES.md` | Keep | D2 |
| Batching statements | Add nothing, remove nothing | D3 |
| Agent `model:` pins | Stay `inherit` | The notes' routing advice (Opus 5 default, Fable 5.1 as the promotion path) is a user-level choice; a pin written against one generation misroutes after the next (`agents/README.md:88`) |
| `evals` / `auto_improve` default model `sonnet` | Keep | Cost; the canary takes `--model` explicitly |
| API-level migration items | Not applicable | No Messages API code in the repo |
| `quality-engineer` proactive test trigger | Keep for now | August judged the arming intentional; 5.1's over-commit tendency is a reason to *measure* (G-j), not to edit without a failure |

## Part 5 — Harness facts (checked 2026-09-03 against `code.claude.com/docs`)

Checked by a `claude-code-guide` agent against the hooks, headless, model-config, and sub-agents reference pages; the answers below are its report, with the one item I could test locally noted.

| Question | Answer | Effect on the plan |
|---|---|---|
| Can a `PreCompact` hook add preservation instructions that the compaction summarizer honors? | **No.** The hooks reference states that Claude Code discards a `PreCompact` hook's `systemMessage` and `continue` fields. A hook can only block compaction (exit 2 or `{"decision":"block"}`). Custom instructions exist only for manual `/compact <text>`, delivered to the hook as `custom_instructions` | G-c has one layer, the session-save SSOT (plan B2/B3). The hook idea is dropped. `context_reset.py` re-injecting dynamic contexts after `compact` stays the mitigation for rule drift |
| Which `claude -p` JSON fields expose a refusal? | **Undocumented** in the headless reference, but readable from the installed CLI binary (2.1.258, checked 2026-09-03): the result-message schema carries a top-level nullable `stop_reason` and no `stop_details` (zero result objects carry it), and the refusal path sets `message.stop_reason = "refusal"` plus `message.stop_details` on the assistant message. So `stream-json` exposes the category on `assistant` events and `--output-format json` exposes only the fact of the refusal | G-e detects on the assistant message first and the result object second, never downgrading a known category; single-object runners report `unknown` |
| Does a `fable` model alias exist? Valid subagent `model:` values? | **Yes.** `/model fable` and `claude --model fable` select Fable 5.1; env override `ANTHROPIC_DEFAULT_FABLE_MODEL`. Subagent `model:` accepts `fable` and full IDs. `inherit` is not in the documented frontmatter field list; omitting the field inherits | S6 becomes a concrete one-line comment edit in `.claude/rules/agent-authoring.md:33`; no agent file changes, since none pins a model |
| Does Claude Code expose the session effort level to hooks or the model? | **Undocumented.** `/effort` levels per the model-config page are `low`, `normal`, `high`, `max`, `ultracode`, where `ultracode` "sends `xhigh` to the model and additionally has Claude orchestrate dynamic workflows". Subagent frontmatter has an `effort:` field (the framework removed it deliberately, commit `8edd05d`) | G-d ships unconditional. Observation, no action: `.claude/rules/schemas.yaml` `effort_values` uses the API names (`medium`, `xhigh`), which is the subagent `effort:` surface, a different surface from `/effort` |
| Are the Fable 5.1 tuning blocks in the Claude Code system prompt documented? | **No.** Nothing in the docs or release notes describes them | The observation in Part 2 stays n=1, which is why D2 keeps the always-loaded duplicate |

## Limits

- **No measurement in this document.** Every behavioral claim is Anthropic's published guidance plus the framework's own recorded research. The plan's gate is the existing canary suite run on `claude-fable-5-1`.
- **Harness observation is n=1.** The system-prompt contents were read in one Fable 5.1 session on Claude Code for Windows. Whether Opus 5 sessions receive the same blocks was not checked, which is why D2 keeps the duplicate.
- **Notes are a secondary source.** They were used as an index; wording in this document comes from the primary pages fetched on 2026-09-03.
