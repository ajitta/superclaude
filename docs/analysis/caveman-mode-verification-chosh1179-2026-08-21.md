---
status: draft
revised: 2026-08-21
---

# Caveman mode — behavior verification from session logs

A log-based check of whether the `caveman@caveman` plugin's compression mode does what its skill
definition says it does. No configuration or installation inspection: every number below comes from
Claude Code session transcripts.

## Method

**Corpus.** `~/.claude/projects/**/*.jsonl`, window 2026-07-22 → 2026-08-21 (Claude Code rotates
transcripts, so this is all that survives). A session counts as caveman-ON if the
`CAVEMAN MODE ACTIVE` hook marker appears anywhere in it.

**Control.** The primary comparison is within one project — `oasis-nakama-dev` — where 87 sessions
ran with the mode on and 4 with it off. Same user, same repository, same kind of work. Cross-project
figures are given where they add signal and labelled as such.

**Measurement.** Only assistant `text` blocks are counted; tool calls are excluded. Fenced code
blocks and inline code are stripped before any prose metric, so code samples do not inflate symbol
counts. Rates are normalized to the script that carries the feature: Korean politeness per 10,000
hangul characters, English articles per 10,000 latin characters, symbols per 10,000 prose
characters.

**Corpus size.** Caveman-ON prose 944,847 characters against OFF 115,452 across all projects; within
`oasis-nakama-dev`, 864,327 against 68,047.

---

## What holds

### Style rules are followed

| Metric | ON | OFF | ON/OFF |
|---|---|---|---|
| Korean politeness endings (습니다/입니다/합니다/하세요/해요), per 10k hangul | 2.10 | 86.44 | 2% |
| English articles (the/a/an), per 10k latin | 31.27 | 68.38 | 46% |
| Invented abbreviations (cfg/impl/req/res/fn/msg/attr/param), per 10k prose | 0.07 | 0.00 | — |
| Self-reference ("caveman"), per 10k prose | 0.31 | 0.34 | 90% |

Politeness endings are effectively eliminated — a 98% reduction, and the single clearest signal in
the data. Articles are halved rather than dropped; the skill says "Drop: articles (a/an/the)", and
31 per 10k latin characters is a long way from zero, so this is partial compliance. Invented
abbreviations are absent, which matters because the skill explicitly forbids them on the grounds
that they save no tokens. Self-reference does not rise, so the "never name or announce the style"
rule holds.

### The mode does not decay over long sessions

The skill claims "ACTIVE EVERY RESPONSE. No revert after many turns." Splitting each caveman-ON
session into five equal parts by assistant-message index (68 sessions in `oasis-nakama-dev`):

| Session quintile | Politeness / 10k hangul | Articles / 10k latin |
|---|---|---|
| 1st | 2.48 | 30.78 |
| 2nd | 0.56 | 33.64 |
| 3rd | 1.02 | 37.61 |
| 4th | 3.60 | 24.46 |
| 5th | 3.07 | 16.55 |

Politeness stays between 0.6 and 3.6 across the whole session against an off-mode baseline of 86.4;
articles decline rather than recover. No drift. The persistence claim is supported.

### Language is preserved

Caveman-ON output is 25.0% hangul by character; OFF output is 6.4%. Korean prompts get Korean
answers — the mode compresses the style, not the language, which is what the skill specifies.

### The "persisted outside chat" boundary holds, decisively

The skill carves out anything written to a durable artifact — code, commits, docs, issue text — as
normal prose. Measuring article density in the 253 `git commit` bodies authored during caveman-ON
sessions:

| Text | Articles per 10k latin |
|---|---|
| Commit bodies written in caveman-ON sessions | **174.4** |
| Caveman-ON chat prose | 31.3 |
| Non-caveman chat prose | 68.4 |

Commit bodies are not merely un-compressed — they are 2.6× denser in articles than ordinary
un-compressed chat, which is what full explanatory prose looks like. A sample:

```
fix(sw): fall through to read-through when bare-read revalidation fails

The CASE 3 bare-read path threw when the HEAD revalidation could not run
(relay timeout or transport error). That error does not match the S3-shaped
404 test in the fetch handler, so it surfaced as a terminal 503.
```

The boundary rule is the most reliably observed rule in the whole corpus.

