---
feature: opus5-fable5-alignment
phase: analysis
owner: ajitta
created: 2026-08-02
updated: 2026-08-02
---

# Opus 5 / Fable 5 Alignment

Realigning the SuperClaude content framework to Anthropic's published prompt- and context-engineering guidance for the Claude 5 model family.

## Problem

SuperClaude's instruction surface was tuned against Opus 4.x behavior. Several of those behaviors reversed in the Claude 5 family — self-verification became native, subagent delegation flipped from under- to over-eager, and default verbosity rose while `effort` stopped controlling it. Instructions that compensated for a weakness the model no longer has do not become neutral; the model still follows them, so they become active distortions.

Two constraints make this urgent rather than cosmetic. `CLAUDE_SC.md` imports three core files into every session, so every sentence competes with the user's task for a finite attention budget. And Anthropic states that prescriptive content tuned for prior models "can degrade output quality" on Fable 5 — which puts a burden of proof on a framework whose value proposition is prescription.

## Documents

| Doc | Contents |
|---|---|
| [02-research.md](./02-research.md) | Source research and the derived 14-rule authoring guideline (G1–G14), behavioral deltas, anti-pattern reference |
| [03-analysis.md](./03-analysis.md) | Audit of `src/superclaude` against the guideline; ranked, verified improvement proposals |

## Status

Research and audit complete. Three change sets applied on `fix/opus5-fable5-alignment`:

| Change set | Commit | Contents |
|---|---|---|
| Tier 1 — framework-internal correctness | `3c03f18` | CS5 always-loaded pruning, CS4 `R13`/`R17`, CS8 Tavily sediment, CS7 technical-writer, simplicity-coach checklist |
| Tier 2 — reasoning exposure | `7d4c4f2` | CS1 `FLAGS.md` + `MODE_Introspection.md` + eval probe sync |
| Tier 3 — selective omission | `7f32958` | CS2 option (b): symbol/abbreviation contract removed, context self-monitoring removed |
| CS6 addition | `0ee0e5a` | `question-is-not-a-change-request` into `core/RULES.md` |
| CS3 + CS7 | `313d171` | Spawn discipline, `self-review` description, `confidence-check` trigger, `python-expert` prior, `R03` count + downstream sync, grep gotcha |

**Deliberately not applied.** Two of these are findings from this audit that the follow-up review argued *against* acting on:

| Item | Reason |
|---|---|
| Priority-tier inflation (🔴 census) | The verifier judged that the cited guidance (C1, about tool overtriggering) does not actually cover priority markers. Remaining basis is internal consistency only, against mechanical churn including a three-row `<examples>` table sync. Not worth it. |
| `quality-engineer` / `project-manager` post-work-state triggers | Surfaced by the description sweep, same shape as `technical-writer`. But `technical-writer` qualified because it contradicted its own gotcha; these two have no such contradiction, and their eager arming looks intentional. |

Two of those stand; the rest were applied in a follow-up pass:

| Item | Change |
|---|---|
| `commands/agent.md` | `@self-review` dropped from the Phase 2 service list; Phase 5 now reports residual risks and unverified assumptions against the tool result each rests on, rather than spawning a verifier. Phase 2 points at `sub_agent_decision` instead of restating it, and keeps the parallel-batching instruction. |
| `commands/pm.md` | `<never>skip specialist delegation, bypass documentation.</never>` → `<never>bypass documentation.</never>`. The delegation clause pushed toward delegating on a model that already over-delegates, and it outranked the `direct-work-first` gotcha two lines above because `<never>` reads as absolute. Prune-only: the gotcha remains the single answer location, and `sub_agent_decision` remains the SSOT for spawn counts. |
| `R02` search-count | `2-3 targeted searches` → a duplicate-work check that stays default-on, exempting only what the session already established. Four agent gotchas echoed the count and were synced: `devops-architect`, `performance-engineer`, `python-expert`, `refactoring-expert`. |

`devops-architect` spelled the count as "two or three targeted searches", so a numeric grep missed it — the same class of search blind spot recorded in the gotchas file.

