# Agent Memory Utilization — Investigation, Analysis, Application

> **Date**: 2026-07-24 · **Author**: ajitta + Claude (Fable 5)
> **Question**: How can Claude Code's subagent memory feature (`memory:` frontmatter) actually be utilized, and why has SuperClaude's 23-agent memory system accumulated nothing?
> **Method**: 4-track parallel investigation (repo wiring / CC feature mechanics / empirical accumulation / ecosystem patterns) + 2 live smoke tests on CC 2.1.218.

## 1. Summary

All 23 SuperClaude agents ship `memory: project` + `<memory_guide>` categories, yet after ~5.5 months of feature availability, **zero memory accumulated at any scope**. Root cause: **agents are almost never invoked** — zero agents were installed at any scope at investigation time, and only 1 subagent spawn exists in all surviving transcripts (self-review, Jul 5). Secondary cause: the WHEN/HOW write protocol (`agent_memory_protocol`) lived in `RULES_QUALITY.md`, which is injected into the *main* session only — subagents receive only their own markdown body, so no shipped instruction to write ever reached the memory owners.

Two live smoke tests on CC 2.1.218 proved the substrate works (both known upstream bugs refuted), so the content-layer fix was applied: the write protocol now ships inside every agent's `<memory_guide>`, enforced by test.

## 2. CC Feature Mechanics (confirmed against docs + live test)

- `memory: user | project | local` → storage `~/.claude/agent-memory/<agent>/` | `.claude/agent-memory/<agent>/` | `.claude/agent-memory-local/<agent>/`.
- At subagent spawn, CC auto-injects the first **200 lines / 25KB** of the agent's `MEMORY.md` (whichever limit hits first); content beyond that is not loaded. Detail belongs in topic files the agent Reads on demand.
- CC provides **no built-in maintenance guidance** — the agent definition must carry the write/curate protocol itself.
- Memory-file writes are **auto-enabled even under restrictive tool allowlists** (verified live, see §3).
- Separate system from main-session auto-memory and from the API memory tool; only the injection pattern (index-first, 200-line cap) is shared.

## 3. Empirical Findings (this machine, CC 2.1.218)

| Finding | Evidence |
|---|---|
| Zero accumulation, all scopes | `~/.claude/agent-memory/` empty since Feb 6 birth; `.claude/agent-memory*/` empty dirs only |
| Agents not installed | `~/.claude/agents/` = `.DS_Store` only; repo `.claude/agents/` absent (pre-test); no plugin |
| 1 subagent spawn in all surviving transcripts (Jul 4–24) | single `self-review` spawn Jul 5 — created its memory dir, wrote nothing |
| **Smoke test 1: mechanism works** | local-scope install → headless spawn with explicit write instruction → `MEMORY.md` created with correct entry |
| **Bug #31294 refuted on 2.1.218** | "Task-spawned subagents never create/update MEMORY.md" did not reproduce |
| **Bug #57507 refuted on 2.1.218** | self-review has `tools: Read, Grep, Glob, Agent` (no Write/Edit) AND session ran `--allowedTools "Task"` — memory write still succeeded → memory auto-enable overrides both allowlists |
| Propensity untested pre-fix | the one organic spawn wrote nothing — consistent with protocol never reaching subagents |
| **Post-fix probe: no spontaneous write** | self-review with protocol-bearing body reviewed a toy plan, wrote nothing — ambiguous: selective gate correctly filtering a no-lesson task, or protocol ignored; n=1 cannot distinguish. Resolution deferred to the §7 metric on real workloads |

Caveat (probe-observer-effect gotcha): smoke tests ran `claude -p` from inside the repo; they verify **mechanism**, which is context-immune. Spontaneous-write **propensity** requires the shipped protocol lines (§5) and longer observation.

## 4. 활용 방안 Catalog (utilization patterns)

