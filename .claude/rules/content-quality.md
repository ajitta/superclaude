---
paths: ["src/superclaude/**", ".claude/rules/*.md", "CLAUDE.md", "AGENTS.md", "README.md"]
---

# Content Quality Rules — Audit Checklist & Pruning Guide

> Source: `docs/good-skills.md` (Matt Pocock "Building Great Agent Skills" + Anthropic Agent Skills docs + arXiv 2602.08004 skill-corpus analysis).
> **Scope.** Content QUALITY only — does each sentence earn its context cost? Schema/field/format rules stay in `*-authoring.md` + `xml-prose-format.md` (SSOT); this file never restates them.
> **Core thesis.** A good component is not a document of many instructions — it is the minimal control surface that makes a probabilistic model act the same way every time.

## The Criteria

### 1. Trigger — who invokes, at what context cost

Model-invoked descriptions sit in the system prompt permanently; user-invoked ones cost the user memory instead. Not a correctness question — a trade-off: context load on the model vs cognitive load on the user. Decide per component, deliberately.

- Workflow with a confirmed side effect — found in use or reported: a run Claude started on its own (nobody asked for it) deployed, committed, published or changed files → user-invoked (`disable-model-invocation: true`), citing where it was found or reported. A possible side effect alone is not enough: keep it model-invocable and gate it in the description and the body's confirmations, so delegated runs still reach it.
- Domain knowledge → model-invoked only when its trigger conditions are distinguishable from every neighbor's.
- Description must answer: "when THIS one and not the adjacent one?" Overlapping descriptions = misfire risk both ways (wrong pick, no pick).

### 2. Structure — procedure vs reference split

Two content kinds: **procedure** (steps the agent follows every invocation) and **reference** (templates, rule detail, examples, domain data needed sometimes). Body carries procedure only; reference moves to `references/` (or sibling file) with a one-line load condition: "Read `references/X.md` only when Y."

Applies beyond skills: command/agent/mode bodies over size target (xml-prose-format.md table) signal a split, not harder compression.

### 3. Strong terms — compress prose into trained vocabulary

The model already knows software engineering. One verified term replaces a paragraph: *vertical slice*, *keystone interface*, *idempotent*, *invariant*, *red-green-refactor*, *evidence-first review*. Long behavioral explanation that a domain term covers → use the term.

**Phase isolation.** When an early phase must not optimize for a later artifact (a questioning step rushing toward the plan document), put the later phase in a separate file loaded after the early phase ends. A single command body that lists every step cannot hide them; do not try.

Test: can this explanation collapse into one term the model already knows?

### 4. Deletion test — every sentence must change the outcome

> If output with the sentence deleted equals output with it kept, the sentence is not needed.

Three accumulation failures to hunt:

- **Duplication** — one answer location per rule. A second full statement of the same rule anywhere (across files included) becomes a pointer or gets deleted.
- **Sediment** — rules referencing removed features, old versions, dead file paths. Grep confirms; then delete.
- **No-op sentences** — plausible prose that changes no behavior: "be careful", "ensure quality", "use best practices", restating what the model does anyway, restating what an adjacent required tag already enforces.

Prefer deleting over adding. Growth pressure is the default failure mode of a content framework.

### 5. Durability — does the sentence expire on its own

A sentence that can become false without anyone editing it does not belong in an always-loaded doc. Ask what routine event falsifies it; if nothing in the repo notices that event, route it out. Destinations per content class: `core/rules/RULES_DOCS.md` `<doc_output_convention>` → *Durability routing* (SSOT).

## Audit Checklist (per file)

| Area | Question |
|---|---|
| Trigger | Must this be model-invoked, or is user-invoked cheaper overall? |
| Description | Does the model know exactly when to pick THIS component over its neighbors? |
| Structure | Is always-needed procedure separated from sometimes-needed reference? |
| Terms | Can any long explanation compress into one verified domain term? |
| Phases | Does an early step see the final goal and rush the middle? |
| Duplication | Does any rule have two or more full answer locations? |
| Deletion test | If this sentence is removed, does actual output change? |
| Durability | Can this sentence become false with nobody editing it? Then route it out. |

## Improvement Workflow

1. Observe a real failure (wrong invocation, missed step, inconsistent output) before adding or rewording; deleting sediment or no-op sentences found by grep (§4) needs no failure.
2. Find the proven engineering concept that addresses it.
3. Compress it into the strong term the model already knows.
4. Keep only minimum procedure in the body; move the rest to `references/`.
5. Delete sentence-by-sentence, comparing outcomes; keep what changes results, drop what doesn't.
6. Record observed failures as test cases before tuning further.

## Anti-Patterns

| Anti-pattern | Fix |
|---|---|
| Adding a new component instead of pruning an existing one | Audit + delete first; add only on demonstrated gap |
| Same rule fully stated in two files | Keep SSOT, replace second with pointer |
| Paragraph explaining what one domain term means | Use the term |
| Long description trying to win auto-invocation by volume | Distinguishing trigger conditions, front-loaded |
| "Improved" wording with no observed failure behind it | Revert; failures drive edits |

## Caveat

Not "shorter is always better" — **content that doesn't change results gets removed whether short or long.** Load-bearing detail stays regardless of length. The deletion test, not line count, is the bar.
