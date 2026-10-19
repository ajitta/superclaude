---
feature: install-upgrade-audit
phase: intent
status: approved
owner: ajitta
created: 2026-10-19
revised: 2026-10-19
---

# 00. Intent — install / upgrade path audit (axis C)

## Original request

After the purpose-opus round closed (v4.29.6) and the remaining-work list recommended axis C:

> c install upgrade path audit 진행

Plan v1 → independent review (APPROVE WITH CHANGES, P-1–P-11) → plan v2 with Q1–Q16, each with a recommended option, put to the owner in chat:

> 추천대로

## Question

Does a real user's upgrade (an older SuperClaude install, then the current CLI) and a later uninstall end in the state the code and README promise, at every scope (user / project / local), without touching user content? The over-engineering audit covered deletability; this round covers correctness.

## Decisions (all recommended options)

| Q | Decision |
|---|---|
| Q1 | Source versions: the fork era — v4.29.5, v4.20.1, the untagged boundaries in the plan's §3, and v4.1.9 as root (checked only for "deletes nothing foreign") |
| Q2 | Windows: synthetic inputs + an owner checklist, plus a `workflow_dispatch`-only `windows-latest` job running only the scenario module |
| Q3 | Stale content after a non-force install: keep skip semantics; install prints that N files differ and how to refresh; `doctor` gets an advisory tier (exit 0) |
| Q4 | `update` refuses (exit 1) at a scope with no install and names the one found; `install --force` creating a scope warns; remediation lines carry `--scope` |
| Q5 | Fix S1/S2 findings in this round; S3 to the backlog |
| Q6 | CI: network-free fixture tests in the default run |
| Q7 | Branch `fix/install-upgrade-audit` |
| Q8 | One release at round end |
| Q9 | `verify-drift`: EXTRA only for ever-shipped names in `agents/`, `output-styles/`; retired SC skill dirs reported `RETIRED`; foreign files ignored |
| Q10 | Retirement guard: shipped-names history from full git history, hook ids and events, plus a test |
| Q11 | Uninstall leftovers: remove a memory dir only if empty; warn when a non-empty `agent-memory-local/` loses its exclude; remove `~/.claude/CLAUDE.md` only if it holds nothing but SC's heading; keep and document `insights.pending.jsonl` |
| Q12 | `--remove-mcp` removes a server only if its command matches `MCP_SERVERS` (if the collision is confirmed) |
| Q13 | A committed retired hook-identity list; install (force or not), `update` and uninstall remove matching SC inner hooks; `superclaude/scripts/` untouched |
| Q14 | The one-day `.claude/hooks/<x>.py` era: unsupported, with an upgrade note |
| Q15 | `CLAUDE_CONFIG_DIR`: install and doctor warn when it is set and differs (honouring it goes to an ADR) |
| Q16 | Encoding preflight: every command validates settings and CLAUDE files before its first write or delete and refuses non-UTF-8 / BOM input (exit 1, nothing changed) |
| C-06 (P4 owner checkpoint) | **(b)**: keep refusing the `memory: user`-era project install, but advise `superclaude update --scope project`; conflict advice never names a scope whose base is not this one. Owner: "b" |

Model sessions: 1 (the P7 independent diff verifier), 2 if it blocks once. Sandbox only — the real `~/.claude` is never touched; no `make sync-*` on this VM.

Plan: `.hermes/plans/2026-10-19_axis-c-plan-v2.md` (v1 and the review alongside); committed split into `05-plan.md` / `05a` / `05b` during P0.
