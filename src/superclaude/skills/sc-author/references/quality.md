---
sources:
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices", retrieved: 2026-10-14}
  - {url: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices", retrieved: 2026-10-14}
  - {url: "https://code.claude.com/docs/en/memory", retrieved: 2026-10-13}
  - {url: "https://code.claude.com/docs/en/sub-agents", retrieved: 2026-10-13}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5", retrieved: 2026-10-14}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5", retrieved: 2026-10-14}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5", retrieved: 2026-10-14}
  - {url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1", retrieved: 2026-10-14}
---

# Quality and no-op review

## Contents

- Writing guidance: what Anthropic's guides say makes an instruction work
- Load set: which documents are read together
- Judgment questions: when a sentence changes nothing
- Keep: sentences that look like no-ops but are not
- Harm: sentences worse than a no-op
- Removal evidence: what each removal candidate must show
- Model differences: what each current model already does
- Audit checklist

## Writing guidance

Each point names the guide section it comes from.

- Be explicit about the result wanted. Write for a capable colleague who lacks the context: if they would be confused, Claude will be too. (Prompting best practices, "Be clear and direct")
- Give the reason behind a rule. Claude generalizes from the explanation to cases the rule does not list. (Prompting best practices, "Add context to improve performance")
- Say what to do rather than what not to do: "write flowing prose paragraphs", not "do not use markdown". (Prompting best practices, "Control the format of responses")
- Specific beats vague: "Use 2-space indentation", not "Format code properly". (Memory docs, "Write effective instructions")
- Strong emphasis over-triggers on current models: "CRITICAL: You MUST use this tool when…" becomes "Use this tool when…". (Prompting best practices, "Tool usage")
- Add only what Claude does not already know; each paragraph must justify its tokens. (Skill best practices, "Concise is key")
- Match specificity to fragility: exact commands for fragile, order-dependent operations; general direction where many approaches work. (Skill best practices, "Set appropriate degrees of freedom")
- Use one term for one thing throughout. (Skill best practices, "Use consistent terminology")
- Leave out information that expires with a date; keep old behavior in a clearly marked old-patterns section if it is still needed. (Skill best practices, "Avoid time-sensitive information")
- Examples steer format and tone reliably: 3 to 5, relevant and varied, each wrapped in `<example>` tags. (Prompting best practices, "Use examples effectively")

## Load set

Whether a sentence is a no-op depends on what is read with it. Settle this before judging duplicates, contradictions or restated defaults.

| Document | Read together with |
|---|---|
| CLAUDE.md, CLAUDE.local.md, rules without `paths` | each other and every file their `@` imports reach, at session start |
| AGENTS.md | the same set, but only when no CLAUDE.md or CLAUDE.local.md exists in the working directory or above, or when a CLAUDE.md imports it |
| Rule with `paths` | the session-start set, plus every other rule matching the same files |
| Subagent body | the CLAUDE.md hierarchy and rules (unless `omitClaudeMd: true`), not the conversation |
| Skill body | the session-start set, plus the files the body tells Claude to read |
| Output style | the session-start set |
| MEMORY.md index | the session-start set; each line costs every session, topic files only when opened |

Check who reads the file. Another tool may read only AGENTS.md; a line that changes nothing for Claude may be that tool's only instruction.

## Judgment questions

Ask these of each sentence, not of a whole rule: one sentence of a rule can be a no-op while the next adds behavior.

- Restated default: would Claude or the harness do this anyway? The answer can differ per model, so the evidence is the harness's own text, a row in Model differences, or a run with and without the sentence. Yes: candidate.
- Vague: does it name an observable trigger, a concrete target or a threshold? No: candidate, or a rewrite that adds one.
- Enforced elsewhere: does a hook, test or linter catch it inside the author's normal loop, before the mistake costs anything, with a failure message that says how to fix it? All three yes: candidate. Any no: keep.
- Fact or reason: does the fact change a decision the reader makes? No: candidate.
- Repeated in other words: does another sentence in this document or the load set already give the same instruction, for example a numbered step restating a rule or the output layout? Yes: candidate; keep the copy where a reader looks for it. The checker finds only word-for-word repeats.

<example>
Sentence: "Run independent tool calls in parallel."
Question: restated default. The harness system prompt already says this.
Verdict: candidate. Evidence: the harness text.
</example>

<example>
Sentence: "Double-check your answer before responding."
Question: restated default. Opus 5 and Opus 5.5 already verify; Sonnet 5.5 at low effort may skip a real check.
Verdict: candidate on Opus; on Sonnet, replace it with the concrete check to run.
</example>

<example>
Sentence: "Run the linter before committing."
Question: enforced elsewhere. CI runs the linter, but only after a push.
Verdict: keep. The enforcement runs after the mistake costs a failed build.
</example>

## Keep

These look like no-ops and are not:

- A recorded "no" that stops a suggestion Claude would otherwise make.
- An instruction that reverses a default habit.
- A harness quirk Claude cannot know from the model alone.
- A note that stops a leftover from being misread, such as a test fixture named after a removed tool.
- A rule whose evidence location is stale: fix the location, keep the rule.

## Harm

Report these before any no-op candidate. A stale sentence often does more damage than an idle one.

- It calls for work that is wrong now: a task already finished or abandoned, a feature that was removed.
- It makes Claude claim a check it did not run: an instruction to use a tool the subagent's `tools` leaves out.
- It contradicts another loaded sentence: one of the two is always wrong, and Claude may pick either.
- It cites a source that does not say what the sentence claims.

## Removal evidence

- A checker candidate quotes the failed check as printed: `path:line: CODE grade: message`.
- A judgment candidate shows the question, the answer, and the evidence: harness text, a Model differences row, or a with/without run.
- Every candidate stays a candidate until the person approves it in the diff. Reformatting removes nothing.

## Model differences

What each model does by default, for the "restated default" question. A cell that says "not stated" means the model's guide does not cover it: judge from a run, not from this table.

| Model | Verification | Scope | Progress updates | Length and format | Subagents |
|---|---|---|---|---|---|
| claude-opus-5-5 | not stated as a default ("Time signals for multiagent harnesses": verifies less under a time budget) | gets to work quickly; explore first on loose multi-app tasks ("Explore context in multi-app workflows") | short updates between tool calls by default ("User-facing progress updates") | fewer tokens than Opus 5; reports plainly what it did (guide introduction) | runs long work with parallel subagents ("Capabilities relevant to prompting") |
| claude-sonnet-5-5 | checks its work before reporting; at low effort may skip a real check ("Verification on coding tasks") | adds tests, docs and files at every effort; core change stays close to the request ("Steer initiative and scope") | notes between tool calls by default; remove "hold findings for the end" lines ("User-facing progress updates") | not stated | at xhigh and max may start reviewer subagents ("Steer initiative and scope") |
| claude-opus-5 | verifies unasked; remove verification and re-check instructions ("Task scope and over-verification", "Self-correction") | can add unrequested steps; constrain scope for narrow tasks ("Task scope and over-verification") | narrates readily; describe the cadence wanted ("User-facing progress updates") | longer responses and files; a short conciseness instruction works ("Response length and verbosity") | delegates readily; give limits ("Controlling subagent spawning") |
| claude-fable-5-1 | not stated as a default; searches less at low effort ("Search triggering at low effort") | may fix nearby code or add tests; follows explicit leave-out instructions ("Keep changes and tests to what the task asks for") | fewer updates than Fable 5; remove lines suppressing narration ("Ask for user-facing progress updates") | less bold, fewer headers and lists; drop anti-formatting rules ("Formatting in chat") | lead agent may wait on subagents ("Let the lead agent keep working while subagents run") |

## Audit checklist

| Area | Question |
|---|---|
| Fields | Does every frontmatter field appear in `fields.yaml` for this type? |
| Trigger | Does the description say what it does and when to use it, in third person? |
| Structure | Is always-needed procedure in the body and sometimes-needed detail in a linked file? |
| Load set | Which documents are read with this one, and by which tool? |
| No-op | For each sentence: does a judgment question say it changes nothing? |
| Harm | Does any sentence call for wrong work, a check that cannot run, or contradict another? |
| Project fit | Does the result match the project's language, terms and layout? |
