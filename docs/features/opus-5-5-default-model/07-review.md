---
status: complete
revised: 2026-09-23
---

# 07 — Independent review and resolution

## Round 1: the folder

`/sc:review docs/features/opus-5-5-default-model`. One independent reviewer read README, 02, 03 and 04 against the original request, the doc convention, the downloaded source pages and every cited `src/superclaude` file:line. It did not see the author's rationale or [06-self-refine.md](./06-self-refine.md). The main loop re-checked each finding against its source before applying it. All findings were accepted.

### Findings and what changed

| ID | Finding | Evidence re-checked | Resolution |
|---|---|---|---|
| C1 | "`opus` pins the 200K variant" was false | `probe_opus.json` `contextWindow: 1000000`; model-config: "Opus 4.7 and later run with the 1M window on every plan … You don't select a `[1m]` variant"; changelog 2.1.280: "1M context" | 03 §1 table and bullets, README summary and 04 §3 rejection rows rewritten; the case against a settings write now rests on overriding user and team choice |
| C2 | `/model fable` was presented as a one-session switch | model-config: "Choosing one with `/model` saves it as the selected model in your user settings, so later sessions start on it"; `--model` applies "only to the session you launch with" it | P1 lists each path with its duration and recommends `claude --model fable`; 02 §3, 03 §1 and README updated |
| I1 | "2.5× per token" ignored cache reads | Fable 5.1 overview: cache reads 2.5% of base on Fable 5.1, 5% on Opus 5.5, so $0.25 against $0.20 | Every occurrence now says 2.5× at list input/output and 1.25× on cache reads |
| I2 | P3 made the mirror table a source without amending `prompt.md:26` and `facts-not-memory`, and relabeled Opus 5 rows as 5.5 facts | `prompt.md:26` "This table is a mirror, not a source"; `:112` | P3 item 3 amends both rules for rows marked `interim`, keeps the column header as `Opus (5 verified; 5.5 carried from 5 unless marked)`, and P4 deletes the interim rows |
| I3 | Request-config and effort quotes named the wrong pages | "matches or exceeds" and "Reserve `xhigh` and `max`…" are at prompting guide lines 38 and 43; the thinking and `tool_choice` facts were read from What's new, not the overview or migration guide | 02 §1 and 04 P3 attributions corrected |
| I4 | P5 missed a second copy of the docstring | `evals/run_eval.py:289` carries "Fable 5.x safety classifiers"; the pin test compares behavior only | P5 edits both copies, with a grep check |
| S1 | Sonnet 5 pricing was already in the sources | Fable 5.1 overview table: Sonnet 5 $2/$10 | D1 now recommends keeping `sonnet` outright |
| S2 | The Fable 1M question was already answered | model-config line on 1M windows; probe `contextWindow` | Removed from 03 §5 unknowns |
| S3 | Text between tool calls now arrives in `thinking` blocks | What's new in Opus 5.5 | Added to P3 request-config |
| S4 | `auto-improve.md:48` shows a headless Fable loop with no billing note | model-config headless billing line | New decision D3 |
| S5 | Overrides of the default were not covered | model-config: saved `model`, organization default, `ANTHROPIC_DEFAULT_MODEL`, resumed session | 04 intro and 03 §5 state them; P6 now leads with a saved-`model` check |
| S6 | The `opus5` alias carried a hidden `--target api` exception | P3 item 1 as drafted | Replaced by one rule for every flag: read the named model's own section, or the nearest earlier one in the family |
| S7 | Anchor line range off by a few lines | `context_loader.py:965-969` | 03 S3 row corrected |
| S8 | Enterprise org-billing members never see the consent prompt | model-config | Added to 02 §3 |

### Reviewer's verdicts on the acceptance criteria (before fixes)

1. Price ratio: partial (I1). 2. Headless billing scope: pass. 3. Request-config sources: fail (I3). 4. Quotes verbatim: mostly pass; the system-card quote the reviewer could not reach was matched afterwards in the downloaded system-card text ("overeager or destructive actions is the lowest among our recent models"). 5. Evaluation verdict present: pass. 6. README convention: pass.

### Still unverified after round 1

