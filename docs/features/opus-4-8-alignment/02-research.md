---
status: complete
revised: 2026-05-30
---

# Opus 4.8 — Research: What Changed and Why It Matters for SuperClaude

**Purpose:** Establish an evidence-based picture of Claude Opus 4.8's documented behavior and how it differs from Opus 4.7, then identify which SuperClaude framework decisions are *validated*, *unaffected*, or *stale* under 4.8. Feeds `./05-plan.md`.

**Lineage:** This is the third link in the model-alignment chain — `docs/archive/specs/2026-03-15-opus46-alignment-design.md` (4.6) → `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md` + `docs/reports/OPUS_4_7_ALIGNMENT.md` (4.7) → this feature (4.8).

**Method:** Primary facts from Anthropic's official docs (`platform.claude.com` "What's new in Claude Opus 4.8" + `anthropic.com/news/claude-opus-4-8`), fetched 2026-05-30. Secondary press used only for benchmark deltas, flagged inline. Cross-checked against the framework's own 4.7 alignment artifacts.

---

## 1. Opus 4.8 at a glance

- **Released:** 2026-05-28 — 41 days after Opus 4.7.
- **Model ID:** `claude-opus-4-8`. Positioned as "Anthropic's most capable model for complex reasoning, long-horizon agentic coding, and high-autonomy work." Same price as 4.7.
- **Context:** 1M-token window by default on Claude API, Amazon Bedrock, Vertex AI (200k on Microsoft Foundry); 128k max output tokens. The Claude Code build runs `claude-opus-4-8[1m]`.
- **Thinking:** Adaptive thinking only — same as 4.7. Extended-thinking budgets (`budget_tokens`) remain unsupported (400 error). `temperature`/`top_p`/`top_k` non-default values still error (unchanged from 4.7).
- **Self-knowledge:** Latest family is Claude 4.x; IDs — Opus 4.8 `claude-opus-4-8`, Sonnet 4.6 `claude-sonnet-4-6`, Haiku 4.5 `claude-haiku-4-5-20251001`.

## 2. What changed from 4.7 → 4.8

| Dimension | Opus 4.7 | Opus 4.8 | Source |
|---|---|---|---|
| Effort default | varied by surface; xhigh advised for coding | **`high` on all surfaces** (API + Claude Code); judged best quality/UX balance | docs "Effort defaults"; news "A note on effort" |
| Higher effort | `high`/`xhigh` available | `xhigh` ("extra") + "max" available; "extra" recommended for hard tasks + long async workflows; CC rate limits raised | news "A note on effort" |
| Tool triggering | **under-triggered** — sometimes skipped a required tool call (user-reported) | **fewer skipped required calls**; "tool calling more efficient, fewer steps" | docs "Behavior changes"; news (CursorBench/Devin quotes) |
| Adaptive thinking | adaptive default | smarter gating — reasons only when the turn needs it; fewer wasted thinking tokens on bimodal workloads at the same effort | docs "Adaptive thinking" |
| Long context / compaction | 1M context | better long-context handling, **fewer compactions, better compaction recovery**; "long agentic traces stay on task with fewer derailments after compaction" | docs "Capability improvements" |
| Effort calibration | per-level behavior less consistent | "more reliable behavior at each effort level across a range of domains" | docs "Improvement areas" |
| Honesty / judgment | — | "sharper judgement", catches its own mistakes, pushes back on unsound plans, flags uncertainty, fewer unsupported claims | news (tester quotes) |
| Prompt cache minimum | 4,096 tokens | **1,024 tokens** | docs "Lower prompt cache minimum" |
| Fast mode | available | 2.5× speed, **3× cheaper** than prior models; research preview on API | docs "Fast mode"; news |
| Mid-task instructions | — | Messages API accepts `role:"system"` entries inside the messages array (update instructions mid-task without breaking prompt cache) | docs "Mid-conversation system messages"; news |

**Source key:** "docs" = `platform.claude.com` What's-new and "news" = `anthropic.com/news` launch post are **both Anthropic first-party**. Quantitative "news" claims (2.5× speed, 3× cheaper fast mode) are first-party and verified in the docs. Only the §7 benchmark deltas are *secondary press*.

## 3. Effort and thinking — the most framework-relevant shift

Anthropic now ships **`high` as the effort default everywhere** and states it is "the best overall balance of quality and user experience." On coding tasks `high` spends a similar token count to 4.7's default but performs better. `xhigh` ("extra") and "max" exist for difficult or long-running asynchronous work.

