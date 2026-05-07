# Research: Converting prose authoring rules to XML+YAML structured format

**Date:** 2026-04-14
**Author:** ajitta
**Depth:** standard (2-hop, ~20 sources)
**Scope:** 4 authoring-rule docs in `.claude/rules/` (~828 lines prose markdown). Question: should they be converted to XML+YAML hybrid (matching the format of the agents/commands/skills they describe)?

## Question

Do AI agent frameworks / prompt-engineering toolkits structure their *authoring guide* documentation (rules for how to write agents/commands/prompts) as machine-parseable formats (XML+YAML, JSON Schema, DSL) rather than prose markdown? What's the observed ROI vs over-engineering risk?

Four sub-questions:
1. Concrete examples from LangChain, CrewAI, Anthropic Skills doc, OpenAI, Cursor
2. Patterns that backfired — "migrated back to markdown" stories
3. Rules as test oracles — JSON Schema+AJV, OpenAPI, ESLint RuleTester, Rego/OPA
4. XML vs Markdown token-efficiency — measurable evidence or folk wisdom?

## Method

Two search hops (Tavily, advanced depth). ~20 distinct sources across official docs, engineering blogs, community forums, benchmarks. Credibility-scored 1-5 (5 = official/standards, 4 = peer-reviewed or vendor engineering post, 3 = industry reports, 2 = expert blogs, 1 = community posts).

## Findings

### Q1. Concrete examples: how do frameworks structure *authoring* docs?

**Critical finding first — the single most load-bearing data point for this decision:**

**Anthropic's own skill-authoring guide explicitly prohibits XML inside SKILL.md bodies.** The official "Complete Guide to Building Skills for Claude" checklist item reads verbatim: *"No XML tags (< >) anywhere"*. Authored by the team that trained Claude to pay attention to XML tags in prompts. (Credibility: 5 — Anthropic primary source.) Source: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

This is a direct contradiction with the "meta-consistency" motivation (matching the format being authored). Anthropic deliberately chose prose markdown for skill bodies while using XML in prompts for Claude itself.

Confidence for this claim: **0.95** (primary source, explicit checklist item).

**Per-tool breakdown:**

| Framework | Authoring rule format | Notes |
|-----------|----------------------|-------|
| **Anthropic Claude Skills** | YAML frontmatter (2 required fields: `name`, `description`) + prose markdown body. Max 500 lines body. "No XML tags anywhere." | Progressive-disclosure design: frontmatter always loaded, body only when skill triggers. (Credibility 5) |
| **Cursor rules (.mdc)** | YAML frontmatter (3 fields: `description`, `globs`, `alwaysApply`) + plain markdown body. File extension `.mdc` = "Markdown Cursor" with structured frontmatter. | Community threads document confusion: multiple competing structures (3+ styles in forum discussions), consensus moving *toward simpler* frontmatter with fewer fields. (Credibility 3) |
| **CrewAI** | Pure YAML config for agents/tasks (role, goal, backstory, description, expected_output). No markdown body. | Recommended path per official docs. Pure data, no free-form prose at all. (Credibility 5) |
| **LangChain PromptTemplate** | YAML or JSON serialization with typed fields. | Schema-first. Single-purpose (prompts), not authoring rules per se. (Credibility 4) |
| **AGENTS.md** | Plain markdown, zero required frontmatter. | 60k+ GitHub repos, supported by Codex, Copilot, Jules, Cursor, Aider, Zed. Explicitly chose "plain markdown" over structured DSL files (`.cursorrules`, `.clinerules`, `CLAUDE.md`). (Credibility 5) |

**Pattern:** When frameworks document *how to author content for the LLM*, they choose either pure-YAML (CrewAI — config-only), YAML+prose (Skills, Cursor, Copilot), or pure-prose (AGENTS.md). **None use XML-in-body.** The hybrid style with YAML frontmatter + prose body is the modal choice.

Sources:
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (5)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (5)
- https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md (5)
- https://agents.md/ (5)
- https://docs.crewai.com/en/concepts/agents (5)
- https://forum.cursor.com/t/optimal-structure-for-mdc-rules-files/52260 (3)
- https://www.datacamp.com/tutorial/cursor-rules (3)
- https://lagnchain.readthedocs.io/en/stable/modules/prompts/prompt_templates/getting_started.html (4)

### Q2. Backfires — when structured authoring hurt adoption