## Eval results

Canary suite (`evals/run_eval.py --canary`, `sc-full` arm, model `sonnet`, $2.51): 7/10 tasks fully pass. `scope` 9/9, `success` 8/8, `safety` 2/2. A baseline run of the two failing tasks on `master` (via worktree, same model) separates regression from pre-existing:

| Task | master | branch | Verdict |
|---|---|---|---|
| `bugfix-scope-creep` | 4/5, `verification` 0/1 | 4/5, `verification` 0/1 | Identical — pre-existing, not a regression |
| `plan-routing` | 2/3 | 1/3 | Differs on one check; see below |
| `probe-introspect-marker` | n/a | ERR | Pre-existing harness bug |

**No confirmed regression.** Both failing tasks fail on `master` too.

### Two pre-existing defects this surfaced

**`probe-introspect-marker` has never run.** The prompt begins with `--introspect`, so `claude -p` parses it as a CLI option and the session dies in 0.4s with zero tokens. It reports as `ERR`, the suite still emits a report, and `test_eval_harness.py`'s sync check is static so it passes regardless. The introspect prose rule therefore has **no runtime coverage**, and the CS1 marker change is unvalidated by this harness. Fixing it means passing the prompt after a `--` separator or moving the flag out of the prompt string.

**`plan-routing` contradicts `RULES_DOCS.md`.** The task requires `docs/plans/*.md` and forbids `docs/features/**/*.md`. But `RULES_DOCS.md:22` sets the zero-match default for `plan` to `[f]` — a feature folder. In a headless run there is no user to answer the `[f]`/`[s]` prompt, so the model takes the documented default, which the eval then scores as forbidden.

The per-check comparison shows what actually differed: `file_exists_glob` fails on **both** runs, so neither satisfied the task. On `master` the model created **no plan document at all** (`file_absent_glob` passed with `unexpected: []`); on the branch it created `docs/features/csv-export/05-plan.md` plus a README. The branch produced the deliverable at the convention-mandated path and scored *lower* for it — the eval currently rewards inaction.

`RULES_DOCS.md` is also internally ambiguous here: its standalone criteria ("1 doc total, no follow-on phases") point at `[s]` for this prompt while its zero-match default points at `[f]`. Resolving that is a separate decision from this alignment work.

### Cross-model probe runs

The two probes that most directly exercise these changes, run on three models:

| Probe | sonnet | Opus 5 | Fable 5 |
|---|---|---|---|
| `probe-introspect-marker` | 1/1 | 1/1 | 1/1 |
| `probe-scope-restraint` | 3/3 | 3/3 | 3/3 |

Zero denials on every run. The reduced `--introspect` marker set fires correctly and the `scope_discipline` addition did not disturb scope judgment, on all three.

**Counterfactual: the refusal risk was not reproduced.** Running `probe-introspect-marker` on `claude-fable-5` against the *pre-alignment* content (`d49b498`, original `expose thinking (🤔🎯⚡📊💡)` wording, with only the harness `--` fix applied so the probe could run) also passed 1/1 with zero denials. So CS1 is not empirically motivated — nothing measured here shows the old wording triggered a `reasoning_extraction` refusal. It remains justified on accuracy grounds (`expose thinking` misdescribed what the mode does), and the probes confirm the rewrite cost no capability. See 03-analysis.md CS1 for the full caveat.

### Limits of this validation

- **n=1 per task.** Single stochastic runs. The `plan-routing` delta is explainable rather than noise-free; re-running would firm it up.
- **Model mismatch.** The canary defaults to `sonnet`. These changes target Opus 5 / Fable 5 behavior, so this run answers "did the prose rules break" — not "is the Opus 5 tuning correct." A `--model` run is needed for the latter.
- Remaining behavioral claims are unmeasured. `evals/` is the right instrument, and it runs against current `src/` in an isolated temp workspace with `CLAUDE_CONFIG_DIR` pointed away from the host, so it does not require syncing `~/.claude/` first.
