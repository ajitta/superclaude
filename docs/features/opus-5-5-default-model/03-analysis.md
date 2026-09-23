---
status: complete
revised: 2026-09-23
---

# 03 — Repository analysis: model-dependent surfaces in `src/superclaude`

Goal under test: an installed SuperClaude user runs on Opus 5.5 by default and reaches for Fable 5.1 only when a task calls for it. This document lists every place in `src/superclaude` whose behavior or text depends on which model runs, measures what Claude Code itself already does, and marks each surface as blocking, drifted, or already aligned. Proposals live in [04-design.md](./04-design.md).

## 1. Measured baseline (Claude Code 2.1.280, this machine, 2026-09-23)

Each row is one headless call, `claude -p [--model X] --output-format json --max-turns 1 "reply with the single word ok"`, reading the `modelUsage` key of the result (model ID and its `contextWindow` field).

| `--model` argument | Resolved model | Note |
|---|---|---|
| (none) | `claude-opus-5-5[1m]` | The account default is already Opus 5.5 with the 1M window |
| `opus` | `claude-opus-5-5` | `contextWindow: 1000000`: the missing `[1m]` is a label, not a smaller window |
| `opus[1m]` | `claude-opus-5-5[1m]` | Same model and window as the default |
| `fable` | `claude-fable-5-1` | `contextWindow: 1000000` |
| `fable[1m]` | `claude-fable-5-1` | Suffix accepted, same model |
| `claude-opus-5` | runs (previous Opus still served) | |

`~/.claude/settings.json` and the project `.claude/settings*.json` carry no `model` key, so the default above comes from Claude Code and the account plan, not from SuperClaude. The installer (`src/superclaude/cli/install_settings.py`) writes only `hooks` and the `CLAUDE.md` import; it has never written a model setting.

Consequences for the goal:

- **Default Opus 5.5 needs no installer change.** The measurement matches the official list: `default` resolves to Opus 5.5 on Pro, Max, Team, Enterprise, the Anthropic API, Bedrock, Google Cloud and Claude Platform on AWS from Claude Code v2.1.280. The exceptions are Microsoft Foundry (Sonnet 4.5) and any Claude Code older than 2.1.280 ([02-research.md §4](./02-research.md)).
- **The window is not at stake.** model-config: "Fable 5.1, Fable 5, Sonnet 5, and Opus 4.7 and later run with the 1M window on every plan, including Pro. You don't select a `[1m]` variant", and the 2.1.280 changelog lists Opus 5.5 with "1M context". The probe agrees: `opus` reports `contextWindow: 1000000`. The case against a settings write rests on overriding user and team choice (04-design §3), not on context size.
- **Fable is one alias away, and the paths last different lengths.** `claude --model fable` applies to that session only; `/model fable` is saved to user settings, so later sessions start on Fable until `/model default`; `model: "fable"` on one Agent-tool call applies to that delegation only (model-config, sub-agents).

A rough cost signal from the same probes: the first uncached call billed $0.212 for 26,200 cache-write tokens on `opus` and $0.597 for 29,728 on `fable`, which puts Fable at about 2.5× Opus 5.5 on cache writes. The follow-up cached calls (`probe_opus.json`, `probe_fable.json`) cost $0.00769 and $0.010175, about 1.3×, because cache reads differ less (1.25×). Inferred from a handful of calls; the first pair was read from the session's console output and not saved to a file. The list prices in 02-research are authoritative.

## 2. Surface inventory

Found by `grep -rniE "opus|fable|sonnet|haiku|claude-[a-z]+-[0-9]" src/superclaude` (29 hits) plus a sweep for `model`, `effort`, context-window constants, and `max_tokens`. No context-window size is hardcoded anywhere in `src/superclaude`: the `--uc` and `--safe-mode` thresholds in `core/FLAGS.md` are percentages, so the 1M default needs no change there.

| # | Surface | file:line | What depends on the model | Status |
|---|---|---|---|---|
| S1 | `/sc:prompt` target set | `commands/prompt.md:2,8,11,15,28,48,102,109` | Targets are `claude-opus-5` and `claude-fable-5-1` only; flag values `opus5 \| fable51`; the delta table has one column per target | **Blocking**: the default session model is not a target |
| S2 | `/sc:prompt` session inference | `commands/prompt.md:15`, example row `:100` | "When either is unstated, infer from the session." On an Opus 5.5 session the inference has no matching column | **Drifted**: behavior undefined, see §3 |
| S3 | Migration-reference anchors | `scripts/context_loader.py:965-969` | `_MIGRATION_REF_ANCHORS` holds Opus 5 and Fable 5.1 headings only | **Blocked upstream**: the reference has no Opus 5.5 section yet (§4) |
| S4 | Hook note when the target has no section | `scripts/context_loader.py:1043-1076` | The note lists the ranges it found; it never says the session's model is missing from them | **Gap**: an absent section is silent |
| S5 | Command summaries | `commands/help.md:54`, `commands/sc.md:54`, `commands/README.md:80` | "Rewrite a prompt for Opus 5 / Fable 5.1" | **Drifted** text, follows S1 |
| S6 | Agent model routing | `agents/README.md:84-92` | Agents omit `model:` and inherit the session model, which delivers Opus 5.5 to every agent with no change. Two lines are wrong: `:90` gives the resolution order as "`CLAUDE_CODE_SUBAGENT_MODEL` env > per-invocation > frontmatter > parent session", the order Claude Code used before v2.1.251 (current: per-invocation > frontmatter > env > main conversation, per the sub-agents docs); `:92` offers "set `model:` in agent frontmatter" as the override, which the project convention forbids | **Drifted**: stale fact plus a convention conflict |
| S7 | Delegation rules | `core/rules/RULES_DELEGATION.md` `<sub_agent_decision>`, `<agent_routing>` | No guidance on when a single delegation may take `model: "fable"` | **Gap** against the "Fable when needed" half of the goal |
| S8 | auto-improve mutator default | `scripts/auto_improve/mutator.py:19`, `coordinator.py:54`, `cli.py:6,80`, `commands/auto-improve.md:40,48` | Spawns `claude -p --model sonnet` per cycle; independent of the session model | **Decision**: deliberate volume-cost choice, not drift |
| S9 | Refusal detection docstring | `utils/__init__.py:313` | "Claude Fable 5.x safety classifiers end a turn with `stop_reason: \"refusal\"`". Claude Code docs now list Fable models, Opus 5.5 and Opus 5 as classifier-bearing, and Opus 5.5 adds the `reasoning_extraction` category, which server-side fallback does not retry. The code is model-agnostic | **Drifted** docstring only |
| S10 | parallel-A/B runner | `scripts/parallel_ab/spec_loader.py:35,101`, `runner.py:81` | `model` is a required spec field, no default | **Aligned**: caller chooses |
| S11 | Removed-flag notices | `scripts/context_loader.py:406-422` | `--fast` and `--effort` are routed to Claude Code natives | **Aligned** |
| S12 | Model tendencies | `core/rules/RULES_QUALITY.md:56-59` | Over- and under-engineering lines, not tied to a model generation | **Aligned** |
| S13 | `superclaude doctor` | `cli/doctor.py:46-80` | Checks the plugin, config, hooks, PATH and CLAUDE_SC import. It never reads the Claude Code version, and Opus 5.5 needs v2.1.280+ (older versions default to Sonnet 5 or Opus 5) | **Gap**, optional |