**The Configuration Complexity Clock (Mike Hadlow, 2012 — canonical reference, still widely cited).** Documents the well-known progression: hard-coded → config file (INI/JSON/XML) → DSL → full programming language. Each step clockwise adds complexity, bugs, and rare-skill dependency. Hadlow's direct warning: *"Writing a good rules engine is hard, writing a DSL is harder still… soon enough you'll find there's little difference in the length of time it takes between changing a line of code and changing a line of configuration."* (Credibility 4.) https://mikehadlow.blogspot.com/2012/05/configuration-complexity-clock.html

**Rego / OPA — concrete abandonment evidence.** Permit.io (vendor — arguable bias, but their product is a Rego alternative): *"Everyone Loves Policy as Code, No One Wants to Write Rego."* Documented via multiple sources: steep learning curve rooted in Prolog/Datalog, limited adoption despite technical superiority. Cedar was explicitly designed as a more-readable replacement. (Credibility 2, corroborated by Styra's own acknowledgment: *"there's a learning curve which makes Rego a main barrier to using OPA"*, credibility 3, vendor.) Sources: https://www.permit.io/blog/no-one-wants-to-write-rego, https://www.styra.com/blog/why-you-should-get-started-with-the-rego-policy-language/, https://www.permit.io/blog/opa-vs-cedar

**Cursor .mdc community confusion.** Forum threads show multiple proposed structures with conflicting frontmatter fields (priority, version, tags, author, date). The eventually-adopted convention reduced to *three fields* (`description`, `globs`, `alwaysApply`) after user complaints. Quote: *"getting rid of the extra fields in the front matter is needed to solve most issues people run into with conflicts on auto rule generation."* (Credibility 3.) https://forum.cursor.com/t/optimal-structure-for-mdc-rules-files/52260

**AGENTS.md is itself a backfire story.** It exists specifically because 60k+ projects wanted *one plain-markdown file* instead of tool-specific configs (`.cursorrules`, `CLAUDE.md`, `.clinerules`, `.windsurfrules`). The InfoQ article quotes maintainers: *"rather than introducing a proprietary configuration file, its markdown-based approach ensures accessibility while fitting neatly into existing project structures."* (Credibility 4.) https://www.infoq.com/news/2025/08/agents-md/

**Direct migration-back-to-markdown stories:** no clean case documented in the corpus I reviewed. This is a real gap — absence of evidence, not evidence of absence. Most "migration" articles found were *toward* markdown from heavier formats (reStructuredText → MyST, legacy docs → markdown, HTML/CMS → markdown). I found zero credible stories of *"we converted our authoring guide to XML/DSL then reverted."* Confidence for this sub-claim: **0.55** (no positive evidence, and the absence may reflect publication bias — projects that backtrack rarely publish post-mortems).

### Q3. Rules as test oracles — the pattern exists, but narrower than it looks

**Clear pattern, but typically validates *data*, not *prose documentation*.**

| System | What's validated | Is the rule doc itself the oracle? |
|--------|-----------------|-----------------------------------|
| **ESLint RuleTester + AJV** | Rule *options* (user config per rule), via JSON Schema `meta.schema`. Validated at rule-load time. | Partial — the schema is *code-adjacent*, lives in `meta.schema` in rule implementation files (`.js`), not in prose docs. (Credibility 5 — official ESLint docs.) |
| **OpenAPI + AJV / Specmatic** | API request/response payloads against the spec. | Yes — the spec *is* the oracle. But it's a schema document designed to be a contract, not an authoring guide. (Credibility 4.) |
| **Rego / OPA** | Policy decisions against input data. | The rules are executable, not prose. (Credibility 5.) |
| **JSON Schema strict mode (OpenAI function calling)** | LLM output shape. | *"Near-100% format conformance with JSON Schema in strict mode versus under 40% with prompting alone"* — cited by Augment Code AI Spec Template. (Credibility 3.) |

**The closest analogue to what SuperClaude might build:** the AI Spec Template pattern from augmentcode.com which explicitly says: *"Use Zod, JSON Schema, or OpenAPI, not prose"* for input/output contracts inside specs. But this is for *runtime contracts*, not for *human-authoring rules*. Their specs still use prose for "Business Rules" (*"Every rule must be deterministic and testable"* — but deterministic in behavior, not in prose structure). Source: https://www.augmentcode.com/guides/ai-spec-template

**Honest assessment:** rules-as-oracle is a valid pattern for structured data (API contracts, LLM output schemas, lint rule options). I found **no credible example** of a framework that made its *prose authoring guide* machine-parseable as a test oracle, with the partial exception of SuperClaude's *own existing approach* (tests like `test_agent_structure.py` parse agent files, validated against rules that are currently in prose). That gap is interesting — it means the proposed direction would be novel, which cuts both ways (innovative or premature).

Confidence: **0.75** for "the pattern exists for data validation"; **0.80** for "no canonical example of parseable-authoring-guides exists publicly."

### Q4. XML vs Markdown token efficiency — folk wisdom partially wrong

**Empirical benchmark directly contradicts the "XML compresses better" claim for nested data.**

From improvingagents.com (three LLMs × 1,000 questions each):
- **XML required 80% more tokens than Markdown for the same nested data.**
- Markdown used 34% fewer tokens than JSON on GPT-5 Nano, 38% fewer on Gemini 2.5 Flash Lite.
- Across GPT-5 Nano / Llama 3.2 3B / Gemini 2.5 Flash Lite, markdown had the best token efficiency; XML had the worst token *and* accuracy profile, with one format producing *54% more correct answers* than another in stress tests.

Source: https://www.improvingagents.com/blog/best-nested-data-format/ (Credibility 3, independent benchmark, methodology disclosed.)

Second benchmark (LinkedIn, Meet Limbani, Gemini 2.0 Flash):
- JSON input: 1,404 tokens
- TOON input: 1,004 tokens
- **Markdown input: 964 tokens** (lowest among three)

Source: https://www.linkedin.com/posts/meet-limbani_i-did-a-practical-comparison-between-toon (Credibility 2, single-model methodology.)

Community/OpenAI forum confirmation: *"Markdown is 15% more token efficient than JSON"* — multiple corroborating threads. https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742 (Credibility 2)

**BUT — Anthropic's own engineering post is important nuance.** From "Effective context engineering for AI agents": *"We recommend organizing prompts into distinct sections… using techniques like XML tagging **or Markdown headers** to delineate these sections, although the exact formatting of prompts is likely becoming less important as models become more capable."* (Credibility 5.) https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

XML tags shine specifically for *delineating large embedded content blocks* inside a prompt (wrapping a 10KB document with `<document>...</document>` costs 4 tokens and helps attention isolate it). That is NOT the use case for an authoring-rule document, which is itself small prose read top-to-bottom.

**Verdict on Q4:** The "XML compresses better" claim is **folk wisdom that fails empirical test for general prose documents.** XML's measurable benefit is specifically (a) delineating embedded data, (b) when post-processing extraction is needed. For 100-250 line prose documents read sequentially, markdown is 30-80% more token-efficient and sometimes also more accurate.

Confidence: **0.85** (multiple independent benchmarks concur; mechanism — markdown's dominance in LLM training corpora — is plausible and widely confirmed).

## Trade-off Summary

| Dimension | Prose markdown (current) | XML+YAML hybrid (proposed) |
|-----------|-------------------------|---------------------------|
| **Token cost per rule doc** | Baseline | Likely +30-80% (Q4 evidence) |
| **Testability** | None; tests hard-code rule knowledge in Python (current state) | High; rules become single source of truth |
| **Meta-consistency** | Mismatch with agents/commands (minor cognitive tax) | Matches — but conflicts with Anthropic's own SKILL.md guidance ("no XML") |
| **Authoring friction** | Low — anyone writes markdown | Medium — contributors must learn the schema; see Cursor .mdc confusion, Rego learning curve |
| **Drift risk** | Rules can drift from tests silently | Rules-as-schema makes drift a test failure |
| **LLM parseability** | Already high (markdown is LLM-native) | Higher for mechanical extraction, lower for natural reading |
| **Industry precedent** | Strong (AGENTS.md, SKILL.md, CLAUDE.md, Copilot instructions — all prose) | Weak to none for *authoring guides* |
| **Reversibility** | High (already here) | Low — schema migration is sticky |

### Specific risk for this project

The `.claude/rules/*.md` files are read by:
- **Humans** (mostly the maintainer, occasionally contributors) — prose is faster to read and edit.
- **Claude** (during `/sc:*` workflows that author new agents/skills) — markdown is LLM-native; XML delineation helps only when embedded in a larger prompt, not when read as a standalone doc.
- **Tests** (`test_agent_structure.py`, `test_command_structure.py`, etc.) — currently hardcode the rules they check. *This* is the real drift risk the conversion would solve.

The drift-risk problem can be solved without full XML+YAML conversion. Options ranked:

1. **Extract a small YAML sidecar** (`agent-authoring-rules.yaml` — field lists, required tags, allowed colors) consumed by tests; keep prose `.md` as human-facing. ~50 lines YAML for validator inputs, prose stays as-is. Lowest complexity, solves drift cleanly.
2. **Add a test that parses the prose** (e.g., markdown tables → dict of field:type:required). Slightly fragile but keeps single source of truth.
3. **Full XML+YAML conversion** of all 4 docs. Highest cost, most novel, contradicts Anthropic Skills authoring guidance, likely 30-80% token-heavier.

## Recommendation

**Do not convert the authoring-rule docs to XML+YAML hybrid.** Specific reasoning:

1. **Anthropic's own stance is decisive for at least `skill-authoring.md`.** Anthropic explicitly tells skill authors: "No XML tags anywhere." Using XML to describe how to author skills — when Anthropic documented the opposite — is a meta-consistency *loss*, not a win.
2. **The "meta-consistency" motivation is weaker than it appears.** Agents/commands/skills use XML in their bodies because CC is trained to weight XML-tagged sections in *prompts*. Authoring-rule docs are read as *standalone guidance*, not as structured prompts with embedded sections needing attention isolation.
3. **Empirical token data contradicts the compression motivation.** XML is ~80% heavier than markdown for nested prose in measured benchmarks.
4. **No credible industry precedent.** AGENTS.md (60k+ repos), CLAUDE.md, Copilot instructions, and Anthropic's own skill docs all chose prose. The one framework that tried heavy schemas for rules (Rego) is actively losing to more readable alternatives.
5. **The testability motivation is real but has cheaper solutions.** A 50-line YAML sidecar consumed by existing pytest structure tests solves the drift problem without the ~30-80% token cost and authoring friction.

**If you pursue testability, the minimum-viable change is:**
- Create `.claude/rules/_schemas/agent.yaml` (and siblings) listing required frontmatter fields, enum values (colors, effort levels), required XML tags in body, regex patterns.
- Update `test_agent_structure.py` et al. to load that YAML instead of hardcoding.
- Keep the four prose `.md` files as-is.
- Add a test `test_authoring_rules_sync.py` that greps the prose doc for claims like "must include `<mission>`" and verifies they're reflected in the YAML schema. (Simple heuristic check — don't boil the ocean.)

This buys ~80% of the drift-protection benefit at ~5% of the cost and ~0% of the novelty/risk of converting four documents into a novel format.

## Open questions

- Has any SuperClaude user ever complained that the prose rules were ambiguous or unparseable? That's the forcing function for increasing structure. If the answer is "no — tests already catch everything we care about," the case for conversion weakens further.
- Would a hybrid approach — keep prose, but add a machine-readable "# Rules contract" code-fence block at the top of each doc containing the YAML schema — capture both audiences without a full conversion? This is the pattern AI Spec Template recommends (prose for rules, Zod/Schema for contracts, side by side).
- What's the actual measured test-hardcoded-rule drift today? (Quick `grep` through `tests/unit/test_*_structure.py` for literal strings that also appear in the rule .md's would reveal the size of the real problem.)