| # | Pattern | Mechanism | Failure mode |
|---|---|---|---|
| 1 | Index + topic files | 200-line/25KB `MEMORY.md` index auto-injected; detail in topic files read on demand | index rot — useful lines fall past the injection cutoff |
| 2 | Bracketed reflection | consult memory at start, distill ≤3 lines at end *only if a future run would act differently* | reflexive low-value writes → bloat |
| 3 | Selective write gate | before storing: novel? non-contradictory? behavior-changing? (~10% absolute gain in cited benchmarks; add-all collapse: 13% vs 39%) | over-strict gate loses rare failure lessons |
| 4 | Promotion to rules | recurring agent-memory lessons promoted to `.claude/rules/gotchas/`, deleted from source on promotion | duplication if promotion doesn't delete |
| 5 | Staleness gardening | `Last reviewed` header + periodic pass (merge/retire/verify) | nobody owns the pass |
| 6 | Type-tagged sections | semantic / procedural / episodic sections with different lifecycles | over-taxonomizing an empty store |
| 7 | Progress-log | memory as recovery journal for long multi-session agents | stale progress claims treated as fact |
| 8 | VCS-reviewed team memory | `memory: project` → committable; PR diff review = poisoning trust boundary | unreviewed merges reintroduce poisoning risk |

Rejected for this project (simplicity constraints): shared memory banks via hooks, vector retrieval, background consolidation — grep + index pointers win below thousands of entries.

## 5. Applied Changes (this commit)

1. **Write protocol relocated to the correct layer.** The 2-line protocol now opens every agent's `<memory_guide>` (23/23), replacing the main-session-only `<agent_memory_protocol>` in `core/rules/RULES_QUALITY.md` (removed; `RULES.md` module index updated):
   ```
   MEMORY.md = prior lessons; verify against current state before acting on them.
   After task: append `- YYYY-MM-DD: Category-Name: lesson` (max 3 lines) only if a future run would act differently; consolidate at 150 lines.
   ```
   This restores the Read/Format rules dropped from the original design spec (`docs/archive/specs/2026-03-20-agent-memory-effectiveness-design-chosh1179.md` §3) and fuses the ecosystem-validated selective-write gate (pattern 3).
2. **Authoring contract updated.** `.claude/rules/agent-authoring.md`: skeleton + Memory Guide section now require the protocol header verbatim; capture triggers (corrections, decisions, 3+ recurrences, surprises) documented for authors.
3. **Test enforcement.** `tests/unit/test_agent_structure.py::test_memory_guide_has_protocol` — every agent must carry the entry-format and consolidation lines. Full suite: 2062 passed.

## 6. Deferred (in recommended order, gated on accumulation evidence)

- **P2 — standing project-scope install** (user decision): agents cannot accumulate memory while uninstalled. Options: commit synced `.claude/agents/` (needs `.gitignore` change — `.claude/agent-memory*/` at line 104 also blocks committing memory itself) or keep `make sync-local` habitual in dev sessions. Highest-impact open item — without invocations, §5 changes stay dormant.
- **P4 — extend `/sc:reflect` gardening glob to `.claude/agent-memory/**`** — worthless until content exists.
- **P5 — promotion path**: one sentence in R19 routing recurring agent-memory lessons to gotchas (delete-on-promote).
- **P6 — "Related:" pointers stay documentation-only** — no cross-agent read machinery until ≥1 quarter of real memory exists.
- **P7 — warn-on-no-match in `_rewrite_agent_memory_scope`** (string-fragile `replace`, `install_components.py:43`) — only while touching the installer anyway.

## 7. Success Metric

Non-empty `MEMORY.md` count across `.claude/agent-memory*/*/`. Baseline from the original spec: 6/22 agents pre-design; current: 0/23; target: any nonzero count with entries matching `<memory_guide>` categories after one month of real agent invocations.

## Sources

- Workflow run `wf_6b3c81b3-e0c` (4 investigation reports + synthesis), session `d3995da9`, 2026-07-24.
- CC docs: `code.claude.com/docs/en/memory.md` (v2.1.210 limit-measurement note), sub-agents doc.
- GitHub issues #31294 (closed-inactive, unfixed upstream; refuted here on 2.1.218), #57507 (refuted here on 2.1.218).
- `docs/archive/specs/2026-03-20-agent-memory-effectiveness-design-chosh1179.md` (original 6-line protocol design).