This directly bears on a decision SuperClaude already made: commit `8edd05d` (2026-04-18) **removed `effort:` from all 11 agents**, choosing inherit-from-parent on the principle "no hardcoded effort without measured evidence." The 4.7 discovery's open item T2-a (whether to add `effort: xhigh` to coding agents) was left to inherit-only.

**Finding:** 4.8 *validates* the inherit-only stance. With `high` now the universal default and judged the best balance, hardcoding `effort: xhigh` on agents would override a well-tuned default and inflate token spend without measured benefit. → No change to the inherit-only stance; confirm and document it.

**One concrete exception surfaced during the audit:** the effort-enum SSOT (`.claude/rules/schemas.yaml`) and `agent-authoring.md` still call `medium` the default, mark `max` "Opus 4.6 only", and omit `xhigh` entirely — all stale against 4.8 (default is `high`; `xhigh` and `max` are both valid). The SSOT also contradicts the authoring doc, which documents `xhigh` as settable, so `effort: xhigh` would fail validation. That is a real accuracy fix (plan T1-c), separate from the inherit-only decision, which stays.

Adaptive thinking is also smarter in 4.8 (reasons only when needed). PRINCIPLES.md already frames this model-neutrally: "adaptive think (model-managed; effort param tune depth)." The framework's standing anti-pattern note — "Adaptive + Manual CoT = redundant; pick one by complexity" — is *more* apt under 4.8, not less.

## 4. Tool triggering and subagents — a partial reversal of 4.7-era tuning

4.7's headline behavioral risk (documented in the 4.7 discovery, D3/D6) was that the model used **tools and subagents less** by default, prompting the framework to add explicit-invocation guidance. The relevant line lives in `RULES.md` `<sub_agent_decision>`:

> `Opus 4.7 note: model spawn subagents less eager than 4.6 — when Sub-agent criteria met, prefer explicit invocation … not assume auto-spawn.`

