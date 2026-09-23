---
status: complete
revised: 2026-09-23
---

# 08 — Implementation record

Branch `fix/opus-5-5-default-model` implements the ready proposals of [04-design.md](./04-design.md): P1, P2, P3, P5 and P7, plus D3 on its recommendation. P4 stays gated: on 2026-09-23 `grep -n '^## .*Opus 5\.5'` over the local `model-migration.md` still returns nothing. The implementation was reviewed by three independent reviewers and corrected ([07-review.md](./07-review.md) round 3); this record describes the result after those fixes.

## 1. What shipped

| Proposal | Files | Change |
|---|---|---|
| P1 | `agents/README.md` | Resolution order corrected to the v2.1.251+ order. The frontmatter-pin override is replaced by a table of the five user-controlled Fable paths and how long each lasts, and a "When Fable 5.1" paragraph gives the routing criterion, list prices and the headless billing note |
| P1 (copy) | `.claude/rules/agent-authoring.md` | The `model` field rule says "omit it" and points to `agents/README.md` Model Routing, in place of a second, stale copy of the resolution order. Checklist step 5 says to omit `model` instead of picking one "by cognitive complexity", which contradicted that rule |
| P2 | `core/rules/RULES_DELEGATION.md` | One `Model:` line in `<sub_agent_decision>`: omit the Agent tool's `model`, pass a model only when the user asked for it for that work |
| P3 | `commands/prompt.md` | `opus55` target; flags resolve to model IDs; session inference for Opus 5, Opus 5.5 and Fable 5.x sessions only; text marked `interim (Opus 5.5 prompting guide)` with its precedence; a fallback to the nearest earlier section, taken only after a Grep for the target's heading finds none; detector rows `think carefully`, "Reasoning write-out" and "No-thinking rule" |
| P3 (hook) | `scripts/context_loader.py` | The injected note's "wins over the mirror table" now carries the interim exception, as does the code comment above it |
| P3 (summaries) | `commands/help.md`, `commands/sc.md`, `commands/README.md`, root `README.md` | "Opus 5 / Fable 5.1" → "Opus 5.5 / Fable 5.1"; the root README entry also says to pass a prompt that asks for written-out reasoning as a file path (§4) |
| P5 | `utils/__init__.py`, `evals/run_eval.py` | Both docstrings name Fable 5.x, Opus 5.5 and Opus 5, say the category set differs by model, and scope the no-retry fact for `reasoning_extraction` to Opus 5.5 |
| P7 | `agents/frontend-architect.md` | The house style names "cream or off-white background"; numbered "01/02/03" labels on sections, steps or list items become a separate never-auto-apply default; the general "cookie-cutter layouts" item is deleted |
| D3 | `commands/auto-improve.md` | The `mutator-model-freeform` gotcha notes that a `fable` mutator, run by `claude -p`, bills usage credits with no consent prompt |

No `.py` file was added or removed, so the component count in `docs/codex/prompting_session_raw/02_component_and_delivery_map.md` is unchanged.

## 2. Departures from 04-design

Each departure is either recorded in 04-design as an amendment or listed here with its source.

| Where | 04-design said | Shipped | Source |
|---|---|---|---|
| P3 No-thinking row | Keep the rule for `claude-opus-5` | Delete for every target | `model-migration.md:972`: "Delete any instruction telling the model not to think or not to reason. That kind of rule *increases* tag leakage"; canaries C1-en-5 and C1-ko-5-file deleted it citing that line. 04 amended |
| P3 keep clause | "Answer directly without deliberating." kept beside `effort: low` on every target | 'claude-opus-5-5' only | Guide line 52 offers it for Opus 5.5; line 972 of the reference contradicts it for Opus 5. 04 amended |
| P3 No-thinking row, effort | `effort: low` "when a deleted rule was there for latency" | Always move the rule's intent to `effort: low` on `--target api`, overriding the default | Guide line 44: lowering effort reduces thinking "more reliably than prompt instructions do"; the latency condition kept C1-en-55-r2 on `medium`. 04 amended |
| P3 unattended paragraph | "add the guide's unattended-run paragraph" | Added as a `[FILL: …]` slot naming its URL, present from the session's first request | The command's `<tools>` cannot read the guide, and `<fact_sourcing>` gives verbatim tuning blocks to the reference; guide line 71 for the timing. 04 amended |
| P3 request config | `"summarized"` "also returns the text but mixed with reasoning summaries" | Dropped | `model-migration.md:1730` states it for Fable 5.1 only. 04 amended |
| P3 self-check | Update the `opus5-verify-inversion` gotcha | Gotcha and the Self-check row both name 'claude-opus-5-5' as carrying the Opus 5 direction | The removal intro takes a row's direction from the delta rule, whose Opus column is carried to 5.5 |
| P3 fallback | "When the reference has no section for the target" | Decided by a Grep for the target's own heading | A reviewer found that the run read the hook's Opus 5 range and never checked for a 5.5 heading, so the rule would keep reporting "no section" after upstream adds one |
| P2 line | "since Fable costs 2.5× Opus 5.5 at list price"; only `fable` named | No ratio; any model only on the user's request | The ratio left out cache reads (1.25×); prices live in `agents/README.md`. 04 amended |
| P5 wording | "Safety classifiers on Fable 5.x, Opus 5.5 and Opus 5"; fallback does not retry `reasoning_extraction` | Adds that the set differs by model and Opus 5 has no `reasoning_extraction`; the no-retry fact is scoped to Opus 5.5 | `model-migration.md:1664` (Opus 5 "cyber-only"); guide line 85 (Opus 5.5 no retry) |
| Copies outside the spec's file list | Not listed | Root `README.md` `/sc:prompt` entry; `.claude/rules/agent-authoring.md:114`; `context_loader.py` note | Each held a live copy of a fact this change corrected |