- Community sources (HN, Willison, Latent Space, The Decoder, CodeRabbit, Every, Artificial Analysis): none was downloaded, so their figures stay tagged COMMUNITY and carry no proposal.
- The Opus 5.5 overview and migration guide pages were never fetched; every fact attributed to them was re-pointed to What's new or the prompting guide.
- YouTube evidence remains titles only.

## Round 2: 04-design after the prompting-guide items

`/sc:review docs/features/opus-5-5-default-model/04-design.md`, run after the prompting-guide alignment check added the no-thinking detector row to P3 and a new P7 (frontend defaults). A fresh reviewer read 04 with 02 and 03 as parent context; it did not open this file, 06 or the README. Round 1's findings travelled to it as acceptance criteria A1–A13 without any claim that they were fixed. The main loop re-checked each finding against its source before applying it, and all were applied.

Verdicts before fixes: A1, A2, A4, A6, A9, A12 pass; A3, A5, A7, A8, A10, A13 partial; A11 fail. No critical findings.

| ID | Finding | Evidence re-checked | Resolution |
|---|---|---|---|
| I1 | "`fable5` reads Fable 5.1" contradicted the nearest-earlier-section rule | Reference `## ` headings: Opus 5 (911), Sonnet 5 (1153), Fable 5.1 (1304), Fable 5.1 from Fable 5 (1541); no Fable 5 section | P3 item 1: flags resolve to model IDs first (`fable5` → `claude-fable-5-1`, as `prompt.md:15` already says), and the section rule applies to IDs only |
| I2 | No precedence between interim rows and the fallback Opus 5 section | `prompt.md:26`: the reference "wins on conflict" | P3 item 3: an interim row wins on the axis it names; the fallback section wins elsewhere |
| I3 | Detector rows were marked interim, so P4 would delete them; they also fired on every target | `prompt.md:43`: `<removal_targets>` is "the command's own, not a mirror" | P3 item 4 split into permanent detector rows, each with its target scope (`claude-opus-5-5`, `claude-fable-5-1`; not `claude-opus-5`), and interim model-delta/request-config rows; P4 deletes only the latter |
| I4 | Progress-text display value and source were wrong | What's new says only "until it sets a `display` value that returns the text"; prompting guide lines 71 and 91 give `display: "updates"` with its beta header | Request-config now says `"updates"` with the header, `"summarized"` as a noted alternative, each with its page |
| I5 | D1 used a flat "half the price" ratio | Sonnet 5 cache reads 10% of $2 = $0.20, equal to Opus 5.5's 5% of $4 | D1 lists input, output and cache-read prices separately and calls keeping `sonnet` an unmeasured cost choice |
| I6 | P7's probe ignored the agent's four-direction step | `frontend-architect.md:38`: "proposes 4 distinct visual directions … before building when brief ambiguous" | P7 probes both the direction-proposal and the direct-build path; necessity restated as unproven until the probe runs |
| S1 | Two default overrides missing | model-config: `ANTHROPIC_MODEL` returns "whatever you saved with `/model`"; project or managed `model` | Added to the 04 intro and P6 |
| S2 | Picker `s` path missing | model-config: "switch model for this session only and leave your default unchanged" | Added to P1 |
| S3 | `don't deliberate` would catch the guide's own latency line | Guide line 52 | Signal dropped; "Answer directly without deliberating." kept beside `effort: low`; canary added |
| S4, S5 | Two verify greps could not decide pass or fail | P3 "only as the legacy alias"; P1 grep matched the old line | Replaced with greps that return a checkable set |
| S6 | "Inherits the session model" ignored frontmatter and `CLAUDE_CODE_SUBAGENT_MODEL` | sub-agents resolution order | P2 sentence names the fall-through order; probe adds the user-asks-for-Fable case |
| S7 | P4 trigger matched table rows; a delta-only section would need a second tuple | Reference layout for Fable 5.1 | Anchored grep; two-tuple case written into P4 |
| S8 | Cache invalidation on effort change and the visual-inputs section were unmapped | Guide lines 46, 155-157 | Added to request-config; visual inputs recorded as not applicable in §3 |
| S9 | The five frontend patterns were called "the defaults" | Guide line 161-164: they appear in an example instruction | P7 wording now says the guide's example names them |

### Still unverified after round 2

- The P7 probe and the P3 canaries have not run; both are verify steps of unimplemented proposals.
- The 2026-08-25 de-pin date comes from auto-memory, not a re-read of the commit.