4.8 explicitly **improves tool triggering** ("fewer cases of skipping a tool call that the task required" — the exact issue users reported on 4.7; Devin's tester quote: 4.8 "fixes the … tool-calling issues we saw with Opus 4.7"). It also "works independently for longer" and "uses fewer steps for the same intelligence."

**Finding:** The version-pinned note is now behaviorally stale — but the *direction* of the residual guidance (prefer explicit invocation when delegation criteria are met) remains safe regardless of model. Two caveats prevent a confident threshold rewrite:
1. "Better tool triggering" is about *tool calls*, not specifically *subagent spawning* — these are related but not identical.
2. "Works independently for longer" is ambiguous: it could mean the model does **more itself** (less delegation) *or* sustains **more delegated** work. The official docs do not settle subagent-spawn eagerness.

→ The right move is **de-pin the version label** (the trait is shared across recent Opus models) and **keep the spawn-threshold rewrite deferred pending eval** — exactly what the 4.7 work already deferred (its own T2-b). See plan T1-a and T2-a.

## 5. Long context, compaction, and the 1M window

4.8 improves long-context quality and compaction recovery. This touches the project gotcha `compaction-drift` ("Rules from session start degrade after ~50 turns auto-compaction; re-read critical rules"). The "~50 turns" figure is an estimate (note the `~`), and "re-read critical rules on drift" is a **safety practice**.

**Finding:** A vendor claim of "better compaction recovery" is not sufficient evidence to weaken a safety practice (R18 + "do NOT simplify safety"). → Treat as a measurement item (does the drift threshold actually move under 4.8?), not a change.

Token Efficiency mode thresholds (`--uc` proactive ≥60%, auto `--token-efficient` 75%, `--safe-mode` 85%) are expressed as **percentages of session context**, so they remain proportionally valid at 1M. The mode already states "token consumption varies by model — monitor proactively." → No change; note only that the *absolute* budget is larger.

## 6. New features — relevance triage

| Feature | What it is | Framework relevance | Disposition |
|---|---|---|---|
| **Dynamic workflows** | CC research preview (Enterprise/Team/Max): Claude plans, runs *hundreds of parallel subagents* in one session, verifies, reports; e.g. codebase-scale migrations kickoff→merge with the test suite as the bar | Overlaps `--delegate`/`--orchestrate`/`--task-manage` and `<sub_agent_decision>`; signals the "under-spawn" gap is being closed at the harness layer | **Monitor** — harness feature, research preview, plan-gated availability; revisit at GA |
| **Mid-conversation system messages** | Messages API accepts `role:"system"` entries mid-array; update instructions without breaking prompt cache | SDK/harness concern; could let a future hook inject mode/MCP context as system entries instead of user-turn text | **Monitor** — not content; possible future `context_loader.py`/hook optimization |
| **1,024-tok cache minimum** (was 4,096) | Shorter prompts become cacheable | On-demand injected contexts (mode files, MCP docs) between 1,024–4,096 tokens now cache | **Note only** — runtime efficiency tailwind; no content change |
| **Fast mode** (2.5×, 3× cheaper) | `speed:"fast"` research preview | Matches FLAGS `--fast` ("same model, faster output"); description already accurate | **No change** |
| **Effort control in claude.ai/Cowork** | User-facing effort selector | Outside CLAUDE.md content scope | **Out of scope** |

## 7. Benchmarks (secondary sources — treat as reported, not official-doc-verified)

The two official pages fetched do not state the headline deltas verbatim (the news footnotes reference Terminal-Bench 2.1, OSWorld-Verified — 4.7 restated to 82.3% — and Finance Agent v2). The following are **reported by press coverage** (9to5Mac, AI-News, VentureBeat) and likely trace to the system card; cite with that caveat:

- Agentic coding ~64.3% → ~69.2%; multidisciplinary reasoning-with-tools ~54.7% → ~57.9%.
- ~4× reduction in the rate the model lets its own code flaws pass unremarked.

If exact figures matter downstream, confirm against the Opus 4.8 system card before quoting as fact.

## 8. Implications for SuperClaude (bridge to plan)

| Theme | 4.8 effect | Framework consequence |
|---|---|---|
| Effort default = high | inherit-only is right; effort-enum SSOT is stale | **Validate inherit-only (T2-c)** + fix enum/doc staleness incl. add `xhigh` (T1-c) |
| Better tool/subagent behavior | reverses 4.7 under-trigger | **De-pin version, defer threshold rewrite** — plan T1-a, T2-a |
| Smarter adaptive thinking | reasons only when needed | PRINCIPLES.md already neutral — **no change** |
| More honesty / 4× fewer flaws | reinforces R15 + review `<finding_policy>` | existing rules become *more* effective — **no change**, note as tailwind |
| Better compaction recovery | may move drift threshold | **measure before relaxing safety** — plan T2-b |
| Literal instruction following (continued) | the design rationale behind declarative-voice authoring | rationale is now multi-version; **de-pin "Opus 4.7" labels** in authoring rules — plan T1-b |
| Dynamic workflows / mid-convo system msgs | harness-level | **monitor** — plan T3 |

**Through-line:** Almost every 4.8 shift *reinforces* decisions SuperClaude already made (model-agnostic content, inherit-only effort, coverage-first review, anti-over-engineering). The only items warranting edits are **version-pinned claims** that now read as 4.6/4.7-specific when they describe a stable, multi-version trait. The corrective is version-*neutral* phrasing — consistent with the framework's model-agnostic design (`docs/archive/specs/2026-03-23-model-agnostic-compatibility-design-chosh1179.md`) and the 4.7 discovery's own open question Q5 — not a 4.7→4.8 stamp that re-stales in ~41 days.

## 9. References

- Official: "What's new in Claude Opus 4.8" — 'https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8'
- Official: "Introducing Claude Opus 4.8" — 'https://www.anthropic.com/news/claude-opus-4-8'
- Official: Opus 4.8 system card — 'https://www.anthropic.com/claude-opus-4-8-system-card' (for benchmark verification)
- Press (secondary, benchmarks): 9to5Mac 'https://9to5mac.com/2026/05/28/anthropic-upgrades-claude-with-new-opus-4-8-model-heres-whats-new/'; TechCrunch 'https://techcrunch.com/2026/05/28/anthropic-releases-opus-4-8-with-new-dynamic-workflow-tool/'; VentureBeat 'https://venturebeat.com/technology/anthropics-claude-opus-4-8-is-here-with-3x-cheaper-fast-mode-and-near-mythos-level-alignment'; Simon Willison 'https://simonwillison.net/2026/May/28/claude-opus-4-8/'
- Prior alignment work: `docs/reports/OPUS_4_7_ALIGNMENT.md`, `docs/specs/opus-4-7-alignment-discovery-ajitta-2026-04-18.md`, `docs/archive/specs/2026-03-15-opus46-alignment-design.md`
- Model-agnostic design: `docs/archive/specs/2026-03-23-model-agnostic-compatibility-design-chosh1179.md`