### Decisions taken on recommendation

- **D1:** the auto-improve mutator stays `sonnet`, as 04 recommends. Nothing changed.
- **D2:** P6 (doctor reports the Claude Code version and model overrides) is not implemented; 04 rates its necessity weak.
- **D3:** applied as 04 recommends, to the gotcha rather than the example row.

These three were user decisions in 04 §2. They were settled on its recommendations without a recorded answer, and each is a one-line revert or a later addition.

## 3. Probe results

All probes ran as `claude -p … --model claude-opus-5-5` (Claude Code 2.1.280). Each ran in its own scratch workspace with its own `superclaude install --scope project`, so no run read this repository's docs. The P3 canary criteria were written before any canary output was read, and the round-2 and round-3 criteria before their runs; the two Korean isolation runs (C1-ko-old, C1-ko-5-file) were judged against the round-1 criteria. The P7 criteria were written before Path A was launched, the Path B direction before Path B was launched, and the naming decision after the before-edit outputs. The pattern scanner was written after the before-edit outputs (see §4). Raw outputs stayed in the session scratchpad and are not committed.

### P3 canaries (`/sc:prompt`, `--permission-mode plan`)

The prompts come from two unrelated domains, a US tax-filing help chat (English) and a company-benefits Q&A bot (Korean). There are also a store-hours voice line (English) and a meeting-notes prompt with no folklore (Korean). In plan mode each rewrite landed in a plan file.

| Run | Tree, flags | Result |
|---|---|---|
| C1-en-55 | first cut, `opus55 --target api` | Removed `Think carefully` (Thinking incantations), the reasoning write-out (Reasoning write-out) and `do not think` (No-thinking rule); config `medium`, `display: "summarized"`, thinking never disabled; named the Opus 5 section read in place of a 5.5 one |
| C1-en-55-r2 | after review fixes | Same removals; ran a heading grep before the fallback; still `medium`, because the row fired only "when the rule was there for latency" |
| C1-en-55-r3 | final | Same removals; "a search for the heading found none"; top-level `medium` with per-message `effort: low` (beta) for the questions the rule called simple, which is the rule's own scope |
| C1-en-5 | first cut, `opus5 --target api` | Removed `Think carefully` and `do not think`, citing reference line 972; kept the reasoning write-out ("Opus 5 has no `reasoning_extraction` refusal category") |
| C1-ko-55-file | first cut, `opus55 --target cc`, prompt as `./benefits-prompt.txt` | All three lines removed, each tied to its row; rewrite in Korean |
| C1-ko-5-file | after review fixes, `opus5 --target cc`, by file | `신중하게 생각해` and `생각하지 말고 바로 답해` removed, the latter "for every target" citing the reference; the write-out kept for 'claude-opus-5' |
| C1-ko-55, C1-ko-5, C1-ko-55 repeat | first cut, inline Korean | Declined before the command ran, 3/3 (§4) |
| C1-ko-old | master's tree, inline Korean | Declined the same way (§4) |
| C2-en-55 | first cut, `opus55 --target api` | "Answer directly without deliberating." kept beside `effort: low`, citing the No-thinking row |
| C2-en-55-r2 | after review fixes | Kept, now scoped to 'claude-opus-5-5'; `effort: "low"` "overrides the `medium` default"; stated that the reference has no `## Migrating to Claude Opus 5.5` section |
| C3-ko-55 | first cut, `opus55 --target cc` | Zero removals, so no new row fired on a clean prompt. It made sourced additions (a notes-tag slot, table columns, a length line from the Opus 5 section) |
| C3-ko-old | master's tree, same prompt | Zero removals and the same kind of additions, so the additions predate this change. Neither tree reports this prompt as "clean" |

### P7 two-path probe (`frontend-architect`, brief "a landing page for a small accounting firm")