## Round 3: the implementation

`/sc:review` of the uncommitted diff on `fix/opus-5-5-default-model` against 04-design. Three independent reviewers ran in parallel, one lens each: spec fidelity and copy consistency (L1), factual accuracy against the downloaded official pages and the local migration reference (L2), and `commands/prompt.md` as an instruction set plus the raw probe outputs (L3). Each received the diff, the spec, the raw probe outputs with the criteria written before them, and earlier rounds' findings as acceptance criteria. None received the author's reasons for departing from the spec, the probe verdicts, or this file. The main loop re-read every cited line in the diff and in the source before applying a finding. No finding was Critical. Tests and lint were green before and after: `uv run pytest` 2637 passed, 25 skipped; `ruff check .` and `ruff format --check .` clean.

### Applied

| Finding (reviewers) | Evidence re-checked | Resolution |
|---|---|---|
| The P2 line said "2.5× Opus 5.5 at list price", leaving out cache reads (L1, L2) | Fable 5.1 overview: cache read $0.25/MTok; What's new: $0.20; announcement: cache reads "make up the majority of agentic and coding work costs" | The line states no ratio ("it is priced above Opus 5.5"), since `agents/README.md` carries the prices, and passes any model only on the user's request. 04-design P2 amended |
| The `"summarized"` note in the interim request config was credited to the prompting guide (L1, L2, L3) | `model-migration.md:1730` says it, in the Fable 5.1 section only; the guide (line 91) names only `"updates"` | Dropped from `prompt.md` and from 04-design P3 |
| The "Answer directly without deliberating." keep clause applied to every target (L2, L3) | Guide line 52 offers it for Opus 5.5; `model-migration.md:972` says delete any don't-reason rule on Opus 5 | Scoped to 'claude-opus-5-5'; "with quality measured" reworded to the guide's condition, "measure quality when you add it" |
| The No-thinking row's `effort: low` and the interim `medium` default had no precedence (L3) | Canary C1-en-55 emitted `medium` although it moved the rule's intent to effort | Interim line: "`medium` unless a removal row below sets it". A second canary (C1-en-55-r2) still chose `medium`, because the row fired only "when the rule was there for latency"; the condition was dropped on guide line 44 ("Lowering effort reduces thinking … more reliably than prompt instructions do"). See 08 §3 for the third run |
| The runtime hook note says the reference section "wins over the mirror table" without the interim exception (L1, L2, L3) | `context_loader.py:1072-1075`; reproduced by L3 with `_emit_prompt_command_reference` | Note and the code comment at `:946` carry the exception; `test_context_loader.py:876` still matches |
| "No Opus 5.5 section" was decided from a "today" remark and the hook's ranges, not a check (L3) | C1-ko-55-file read the Opus 5 range and never searched for a 5.5 heading | `<fact_sourcing>` takes the fallback only when a Grep for the target's own `## Migrating to Claude <model>` heading finds none. Both reruns grepped the headings first |
| `reasoning_extraction` "never retried" was stated for every model (L1, L2, L3) | Guide line 85 says it for Opus 5.5; for Fable the reference says only that "some categories decline with no fallback" (`:1666`) | Row and both docstrings scope the retry claim to Opus 5.5; the row says the classifiers "can decline" (guide wording) |
| The docstrings listed `bio` and `reasoning_extraction` for Opus 5 (L2, L3) | `model-migration.md:1664` "Claude Opus 5's cyber-only classifiers"; model-config line 510 mentions "a biology flag on Opus 5", so the sources disagree on `bio` | Docstrings say the set differs by model and that Opus 5 has no `reasoning_extraction`, and make no claim about `bio` on Opus 5 |
| "Both targets" wording left at three places (L1) | `prompt.md` Verifiability switch, Prefill row, fact-sourcing | "Both families" for the user-decided Verifiability row, "every target" for the other two |
| The detector rows' own per-model reasons conflicted with the gotcha's "one exception" and the intro's "direction still comes from the delta rule" (L1, L2, L3) | `prompt.md` removal intro and `facts-not-memory` | Intro: a row without its own reason takes its direction from the delta rule; the gotcha names both exceptions |
| The fact-sourcing section's last sentence still stated the old absolute (L3) | `prompt.md` fact-sourcing closing sentence | Adds "its interim text only while the reference lacks the target's section" |
| Session inference left sessions on other models undefined; "Opus-family" would send an Opus 4.8 session to the Opus 5 direction (L3) | `model-migration.md:1079`: Opus 4.8's delegation direction is the opposite | Opus 5 and 5.5 sessions resolve to their own IDs, Fable 5.x to 'claude-fable-5-1'; any other model infers no target |
| The unattended-run clause left out when to add the paragraph (L2) | Guide line 71: "from the first request of the session" | Added |
| The self-check inversion was stated for Opus 5.5 without saying it is carried (L2) | `model-migration.md:1069` frames it for Opus 5 | Row and gotcha say 'claude-opus-5-5' carries it |
| P1 table: `--model fable` "cannot leave a user on Fable by accident" ignored resumed sessions; `/model fable` in `-p` mode is not saved; forks keep the session model (L2, L3) | model-config lines 141 and 133; sub-agents line 1143 | Rows corrected |
| P1 paragraph dropped "your evals" and re-aimed the "single sitting" quote (L1, L2) | choosing.md line 46; model-config line 69 | Reworded to the sources |
| `.claude/rules/agent-authoring.md:114` still said "default `inherit`" and "Use `sonnet`" while pointing to the README as SSOT (L1, L2, L3) | `agents/README.md:86` "Every agent omits `model:`"; sub-agents line 302 | Line rewritten to "omit it"; line 33's `model: sonnet` example stays in 04 §4's deferred docs pass |
| P7 folded numbered labels into the cream/serif/terracotta house style, and "section or step" did not match what the probes saw (L1, L2, L3) | Probes: leading-zero numbers on steps and list items, on white and off-white pages alike | A separate never-auto-apply default: numbered "01/02/03" labels "on sections, steps or list items" |
| Inline Korean prompts with a reasoning write-out are declined on the session before the command runs (L1, L3) | 3/3 on the edited tree; a master-tree control was declined too (4/4 in all); the same text by file path passed 2/2; English inline passed | Not caused by this branch. Text in `prompt.md` cannot help, since the command never loads, so the root README's `/sc:prompt` entry says to pass such a prompt as a file path on an Opus 5.5 session. 04-design P3 Verify now passes the Korean canary by file |
| 04-design disagreed with the implementation on the No-thinking row for Opus 5 and on the unattended paragraph (L1, L3) | `model-migration.md:972`; the command's `<tools>` has no reader for the guide | 04-design P3 item 4 and Verify amended; status moved to `implementing` |

