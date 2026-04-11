---
status: reviewed
revised: 2026-04-11
source: "https://www.youtube.com/watch?v=ZmRu5k63xLk"
author_channel: "AI 엔지니어의 시선 (Sam Hotman)"
published: 2026-04-06
methodology: sequential-thinking + verbalized-sampling + web-research + self-review
---

# Research Analysis: "Claude Code 50만 줄에서 발견한 7가지 프롬프트 설계 기법"

## 1. Source Overview

| Field | Value |
|-------|-------|
| Title | 클로드코드 50만 줄로부터 실력 향상을 위한 7가지 레슨런 포인트와 원칙들 |
| Format | YouTube transcript (Korean, auto-generated) |
| Author | AI 엔지니어의 시선 (Sam Hotman) |
| Published | 2026-04-06 |
| Source material | Claude Code TypeScript source (~512K lines, DMCA'd) |
| Tags | ai-agent, claude-code, context-engineering, prompt-engineering |

**Content type**: Practitioner analysis of Claude Code's leaked internal system prompts, extracting 7 prompting techniques ordered by difficulty (easy-to-apply → structural).

## 2. The 7 Techniques — Claim-by-Claim Analysis

### T1: DO & DON'T Contrast Pattern + Numeric Criteria

| Aspect | Assessment |
|--------|------------|
| **Claim** | Anthropic pairs positive/negative instructions with measurable numeric thresholds (e.g., "25 words between tool calls", "100 words final response") |
| **Evidence Quality** | HIGH — verifiable in CC system prompt. Reddit source analysis confirms "≤25 words" and "≤100 words" exist in internal build but NOT external build |
| **Accuracy** | ACCURATE. CC source contains tool preference pairs (e.g., "Use Glob — NOT find or ls") and numeric constraints |
| **Novelty** | LOW — DO/DON'T is established prompt engineering. The NUMERIC anchoring insight is more novel |
| **Practical Value** | HIGH — immediately applicable to CLAUDE.md |

**Cross-reference**: Anthropic's official "Effective context engineering for AI agents" post recommends "specific numerical data" over "repeatedly emphasising the same instruction in different ways." The divergence between CC's internal prompt (numeric constraints) and external build (vague "short and concise") correlates with user complaints about verbosity.

### T2: Result Verification Enforcement

| Aspect | Assessment |
|--------|------------|
| **Claim** | Anthropic forces verification before completion + grants explicit permission to say "can't verify" + enumerates all forms of false reporting (prose, summary, structured output) |
| **Evidence Quality** | HIGH — matches known CC system prompt patterns |
| **Accuracy** | ACCURATE. The enumeration of evasion forms (산문/요약/구조화 출력) is directly from source |
| **Novelty** | MEDIUM — verification forcing is known; FORM ENUMERATION is the novel insight |
| **Practical Value** | HIGH — directly applicable |

**Key insight worth preserving**: "금지만 하면 AI가 뭘 해야 할지 모릅니다" (prohibition alone leaves AI without direction). Every DON'T needs a paired DO as alternative behavior.

### T3: Triple Repetition Pattern

| Aspect | Assessment |
|--------|------------|
| **Claim** | Critical rules appear 3 times (beginning, middle, end) to counter recency bias. Research shows distributed placement > single strong statement |
| **Evidence Quality** | MEDIUM — the auto-compaction "do not call tools" x3 example is verifiable, but the general "research shows" claim lacks citation |
| **Accuracy** | PARTIALLY ACCURATE. The specific example is real. The generalized principle (3x repetition > 1x strong) is plausible but unsubstantiated with specific research |
| **Novelty** | HIGH — positional diversity as an engineering strategy is underexplored |
| **Practical Value** | HIGH — addresses a real failure mode (rule drift in long conversations) |

**Caveat**: The document implies ALL rules should be tripled. More accurate framing: only CRITICAL rules warrant positional repetition, and the 3 positions should be structurally different (system prompt → section-level → reminder/hook) not just copy-paste.

### T4: Turn Strategy & Context Cost Awareness

| Aspect | Assessment |
|--------|------------|
| **Claim** | Batch reads (up to 10 parallel) in turn 1, writes in turn 2. Context = cost per API call. |
| **Evidence Quality** | HIGH — parallel tool execution limit and turn-batching are verifiable in CC source |
| **Accuracy** | ACCURATE. CC runs up to 10 safe tools in parallel; file modifications run sequentially |
| **Novelty** | MEDIUM — parallel execution is documented; the "context = cost" framing is pedagogically valuable |
| **Practical Value** | MEDIUM — mostly handled by CC's runtime, not user-configurable |

**Correction**: The document says "컨텍스트에 올라간 모든 파일이 매턴마다 API로 전송됩니다" (all files in context are sent every turn). This is technically correct but oversimplified — CC uses prompt caching (5-minute TTL) to reduce actual cost of repeated context.

### T5: Chain of Thought Stripping

| Aspect | Assessment |
|--------|------------|
| **Claim** | CC uses `<analysis>` tags for thinking, then strips them from output. "생각하게 만드는 것과 생각을 관리하는 것은 다른 차원의 기술" |
| **Evidence Quality** | HIGH — the auto-compaction analysis tag pattern is documented |
| **Accuracy** | ACCURATE for CC's internal use. MISLEADING for end-user application |
| **Novelty** | LOW — CoT is well-established; tag stripping is implementation detail |
| **Practical Value** | LOW for Claude Code users — extended thinking is runtime-managed, not prompt-controllable. API users can use this directly |

**Important correction**: The document suggests users can replicate this with `<thinking>` tags in prompts. In practice, Claude models have built-in extended thinking (controlled by `thinking` parameter in API, automatic in Claude Code). Manual tag-based CoT in CLAUDE.md is unnecessary and potentially counterproductive.

### T6: Skills Description Budget

| Aspect | Assessment |
|--------|------------|
| **Claim** | Skills listing gets 1% of context window. Individual description max 250 chars. Custom skills trimmed first. |
| **Evidence Quality** | MIXED — the 250-char truncation and priority ordering are accurate, but the "1%" figure is questionable |
| **Accuracy** | PARTIALLY ACCURATE — see corrections below |
| **Novelty** | HIGH — this constraint is poorly documented and causes real user confusion |
| **Practical Value** | HIGH — directly explains "why my skill doesn't trigger" |

**Critical correction from web research**:
- The actual budget mechanism is `SLASH_COMMAND_TOOL_CHAR_BUDGET = 15,000 characters` (total, not per-skill) — NOT a percentage-based allocation
- Individual skill descriptions are truncated at 250 characters in the listing
- `description` field supports up to 1,024 characters, but only ~250 appear in the skill listing shown to Claude
- The priority ordering (Anthropic bundled > custom) is accurate
- The 15,000-character total budget is the definitive finding from source analysis

### T7: Context Pollution Prevention

| Aspect | Assessment |
|--------|------------|
| **Claim** | Fork agents' work logs are explicitly blocked from reading by main context to prevent "도구 노이즈" contamination |
| **Evidence Quality** | HIGH — fork agent isolation is verifiable in CC source |
| **Accuracy** | ACCURATE. The "목적 자체를 무산시킨다" (defeats the purpose itself) framing is directly from source |
| **Novelty** | HIGH — context boundaries as deliberate engineering is underappreciated |
| **Practical Value** | MEDIUM — more relevant for framework builders than end users |

**Extended finding**: Fork isolation serves dual purpose — (1) token efficiency (don't bloat parent context) AND (2) intentional information asymmetry (sub-agent works independently without anchoring bias from parent's partial analysis).

## 3. Cross-Cutting Analysis

### What the Document Gets Right

1. **Mental model foundation**: "클로드 코드는 챗봇이 아니라 에이전트 런타임" (Claude Code is agent runtime, not chatbot) — correctly frames all 7 techniques
2. **Progressive difficulty**: Techniques 1-3 (prompt writing) → 4-5 (system understanding) → 6-7 (architecture design) is pedagogically sound
3. **Paradigm insight**: "코드를 짜는 기술이 아니라 코드를 짜게 만드는 기술" (not coding skill, but the skill of making code get written) — captures the real shift
4. **Form enumeration**: T2's insight that prohibitions must enumerate all evasion forms is genuinely valuable and under-discussed

### What the Document Oversimplifies

1. **T5 applicability**: CoT stripping is presented as user-applicable, but it's runtime-managed in Claude Code
2. **T4 cost model**: Ignores prompt caching, which significantly changes the "every turn = full cost" claim
3. **T3 research claims**: "연구에 따르면" without citation undermines an otherwise strong practical recommendation
4. **T6 budget numbers**: The 1% figure appears to be a misinterpretation or outdated; actual mechanism is character-based (15K chars)

### What the Document Misses Entirely

1. **Hooks system**: Claude Code's hook infrastructure (PreToolUse, PostToolUse, Notification) is a major enforcement mechanism for many of these patterns — no mention
2. **Deferred tool loading**: CC v2.1.7+ introduced MCPSearch for lazy-loading tool schemas (~85% token reduction) — related to T6's budget concern
3. **Context compaction strategy**: CC's auto-compaction is mentioned but the engineering implications (rules loss, summary degradation) aren't explored
4. **Skills `when-to-use` field**: The separation of `description` and `when-to-use` (added in CC) addresses T6's trigger problem — description for "what", when-to-use for trigger keywords
5. **System-reminder injection**: CC can inject system-reminders at various conversation points — this IS the mechanism for T3-style repetition

## 4. Evidence Quality Summary

| Technique | Claim Accuracy | Evidence Strength | Practical Value | Overall |
|-----------|---------------|-------------------|-----------------|---------|
| T1: DO/DON'T + Numbers | ACCURATE | HIGH | HIGH | A |
| T2: Verification Enforcement | ACCURATE | HIGH | HIGH | A |
| T3: Triple Repetition | PARTIALLY | MEDIUM | HIGH | B+ |
| T4: Turn Strategy | ACCURATE | HIGH | MEDIUM | B+ |
| T5: CoT Stripping | ACCURATE (source) / MISLEADING (application) | HIGH | LOW (end users) | B- |
| T6: Skills Budget | PARTIALLY (wrong numbers) | MIXED | HIGH | B |
| T7: Context Isolation | ACCURATE | HIGH | MEDIUM | A- |

## 5. Verdict

**Overall quality**: B+ — High-value practitioner guide grounded in real source code analysis, with specific factual inaccuracies (T6 budget numbers) and one misleading application suggestion (T5). The document's greatest strength is its pedagogical framing and the "agent runtime" mental model. Its greatest weakness is the transcript quality (speech-to-text artifacts) and missing context about CC's hook/MCP infrastructure.

**Recommended use**: Treat as a conceptual framework for understanding CC's internal prompt design philosophy. Verify specific numbers independently before implementing. The DO/DON'T + numeric criteria pattern (T1) and form enumeration (T2) are immediately actionable with high confidence.