## Sources table

| URL | Title / Source | Date | Credibility | Notes |
|-----|----------------|------|-------------|-------|
| https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf | Anthropic — Complete Guide to Building Skills | 2025 | 5 | Primary: "No XML tags anywhere" |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | Anthropic — Agent Skills overview | 2026 | 5 | Authoritative SKILL.md structure |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Anthropic — Skill authoring best practices | 2026 | 5 | 500-line body guidance |
| https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Anthropic engineering blog | 2025 | 5 | XML tags vs markdown headers guidance |
| https://agents.md/ | AGENTS.md spec site | 2026 | 5 | Plain markdown, 60k+ repos |
| https://www.infoq.com/news/2025/08/agents-md/ | InfoQ — AGENTS.md as open standard | 2025-08 | 4 | Adoption + rationale |
| https://docs.crewai.com/en/concepts/agents | CrewAI docs | 2026 | 5 | YAML-first authoring |
| https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md | Anthropic skill-creator SKILL.md | 2026 | 5 | Reference skill implementation |
| https://forum.cursor.com/t/optimal-structure-for-mdc-rules-files/52260 | Cursor community forum | 2025 | 3 | .mdc confusion + field reduction |
| https://www.datacamp.com/tutorial/cursor-rules | DataCamp — Cursor rules tutorial | 2026 | 3 | .mdc format confirmation |
| https://www.improvingagents.com/blog/best-nested-data-format/ | improvingagents.com benchmark | 2025 | 3 | XML 80% token-heavier; 54% accuracy delta |
| https://shshell.com/blog/token-efficiency-module-4-lesson-4-efficient-formatting | ShShell — token efficiency | 2025 | 2 | Density table; XML-for-delineation caveat |
| https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742 | OpenAI community | 2025 | 2 | Markdown 15% more efficient than JSON |
| https://mikehadlow.blogspot.com/2012/05/configuration-complexity-clock.html | Hadlow — Configuration Complexity Clock | 2012 | 4 | Canonical reference, DSL anti-pattern |
| https://www.permit.io/blog/no-one-wants-to-write-rego | Permit.io — Rego adoption | 2024 | 2 | Vendor-biased but corroborated |
| https://www.styra.com/blog/why-you-should-get-started-with-the-rego-policy-language/ | Styra — Rego intro | 2023 | 3 | Vendor acknowledges learning curve |
| https://www.permit.io/blog/opa-vs-cedar | Permit.io — OPA vs Cedar | 2024 | 2 | Cedar designed as readable Rego alternative |
| https://eslint.org/docs/latest/extend/custom-rules | ESLint custom rules docs | 2026 | 5 | JSON Schema for rule options |
| https://www.speakeasy.com/blog/contract-testing-with-openapi | Speakeasy — Contract testing | 2025 | 4 | OpenAPI + AJV as oracle |
| https://www.augmentcode.com/guides/ai-spec-template | Augment Code — AI Spec Template | 2025 | 3 | "Use Zod/Schema, not prose" for contracts |