Outside `src/` (listed for completeness; out of the requested scope): `.claude/rules/agent-authoring.md:33` shows `model: sonnet` as the example value for an optional field, `evals/README.md:72` uses `claude-fable-5-1` as the canary example, and `tests/unit/test_context_loader.py:774-875` pins the Opus 5 anchor in fixtures.

## 3. Probe: what `/sc:prompt` does on an Opus 5.5 session today

Command: `claude -p '/sc:prompt "refactor the auth module so tokens refresh silently"' --permission-mode plan --output-format json`, run from the repo root with the local-scope install, default model (resolved `claude-opus-5-5[1m]`). One run.

Result, quoted from the report the command produced:

> **Target model:** `claude-opus-5`. This session runs Opus 5.5, and the migration reference has no 5.5 section, so I used the nearest one (lines 1034–1152).

The fallback was reasonable and was disclosed, but nothing in `prompt.md` prescribes it. The command's own gotcha `model-required` says "An unresolved target model yields opposite instructions on delegation and verification", and the step that avoided that outcome here was the model's judgment, not a rule. One run cannot show that the fallback is stable; a Fable session, or a reference that later gains an Opus 5.5 section under a different heading, can change it.

## 3b. Probe: do the reasoning-exposure modes trip `reasoning_extraction`?

Opus 5.5 can decline "requests that push the model to reproduce its internal reasoning in the response text". Two shipped surfaces ask for visible reasoning: `--introspect` (`core/FLAGS.md:10`, "surface decision logic"; `modes/MODE_Introspection.md:7,32`) and `--vs cot` (`modes/MODE_Verbalized_Sampling.md:50,60`, a **Reasoning** line per candidate). One headless run each on the default model (`claude-opus-5-5[1m]`), flag placed at the end of the prompt:

| Probe | stop_reason | Outcome |
|---|---|---|
| `... reflect on the choice. --introspect` | `end_turn` | Normal answer with 🎯/⚡ sections; it said up front that the reasoning was "reconstructed after the fact" |
| `Suggest names for a CLI tool ... --vs cot` | `end_turn` | Normal `Variant: cot` output with per-candidate **Reasoning** lines |

Neither was declined. Both modes ask for a report of decisions and rationale rather than a transcript of internal thinking, which is the shape the classifier targets. `core/PRINCIPLES.md:27` already names restating chain-of-thought in the response as an anti-pattern. n=1 each, so this is absence of a failure, not proof of safety.

## 4. Upstream fact source

`/sc:prompt` and `context_loader.py` treat the `claude-api` skill's `shared/model-migration.md` as the owner of per-model facts.

- Local copy: `~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/claude-api/shared/model-migration.md`, clone at `34040c9` (2026-09-10).
- Upstream `main`, fetched 2026-09-23 from `raw.githubusercontent.com/anthropics/skills/main/...`: same byte size (244,863).
- Neither contains an Opus 5.5 section: `grep -c "5\.5\|opus-5-5"` returns 0. The "Destination Models" table still calls `claude-opus-5` "The current Opus" and says "Default to the latest Opus for the caller's tier unless they explicitly chose otherwise."

So the per-model behavioral delta for Opus 5.5 has no official prompt-tunable source that this framework can read today. Any Opus 5.5 column written now would come from the official prompting guide rather than the reference, which `prompt.md`'s `facts-not-memory` gotcha and its "mirror, not a source" line (`:26`) forbid as written. 04-design P3 therefore amends those two rules explicitly for interim rows instead of working around them.

## 5. Counterevidence and unknowns

- The measured default in §1 is one account on one plan; other plans rest on the official docs, not on measurement.
- The default is only what a user gets when nothing overrides it. Only this machine's settings files were checked; a `model` saved by `/model`, an organization default model, `ANTHROPIC_DEFAULT_MODEL`, or a resumed session each replace it (model-config). 04-design P6 turns this into a doctor check.
- The §3 probe is n=1 and on the `cc` surface only.
- No test covers `/sc:prompt`'s target resolution; a change to S1/S2 is guarded only by the anchor fixtures in `test_context_loader.py`.
