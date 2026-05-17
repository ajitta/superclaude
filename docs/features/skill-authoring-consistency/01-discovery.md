---
status: approved-for-plan
revised: 2026-04-25
review_iteration: 2
---

> **Revision note (2026-04-25, post self-review).** A self-review (subagent `self-review`) flagged 3 critical and 9 important issues against the v1 spec. Key reversals: P0 changes from "rename hyphen→underscore" to "remove the field entirely; fold triggers into `description`" (Anthropic's canonical `skill-development` skill confirms `when_to_use` is deprecated). P2-7 install-path claim corrected from "3 targets" to "2 targets". I1, I5, I8, S3 re-graded into P1 / out of scope. See "Review iteration log" at the bottom for the full delta.

# skill-authoring.md 정합성 (Consistency) Discovery

## Problem statement

`.claude/rules/skill-authoring.md` (205 lines) is the canonical authoring guide for skills in this project. It governs:
- Five shipped skills (`confidence-check`, `finishing-a-development-branch`, `ship`, `simplicity-coach`, `verbalized-sampling`).
- Future custom skills written by the team.
- Cross-references from peer authoring files (`agent-`, `command-`, `mode-authoring.md`).

Two parallel audits — external (Anthropic docs / agentskills.io spec / CC v2.1.84–v2.1.119 changelog) and internal (5 shipped skills + 3 peer authoring files + install pipeline) — surface drift between **what the guide prescribes** and **what is actually true** of (a) the upstream Claude Code runtime and (b) the project's own shipped artifacts.

The **most consequential finding** is a candidate silent-bug: the guide and all shipped skills use `when-to-use` (hyphen), while Anthropic's official frontmatter table documents `when_to_use` (underscore). If CC's parser strictly drops unknown keys, every shipped skill is losing its trigger keywords. This must be verified before any other action.

## Scope

### In scope
- Drift between skill-authoring.md and **Anthropic's current public guidance** (`code.claude.com/docs/en/skills`, `platform.claude.com/.../best-practices`, the Complete Guide PDF, agentskills.io spec).
- Drift between skill-authoring.md and **Claude Code v2.1.119** runtime fields/limits.
- Conformance of the **5 shipped skills** to skill-authoring.md.
- Structural / terminology / naming **symmetry with peer authoring files** (agent / command / mode).
- Internal coherence within skill-authoring.md (archetype model, field-rule contradictions, optional-vs-required ambiguity).
- Install-pipeline accuracy (`{{SKILLS_PATH}}` / `{{SCRIPTS_PATH}}` claims).

### Out of scope (explicitly deferred)
- **Bulk migration of XML `<component>` body to Markdown headings.** Already adjudicated in `docs/research/rules-xml-conversion-ajitta-2026-04-14.md` — keep XML; flag the divergence from Anthropic's PDF with an explicit house-style note.
- Adding a YAML schema sidecar (also adjudicated 2026-04-14).
- Refactoring the 5 shipped skills to demonstrate every advertised field. Demonstrability is a doc problem, not a skill problem.
- Translation of the entire framework's bilingual prose. (skill-authoring.md's Korean YAML-comments, however, are in scope as a localized peer-symmetry issue.)

## Findings, by severity

### P0 — confirmed silent issue, but the fix is NOT a rename

**P0-1. `when-to-use` is dead-on-arrival — and `when_to_use` is deprecated upstream.**

**Stronger verdict than v1.** Two converging sources:

1. **Leaked CC parser** (`leehanchung.github.io`) reads `frontmatter.when_to_use` via dot-notation — so the project's hyphenated `when-to-use` is silently dropped (JS dot-notation cannot read hyphenated keys; a YAML key with a hyphen would need bracket-notation `frontmatter['when-to-use']`, which is not in the source). Effect: every shipped skill's trigger block is invisible to CC today.

2. **Anthropic's own canonical `skill-reviewer` agent** (installed at `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/agents/skill-reviewer.md:57`) says verbatim:
   > `Optional fields: version, when_to_use (note: deprecated, use description only)`
   And the canonical `skill-development/SKILL.md` (same plugin tree) uses **neither** form — it bakes triggers into `description` ("This skill should be used when the user wants to ...").