Path A gives the brief alone. Path B adds a fixed direction in the agent's own four-field form: `#FFFFFF`, `#1F4E79`, Source Serif 4 headings, Source Sans 3 body. Each path ran twice before the edit and twice after. The five patterns are the guide's example list (prompting guide line 164).

| Pattern | Before A | Before B | After A | After B |
|---|---|---|---|---|
| Cream or off-white page background | 2/2 (`#f4f6f3`, `#f3f5f2`) | n/a (given) | 0/2 (white body) | n/a |
| Italic accent words in headlines | 0/2 | 0/2 | 0/2 | 0/2 |
| Numbered "01/02/03" labels | 2/2 | 1/2 | 0/2 | 0/2 |
| Monospace labels | 0/2 | 0/2 | 0/2 | 0/2 |
| Pill-shaped buttons | 0/2 | 0/2 | 0/2 | 0/2 |

The before-edit numbers appeared on process steps (`counter(step, decimal-leading-zero)`) and on a list (`<span class="ledger-no">01</span>`), not on section labels, which is why the edit names sections, steps and list items. After the edit, off-white moved from the page body to hero and alternate-section bands (`#EEF3F1`, `#f1f5f3`): reduced, not gone. Both after-edit Path A pages share IBM Plex type and a dark green accent. That green (`#1d6b58`) and IBM Plex Sans were already present before the edit, so the edit did not bring in a new style wholesale. Two runs per cell cannot rule out a pattern that appears at low frequency.

Every delegation in the eight runs was an Agent call with no `model` field. That is the behavior P2 writes down, although RULES_DELEGATION.md was not necessarily injected in those runs.

## 4. Observed, not acted on

- **Inline prompts that ask for written-out reasoning.** On an Opus 5.5 session, `/sc:prompt "<Korean prompt with 답변에 네 추론 과정을 풀어서 써>"` ended with `stop_reason: "refusal"` and `stop_details.category: "reasoning_extraction"` before the command loaded. That happened 3/3 on this branch and 1/1 on master, and Claude Code reported "can't respond to this message with Opus 5.5". The same text passed as a file path ran normally (2/2), and the English inline prompt with its own write-out line passed (4/4), so the trigger depends on phrasing. Text inside `prompt.md` cannot help, because the command never loads, so the only change is the root README note. Whether Fable sessions behave the same was not tested.
- **The four-direction step never fired in delegated runs.** In all four Path A runs, the probe session's own delegation prompt told the agent to pick sensible defaults, and the agent said so ("I picked one rather than showing you options, because the brief said to choose a sensible default"). The proposal path in 04 P7 was therefore never measured. What was measured is a build with no design direction, which is the guide's own condition. The agent's instruction-following here was left as it is.
- **Probe method limits.** The pattern scanner (`p7scan.py`) was written after the before-edit outputs. Its off-white test (every channel ≥ `0xEA`, not pure white) is broader than the example range in the pre-registered criteria (`#F5F0E6..#FFFBF2`, warm). Both observed values are cool off-whites outside that example, and the guide's wording is "cream or off-white". The scanner's variable regex also missed `--mist`, which a reviewer found by hand.
- **Probe noise.** The workspaces carried this framework's Stop hook, which replaced each canary's `result` with an insight reply. The rewrites were read from the plan files and the stream.
- **Not run on purpose.** The P2 optional probe in which the user asks for Fable on one delegation was not run, because in `-p` mode it can bill Fable to usage credits with no consent prompt.
- **Stale copies elsewhere.** `okf/superclaude/commands/prompt.md` and `index.md` still say "Opus 5 or Fable 5"; they predate Fable 5.1 and are generated separately. `.claude/rules/agent-authoring.md:33` keeps `model: sonnet` as its example value and stays in 04 §4's deferred docs pass: that block lists every field's syntax, its comment says to omit the field, and it shows `effort: high` the same way although checklist step 4 says to omit `effort`.
- **Hook ranges.** The injected note lists ranges only for 'claude-opus-5' and 'claude-fable-5-1'; P4 adds the 5.5 range once upstream publishes a section.

## 5. Refine pass

After the round-3 fixes, one pass over the whole diff and this folder, in the order: factual errors, logical leaps, missing requirements, repetition. It found no new factual error and no missing 04-design item. Three wording defects were fixed: the P2 line said "the reason is cost: it costs" (now "Fable is the case that matters: it is priced above Opus 5.5"); the frontend-architect sentence read "Never auto-apply it, nor the separate default" (now "it or the separate default"); and this record did not say which criteria the two Korean isolation runs were judged against. Two points were checked and kept. First, the Opus 5 half of the No-thinking row cites the thinking-disabled case, while its effort sentence covers thinking-on use, which the reference's primary recommendation (`model-migration.md:960`, "turn thinking back on and use a lower `effort`") supports. Second, the `--model opus55` example row still says `medium`, because its prompt carries no no-thinking rule.