## Confidence summary (per claim, not overall)

- Anthropic forbids XML in SKILL.md bodies: **0.95**
- Markdown is more token-efficient than XML for prose docs: **0.85**
- XML tags are useful for delineating embedded data in prompts (not standalone docs): **0.90**
- Rego-style DSLs suffer from adoption friction: **0.80**
- No public example of parseable-authoring-guides exists: **0.80** (absence of evidence)
- AGENTS.md (plain markdown) is the dominant industry convention for AI-agent-facing project docs: **0.90**
- The testability benefit can be achieved with a YAML sidecar at ~5% of the conversion cost: **0.75** (architectural judgment, not a researched claim)

Overall recommendation confidence: **0.85**. The empirical evidence against XML-heavy authoring docs is unusually consistent across (a) Anthropic's own authoritative guidance, (b) multiple independent token benchmarks, (c) the adoption curve of AGENTS.md over tool-specific files, and (d) the canonical Configuration Complexity Clock pattern. The main uncertainty is a possible novel win from doing what no one else has done — but "novel" and "unjustified" are hard to distinguish ex-ante, and the necessity test ([R18 Necessity Test]) is not currently passed by the proposal.

---

## Correction / Nuance (appended 2026-04-14)

The original claim "Anthropic's own skill-authoring guide explicitly forbids XML in SKILL.md bodies" was **overstated**. Two scopes were conflated:

### Exact sources

| Source | Scope | Verbatim |
|---|---|---|
| [platform.claude.com — skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (API doc, live) | `name` + `description` frontmatter fields only | "Cannot contain XML tags" |
| [Anthropic — Complete Guide to Building Skill (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) | During-development checklist (scope ambiguous — most likely frontmatter, not body) | "No XML tags (< >) anywhere" |
| [code.claude.com — sub-agents](https://code.claude.com/docs/en/sub-agents) | Sub-agent body | "the body becomes the system prompt" — no XML prohibition |
| Anthropic prompt-engineering guide | System prompts generally | **Encourages** XML tags |

### Reconciled rules

- **Hard ban (API-enforced)**: XML tags in `name` and `description` frontmatter fields — skills only.
- **Soft guidance (PDF tutorial)**: "No XML anywhere" appears in a during-development checklist; contextually most likely refers to frontmatter, but wording is ambiguous.
- **Encouraged**: XML in system prompts (agents, commands, modes — all become system prompts in Claude Code).

### Impact on `src/superclaude/**`

- `agents/`, `commands/`, `modes/` → **not wrong**. Bodies become system prompts where XML is canonical.
- `skills/*/SKILL.md` bodies (5 files with `<component>`) → **partial divergence**. Stays within API-enforced rules (frontmatter is XML-free). Soft risk only if uploaded via Skills SDK where the PDF tutorial checklist applies.

### Recalibrated confidence

- "Anthropic forbids XML in SKILL.md bodies": **0.95 → 0.40** (narrow to frontmatter fields; body-level prohibition is ambiguous guidance, not rule)
- Other claims (markdown token efficiency, industry convention, Configuration Complexity Clock, testability via YAML sidecar) unchanged.
- **Overall recommendation confidence: 0.85 → 0.78.** Partial-extraction path remains correct; the Anthropic-ban argument was a weaker pillar than presented, but the other pillars (zero test references, ~3 enum duplications, existing color drift, YAGNI) independently support the recommendation.