**Implication:** renaming hyphen → underscore would migrate from "ignored" to "deprecated". That's not a fix.

**Correct fix (replaces v1 fix scope):**
1. **Remove `when-to-use:` entirely** from all 5 shipped SKILL.md files.
2. **Fold the trigger keywords into `description`** using Anthropic's third-person voice pattern: `description: <one-line purpose>. This skill should be used when <trigger contexts>.`
3. **Update skill-authoring.md** to:
   - Drop `when-to-use` from the field reference and all examples.
   - Add a "Description authoring pattern" subsection: third-person voice, trigger phrases first ~100 chars, max length governed by 1,536-char listing cap (which is now `description` alone, since `when_to_use` is gone).
4. **Retire the stale memory** `reference_cc-native-fields.md` (Skill section L37) — it lists `when-to-use` as a valid field; that line predates the canonical Anthropic guidance.

**Definition of done (PR1 acceptance):**
Probe-verify the fix with one canary skill. Add a unique trigger phrase in the new `description` (e.g., a nonsense word), invoke a fresh CC session, observe whether the skill auto-loads on the trigger phrase. Document the result in the PR. Without this probe, "5 SKILL.md edited" is a code change without proof of behavior.

**Naming taxonomy clarification (still useful for the guide):**
The CC parser uses literal key matching with mixed conventions:
- `kebab-case`: `disable-model-invocation`, `allowed-tools`, `user-invocable`, `argument-hint`
- `single-word`: `name`, `description`, `model`, `effort`, `version`, `paths`, `arguments`, `shell`
- `snake_case`: only `when_to_use` (deprecated — do not use).

Authors should not reflexively kebab-case everything; exact key match is required.

### P1 — drift / inaccuracy (update with confidence)

**P1-1. `SLASH_COMMAND_TOOL_CHAR_BUDGET` figure is stale.**
- Guide (L106): "전체 skill/command description 합산 ~15,000 chars".
- Anthropic current docs: **1% of context window, fallback ~8,000 chars**, override via env var.
- The 15,000/16,000 figure is from a previous 2% formula.
- Fix: replace with the formula + fallback.

**P1-2. 1,536 cap simplifies after P0 fix.**
- Guide (L70 inline comment): `description: One-line purpose. # ≤1,536 chars`.
- Anthropic docs: cap applies to **combined `description` + `when_to_use`** — but since P0-1 removes `when_to_use`, the 1,536-char cap effectively becomes a per-`description` cap going forward.
- agentskills.io spec separately caps `description` at 1024 (authoring-time validator); 1,536 is downstream listing-truncation.
- Fix: state both numbers — "≤1024 chars (validator-friendly), ≤1,536 chars (CC listing cap, soft)" — and drop the "combined" framing once `when_to_use` is removed from the project.

**P1-3. `allowed-tools` format.**
- Guide (L79, L122): comma-separated, e.g., `Read, Grep, Glob`.
- Anthropic docs: **space-separated** string (`Read Grep Glob`) is canonical, though YAML list also accepted.
- Guide framing as "minimum-permission whitelist" is also imprecise — Anthropic clarifies `allowed-tools` is permission-grant (no-prompt list), not access-restriction.
- Fix: change examples to space-separated + add 1-line clarification of grant vs restriction.

**P1-4. Missing supported fields — narrowed to what's actually relevant.**

Self-review (I5) flagged scope-inflation risk: most "missing" fields have zero current usage and would pad the doc with phantom guidance. Trimmed list:

- **Keep — `${CLAUDE_SKILL_DIR}`**: Anthropic's official template var. Worth documenting because `{{SKILLS_PATH}}` is SuperClaude-specific install-time substitution; if SuperClaude skills ever ship via `/plugin install` (a real near-term consideration), the install-time substitution might not fire and `${CLAUDE_SKILL_DIR}` is the portable fallback. **Action:** add as the redistribution-friendly alternative.
- **Keep — `paths:` for skills**: The project already uses `paths:` in its own rules frontmatter, so authors will reach for it. Brief mention prevents confusion. **Action:** 1-2 line mention of "supported but rarely needed; use only if a skill should auto-load only when working in matching files."
- **Drop — `arguments:`, `shell:`, inline `` !`<cmd>` ``**: 0/5 shipped skills use these. Not currently relevant. Add only if/when a real authoring need surfaces.

