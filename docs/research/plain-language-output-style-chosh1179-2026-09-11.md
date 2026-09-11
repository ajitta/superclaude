---
status: complete
revised: 2026-09-11
---

# Plain Language output style: evidence review and A/B measurement

What this settles: the wording of `src/superclaude/output-styles/plain-language.md`, the first Claude Code output style SuperClaude ships, and how to re-measure it. The style started as a personal file in an Obsidian vault with Korean example phrases; it now ships language-neutral to every user.

## 1. Constraints that shaped the file

- **Global.** No text in a natural language other than English, no one language's example phrase, no rule that only makes sense for one language. `tests/unit/test_output_style_structure.py` fails on any non-Latin letter. The class of a tell generalizes ("decorative contrast", "translationese"); its instances do not.
- **`keep-coding-instructions: true`.** Claude Code drops its own software-engineering instructions (scoping changes, verifying work) from the system prompt for a custom style unless this field is set (https://code.claude.com/docs/en/output-styles, "How output styles work"). A style from a coding framework must keep them; the test enforces the field.
- **Sent with every request.** Body capped at 600 words by the same test. Shipped body: 590 words.
- **Positive form for formatting.** Anthropic's Fable 5.1 prompting page: "If your prompt contains anti-formatting language, remove it or replace it with a rule that says when specific formatting is appropriate." The formatting rule names when bullets, headings and bold are appropriate instead of forbidding them.

## 2. Evidence behind each change from the vault draft

Sources were fetched by a research delegate on 2026-09-11 and spot-checked here (raw Wikipedia wikitext, the Fable 5.1 prompting page, the 국립국어원 paper). Tavily was quota-exhausted; everything came through WebSearch/WebFetch.

| Change | Source |
|---|---|
| Translationese named as a class: "possession, passive, prepositional, or plural patterns" carried over from another language | 김순영, 새국어생활 22(1) 2012: 번역투 as "영어의 구조가 그대로 전이된" sentences; the three classes there are 구문 (have→가지다, by→에 의하여 피동), 굴절 (복수 '-들'), 전치사구 (~에 관하여, ~로부터). The instances are Korean; the class is not. |
| "Use the same term for the same thing throughout" | Wikipedia:Signs of AI writing, "elegant variation" (synonym cycling). |
| "Keep one register of formality throughout a response" | Observed in this study, not in a source: the v1 Korean probe on Opus 5 mixed 습니다체 and 해요체 in one reply under both conditions. |
| Dash rule: commas, colons or parentheses first | Wikipedia AISIGNS "Style": em dashes "in places where humans are more likely to use commas"; the same page cites a July 2026 study finding "only Claude used em dashes more than professional writers" (study not located; treat as unverified). Korean press describes the same tell ("줄표를 쉼표 자리에 남발", 오마이뉴스 2026-09-06). |
| Bold only for a term the reader must find again | AISIGNS "Style": boldface overuse in a "key takeaways" fashion. |
| Name the source or state the claim as your own | AISIGNS "Vague attributions" ("Experts argue", "Industry reports"). |
| Literal phrase over metaphor, "is" over "serves as" | Fable 5.1 prompting page, "Writing density": "Mannered prose substitutes metaphor and flourish for direct statement … When a literal phrase is available, use it." AISIGNS "Avoidance of copulatives". |
| Mark reproduced source text as a quotation | Fable 5.1 prompting page, "Quoting retrieved sources". |
| All three contrast shapes ("not just X but Y", "Y rather than X") | AISIGNS "Negative parallelisms" lists three subtypes; the draft covered one. |
| Warning phrases cut from six to two, class named first | Anthropic prompting best practices: "Tell Claude what to do instead of what not to do"; arXiv 2511.12381 (negation rebound: "do not mention X" raises X's accessibility); arXiv 2507.11538 (instruction density degrades compliance, earlier instructions win). arXiv 2604.02699 finds short ban lists do not hurt, so two examples stay. |
| "A bare acknowledgement is not a reply" | Claude Fable 5.1 system prompt (2026-09-01): "a sign-off alone, such as 'Done.', is not a reply". |
| Silent-revision list merged from six items to four | Same density evidence; Opus 5 prompting page warns verification instructions cause over-verification. |
| Dropped: "Include technical detail when it helps …", "Use abstract or fashionable terms when technically correct …" | Deletion test (`.claude/rules/content-quality.md`): both restate the opening "keep enough detail" and "precise common words" rules. |
| Not added: "do not mention being an AI or a knowledge cutoff" | AISIGNS lists it, but for encyclopedia text; a Claude Code turn does not produce it. Fails the deletion test. |

## 3. A/B measurement

Method: `claude -p "<prompt>" --model <model> --output-format text` from an empty scratch directory (the model reads any file in cwd as an environment fact). Style condition adds `--settings '{"outputStyle":"Plain Language"}'` with the file at `.claude/output-styles/plain-language.md` in that directory; default condition has neither. Four prompts, two languages, unrelated domains: a Flask production-only 500 (en), where to start testing a React project with no tests (ko), optimistic vs pessimistic locking (en), the first paragraph of a payments-team onboarding doc (ko). Counters are regexes over the output (`scratchpad/probe/score.py`, not committed): headers, bullets, bold spans, em dashes, "not just X but Y" shapes, importance signposts, praise openers, closing offers, recaps. Single run per cell.

Opus 5, shipped wording:

| prompt | cond | words | headers | bullets | bold | em-dash | closer-offer | recap |
|---|---|---|---|---|---|---|---|---|
| en-debug | default | 474 | 6 | 0 | 5 | 6 | 0 | 0 |
| en-debug | style | 451 | 1 | 5 | 8 | 5 | 0 | 0 |
| en-explain | default | 687 | 4 | 14 | 10 | 9 | 0 | 0 |
| en-explain | style | 628 | 3 | 6 | 2 | 3 | 0 | 0 |
| ko-testing | default | 355 | 7 | 5 | 7 | 1 | 0 | 0 |
| ko-testing | style | 355 | 5 | 2 | 3 | 3 | 0 | 0 |
| ko-writing | default | 170 | 1 | 0 | 3 | 1 | 0 | 0 |
| ko-writing | style | 117 | 0 | 0 | 0 | 0 | 0 | 0 |

Fable 5.1, shipped wording:

| prompt | cond | words | headers | bullets | bold | em-dash | closer-offer | recap |
|---|---|---|---|---|---|---|---|---|
| en-debug | default | 417 | 0 | 9 | 9 | 0 | 0 | 0 |
| en-debug | style | 513 | 1 | 6 | 4 | 0 | 1 | 0 |
| ko-testing | default | 252 | 0 | 4 | 8 | 0 | 0 | 0 |
| ko-testing | style | 260 | 0 | 0 | 5 | 0 | 0 | 0 |

The same prompts were run three times over the day on Opus 5 (vault draft, then two revisions differing by one sentence). Run-to-run variance is large: the styled Korean testing answer had 0 headers and 0 em dashes in one run and 5 and 3 in the next, under wording that differs only in the closing-offer sentence. Read the tables as direction, not magnitude.

Reading: on Opus 5 the style cuts headers, bullets and bold in every run and shortens answers by 5 to 30 percent without dropping content (the styled en-debug still carries the log commands, the ranked causes and a curl reproduction). Fable 5.1's default is already clean on the classic tells (no headers, no em dashes, no praise openers in either condition), so the style's effect there is small: it removes bullets and a closing recap in the Korean answer and keeps one formality register throughout. The last revision added "Ask for input only when the work cannot proceed without it" and "offer of variants" to the closing rule after the styled onboarding-paragraph answer ended with an offer to produce alternative versions; after the change that answer ends with the fill-in instructions instead. Requests for a missing traceback still close the debugging answers, which the blocker rule permits.

Injection was verified directly, not inferred from output shape: asked to quote the first sentence of any output-style instructions, Opus 5 quoted "Write natural, direct prose in the user's language." with the file under the working directory's `.claude/output-styles/` and `outputStyle` set, and again with the file under `~/.claude/output-styles/`; with the file present but no `outputStyle` selection, and in a control with no file, it answered that there was no output style. So the file alone does nothing until selected, at either level.

Residual: bold is still used as an inline heading ("**Runner setup.**") in both conditions on both models, despite the rule limiting bold to terms the reader must find again. Not iterated further; a stronger rule risks the anti-formatting over-correction Anthropic warns about for Fable.

## 4. Not shipped, kept for a Korean variant

Korean-specific 번역투 instances (~을 가지다, ~에 의해 피동, ~에 있어서, ~에 다름 아니다, '-들' 남용, 무생물 주어) are documented in the 국립국어원 paper above and belong in a user's own CLAUDE.md or a per-language style, not in the global file. Claims about "~하는 것이 중요합니다", "~알아보겠습니다", 존댓말 겹침 and 개조식 as AI markers had community sources only and were not adopted.