---

## What fails

Three constructs the skill bans outright all become **more** frequent when the mode is on. Same
project, ON versus OFF:

| Construct | ON | OFF | Ratio |
|---|---|---|---|
| Causal arrows `→`, per 10k prose | 27.6 | 12.9 | 2.1× |
| Emoji, per 10k prose | 10.0 | 1.3 | 7.7× |
| Markdown table rows, share of prose lines | 11.0% | 4.8% | 2.3× |

The skill's own words: *"No causal arrows (→) either — own token, save nothing"* and *"no decorative
tables/emoji"*. Cross-project figures agree (arrows 26.8 vs 9.2; emoji 9.4 vs 1.3).

The emoji are not ornamental in intent — they are severity and status markers:

```
🔴 265   ✅ 166   ⚠ 130   🟡 88   ✕ 70   ✓ 59   🟢 48   ❌ 31
```

**Reading.** This is a side effect of the compression instruction rather than disobedience. Told to
drop articles, filler and connective prose, the model reaches for telegraphic notation: an arrow
instead of a verb, a coloured circle instead of the word "critical", a table instead of a paragraph.
Those are exactly the substitutions the skill forbids, and for exactly the reason it gives — they
cost a token each and save nothing. The rule is stated but the pressure of the surrounding
instruction runs against it.

**A contributing contradiction.** The plugin's own `cavecrew-reviewer` subagent specifies its output
format as `path:line: <emoji> <severity>: <problem>. <fix>.` — it *requires* the emoji the main
skill bans. A model reading both surfaces has no consistent rule to follow.

---

## The token claim

The plugin advertises "Cuts output tokens 65% (measured)". Measured here, in `oasis-nakama-dev`:

| Metric | ON | OFF | ON/OFF |
|---|---|---|---|
| `output_tokens` per assistant message, mean | 959.6 (n=27,957) | 1,244.1 (n=1,952) | 77% |
| `output_tokens` per assistant message, median | 603.0 | 873.5 | 69% |
| `output_tokens` per user turn, mean | 1,559.9 (n=88 sessions) | 2,485.8 (n=4) | 63% |
| `output_tokens` per user turn, median | 1,395.9 | 2,514.9 | 56% |
| Text characters per message, median | 83 | 94 | 88% |
| Text characters per message, **mean** | 370 | 197 | **188%** |

Per message the reduction is **23–31%**, not 65%. The per-turn figures (37–44%) are closer to the
claim but rest on four control sessions and should not be leaned on.

The last two rows are the interesting pair. The median message gets shorter while the mean nearly
doubles — a distribution that stretches at the top. Compressed short replies coexist with much
longer structured reports, and those reports are built from the tables and emoji counted in the
previous section. The same mechanism that breaks the notation rules also works against the token
goal.

---

## Limitations

- **The control group is thin.** Four off-mode sessions and 1,952 assistant messages, against 87
  sessions and 27,957 messages on. A difference in task mix between the two groups cannot be ruled
  out, and the per-turn token figures in particular carry wide uncertainty.
- **Thirty-day window.** Transcripts before 2026-07-22 are gone. The mode was adopted in May 2026,
  so the immediate post-adoption period is unobservable.
- **`output_tokens` overstates the denominator.** It includes tool-call JSON and thinking, neither of
  which caveman compresses, so the per-message reduction figure *understates* prose compression.
- **Injection cadence is not measurable.** The `CAVEMAN MODE ACTIVE` reminder is stored on
  `type: "attachment"` records (713 in this project), which cannot be mapped one-to-one onto user
  prompts. No claim is made here about how often the hook fires; the drift table is the behavioral
  evidence instead, and it needs no such mapping.

## Verdict

Style compliance and persistence work: politeness, articles, abbreviations, language preservation
and the durable-artifact boundary all behave as specified, and none of them decay over long
sessions. Three explicitly banned constructs — arrows, emoji, tables — move in the wrong direction
under the mode, driven by the compression instruction itself and reinforced by a contradictory
subagent output spec. Token savings are real but roughly half to a third of the advertised figure at
the message level.

The actionable item, if the plugin is to be tuned, is the notation rules: they are stated as
prohibitions but compete with the compression directive that surrounds them, and the reviewer
subagent contradicts them outright.