### Declined, with the reason

| Finding | Reason |
|---|---|
| Scope `think carefully` to Opus 5.5 chat prompts (L2) | The row's existing reason, "redundant on thinking models", holds for all three targets: thinking is on by default on Opus 5 (`model-migration.md:927-929`) and always on for Opus 5.5 and Fable. The reference's positive use of "Think carefully through the problem" is for Opus 4.7 and Sonnet 5 at `low` (`:738`, `:1222`), neither a target |
| Carry the ~200-word unattended paragraph verbatim as interim text (L1) | `<fact_sourcing>` gives verbatim tuning blocks to the reference, not the command; P4 would delete it again; the `[FILL]` slot names the URL |
| The fallback is stated in both `<fact_sourcing>` and `<bounds>` (L3) | 04-design P3 item 3 asks for both places |
| The P2 line changes nothing measured, since 8/8 delegations already omitted `model` (L3) | It governs the case the eight runs did not exercise: a user asking for a model, or an escalation that looks tempting |
| Treat off-white section bands after the edit as the guide's pattern and tighten the clause (L3) | Two runs per cell; the guide names "a cream or off-white background". 08 reports the bands as reduced, not absent |
| Update the `okf/superclaude/commands/` copies (L1) | Stale since before Fable 5.1 and generated separately; out of this change |
| The insight Stop hook replaced canary `result` text (L3) | Outside the diff; noted in 08 as probe noise |

D3 was applied on 04-design's recommendation rather than on a recorded user answer (L3 asked); 08 says so.

### Still unverified after round 3

- One run per canary condition; two per P7 cell.
- Whether `reasoning_extraction` declines skip server-side fallback on Fable 5.1 (the Refusals-and-fallback page was not fetched).
- Interactive-session behavior of every change; all probes were headless.