**P1-5. Acknowledge XML-in-body divergence from Anthropic.**
- Anthropic's Complete Guide PDF authoring checklist: "No XML tags `<` `>` anywhere".
- All 100% of Anthropic first-party skills use Markdown headings (`## Instructions`, `## Examples`, etc.).
- Our guide prescribes a `<component name="..." type="skill">` XML envelope — heavily entrenched (2026-04-17 grep: 200 occurrences in 194 files).
- Past research (`docs/research/rules-xml-conversion-ajitta-2026-04-14.md`) decided to keep XML. Decision is not in question.
- **Drift symptom:** skill-authoring.md presents the XML body as if it were canonical, with no note about the divergence. Readers checking against Anthropic's docs will see a contradiction and not know which to trust.
- Fix: add a 2-3 line callout in the "Body Structure" section: house style; CC accepts XML in body without issue; if redistributing the skill outside SuperClaude, prefer Markdown headings.

**P1-6. Optional vs required XML body tags.**
- Guide L137-172 lists 9 tags (`<role>`, `<references>`, `<syntax>`, `<flow>`, `<tools>`, `<gotchas>`, `<examples>`, `<bounds>`, `<handoff>`) with no optional marker.
- Real conformance: only `<role>`, `<bounds>`, `<handoff>` appear in 5/5 shipped skills. `<tools>` appears in 1/5; `<syntax>` and `<examples>` appear in 3/5.
- Fix: mark required vs optional explicitly. Probable required set: `<role>`, `<gotchas>`, `<bounds>`, `<handoff>`. Everything else optional.

**P1-7. Reserved-words constraint on `name:` field — runtime-fail, not a style issue.**
Anthropic's authoring guidance (best-practices doc + Complete Guide PDF) says reserved words `anthropic`, `claude` cannot appear in the skill `name:` field. A skill named `claude-helper` silently fails to install. Self-review (S3) re-graded this from P3 cosmetic to P1 because it's a hard runtime failure, not a stylistic preference. **Fix:** add to the Field Rules section as a 1-line constraint with the failure mode noted.

### P2 — internal coherence (project-internal alignment)

**P2-1. `<bounds>` attribute count: actually 4-way drift, not 1-vs-3.**
- skill-authoring.md (L176, L187): requires `should + avoid`.
- agent-authoring.md (L134): requires `should + avoid + fallback`.
- command-authoring.md (L84): rule says "`should + avoid` required"; example at L70 includes `fallback`. **Internally inconsistent — flagged by self-review (I1).**
- mode-authoring.md (L101): requires `should + avoid + fallback` per audit (note: original spec cited L68, corrected after self-review).
- All 5 shipped skills: have only `should + avoid`.
- **Real shape of the problem:** skill+command share 2-attr formal rule (with command's example contradicting itself); agent+mode require 3-attr. Aligning to a single rule across all 4 authoring files is the right move, but is a separate design question.

**P2-2. `effort: high` example without policy guidance.**
- skill-authoring.md L78: `effort: high # low|medium|high|max 추론 깊이`.
- agent-authoring.md L26 + L47-58: extensive "omit by default — inherit from parent" guidance.
- 0 of 5 shipped skills set `effort:`. The example is unverified in production.
- Memory note 1804 (2026-04-18) confirms `effort` was kept "intentionally for skills" while scrubbed from agents — but the **rationale is not in the doc**.
- Fix: either drop the example OR add a 1-line policy note matching agent-authoring.md (`omit by default`).

**P2-3. Archetype seam — ② is leakier than the doc suggests.**
- L18 describes ② as "Side-effect operations (deploy, release). Protect from auto-trigger".
- `simplicity-coach` is ② (`disable-model-invocation: true`) but has no side effects — it uses ② for **invocation discipline** (delegating to a peer agent reliably).
- Fix: either add a fourth row to the archetype table OR broaden ② to "Workflow / explicit-invocation skill (side-effects OR delegation discipline)".

**P2-4. Opener divergence from peer files.**
- agent / command / mode-authoring.md openers (L7-11) all use a unified 4-dimension table: `Agent = WHO TO BE | Command = WHAT TO DO | Skill = WHICH CAPABILITY | Mode = HOW TO THINK`.
- skill-authoring.md L7-11 uses a different framing (decision-gate with two trigger conditions, then 3 redirect arrows).
- Fix: open with the unified 4-dim table for symmetry.

**P2-5. `{{SKILLS_PATH}}` scope ambiguity.**
- L129-131 says "scripts must use `{{SKILLS_PATH}}` (no hardcoded paths)".
- `simplicity-coach/SKILL.md:29` writes `scripts/dependency-audit.py` as a bare path inside `<references>`.
- Ambiguous: does the rule govern only `command:` strings, or also `<references>` paths?
- Fix: clarify scope (most likely: `command:` strings only — `<references>` paths are project-relative and resolved by the reader, not the runtime).

**P2-6. Field reference advertises fields no shipped skill exercises.**
- 8 of 13 fields in the YAML example block (L66-95) have zero usage in production: `argument-hint`, `model: opus`, `effort: high`, `context: fork`, `agent:`, `metadata:`, `user-invocable: false`, `hooks:` example.
- Not necessarily wrong to advertise them — but the example block gives equal visual weight, suggesting they are routine. They are not.
- Fix: split into a "Common" minimal example + an "Advanced" expanded reference, OR annotate rare fields with a "rarely needed" marker.

**P2-7. Install-path scope variance — corrected.**
- Guide L57: "Install path: `src/superclaude/skills/ → ~/.claude/skills/`".
- Verified at `src/superclaude/cli/install_components.py:46-55`: **two** rewrite targets, not three:
   - `user` scope → absolute `~/.claude/skills/` (resolved via `as_posix()`).
   - `project` and `local` scopes → both share `.claude/skills/` (relative).
- Self-review (C3) caught the original "three targets" claim. Corrected here.
- Fix: 2-line note distinguishing user-absolute vs project/local-relative.

### P3 — cosmetic / nice-to-have

**P3-1. Bilingual YAML comments.**
- skill-authoring.md L60-95 inline YAML comments are Korean: `# 권장 | lowercase+hyphens, ≤64자`.
- agent / command / mode-authoring.md inline comments are English.
- Memory 223 (2026-03-29) flagged this as a known incomplete fix.
- Fix: choose one language for inline YAML comments across all 4 authoring files. (Prose can remain bilingual where it adds value.)

**P3-2. Anthropic best-practices recommendations not yet adopted.**
- Third-person voice rule for descriptions ("Avoid 'I can help'") — partially absorbed by P0-1's description authoring pattern.
- Gerund naming convention (`processing-pdfs` over `pdf-processor`).
- Reference-file ToC requirement for files >100 lines.
- "Old patterns" `<details>` collapsible for time-sensitive content.
- (Reserved-words constraint moved to P1-7 — it's a runtime failure, not a style point.)
- Fix: optional uplift to a "Style recommendations" subsection. Low priority — none of these fail the runtime.

**P3-3. Runtime-bug gotchas — conditional inclusion.**
- GH #17688: skill-frontmatter hooks not triggered when skill loads inside a plugin (CC v2.1.5).
- GH #40630: skill-frontmatter hooks not propagated into forked subagent when `context: fork` set.
- GH #30874: skill-frontmatter hooks persist after skill ends.
- Self-review (I7) flagged that listing stale runtime-bug warnings is worse than omitting them. **Precondition before adopting:** verify each issue is still open as of the PR4 date; drop any that are closed/fixed. If all three are stale, omit the subsection entirely.

## Decisions (revised 2026-04-25 after self-review)

**D1 — REVERSED. P0 fix = remove the field, not rename.**
Original v1 decision (rename hyphen→underscore) was wrong. Anthropic's own canonical `skill-reviewer` agent labels `when_to_use` deprecated. Correct fix: drop the field entirely from all 5 shipped skills + skill-authoring.md, fold trigger keywords into `description` using third-person voice. Add a probe-verification step to PR1 (canary skill with unique trigger word, fresh-session test). See P0-1 for full scope.

**D2 — REVISED (user chose option b). Resolve 4-way `<bounds>` drift in PR3.**
User decision (2026-04-25): include 4-file consistency work in PR3 rather than defer.

Approach for PR3:
1. **Pick a single rule across all 4 authoring files.** Recommendation: `should + avoid` as required, `fallback` as optional. Reasoning: skills are short-lived (no persistent state needing explicit recovery posture); commands are wrappers (fallback is the parent context); agent/mode benefit from explicit fallback but it's not always meaningful. Optional-with-guidance is more honest than required-but-unused.
2. **Update each authoring file** to the unified rule. command-authoring.md's internal contradiction (rule says 2-attr, example shows 3) gets fixed by aligning to the rule.
3. **Sweep shipped components** for `<bounds>` usage. Skills: 5 files, all 2-attr (no change needed under the unified rule). Agents/modes: spot-check; if any have `fallback=` that's now redundant, leave them (optional means optional). If any are missing required attrs, fix.
4. **No invalidating edits to shipped skills** — the unified rule was chosen so existing 2-attr skills remain compliant.

**D3 — UPDATED. PR1 is single coordinated PR + probe verification.**
Single-PR scope for atomicity (no half-broken intermediate state) PLUS one canary verification probe to prove the fix actually changes auto-invocation behavior, addressing self-review C2. PR1 acceptance: 5 SKILL.md edited, skill-authoring.md edited, stale memory retired, ONE canary probe documented in PR description.

**D4 — UNCHANGED.** Inline YAML comments in English. Per user instruction.

**D5 — REPLACED. Annotate fields with usage count instead of split.**
Self-review (I4) showed the split-minimal-vs-advanced approach was shuffling, not solving. Better fix: keep a single field-reference block but annotate each rarely-used field with `# 0/5 shipped use this` so readers see honest usage. Pairs with P1-4's trim of phantom fields. Anthropic's "minimal required format" pattern is preserved at the top of the section (just `name` + `description`).

**D6 — UPGRADED. Two-location callout for the XML house-style note.**
Self-review (I3) showed a single inline callout could be skimmed past. Final placement:
1. **Top-of-file frontmatter callout** (after the title, before the decision-gate): `> House style note. SuperClaude uses XML body for all authoring; this diverges from Anthropic's "no XML anywhere" guidance. Decision rationale: docs/research/rules-xml-conversion-ajitta-2026-04-14.md.`
2. **Inline reminder** at the top of the Body Structure section: 1-line reference back to the top-of-file callout.

This catches readers who land mid-doc via search AND readers who read top-down.

**D7 — UNCHANGED.** v2.1.111 exact-name-match note dropped.

**D8 (NEW, addresses I5 trim).** P1-4 reduced to `${CLAUDE_SKILL_DIR}` and `paths:` only. `arguments`, `shell`, inline `` !`<cmd>` `` not added until a shipped skill needs them.

**D9 (NEW, addresses I7 conditional gating).** P3-3 (runtime-bug gotchas) is **conditional on verification**: each cited GitHub issue must be confirmed still-open before inclusion. If all three are closed/fixed, P3-3 is omitted from PR4.

**D10 (NEW, addresses S3 re-grade).** Reserved-words constraint (`anthropic`, `claude` in `name:`) moved from P3 to P1-7 — runtime-fail, not style.

**D11 (NEW, addresses I8 honesty).** PR1 task "search/update test fixtures" stands as a defensive sweep, but spec acknowledges no `when-to-use` references exist in `tests/` today (verified). PR description should note "no fixtures found, no fixture changes needed" rather than implying fixtures will be modified.

**D12 (NEW, addresses I6 plugin-distribution).** Add a 1-line investigation task to PR2: confirm whether `{{SKILLS_PATH}}` substitution fires for plugin-marketplace installs (vs. only `superclaude install`). If it doesn't, that's a separate bug surfaced for triage — not blocking PR2 but logged as a follow-up.

## Recommended next steps

1. **User reviews this revised spec** (decisions D1–D12; v2 reflects self-review corrections). The biggest direction change is D1 (P0 = remove `when-to-use`, not rename). If any decision needs redirection, reply now.
2. On approval, hand off to **`/sc:plan`** with this spec as input. The plan should sequence:
   - **PR1 (P0 + verification):** remove `when-to-use` from 5 SKILL.md; fold triggers into `description`; update skill-authoring.md; retire stale memory `reference_cc-native-fields.md` Skill section; **probe-verify with one canary skill** before merge.
   - **PR2 (P1):** drift fixes — budget figure, post-P0 1,536-cap simplification, `allowed-tools` format, narrowed missing-fields per D8 (`${CLAUDE_SKILL_DIR}` + `paths:` only), XML house-style two-location callout per D6, optional/required tag markers, reserved-words constraint per D10, install-path scope correction per P2-7. Plus the D12 plugin-distribution investigation.
   - **PR3 (P2):** internal coherence — **4-file `<bounds>` unification per revised D2** (single rule across skill+agent+command+mode; command's internal contradiction fixed; shipped-component sweep), `effort:` policy clarification, archetype ② broadening, opener uplift to peer-symmetry, `{{SKILLS_PATH}}` scope rule, field-reference annotation per D5.
   - **PR4 (P3, conditional):** YAML-comment language standardization per D4, optional Anthropic style recommendations. Runtime-bug gotcha section ONLY if D9 verification confirms issues still-open.
3. After each PR, re-run the conformance audit (the same one used for this spec) as a regression check.

## Review iteration log

**v1 → v2 (2026-04-25, post self-review by `self-review` subagent):**

| Issue | Severity | Status | Resolution |
|-------|----------|--------|------------|
| C1: `when_to_use` is deprecated upstream | Critical | Fixed | P0/D1 reversed: remove field, fold into description |
| C2: P0 has no empirical verification | Critical | Fixed | D3 adds canary probe to PR1 acceptance |
| C3: P2-7 install-path "3 targets" wrong | Critical | Fixed | Corrected to 2 targets (user vs project/local) |
| I1: command-authoring `<bounds>` self-inconsistent | Important | Acknowledged | P2-1 reframed as 4-way drift |
| I2: D2 was path-dependent reasoning | Important | Fixed | D2 rationale rewritten with positive justification |
| I3: D6 callout could be skimmed | Important | Fixed | D6 upgraded to two-location callout |
| I4: D5 was shuffling, not solving | Important | Fixed | D5 replaced with usage-count annotation |
| I5: P1-4 padding risk | Important | Fixed | P1-4 trimmed to 2 fields; D8 records the trim |
| I6: Plugin-distribution unaddressed | Important | Acknowledged | D12 adds an investigation task to PR2 |
| I7: P3-3 staleness unverified | Important | Fixed | D9 makes P3-3 conditional on verification |
| I8: PR1 test fixtures don't exist | Important | Fixed | D11 adjusts PR1 description honesty |
| I9: Stale memory contradicts spec | Important | Fixed | P0-1 fix scope now retires `reference_cc-native-fields.md` |
| S3: Reserved words is runtime-fail | Suggestion | Re-graded | Promoted to P1-7 per D10 |
| S4: PR1 needs definition of done | Suggestion | Fixed | D3 + canary probe |
| S6: `disable-model-invocation` form check | Suggestion | Verified | All shipped skills use kebab-case correctly |

## Sources

External research sources are catalogued in the deep-researcher agent's report (this turn). Key citations:
- `https://code.claude.com/docs/en/skills` (canonical CC frontmatter table; `when_to_use` underscore; budget formula)
- `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` (body conventions, naming, voice)
- `https://agentskills.io/specification` (open-standard CC-extension boundary)
- `https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf` ("No XML tags anywhere" checklist)
- `https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md` (v2.1.105 cap raise; v2.1.111 exact-match)

Internal evidence cited inline by `file:line`. See agent transcripts (this turn) for the full conformance matrix and install-pipeline trace.
